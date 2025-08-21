import hashlib
import os
import traceback
import yaml
import tempfile
from slugify import slugify
from glob import glob
from cachetools import TTLCache
from filelock import FileLock

from ..server.kawa_log_manager import get_kawa_logger
from ..scripts.kawa_tool_kit import build_kawa_toolkit_from_yaml_file

# Will store instances of synced GitRepository
# This allows to avoid doing too many calls to git clone/pull methods
git_cache = TTLCache(maxsize=100, ttl=5)
KEY_PLACEHOLDER = '(κλειδί)'


def build_and_sync_git_repository(repo_directory: str, ssh_remote_url: str, branch: str, private_key: str):
    """
    Utility to build and sync a Git repo.
    This wraps the call to the native constructor + sync into a lock + short-lived cache mechanism
    """
    cache_key = f'{repo_directory}+{ssh_remote_url}+{branch}'
    md5 = hashlib.md5(cache_key.encode('utf-8')).hexdigest()
    lock = FileLock(f'/tmp/{md5}.lock')
    with lock:
        try:
            cached_repo = git_cache[cache_key]
            return cached_repo
        except KeyError:
            git_repo = GitRepository(
                repo_directory=repo_directory,
                ssh_remote_url=ssh_remote_url,
                branch=branch,
                private_key=private_key
            )
            # Store synced instances in the cache
            # (A repo will not pull from remote during the TTL)
            git_repo.sync()
            git_cache[cache_key] = git_repo
            return git_repo


class GitRepository:

    # It is recommended to use build_and_sync_git_repository
    def __init__(self, repo_directory: str, ssh_remote_url: str, branch: str, private_key: str):
        self._branch = branch
        self._ssh_remote_url = ssh_remote_url
        self._working_directory = repo_directory
        self._private_key = private_key
        self.logger = get_kawa_logger()
        self.logger.info(f'✨ GIT repo is ready: remote={ssh_remote_url} on branch={branch}')

    def sync(self):
        """
        If the local repo directory does not exist yet, create it and clone the project inside.
        Otherwise, perform a git pull to retrieve the latest commits on the branch.
        """
        try:
            path = self.local_repo_directory
            self.logger.info(f'✨ Sync the repository {self._ssh_remote_url}+{self._branch} in {path}')

            if os.path.isdir(path) and len(os.listdir(path)) == 0:
                self.logger.info(f'✨ Empty directory - delete it to get ready for the clone operation')
                os.rmdir(path)

            dir_exists = os.path.isdir(path)
            git_command = self._pull_command if dir_exists else self._clone_command
            self.logger.info(f'✨ Will run the following git command: {git_command}')
            self._run_git_command(git_command)

        except Exception as e:
            tb_str = traceback.format_exc()
            self.logger.error(f'✨ Error in sync: {tb_str}')
            raise e

    def load_toolkits(self):
        try:
            root_path = self.local_repo_directory
            result = {}
            for dirpath, dirnames, filenames in os.walk(root_path):
                if 'kawa-toolkit.yaml' in filenames:
                    full_path = os.path.join(dirpath, 'kawa-toolkit.yaml')
                    with open(full_path, 'r') as f:
                        content = yaml.safe_load(f)
                    result[dirpath] = content

            self.logger.info(f'✨ The files were loaded from {root_path} successfully')
            return result

        except Exception as e:
            tb_str = traceback.format_exc()
            self.logger.error(f'✨ Error when running load_repository_files: {tb_str}')
            raise e

    def find_one_tool(self, toolkit_name: str, tool_name: str):
        path = self.local_repo_directory
        files = glob(f'{path}/**/kawa-toolkit.yaml', recursive=True)
        kawa_toolkits = [build_kawa_toolkit_from_yaml_file(path, file) for file in files]
        for kawa_toolkit in kawa_toolkits:
            if kawa_toolkit.name == toolkit_name:
                for tool in kawa_toolkit.tools:
                    if tool.name == tool_name:
                        self.logger.debug(f'✨ Found tool {tool_name}')
                        return tool.module

        raise Exception(f'✨ No module found in the repo for toolkit: {toolkit_name} and tool: {tool_name}')

    def load_one_file(self, filename: str):
        self.logger.info(f'✨ Reading the content of: {filename}')
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

    def check_repository_structure(self):
        self.logger.info(f'✨ Checking the repository structure: repo: {self._ssh_remote_url} branch: {self._branch}')
        path = self.local_repo_directory

        # At least one file named: kawa-toolkit.yaml
        toolkit_files = glob(f'{path}/**/kawa-toolkit.yaml', recursive=True)
        at_least_one_toolkit = len(toolkit_files) > 0

        # requirements.txt is present at the root
        path_requirements = path / 'requirements.txt'
        requirements_file_exists = os.path.isfile(path_requirements)

        if requirements_file_exists and at_least_one_toolkit:
            self.logger.info('✅ - Looks good')

        return {
            'sourceControlApiConfiguration': True,
            'requirements': requirements_file_exists,
            'kawaToolKits': at_least_one_toolkit,
        }

    def _run_git_command(self, command: str):
        self.logger.info('🚀✨ Running: ' + command)
        private_key_content = self._private_key
        with tempfile.NamedTemporaryFile(mode='w+t', delete=True) as tmp_file:
            tmp_file.write(private_key_content + '\n')
            tmp_file.flush()
            tmp_file.seek(0)
            command_wth_key = command.replace(KEY_PLACEHOLDER, tmp_file.name)
            os.system(command_wth_key)

    @property
    def local_repo_directory(self):
        concat = f'{self._branch}-⍺-{self._ssh_remote_url}'
        slug = slugify(self._ssh_remote_url + '-' + self._branch)
        md5 = hashlib.md5(concat.encode('utf-8')).hexdigest()  # Add md5 to strengthen slug unicity
        return self._working_directory / f'{slug}-{md5}'

    @property
    def _ssh_command(self):
        return f'ssh -i {KEY_PLACEHOLDER} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no'

    @property
    def _clone_command(self):
        return (f'git clone '
                f'-c core.sshCommand="{self._ssh_command}" '
                f'-b {self._branch} --single-branch --depth 1 {self._ssh_remote_url} {self.local_repo_directory}')

    @property
    def _pull_command(self):
        return (f'git -C /{self.local_repo_directory} -c core.sshCommand="{self._ssh_command}" '
                f'pull origin {self._branch}')
