import sys
import traceback

from .interpreter_error import InterpreterError


class KawaErrorManager:

    def rethrow(self, err):
        if isinstance(err, InterpreterError):
            raise err
        else:
            raise InterpreterError(self.error_to_str(err))

    def error_to_str(self, err):
        if isinstance(err, SyntaxError):
            return self.syntax_error_to_str(err)
        else:
            return self.non_syntax_error_to_str(err)

    @staticmethod
    def syntax_error_to_str(err: SyntaxError):
        detail = err.args[1][3]
        return '%s at line %d, column %d: %s' % (err.msg, err.lineno, err.offset, detail)

    @staticmethod
    def non_syntax_error_to_str(err: Exception):
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        try:
            lineno = traceback.extract_tb(tb)[-1].lineno
            return '%s at line %d: %s' % (error_class, lineno, detail)
        except:
            return f'Error: {err}, {traceback.extract_tb(tb)}'
