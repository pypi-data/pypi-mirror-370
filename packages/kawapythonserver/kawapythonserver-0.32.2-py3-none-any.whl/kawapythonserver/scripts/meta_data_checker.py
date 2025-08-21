import logging
from dataclasses import dataclass
from typing import List

from kywy.client.kawa_decorators import KawaScriptParameter

from .name_with_type import NameWithType


@dataclass
class MetaDataChecker:
    """
    This class checks the consistency between Kawa script entity metadata and
    the source control metadata.

    In theory, this is already handled on the server.
    """

    # Kawa inputs and outputs correspond to the metadata as per Kawa database
    # (from the script entity)
    kawa_inputs: List[NameWithType]
    kawa_outputs: List[NameWithType]
    kawa_parameters: List[NameWithType]

    # Repo inputs and outputs correspond to the metadata in the file
    # when read from the source control repo.
    repo_inputs: List[NameWithType]
    repo_outputs: List[NameWithType]
    repo_parameters: List[NameWithType]

    kawa_logger: logging.Logger

    @classmethod
    def from_dicts(cls,
                   kawa_inputs: List[dict],
                   kawa_outputs: List[dict],
                   kawa_parameters: List[dict],
                   repo_inputs: List[dict],
                   repo_outputs: List[dict],
                   repo_parameters: List[KawaScriptParameter],
                   kawa_logger: logging.Logger) -> 'MetaDataChecker':
        return cls([NameWithType.from_dict(i) for i in kawa_inputs],
                   [NameWithType.from_dict(i) for i in kawa_outputs],
                   [NameWithType.from_dict(i) for i in kawa_parameters],
                   [NameWithType.from_dict(i) for i in repo_inputs],
                   [NameWithType.from_dict(i) for i in repo_outputs],
                   [NameWithType(p.name, p.type) for p in repo_parameters],
                   kawa_logger)

    def check(self):
        self.check_missing_inputs()
        self.check_outputs_with_different_types()
        self.check_missing_outputs_in_repo()
        self.check_parameters()

    def check_parameters(self):
        if self.repo_parameters != self.kawa_parameters:
            message = 'The parameters defined in the repo and in kawa are different. Please synchronise the script.'
            self.kawa_logger.error(message)
            raise Exception(message)

    def check_missing_inputs(self):
        missing_inputs = {p for p in self.repo_inputs if p not in self.kawa_inputs}
        if missing_inputs:
            message = f'Some inputs declared in the script are missing in Kawa: {missing_inputs}. ' \
                      'Please reload the script in Kawa GUI'
            self.kawa_logger.error(message)
            raise Exception(message)

    def check_outputs_with_different_types(self):
        outputs_with_changed_type = []
        for output in self.repo_outputs:
            output_name = output.name
            output_type = output.type
            associated_script_outputs = [o for o in self.kawa_outputs if o.name == output_name]
            if associated_script_outputs:
                associated_script_output = associated_script_outputs[0]
                type_in_kawa = associated_script_output.type
                if type_in_kawa != output_type:
                    outputs_with_changed_type.append({'output_name': output_name,
                                                      'type in kawa': type_in_kawa,
                                                      'type in repo': output_type})
        if outputs_with_changed_type:
            message = f'Some outputs have changed types: {outputs_with_changed_type}'
            self.kawa_logger.error(message)
            raise Exception(message)

    def check_missing_outputs_in_repo(self):
        missing_outputs_in_repo = []
        for kawa_output in self.kawa_outputs:
            kawa_output_name = kawa_output.name
            if not any([repo_output.name == kawa_output_name for repo_output in self.repo_outputs]):
                missing_outputs_in_repo.append(kawa_output_name)

        if missing_outputs_in_repo:
            raise Exception(f'There is outputs defined in the script that are now missing in the repo: {missing_outputs_in_repo}')
