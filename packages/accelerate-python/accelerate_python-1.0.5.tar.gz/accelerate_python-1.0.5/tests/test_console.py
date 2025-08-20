## external imports
import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import Console


## test cases
class TestConsole:
    @pytest.mark.parametrize(
        "method, message, expected",
        [
            (
                Console.success,
                "Success message",
                f"{Console.SUCCESS}{Console.BOLD}Success message{Console.NONE}",
            ),
            (
                Console.warning,
                "Warning message",
                f"{Console.WARNING}Warning message{Console.NONE}",
            ),
            (
                Console.notice,
                "Notice message",
                f"{Console.NOTICE}Notice message{Console.NONE}",
            ),
            (Console.info, "Info message", f"{Console.INFO}Info message{Console.NONE}"),
            (
                Console.verbose,
                "Verbose message",
                f"{Console.VERBOSE}Verbose message{Console.NONE}",
            ),
            (
                Console.debug,
                "Debug message",
                f"{Console.DEBUG}Debug message{Console.NONE}",
            ),
        ],
    )
    def test_console_methods(self, capsys, method, message, expected):
        method(message)
        captured = capsys.readouterr()
        assert_that(captured.out, method.__name__).ends_with(f"{expected}\n")

    def test_console_error(self, capsys):
        Console.error("Error message")
        captured = capsys.readouterr()
        assert_that(captured.err, "Console Error").ends_with(
            f"{Console.ERROR}Error message{Console.NONE}\n"
        )

    @pytest.mark.parametrize(
        "message, formats, expected",
        [
            (
                "Formatted message",
                [Console.BOLD],
                f"{Console.BOLD}Formatted message{Console.NONE}",
            ),
            (
                "Another message",
                [Console.UNDERLINE, Console.RED],
                f"{Console.UNDERLINE}{Console.RED}Another message{Console.NONE}",
            ),
        ],
    )
    def test_console_print(self, capsys, message, formats, expected):
        Console.print("LEVEL", message, formats=formats)
        captured = capsys.readouterr()
        assert_that(captured.out, "Console Print").ends_with(f"{expected}\n")


if __name__ == "__main__":
    pytest.main([__file__])
