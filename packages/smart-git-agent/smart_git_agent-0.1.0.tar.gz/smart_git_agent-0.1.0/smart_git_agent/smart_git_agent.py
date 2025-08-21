import time
import logging
import os
from git import Repo
from watchdog.events import FileSystemEventHandler
from .commit_analyze import CommitAnalyzer
from .file_utils import FileUtils

logger = logging.getLogger(__name__)


class SmartGitAgent(FileSystemEventHandler):
    def __init__(self, repo_path: str, config: dict):
        self.repo_path = repo_path
        self.config = config
        self.repo = Repo(repo_path)
        self.last_commit_time = time.time()
        self.file_utils = FileUtils(repo_path, config)
        self.commit_analyzer = CommitAnalyzer(config, self.file_utils)
        self.dry_run = config.get('dry_run', False)

    def on_any_event(self, event):
        """Handle file system events."""
        if (event.is_directory or
                '.git' in event.src_path or
                self.file_utils.should_ignore_file(event.src_path)):
            return

        current_time = time.time()
        if current_time - self.last_commit_time < self.config.get('debounce_time', 10):
            return

        self.last_commit_time = current_time
        self.process_changes()

    def _check_index_lock(self, max_retries=3, delay=5):
        """Check for index.lock file and retry if it exists."""
        lock_file = os.path.join(self.repo_path, '.git', 'index.lock')
        for attempt in range(max_retries):
            if not os.path.exists(lock_file):
                return True
            logger.warning(
                f"⚠️ Git index.lock detected at '{lock_file}'. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        logger.error(
            f"❌ Failed to obtain index lock after {max_retries} attempts. Please ensure no other Git processes are running and delete '{lock_file}' if stale.")
        return False

    def commit_and_push(self):
        """Perform commit and push operations."""
        try:
            # Check for index.lock before proceeding
            if not self._check_index_lock():
                return

            branch_name = self.config.get('branch', 'main')

            if self.dry_run:
                logger.info("🧪 Dry-run mode: Simulating commit and push")
                analysis = self.commit_analyzer.analyze_changes(self.repo)
                commit_message = self.commit_analyzer.generate_smart_commit_message(analysis)
                logger.info(f"📝 Simulated commit message: {commit_message}")
                return

            # Create branch if it doesn't exist
            if branch_name not in self.repo.heads:
                self.repo.create_head(branch_name)
            self.repo.heads[branch_name].checkout()

            # Add non-ignored files
            for file_path in self.repo.untracked_files:
                if not self.file_utils.should_ignore_file(file_path):
                    self.repo.index.add([file_path])

            # Add modified files
            modified_files = [item.a_path for item in self.repo.index.diff(None)]
            for file_path in modified_files:
                if not self.file_utils.should_ignore_file(file_path):
                    self.repo.index.add([file_path])

            # Check for meaningful changes
            if not self.file_utils.has_meaningful_changes(self.repo):
                logger.info("ℹ️ No significant changes detected")
                return

            # Analyze and generate commit message
            analysis = self.commit_analyzer.analyze_changes(self.repo)
            commit_message = self.commit_analyzer.generate_smart_commit_message(analysis)

            # Commit
            self.repo.index.commit(commit_message)
            logger.info(f"✅ Commit: {commit_message}")

            # Update file hashes
            self.file_utils.update_file_hashes(self.repo)

            # Push if configured
            if self.config.get('auto_push', True):
                try:
                    origin = self.repo.remote(name='origin')
                    origin.push(branch_name)
                    logger.info(f"📤 Pushed to {branch_name}")
                except Exception as e:
                    logger.error(f"Push error: {e}")

        except Exception as e:
            logger.error(f"Commit/push error: {e}")

    def process_changes(self):
        """Process detected changes."""
        self.commit_and_push()