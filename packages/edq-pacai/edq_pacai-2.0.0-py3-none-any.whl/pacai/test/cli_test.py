import argparse
import contextlib
import glob
import importlib
import io
import os
import re
import sys
import typing
import unittest

import edq.util.dirent
import edq.util.json

import pacai.test.base

THIS_DIR: str = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_CASES_DIR: str = os.path.join(THIS_DIR, "cli_tests")
DATA_DIR: str = os.path.join(THIS_DIR, "data")

TEST_CASE_SEP: str = '---'
DATA_DIR_ID: str = '__DATA_DIR__'
TEMP_DIR_ID: str = '__TEMP_DIR__'
REL_DIR_ID: str = '__REL_DIR__'

DEFAULT_OUTPUT_CHECK: str = 'content_equals_normalize'

LOG_PREFIX_REGEX: str = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ \[\S+ *\] - .*\.py:\d+ -- '
LOG_PREFIX_REPLACEMENT: str = '<LOG_PREFIX> -- '

TIME_SECS_REGEX: str = r'\d+\.\d+ seconds'
TIME_SECS_REPLACEMENT: str = '<DURATION_SECONDS>'

TRACEBACK_LINE_REGEX: str = r'^\s*File "[^"]+", line \d+,.*$\n.*$(\n\s*[\^~]+\s*$)?'
TRACEBACK_LINE_REPLACEMENT: str = '<TRACEBACK_LINE>'

TRACEBACK_FULL_REGEX: str = rf'{TRACEBACK_LINE_REPLACEMENT}(\n{TRACEBACK_LINE_REPLACEMENT})*'
TRACEBACK_FULL_REPLACEMENT: str = '<TRACEBACK>'

class CLITest(pacai.test.base.BaseTest):
    """
    Test CLI tools using a JSON file which describes a test case,
    which is essentially an invocation of a CLI tool and the expected output.

    The test case file must live in TEST_CASES_DIR.
    The file contains two parts (separated by a line with just TEST_CASE_SEP):
    the first part which is a JSON object (see below for available keys),
    and a second part which is the expected text output (stdout).
    The JSON section can have the following keys:
     - `cli: str` -- Qualified path of the CLI's module (which should have a `main()` function that takes in optional list[string] and returns an int.
     - `exit_status: int` -- Expected exit status for the CLI. Defaults to 0.
     - `error: bool` -- Indicates that the CLI should raise an exception and the expected output is from the exception, not stdout. Defaults to false.
     - `output-check: str` -- The name of the function (in this module) to use to compare output. Defaults to DEFAULT_OUTPUT_CHECK.
     - `arguments: list[str]` -- The list of arguments to send to the CLI's main() function. Defaults to an empty list.

    The expected output or any argument can reference the test's current temp or data dirs with `__TEMP_DIR__()` or `__DATA_DIR__()`, respectively.
    An optional slash-separated path can be used as an argument to reference a path within those base directories.
    For example, `__DATA_DIR__(foo/bar.txt)` references `bar.txt` inside the `foo` directory inside the data directory.
    """

    _base_temp_dir: str = edq.util.dirent.get_temp_path('pacai_CLITest_')

    def _get_test_info(self, test_name: str, path: str) -> tuple[str, list[str], str, typing.Callable, int, bool, bool, bool]:
        options, expected_output = _read_test_file(path)

        base_dir = os.path.dirname(os.path.abspath(path))

        temp_dir = os.path.join(CLITest._base_temp_dir, test_name)
        os.makedirs(temp_dir, exist_ok = True)

        module_name = options['cli']
        exit_status = options.get('exit_status', 0)
        is_error = options.get('error', False)
        skip_windows = options.get('skip_windows', False)
        skip_mac = options.get('skip_mac', False)

        output_check_name = options.get('output-check', DEFAULT_OUTPUT_CHECK)
        if (output_check_name not in globals()):
            raise ValueError(f"Could not find output check function: '{output_check_name}'.")

        output_check = globals()[output_check_name]

        if (is_error):
            expected_output = expected_output.strip()

        cli_arguments = options.get('arguments', [])

        # Make any substitutions.
        expected_output = _prepare_string(expected_output, temp_dir, base_dir)
        for (i, cli_argument) in enumerate(cli_arguments):
            cli_arguments[i] = _prepare_string(cli_argument, temp_dir, base_dir)

        return module_name, cli_arguments, expected_output, output_check, exit_status, is_error, skip_windows, skip_mac

def _prepare_string(text: str, temp_dir: str, base_dir: str) -> str:
    """ Prepare a string for testing. """

    replacements = [
        (DATA_DIR_ID, DATA_DIR),
        (TEMP_DIR_ID, temp_dir),
        (REL_DIR_ID, base_dir),
    ]

    for (key, target_dir) in replacements:
        text = _replace_path(text, key, target_dir)

    return text

def _replace_path(text: str, key: str, target_dir: str) -> str:
    """ Make any test replacement inside the given string. """

    match = re.search(rf'{key}\(([^)]*)\)', text)
    if (match is not None):
        filename = match.group(1)

        # Normalize any path seperators.
        filename = os.path.join(*filename.split('/'))

        if (filename == ''):
            path = target_dir
        else:
            path = os.path.join(target_dir, filename)

        text = text.replace(match.group(0), path)

    return text

def _read_test_file(path: str) -> tuple[dict, str]:
    """ Read a test case file and split the output into JSON data and text. """

    json_lines: list[str] = []
    output_lines: list[str] = []

    text = edq.util.dirent.read_file(path, strip = False)

    accumulator = json_lines
    for line in text.split("\n"):
        if (line.strip() == TEST_CASE_SEP):
            accumulator = output_lines
            continue

        accumulator.append(line)

    options = edq.util.json.loads(''.join(json_lines))
    output = "\n".join(output_lines)

    return options, output

def _discover_test_cases() -> None:
    """ Look in the text cases directory for any test cases and add them as test methods to the test class. """

    for path in sorted(glob.glob(os.path.join(TEST_CASES_DIR, "**", "*.txt"), recursive = True)):
        try:
            _add_test_case(path)
        except Exception as ex:
            raise ValueError(f"Failed to parse test case '{path}'.") from ex

def _add_test_case(path: str) -> None:
    """ Attach a test method to the test class. """

    test_name = 'test_cli__' + os.path.splitext(os.path.basename(path))[0]
    setattr(CLITest, test_name, _get_test_method(test_name, path))

def _get_test_method(test_name: str, path: str) -> typing.Callable:
    """ Get a test method that represents the test case at the given path. """

    def __method(self):
        (module_name, cli_arguments, expected_output, output_check,
        expected_exit_status, is_error, skip_windows, skip_mac) = self._get_test_info(test_name, path)

        if (skip_windows and sys.platform.startswith("win")):
            self.skipTest("Test is not available on Windows.")
        elif (skip_mac and (sys.platform == "darwin")):
            self.skipTest("Test is not available on Mac.")

        module = importlib.import_module(module_name)

        old_args = sys.argv
        sys.argv = [module.__file__] + cli_arguments

        try:
            with contextlib.redirect_stdout(io.StringIO()) as stdout_output:
                with contextlib.redirect_stderr(io.StringIO()) as stderr_output:
                    module.main()

            stdout_text = stdout_output.getvalue()
            stderr_text = stderr_output.getvalue()

            actual_output = ''

            if ((len(stdout_text) > 0) and (len(stderr_text) > 0)):
                actual_output = stdout_text + "\n---\n" + stderr_text
            elif (len(stdout_text) > 0):
                actual_output = stdout_text
            else:
                actual_output = stderr_text

            if (is_error):
                self.fail(f"No error was not raised when one was expected ('{str(expected_output)}').")
        except BaseException as ex:
            if (not is_error):
                raise ex

            output = str(ex)

            if (isinstance(ex, SystemExit) and (ex.__context__ is not None)):
                output = str(ex.__context__)

            self.assertEqual(expected_output, output)
            return
        finally:
            sys.argv = old_args

        self.assertEqual(expected_exit_status, 0)

        output_check(self, expected_output, actual_output)

    return __method

def content_equals_raw(test: CLITest, expected: str, actual: str, **kwargs) -> None:
    """ Check for equality using a simple string comparison. """

    test.assertEqual(expected, actual)

def content_equals_normalize(test: CLITest, expected: str, actual: str, **kwargs) -> None:
    """
    Perform some standard normalizations before using simple string comparison:
     - Replace log prefixes with LOG_PREFIX_REPLACEMENT.
     - Replace what looks like seconds duraton with TIME_SECS_REPLACEMENT.
     - Replace traceback lines with TRACEBACK_LINE_REPLACEMENT.
    """

    expected = re.sub(LOG_PREFIX_REGEX, LOG_PREFIX_REPLACEMENT, expected, flags = re.MULTILINE)
    actual = re.sub(LOG_PREFIX_REGEX, LOG_PREFIX_REPLACEMENT, actual, flags = re.MULTILINE)

    expected = re.sub(TIME_SECS_REGEX, TIME_SECS_REPLACEMENT, expected, flags = re.MULTILINE)
    actual = re.sub(TIME_SECS_REGEX, TIME_SECS_REPLACEMENT, actual, flags = re.MULTILINE)

    expected = re.sub(TRACEBACK_LINE_REGEX, TRACEBACK_LINE_REPLACEMENT, expected, flags = re.MULTILINE)
    actual = re.sub(TRACEBACK_LINE_REGEX, TRACEBACK_LINE_REPLACEMENT, actual, flags = re.MULTILINE)

    expected = re.sub(TRACEBACK_FULL_REGEX, TRACEBACK_FULL_REPLACEMENT, expected, flags = re.MULTILINE)
    actual = re.sub(TRACEBACK_FULL_REGEX, TRACEBACK_FULL_REPLACEMENT, actual, flags = re.MULTILINE)

    content_equals_raw(test, expected, actual)

def has_content_100(test: CLITest, expected: str, actual: str, **kwargs) -> None:
    """ Check the that output has at least 100 characters. """

    return has_content(test, expected, actual, min_length = 100)

def has_content(test: CLITest, expected: str, actual: str, min_length: int = 100) -> None:
    """ Ensure that the output has content of at least some length. """

    message = f"Output does not meet minimum length of {min_length}, it is only {len(actual)}."
    test.assertTrue((len(actual) >= min_length), msg = message)

def main(args: argparse.Namespace) -> int:
    """
    A main for function for testing a specific CLI test file.
    """

    for path in args.paths:
        _add_test_case(path)

    runner = unittest.TextTestRunner(verbosity = 2)
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(CLITest)
    results = runner.run(tests)

    return len(results.errors) + len(results.failures)

def _load_args() -> argparse.Namespace:
    """ Load arguments from the CLI for the main. """

    parser = argparse.ArgumentParser(description = 'Run specific CLI test files.')

    parser.add_argument('paths', metavar = 'PATH',
        type = str, nargs = '+',
        help = 'Path to CLI test case files.')

    return parser.parse_args()

if (__name__ == '__main__'):
    sys.exit(main(_load_args()))
else:
    _discover_test_cases()
