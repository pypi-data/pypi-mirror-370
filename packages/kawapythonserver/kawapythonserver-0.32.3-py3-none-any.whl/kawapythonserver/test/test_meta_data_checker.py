import unittest
import logging

from ..scripts.meta_data_checker import MetaDataChecker
from ..scripts.name_with_type import NameWithType


class MetaDataCheckerTest(unittest.TestCase):
    def test_do_not_throw_when_same_meta_data(self):
        kawa_input = [NameWithType('measure1', 'DECIMAL')]
        kawa_output = [NameWithType('output1', 'TEXT')]
        repo_input = [NameWithType('measure1', 'DECIMAL')]
        repo_output = [NameWithType('output1', 'TEXT')]

        meta_data_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            kawa_logger=logging.getLogger()
                                            )
        try:
            meta_data_checker.check()
        except Exception:
            self.fail('Should not raise when meta data are the same')

    def test_throw_when_missing_input_in_kawa(self):
        kawa_input = [NameWithType('measure1', 'DECIMAL')]
        kawa_output = [NameWithType('output1', 'TEXT')]
        repo_input = [NameWithType('measure1', 'DECIMAL'), NameWithType('measure2', 'DECIMAL')]
        repo_output = [NameWithType('output1', 'TEXT')]

        meta_data_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            kawa_logger=logging.getLogger()
                                            )

        self.assertRaises(Exception, lambda x: meta_data_checker.check())

    def test_throw_when_outputs_have_different_types(self):
        kawa_input = [NameWithType('measure1', 'DECIMAL')]
        kawa_output = [NameWithType('output1', 'TEXT')]
        repo_input = [NameWithType('measure1', 'DECIMAL')]
        repo_output = [NameWithType('output1', 'DECIMAL')]

        meta_data_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            kawa_logger=logging.getLogger()
                                            )

        self.assertRaises(Exception, lambda x: meta_data_checker.check())

    def test_throw_when_repo_misses_outputs(self):
        kawa_input = [NameWithType('measure1', 'DECIMAL')]
        kawa_output = [NameWithType('output1', 'TEXT'), NameWithType('output2', 'TEXT')]
        repo_input = [NameWithType('measure1', 'DECIMAL')]
        repo_output = [NameWithType('output1', 'TEXT')]

        meta_data_checker = MetaDataChecker(kawa_inputs=kawa_input,
                                            kawa_outputs=kawa_output,
                                            repo_inputs=repo_input,
                                            repo_outputs=repo_output,
                                            kawa_logger=logging.getLogger()
                                            )

        self.assertRaises(Exception, lambda x: meta_data_checker.check())




if __name__ == '__main__':
    unittest.main()
