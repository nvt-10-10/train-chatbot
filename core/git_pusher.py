"""
Automated Git commit & push module using GitPython.
"""

import os
import datetime
import logging
from typing import List, Optional
import git

logger = logging.getLogger(__name__)


class GitDatasetPusher:
    """Handles automatic staging, committing, and pushing of dataset files to GitHub."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            logger.error(f"Directory '{repo_path}' is not a valid Git repository.")
            self.repo = None

    def commit_and_push(
        self,
        files_to_push: List[str],
        commit_message: Optional[str] = None,
        remote_name: str = "origin",
        branch_name: Optional[str] = None,
    ) -> bool:
        """Stage, commit, and push specified dataset files to remote repository."""
        if not self.repo:
            logger.error("Git repository not initialized.")
            return False

        try:
            # Staging files
            for file_path in files_to_push:
                if os.path.exists(file_path):
                    self.repo.index.add([os.path.abspath(file_path)])
                    logger.info(f"Staged file: {file_path}")
                else:
                    logger.warning(f"File not found for staging: {file_path}")

            # Check if there are changes to commit
            if not self.repo.is_dirty(index=True):
                logger.info("No changes in dataset files to commit.")
                return True

            # Prepare commit message
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not commit_message:
                commit_message = f"auto(data): Update Đà Nẵng - Quảng Nam Tráp dataset [{now_str}]"

            # Commit
            commit = self.repo.index.commit(commit_message)
            logger.info(f"Committed changes ({commit.hexsha[:7]}): {commit_message}")

            # Determine branch
            current_branch = branch_name or self.repo.active_branch.name
            remote = self.repo.remote(name=remote_name)

            logger.info(f"Pushing to remote '{remote_name}' on branch '{current_branch}'...")
            push_info = remote.push(refspec=f"{current_branch}:{current_branch}")

            for info in push_info:
                if info.flags & info.ERROR:
                    logger.error(f"Git push failed: {info.summary}")
                    return False

            logger.info("Git push succeeded successfully!")
            return True
        except Exception as e:
            logger.error(f"Git push exception: {e}")
            return False
