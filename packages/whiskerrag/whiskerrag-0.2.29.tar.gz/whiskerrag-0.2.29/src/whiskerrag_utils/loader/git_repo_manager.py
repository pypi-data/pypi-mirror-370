import hashlib
import logging
import os
import shutil
import tempfile
import zipfile
from typing import Any, Dict, Iterator, Optional, Tuple, Union

from whiskerrag_types.model.knowledge_source import GithubRepoSourceConfig

from .utils import log_system_info

logger = logging.getLogger(__name__)


def _check_git_installation() -> bool:
    """Check if git is installed in the system"""
    try:
        import subprocess

        subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _lazy_import_git() -> Tuple[Any, Any, Any]:
    """Lazy import git modules to avoid direct dependency"""
    try:
        from git import Repo
        from git.exc import GitCommandNotFound, InvalidGitRepositoryError

        return Repo, GitCommandNotFound, InvalidGitRepositoryError
    except ImportError as e:
        raise ImportError(
            "GitPython is required for Git repository loading. "
            "Please install it with: pip install GitPython"
        ) from e


def _lazy_import_requests() -> Any:
    """Lazy import requests module"""
    try:
        import requests

        return requests
    except ImportError as e:
        raise ImportError(
            "requests is required for GitHub zip download. "
            "Please install it with: pip install requests"
        ) from e


class MockCommit:
    """模拟 GitPython Commit 对象"""

    def __init__(
        self,
        sha: str,
        author_name: str = "Unknown",
        author_email: str = "unknown@example.com",
        message: str = "Mock commit message",
    ):
        self.hexsha = sha
        self.author = MockAuthor(author_name, author_email)
        self.message = message
        self.tree: Optional[MockTree] = None


class MockAuthor:
    """模拟 GitPython Author 对象"""

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email


class MockTreeItem:
    """模拟 GitPython Tree 遍历返回的对象"""

    def __init__(self, full_path: str, relative_path: str, item_type: str):
        self.full_path = full_path
        self.path = relative_path
        self.type = item_type  # "blob" for files, "tree" for directories


class MockTree:
    """模拟 GitPython Tree 对象"""

    def __init__(self, repo_path: str = ""):
        self.repo_path = repo_path

    def __truediv__(self, path: str) -> "MockBlob":
        """支持 tree / path 语法"""
        full_path = os.path.join(self.repo_path, path)
        return MockBlob(full_path, path)

    def traverse(self) -> Iterator[MockTreeItem]:
        """遍历目录树中的所有文件和目录"""
        if not os.path.exists(self.repo_path):
            return

        for root, dirs, files in os.walk(self.repo_path):
            # 跳过 .git 目录
            if ".git" in dirs:
                dirs.remove(".git")

            # 返回目录对象
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                relative_path = os.path.relpath(dir_path, self.repo_path)
                yield MockTreeItem(dir_path, relative_path, "tree")

            # 返回文件对象
            for file_name in files:
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, self.repo_path)
                yield MockTreeItem(file_path, relative_path, "blob")


class MockBlob:
    """模拟 GitPython Blob 对象"""

    def __init__(self, file_path: str, relative_path: str):
        self.file_path = file_path
        self.relative_path = relative_path
        self.path = relative_path  # 添加 path 属性
        self.type = "blob"  # 添加 type 属性

    @property
    def hexsha(self) -> str:
        """计算文件的 SHA 值"""
        try:
            with open(self.file_path, "rb") as f:
                content = f.read()
                return hashlib.sha1(content).hexdigest()
        except Exception:
            return "0" * 40  # 默认 SHA

    @property
    def size(self) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(self.file_path)
        except Exception:
            return 0

    @property
    def mode(self) -> int:
        """获取文件模式"""
        try:
            stat = os.stat(self.file_path)
            return stat.st_mode
        except Exception:
            return 0o100644  # 默认文件模式


class MockHead:
    """模拟 GitPython Head 对象"""

    def __init__(self, commit: MockCommit):
        self.commit = commit


class MockBranch:
    """模拟 GitPython Branch 对象"""

    def __init__(self, name: str):
        self.name = name


class MockRepo:
    """模拟 GitPython Repo 对象，用于 zip 下载模式"""

    def __init__(
        self, repo_path: str, config: GithubRepoSourceConfig, repo_info: Dict[str, Any]
    ):
        self.working_dir = repo_path
        self.repo_path = repo_path
        self.config = config
        self.repo_info = repo_info

        # 创建模拟的 commit 对象
        commit_sha = repo_info.get("default_branch_sha", "unknown")
        author_name = repo_info.get("owner", {}).get("login", "Unknown")
        self._commit = MockCommit(commit_sha, author_name)
        self._commit.tree = MockTree(repo_path)

        # 创建模拟的 head 和 active_branch
        self.head = MockHead(self._commit)
        branch_name = config.branch or repo_info.get("default_branch", "main")
        self.active_branch = MockBranch(branch_name)

    def iter_commits(
        self,
        rev: Optional[str] = None,
        max_count: Optional[int] = None,
        reverse: bool = False,
    ) -> Iterator[MockCommit]:  # 添加返回类型注解
        """模拟提交历史迭代，只返回一个模拟提交"""
        yield self._commit


class GitRepoManager:
    """manage git repo download and cache"""

    def __init__(self) -> None:
        self.repos_dir = os.environ.get("WHISKER_REPO_SAVE_PATH") or os.path.join(
            tempfile.gettempdir(), "repo_download"
        )
        self._repos_cache: Dict[str, str] = {}  # cache for downloaded repos
        self._repo_info_cache: Dict[str, Dict[str, Any]] = {}  # cache for repo info
        os.makedirs(self.repos_dir, exist_ok=True)

    def get_repo_path(self, config: GithubRepoSourceConfig) -> str:
        """
        获取仓库路径，如果不存在则下载

        Args:
            config: 仓库配置信息

        Returns:
            str: 仓库本地路径
        """
        # 生成唯一标识：repo_name + branch + commit_id
        repo_key = self._generate_repo_key(config)

        if repo_key in self._repos_cache:
            repo_path = self._repos_cache[repo_key]
            if os.path.exists(repo_path):
                logger.info(f"Using cached repository: {repo_path}")
                return repo_path
            else:
                # 缓存中的路径不存在，清理缓存
                del self._repos_cache[repo_key]

        # 下载仓库
        repo_path = self._download_repo(config)
        self._repos_cache[repo_key] = repo_path
        return repo_path

    def _generate_repo_key(self, config: GithubRepoSourceConfig) -> str:
        """生成仓库的唯一标识"""
        parts = [config.repo_name]
        if config.branch:
            parts.append(config.branch)
        if config.commit_id:
            parts.append(config.commit_id)
        return "_".join(parts).replace("/", "_")

    def _is_github_repo(self, config: GithubRepoSourceConfig) -> bool:
        """判断是否为 GitHub 仓库"""
        return "github.com" in config.url.lower()

    def _download_repo(self, config: GithubRepoSourceConfig) -> str:
        """
        下载仓库到本地，优先使用 git clone，失败时使用 zip 下载

        Args:
            config: 仓库配置信息

        Returns:
            str: 下载后的仓库路径
        """
        # 确定本地路径
        repo_name = config.repo_name.replace("/", "_")
        repo_saved_path = os.path.join(self.repos_dir, repo_name)

        # 如果路径已存在，先清理
        if os.path.exists(repo_saved_path):
            try:
                shutil.rmtree(repo_saved_path)
            except Exception as e:
                logger.warning(
                    f"Failed to clean existing directory {repo_saved_path}: {e}"
                )
                # 使用带时间戳的路径避免冲突
                import time

                repo_saved_path = f"{repo_saved_path}_{int(time.time())}"

        # 首先尝试 git clone
        if _check_git_installation():
            try:
                clone_url = self._build_clone_url(config)
                self._clone_repo(
                    clone_url, repo_saved_path, config.branch, config.commit_id
                )
                logger.info(f"Successfully cloned repository to {repo_saved_path}")
                return repo_saved_path
            except Exception as e:
                logger.warning(f"Git clone failed: {e}")
                log_system_info()
                # 清理失败的克隆目录
                if os.path.exists(repo_saved_path):
                    shutil.rmtree(repo_saved_path)

        # 如果是 GitHub 仓库且 git clone 失败，尝试 zip 下载
        if self._is_github_repo(config):
            try:
                self._download_github_zip(config, repo_saved_path)
                logger.info(
                    f"Successfully downloaded repository zip to {repo_saved_path}"
                )
                return repo_saved_path
            except Exception as e:
                logger.error(f"GitHub zip download failed: {e}")
                log_system_info()
                raise ValueError(
                    f"Failed to download repository {config.repo_name}: {str(e)}"
                )
        raise ValueError(f"Failed to download repository by config {config}")

    def _download_github_zip(
        self, config: GithubRepoSourceConfig, repo_path: str
    ) -> None:
        """
        从 GitHub 下载 zip 文件

        Args:
            config: 仓库配置信息
            repo_path: 本地保存路径（必须在 self.repos_dir 下）
        """
        # 验证 repo_path 必须在 repos_dir 下
        if not repo_path.startswith(self.repos_dir):
            raise ValueError(f"repo_path must be under repos_dir: {self.repos_dir}")

        requests = _lazy_import_requests()

        # 获取仓库信息
        repo_info = self._get_github_repo_info(config)

        # 确定要下载的分支或提交
        ref = (
            config.commit_id or config.branch or repo_info.get("default_branch", "main")
        )

        # 构建下载 URL
        download_url = f"https://api.github.com/repos/{config.repo_name}/zipball/{ref}"

        # 设置请求头
        headers = {}
        if config.auth_info:
            headers["Authorization"] = f"token {config.auth_info}"

        # 下载 zip 文件
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()

        # 构建 ZIP 文件保存路径
        repo_name_safe = config.repo_name.replace("/", "_")
        zip_filename = f"{repo_name_safe}_{ref}.zip"
        zip_path = os.path.join(self.repos_dir, zip_filename)

        # 保存 ZIP 文件
        with open(zip_path, "wb") as zip_file:
            for chunk in response.iter_content(chunk_size=8192):
                zip_file.write(chunk)

        try:
            # 解压前先清理可能重名的目录
            repo_name_part = config.repo_name.split("/")[-1]  # 获取仓库名部分

            # 删除目标路径（如果存在）
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)

            # 删除可能重名的目录
            if os.path.exists(self.repos_dir):
                for d in os.listdir(self.repos_dir):
                    dir_path = os.path.join(self.repos_dir, d)
                    if os.path.isdir(dir_path) and repo_name_part in d:
                        shutil.rmtree(dir_path)

            # 解压到 repos_dir
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                logger.info(f"Extracting ZIP file: {zip_filename}")
                zip_ref.extractall(self.repos_dir)

                # 查找解压后的目录
                all_dirs = [
                    d
                    for d in os.listdir(self.repos_dir)
                    if os.path.isdir(os.path.join(self.repos_dir, d))
                ]

                # 查找包含仓库名的目录
                extracted_dir = None
                for d in sorted(all_dirs):
                    # 排除ZIP文件名对应的目录
                    if d == zip_filename.replace(".zip", ""):
                        continue

                    # GitHub ZIP 解压后的目录名通常包含仓库名
                    if repo_name_part in d:
                        extracted_dir = d
                        break

                if extracted_dir:
                    extracted_path = os.path.join(self.repos_dir, extracted_dir)

                    # 移动到目标路径
                    shutil.move(extracted_path, repo_path)
                    logger.info(f"Successfully extracted repository to: {repo_path}")
                else:
                    raise ValueError(
                        f"Could not find extracted directory. "
                        f"Available directories: {sorted(all_dirs)}, "
                        f"Looking for: '{repo_name_part}'"
                    )

        finally:
            # 删除 ZIP 文件
            if os.path.exists(zip_path):
                os.unlink(zip_path)

    def _get_github_repo_info(self, config: GithubRepoSourceConfig) -> Dict[str, Any]:
        """
        获取 GitHub 仓库信息

        Args:
            config: 仓库配置信息

        Returns:
            Dict: 仓库信息
        """
        requests = _lazy_import_requests()

        repo_key = self._generate_repo_key(config)

        # 检查缓存
        if repo_key in self._repo_info_cache:
            return self._repo_info_cache[repo_key]

        # 构建 API URL
        api_url = f"https://api.github.com/repos/{config.repo_name}"

        # 设置请求头
        headers = {}
        if config.auth_info:
            headers["Authorization"] = f"token {config.auth_info}"

        # 获取仓库信息
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        repo_info: Dict[str, Any] = response.json()  # 显式类型注解

        # 获取默认分支的最新提交 SHA
        if config.branch or config.commit_id:
            ref = config.commit_id or config.branch
        else:
            ref = repo_info.get("default_branch", "main")

        # 获取分支信息
        branch_url = f"https://api.github.com/repos/{config.repo_name}/branches/{ref}"
        branch_response = requests.get(branch_url, headers=headers)
        if branch_response.status_code == 200:
            branch_info: Dict[str, Any] = branch_response.json()  # 显式类型注解
            repo_info["default_branch_sha"] = branch_info["commit"]["sha"]
        else:
            repo_info["default_branch_sha"] = "unknown"

        # 缓存结果
        self._repo_info_cache[repo_key] = repo_info

        return repo_info

    def _build_clone_url(self, config: GithubRepoSourceConfig) -> str:
        """
        构建克隆URL，只区分GitHub和GitLab两种模式

        Args:
            config: 仓库配置信息

        Returns:
            str: 克隆URL
        """
        base_url = config.url.rstrip("/")
        repo_name = config.repo_name

        # 移除 base_url 中的协议部分，避免重复
        if base_url.startswith("https://"):
            url_no_scheme = base_url[8:]  # 移除 "https://"
        elif base_url.startswith("http://"):
            url_no_scheme = base_url[7:]  # 移除 "http://"
        else:
            url_no_scheme = base_url

        if config.auth_info:
            return f"https://{config.auth_info}@{url_no_scheme}/{repo_name}.git"
        else:
            return f"https://{url_no_scheme}/{repo_name}.git"

    def _clone_repo(
        self,
        clone_url: str,
        repo_path: str,
        branch: Optional[str] = None,
        commit_id: Optional[str] = None,
        initial_depth: int = 1,
        max_fetch_tries: int = 5,
        depth_step: int = 20,
        max_retry_attempts: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        """
        克隆仓库，若 checkout commit 失败自动加深 depth 增量获取

        Args:
            clone_url: 克隆URL
            repo_path: 本地仓库路径
            branch: 分支名
            commit_id: 提交ID
            initial_depth: 初始克隆深度
            max_fetch_tries: 最大fetch尝试次数
            depth_step: 每次加深的深度
            max_retry_attempts: 最大重试次数
            retry_delay: 重试间隔时间（秒）
        """
        import time

        Repo, GitCommandNotFound, InvalidGitRepositoryError = _lazy_import_git()

        last_exception = None

        for attempt in range(max_retry_attempts):
            try:
                # 如果不是第一次尝试，先清理可能存在的部分克隆目录
                if attempt > 0 and os.path.exists(repo_path):
                    logger.info(
                        f"Cleaning up partial clone from previous attempt: {repo_path}"
                    )
                    shutil.rmtree(repo_path)

                logger.info(
                    f"Cloning repository (attempt {attempt + 1}/{max_retry_attempts}): {clone_url}"
                )

                # 先浅克隆最近 N 个
                if branch:
                    repo = Repo.clone_from(
                        clone_url,
                        repo_path,
                        multi_options=["--filter=blob:limit=5m"],
                        branch=branch,
                        depth=initial_depth,
                    )
                else:
                    repo = Repo.clone_from(
                        clone_url,
                        repo_path,
                        multi_options=["--filter=blob:limit=5m"],
                        depth=initial_depth,
                    )

                # 如果指定了 commit_id，尝试 checkout，若失败则增量 fetch
                if commit_id:
                    for i in range(max_fetch_tries):
                        try:
                            repo.git.checkout(commit_id)
                            logger.info(
                                f"Checked out commit {commit_id} successfully after {i + 1} attempts."
                            )
                            break
                        except Exception as e:
                            err_msg = str(e)
                            if (
                                "did not match any file" in err_msg
                                or "reference is not a tree" in err_msg
                                or "unknown revision" in err_msg
                                or "not found" in err_msg
                                or "pathspec" in err_msg
                            ):
                                logger.warning(
                                    f"Commit {commit_id} not found. Deepening history (attempt {i + 1}/{max_fetch_tries})..."
                                )
                                repo.git.fetch("origin", f"--deepen={depth_step}")
                                if branch:
                                    repo.git.checkout(branch)
                                continue
                            else:
                                raise
                    else:
                        raise ValueError(
                            f"Failed to fetch commit {commit_id} after {max_fetch_tries} incremental fetches."
                        )

                # 克隆成功，退出重试循环
                logger.info(f"Repository cloned successfully: {repo_path}")
                return

            except GitCommandNotFound:
                # Git命令未找到，不需要重试
                raise ValueError(
                    "Git command not found. Please ensure git is installed."
                )

            except InvalidGitRepositoryError as e:
                # 无效的git仓库，不需要重试
                raise ValueError(f"Invalid git repository: {str(e)}")

            except Exception as e:
                last_exception = e
                err_msg = str(e)

                # 检查是否是认证失败，不需要重试
                if (
                    "Authentication failed" in err_msg
                    or "authentication failed" in err_msg.lower()
                ):
                    raise ValueError("Authentication failed. Please check your token.")

                # 检查是否是永久性错误，不需要重试
                if any(
                    keyword in err_msg.lower()
                    for keyword in [
                        "repository not found",
                        "does not exist",
                        "permission denied",
                        "access denied",
                        "forbidden",
                    ]
                ):
                    raise ValueError(f"Repository access error: {err_msg}")

                # 其他错误（网络问题、临时服务器错误等）可以重试
                if attempt < max_retry_attempts - 1:
                    logger.warning(
                        f"Clone attempt {attempt + 1} failed: {err_msg}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    # 指数退避：每次重试延迟时间翻倍
                    retry_delay *= 2
                else:
                    logger.error(f"All {max_retry_attempts} clone attempts failed.")

        # 所有重试都失败了，抛出最后一个异常
        if last_exception:
            raise ValueError(
                f"Failed to clone repository after {max_retry_attempts} attempts: {str(last_exception)}"
            )
        else:
            raise ValueError(
                f"Failed to clone repository after {max_retry_attempts} attempts"
            )

    def get_repo(self, config: GithubRepoSourceConfig) -> Union[Any, MockRepo]:
        """
        获取 Repo 对象，可能是真实的 GitPython Repo 或模拟的 MockRepo

        Args:
            config: 仓库配置信息

        Returns:
            Union[Repo, MockRepo]: Repo 对象
        """
        repo_path = self.get_repo_path(config)

        # 检查是否是真实的 git 仓库
        git_dir = os.path.join(repo_path, ".git")
        if os.path.exists(git_dir):
            # 是真实的 git 仓库，返回 GitPython Repo
            try:
                Repo, _, _ = _lazy_import_git()
                return Repo(repo_path)
            except Exception as e:
                logger.warning(f"Failed to create GitPython Repo: {e}")

        # 不是 git 仓库或创建失败，返回 MockRepo
        if self._is_github_repo(config):
            repo_key = self._generate_repo_key(config)
            repo_info = self._repo_info_cache.get(repo_key, {})
            return MockRepo(repo_path, config, repo_info)
        else:
            raise ValueError("Repository is not a git repository and not on GitHub")

    def cleanup_repo(self, config: GithubRepoSourceConfig) -> None:
        """
        清理指定的仓库

        Args:
            config: 仓库配置信息
        """
        repo_key = self._generate_repo_key(config)
        if repo_key in self._repos_cache:
            repo_path = self._repos_cache[repo_key]
            try:
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                    logger.info(f"Cleaned up repository: {repo_path}")
            except Exception as e:
                logger.error(f"Error cleaning up repository {repo_path}: {e}")
            finally:
                del self._repos_cache[repo_key]

        # 清理仓库信息缓存
        if repo_key in self._repo_info_cache:
            del self._repo_info_cache[repo_key]


# 全局仓库管理器实例
_repo_manager = GitRepoManager()


def get_repo_manager() -> GitRepoManager:
    """获取全局仓库管理器实例"""
    return _repo_manager
