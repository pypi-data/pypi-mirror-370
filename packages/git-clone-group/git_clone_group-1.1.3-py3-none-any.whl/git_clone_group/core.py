import json
import os
import subprocess
from pathlib import Path
import requests
from urllib.request import urlopen
import argparse
from tqdm import tqdm
from typing import Set, List, Dict, Optional
import sys
import asyncio
import aiohttp
import warnings
from functools import wraps
from dataclasses import dataclass
import logging

# 禁用所有 aiohttp 相关警告
warnings.filterwarnings("ignore", category=ResourceWarning)
# 禁用 aiohttp 内部日志
logging.getLogger("aiohttp").setLevel(logging.ERROR)


class SessionManager:
    """全局会话管理器"""

    def __init__(self):
        self._session = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session is not None:
            await self._session.close()
            self._session = None


# 创建全局会话管理器
session_manager = SessionManager()


@dataclass
class GitLabConfig:
    gitlab_addr: str
    token: str
    dest_dir: Path
    branch: Optional[str] = None  # 指定要克隆或拉取的分支
    max_retries: int = 3
    timeout: int = 30
    max_concurrent_tasks: int = 5


@dataclass
class ProjectStats:
    """项目统计信息"""

    cloned: int = 0
    updated: int = 0
    empty: int = 0
    failed: int = 0
    empty_repos: List[str] = None  # 新增：存储空仓库列表

    def __post_init__(self):
        self.empty_repos = []


class GitLabError(Exception):
    """Base exception for GitLab operations"""

    pass


class GitLabPermissionError(GitLabError):
    """Permission denied error"""

    pass


class GitLabClient:
    def __init__(self, config: GitLabConfig):
        self.config = config
        self.session = None
        self.failed_projects = []

    async def __aenter__(self):
        self.session = await session_manager.get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 不在这里关闭会话，由全局管理器管理
        pass

    async def get_group_id_by_name(self, group_name: str) -> int:
        """Get group ID by group name/path."""
        # 首先尝试直接通过路径获取组信息
        url = f"http://{self.config.gitlab_addr}/api/v4/groups/{group_name}?private_token={self.config.token}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    group_data = await response.json()
                    return group_data["id"]
        except Exception:
            pass

        # 如果直接获取失败，则搜索组
        search_url = f"http://{self.config.gitlab_addr}/api/v4/groups?search={group_name}&private_token={self.config.token}"
        async with self.session.get(search_url) as response:
            response.raise_for_status()
            groups = await response.json()

            if not groups:
                raise GitLabError(f"Group '{group_name}' not found")

            # 优先查找完全匹配的组名或路径
            for group in groups:
                if (
                    group["name"] == group_name
                    or group["path"] == group_name
                    or group["full_path"] == group_name
                ):
                    return group["id"]

            # 如果没有完全匹配，返回第一个搜索结果
            if len(groups) == 1:
                return groups[0]["id"]

            # 如果有多个结果，让用户选择
            print(f"\nFound {len(groups)} groups matching '{group_name}':")
            for i, group in enumerate(groups, 1):
                print(f"{i}. {group['full_path']} (ID: {group['id']})")

            while True:
                try:
                    choice = input(f"\nSelect a group (1-{len(groups)}): ").strip()
                    index = int(choice) - 1
                    if 0 <= index < len(groups):
                        return groups[index]["id"]
                    else:
                        print(f"Please enter a number between 1 and {len(groups)}")
                except ValueError:
                    print("Please enter a valid number")
                except KeyboardInterrupt:
                    raise GitLabError("Operation cancelled by user")

    async def get_projects(self, group_id: int, page: int = 1) -> List[Dict]:
        """Get projects for a given group ID and page."""
        url = self._gen_next_url(group_id, page)
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    def _gen_next_url(self, target_id: int, page: int = 1) -> str:
        """Generate URL for getting group projects."""
        return f"http://{self.config.gitlab_addr}/api/v4/groups/{target_id}/projects?page={page}&private_token={self.config.token}"

    def _gen_subgroups_url(self, target_id: int) -> str:
        """Generate URL for getting subgroups."""
        return f"http://{self.config.gitlab_addr}/api/v4/groups/{target_id}/subgroups?private_token={self.config.token}"

    def _gen_global_url(self) -> str:
        """Generate URL for getting all projects."""
        return f"http://{self.config.gitlab_addr}/api/v4/projects?private_token={self.config.token}"

    async def get_sub_groups(self, parent_id: int) -> List[int]:
        """Get list of subgroup IDs for a parent group."""
        url = self._gen_subgroups_url(parent_id)
        async with self.session.get(url) as response:
            response.raise_for_status()
            groups = await response.json()
            return [group["id"] for group in groups]

    async def have_next_projects(self, group_id: int) -> bool:
        """Check if group has any projects."""
        url = self._gen_next_url(group_id)
        async with self.session.get(url) as response:
            response.raise_for_status()
            projects = await response.json()
            return bool(projects)

    async def retry_failed_projects(self, stats: ProjectStats):
        """重试失败的项目"""
        if not self.failed_projects:
            return

        retry_projects = self.failed_projects.copy()
        self.failed_projects.clear()

        print(f"Retrying {len(retry_projects)} failed projects...")
        for project in retry_projects:
            try:
                await clone_or_pull_project(self.config, project, stats)
            except GitLabPermissionError as e:
                print(f"Permission denied, skipping: {e}")
                stats.failed += 1
            except Exception as e:
                print(f"Retry failed: {e}")
                stats.failed += 1
                self.failed_projects.append(project)


async def clone_or_pull_project(
    config: GitLabConfig, project: Dict, stats: ProjectStats
) -> None:
    """Clone or pull a single project asynchronously."""
    project_url = project["ssh_url_to_repo"]
    project_path = project["path_with_namespace"]
    full_path = config.dest_dir / project_path

    async def run_git_command(command: List[str]) -> None:
        try:
            proc = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            stderr_text = stderr.decode()
            stdout_text = stdout.decode().strip()

            if proc.returncode != 0:
                if "Permission denied" in stderr_text:
                    raise GitLabPermissionError(f"Permission denied for {project_path}")
                raise RuntimeError(f"Git command failed: {stderr_text}")
            return stdout_text
        except GitLabPermissionError:
            raise
        except Exception as e:
            raise RuntimeError(f"Git operation failed: {str(e)}")

    async def safe_pull(path: Path) -> None:
        """Safe pull operation with fetch first"""
        try:
            # First fetch to update remote refs
            await run_git_command(["git", "-C", str(path), "fetch", "origin"])

            # 使用配置中指定的分支或项目默认分支
            target_branch = config.branch or project.get("default_branch", "master")

            try:
                # 检查本地分支是否存在
                current_branch = await run_git_command(
                    ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"]
                )

                # 如果当前分支不是目标分支，切换到目标分支
                if current_branch != target_branch:
                    try:
                        # 尝试切换到目标分支
                        await run_git_command(
                            ["git", "-C", str(path), "checkout", target_branch]
                        )
                    except RuntimeError:
                        # 如果分支不存在，创建新分支并跟踪远程分支
                        await run_git_command(
                            [
                                "git",
                                "-C",
                                str(path),
                                "checkout",
                                "-b",
                                target_branch,
                                f"origin/{target_branch}",
                            ]
                        )
            except RuntimeError:
                # 如果获取分支失败，检查是否为空仓库
                remote_branches = await run_git_command(
                    ["git", "-C", str(path), "branch", "-r"]
                )
                if not remote_branches:
                    stats.empty += 1
                    stats.empty_repos.append(project_path)
                    return

                # 尝试检出指定分支
                try:
                    await run_git_command(
                        [
                            "git",
                            "-C",
                            str(path),
                            "checkout",
                            "-b",
                            target_branch,
                            f"origin/{target_branch}",
                        ]
                    )
                except RuntimeError:
                    print(
                        f"Failed to checkout branch {target_branch} for {project_path}, skipping pull"
                    )
                    return

            # Pull using specific branch
            await run_git_command(
                ["git", "-C", str(path), "pull", "origin", target_branch]
            )
            stats.updated += 1
        except Exception as e:
            raise RuntimeError(f"Pull failed: {str(e)}")

    async def init_repo(path: Path) -> None:
        """Initialize new repository"""
        try:
            clone_cmd = ["git", "clone", project_url, str(path)]
            if config.branch:
                clone_cmd.extend(["-b", config.branch])
            await run_git_command(clone_cmd)

            if not path.exists():
                raise RuntimeError("Clone completed but directory not found")

            # 检查是否为空仓库
            try:
                await run_git_command(["git", "-C", str(path), "rev-parse", "HEAD"])
                stats.cloned += 1
            except RuntimeError:
                stats.empty += 1
                stats.empty_repos.append(project_path)
        except Exception as e:
            raise RuntimeError(f"Clone failed: {str(e)}")

    for attempt in range(config.max_retries):
        try:
            if full_path.exists():
                await safe_pull(full_path)
            else:
                await init_repo(full_path)
            return
        except GitLabPermissionError:
            raise
        except Exception as e:
            if attempt == config.max_retries - 1:
                print(
                    f"Failed after {config.max_retries} attempts for {project_path}: {e}"
                )
                stats.failed += 1
                raise
            await asyncio.sleep(1 * (attempt + 1))


async def process_group(
    config: GitLabConfig, group_id: int, stats: ProjectStats
) -> None:
    """Process a single group asynchronously with error handling."""
    async with GitLabClient(config) as client:
        page = 1
        while True:
            try:
                projects = await client.get_projects(group_id, page)
                if not projects:
                    break

                sem = asyncio.Semaphore(config.max_concurrent_tasks)

                async def bounded_clone(project):
                    async with sem:
                        try:
                            await clone_or_pull_project(config, project, stats)
                            return True
                        except Exception as e:
                            print(
                                f"Error processing {project['path_with_namespace']}: {e}"
                            )
                            stats.failed += 1
                            return False

                tasks = []
                for project in projects:
                    task = asyncio.create_task(bounded_clone(project))
                    tasks.append(task)

                with tqdm(
                    total=len(tasks), desc=f"Group {group_id} - Page {page}"
                ) as pbar:
                    for task in tasks:
                        try:
                            success = await task
                            if not success:
                                client.failed_projects.append(project)
                        except Exception as e:
                            print(f"Unexpected error: {e}")
                            client.failed_projects.append(project)
                            stats.failed += 1
                        finally:
                            pbar.update(1)

                # 重试失败的项目
                await client.retry_failed_projects(stats)

                page += 1
            except Exception as e:
                print(f"Error processing group {group_id} page {page}: {e}")
                break


async def cal_next_sub_group_ids(config: GitLabConfig, parent_id: int) -> Set[int]:
    """Calculate all subgroup IDs recursively."""
    parent_list = set()
    async with GitLabClient(config) as client:
        sub_ids = await client.get_sub_groups(parent_id)
        has_projects = await client.have_next_projects(parent_id)

        if sub_ids:
            if has_projects:
                parent_list.add(parent_id)
            for sub_id in sub_ids:
                parent_list.update(await cal_next_sub_group_ids(config, sub_id))
        elif has_projects:
            parent_list.add(parent_id)

    return parent_list


async def get_group_stats(config: GitLabConfig, group_ids: Set[int]) -> Dict[str, int]:
    """Get statistics for all groups"""
    total_projects = 0
    async with GitLabClient(config) as client:
        for group_id in group_ids:
            page = 1
            while True:
                projects = await client.get_projects(group_id, page)
                if not projects:
                    break
                total_projects += len(projects)
                page += 1

    return {"total_groups": len(group_ids), "total_projects": total_projects}


async def download_code(config: GitLabConfig, parent_id: int) -> None:
    """Download code for a group and all its subgroups with error handling."""
    try:
        print("Scanning groups and projects...")
        stats = ProjectStats()

        async with GitLabClient(config) as client:
            group_ids = await cal_next_sub_group_ids(config, parent_id)

            if await client.have_next_projects(parent_id):
                group_ids.add(parent_id)

            # 获取并显示初始统计信息
            initial_stats = await get_group_stats(config, group_ids)
            print(f"\nSummary:")
            print(f"- Total groups to process: {initial_stats['total_groups']}")
            print(
                f"- Total projects to clone/update: {initial_stats['total_projects']}"
            )

            # 请求用户确认
            response = input("\nDo you want to proceed? [y/N]: ")
            if response.lower() != "y":
                print("Operation cancelled by user")
                return

            print("\nStarting clone/pull operations...")
            sem = asyncio.Semaphore(config.max_concurrent_tasks)

            async def bounded_process(group_id):
                async with sem:
                    await process_group(config, group_id, stats)

            tasks = [bounded_process(group_id) for group_id in group_ids]
            await asyncio.gather(*tasks, return_exceptions=True)

            # 显示最终统计信息
            print("\nOperation completed!")
            print("Summary:")
            print(f"- Repositories cloned: {stats.cloned}")
            print(f"- Repositories updated: {stats.updated}")
            print(f"- Empty repositories: {stats.empty}")
            print(f"- Failed operations: {stats.failed}")
            print(
                f"- Total repositories processed: {stats.cloned + stats.updated + stats.empty}"
            )

            if stats.empty_repos:
                print("\nEmpty repositories:")
                for repo in sorted(stats.empty_repos):
                    print(f"  - {repo}")

    except Exception as e:
        print(f"Error in download_code: {e}")
    finally:
        # 确保会话被正确关闭
        await session_manager.close()


async def download_code_by_name(config: GitLabConfig, group_name: str) -> None:
    """Download code for a group by name and all its subgroups."""
    try:
        print(f"Looking up group: {group_name}...")

        async with GitLabClient(config) as client:
            # 根据组名获取组ID
            group_id = await client.get_group_id_by_name(group_name)
            print(f"Found group '{group_name}' with ID: {group_id}")

        # 使用现有的 download_code 函数
        await download_code(config, group_id)

    except GitLabError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error in download_code_by_name: {e}")


def cli() -> None:
    """Command line interface with improved argument handling."""
    parser = argparse.ArgumentParser(
        description="Clone all projects from a GitLab group and its subgroups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clone by group ID
  gcg -g gitlab.com -t token -i 123 -d ./repos
  
  # Clone by group name/path
  gcg -g gitlab.com -t token -n my-group -d ./repos
  
  # Clone specific branch
  gcg -g gitlab.com -t token -n my-group -b develop
        """,
    )

    parser.add_argument(
        "--gitlab-addr",
        "-g",
        required=True,
        help="GitLab server address (e.g. gitlab.com)",
    )
    parser.add_argument(
        "--token",
        "-t",
        required=True,
        help="GitLab private token (create from Settings > Access Tokens)",
    )

    # 创建互斥组，只能选择其中一个
    group_spec = parser.add_mutually_exclusive_group(required=True)
    group_spec.add_argument(
        "--group-id",
        "-i",
        type=int,
        help="GitLab group ID to clone (found in group page URL or settings)",
    )
    group_spec.add_argument(
        "--group-name",
        "-n",
        help="GitLab group name/path to clone (e.g. 'my-group' or 'namespace/my-group')",
    )
    parser.add_argument(
        "--dest-dir",
        "-d",
        default=".",
        help="Destination directory for cloned repositories (default: current directory)",
    )
    parser.add_argument(
        "--branch",
        "-b",
        help="Specify a branch to clone/pull (default: repository's default branch)",
    )

    args = parser.parse_args()

    config = GitLabConfig(
        gitlab_addr=args.gitlab_addr,
        token=args.token,
        dest_dir=Path(args.dest_dir),
        branch=args.branch,
        max_retries=3,
        timeout=30,
        max_concurrent_tasks=5,
    )

    try:
        if args.group_id:
            asyncio.run(download_code(config, args.group_id))
        else:  # args.group_name
            asyncio.run(download_code_by_name(config, args.group_name))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        # 确保清理所有资源
        asyncio.new_event_loop()


if __name__ == "__main__":
    cli()
