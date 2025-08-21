import json
from typing import Optional

from ..scripts.kawa_secrets import KawaSecrets
from .aes_cipher import decrypt_script


class ClearScriptWithSecrets:

    def __init__(self, toolkit: str,
                 tool: str,
                 meta_data: dict,
                 repo_url: Optional[str],
                 repo_key: Optional[str],
                 branch: Optional[str],
                 secrets: dict,
                 content: Optional[str],
                 requirements: Optional[str],
                 api_key: str,
                 ssh_git: bool):
        self.toolkit: str = toolkit
        self.tool: str = tool
        self.meta_data: dict = meta_data
        self.repo_url: str = repo_url
        self.repo_key: str = repo_key
        self.branch: str = branch
        self.kawa_secrets: KawaSecrets = KawaSecrets(secrets)
        self.content = content
        self.requirements = requirements
        self.api_key = api_key
        self.ssh_git = ssh_git

    def is_from_kawa_source_control(self) -> bool:
        if self.toolkit == '__KAWA_FILE_STORE__':
            if self.content:
                return True
            else:
                raise Exception('It seems the content of the script is missing in KAWA_FILE_STORE mode')
        return False

    @staticmethod
    def decrypt(encrypted: str,
                aes_key: str):
        # Serialized by Java server as a JSON object before encryption, see ScriptWithSecrets in ComputationApi
        decrypted = decrypt_script(encrypted, aes_key)
        deserialized_json = json.loads(decrypted)
        toolkit = deserialized_json['toolKit']
        tool = deserialized_json['tool']
        meta_data = deserialized_json['metaData']
        repo_url = deserialized_json.get('repoUrl')
        repo_key = deserialized_json.get('repoKey')
        branch = deserialized_json.get('branch')
        secrets = deserialized_json['secrets']
        content = deserialized_json.get('content')
        requirements = deserialized_json.get('requirements')
        api_key = deserialized_json.get('apiKey')
        ssh_git = deserialized_json.get('sshGit', False)
        return ClearScriptWithSecrets(toolkit, tool, meta_data, repo_url, repo_key, branch,
                                      secrets, content, requirements, api_key, ssh_git)
