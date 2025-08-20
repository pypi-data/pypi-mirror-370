from yta_validation.parameter import ParameterValidator


class ConsolePrinter:
    """
    Class to wrap functionality related to printing
    messages in the console.
    """

    @staticmethod
    def print_error(
        message: str = ''
    ):
        ParameterValidator.validate_string('message', message, do_accept_empty = True)

        print(f'>>>> [ERROR] <<<< {message}')

    @staticmethod
    def print_in_progress(
        message: str = ''
    ):
        ParameterValidator.validate_string('message', message, do_accept_empty = True)

        print(f'.... {message}')

    @staticmethod
    def print_completed(
        message: str = ''
    ):
        ParameterValidator.validate_string('message', message, do_accept_empty = True)
        
        print(f'[OK] {message}')