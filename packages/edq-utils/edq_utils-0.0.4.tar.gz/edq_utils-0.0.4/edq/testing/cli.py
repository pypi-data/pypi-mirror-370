"""
Infrastructure for testing CLI tools using a JSON file which describes a test case,
which is essentially an invocation of a CLI tool and the expected output.

The test case file must be a `.txt` file that live in TEST_CASES_DIR.
The file contains two parts (separated by a line with just TEST_CASE_SEP):
the first part which is a JSON object (see below for available keys),
and a second part which is the expected text output (stdout).
For the keys of the JSON section, see the defaulted arguments to CLITestInfo.
The options JSON will be splatted into CLITestInfo's constructor.

The expected output or any argument can reference the test's current temp or data dirs with `__TEMP_DIR__()` or `__DATA_DIR__()`, respectively.
An optional slash-separated path can be used as an argument to reference a path within those base directories.
For example, `__DATA_DIR__(foo/bar.txt)` references `bar.txt` inside the `foo` directory inside the data directory.
"""

import contextlib
import glob
import io
import os
import re
import sys
import typing

import edq.testing.asserts
import edq.testing.unittest
import edq.util.dirent
import edq.util.json
import edq.util.pyimport

THIS_DIR: str = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
BASE_TESTDATA_DIR: str = os.path.join(THIS_DIR, "testdata", "cli")
TEST_CASES_DIR: str = os.path.join(BASE_TESTDATA_DIR, "tests")
DATA_DIR: str = os.path.join(BASE_TESTDATA_DIR, "data")

TEST_CASE_SEP: str = '---'
DATA_DIR_ID: str = '__DATA_DIR__'
TEMP_DIR_ID: str = '__TEMP_DIR__'
REL_DIR_ID: str = '__REL_DIR__'

DEFAULT_ASSERTION_FUNC_NAME: str = 'edq.testing.asserts.content_equals_normalize'

BASE_TEMP_DIR_ATTR: str = '_edq_cli_base_test_dir'

class CLITestInfo:
    """ The required information to run a CLI test. """

    def __init__(self,
            test_name: str,
            base_dir: str,
            temp_dir: str,
            cli: typing.Union[str, None] = None,
            arguments: typing.Union[typing.List[str], None] = None,
            error: bool = False,
            platform_skip: typing.Union[str, None] = None,
            stdout_assertion_func: typing.Union[str, None] = DEFAULT_ASSERTION_FUNC_NAME,
            stderr_assertion_func: typing.Union[str, None] = None,
            expected_stdout: str = '',
            expected_stderr: str = '',
            strip_error_output: bool = True,
            **kwargs: typing.Any) -> None:
        self.test_name: str = test_name
        """ The name of this test. """

        self.base_dir: str = base_dir
        """ The base directory for this test (usually the dir the CLI test file lives. """

        self.temp_dir: str = temp_dir
        """ A temp directory that this test has access to. """

        edq.util.dirent.mkdir(temp_dir)

        if (cli is None):
            raise ValueError("Missing CLI module.")

        self.module_name: str = cli
        """ The name of the module to invoke. """

        self.module: typing.Any = edq.util.pyimport.import_name(self.module_name)
        """ The module to invoke. """

        if (arguments is None):
            arguments = []

        self.arguments: typing.List[str] = arguments
        """ The CLI arguments. """

        self.error: bool = error
        """ Whether or not this test is expected to be an error (raise an exception). """

        self.platform_skip: typing.Union[str, None] = platform_skip
        """ If the current platform matches this regular expression, then the test will be skipped. """

        self.stdout_assertion_func: typing.Union[edq.testing.asserts.StringComparisonAssertion, None] = None
        """ The assertion func to compare the expected and actual stdout of the CLI. """

        if (stdout_assertion_func is not None):
            self.stdout_assertion_func = edq.util.pyimport.fetch(stdout_assertion_func)

        self.stderr_assertion_func: typing.Union[edq.testing.asserts.StringComparisonAssertion, None] = None
        """ The assertion func to compare the expected and actual stderr of the CLI. """

        if (stderr_assertion_func is not None):
            self.stderr_assertion_func = edq.util.pyimport.fetch(stderr_assertion_func)

        self.expected_stdout: str = expected_stdout
        """ The expected stdout. """

        self.expected_stderr: str = expected_stderr
        """ The expected stderr. """

        if (error and strip_error_output):
            self.expected_stdout = self.expected_stdout.strip()
            self.expected_stderr = self.expected_stderr.strip()

        # Make any path normalizations over the arguments and expected output.
        self.expected_stdout = self._expand_paths(self.expected_stdout)
        self.expected_stderr = self._expand_paths(self.expected_stderr)
        for (i, argument) in enumerate(self.arguments):
            self.arguments[i] = self._expand_paths(argument)

    def _expand_paths(self, text: str) -> str:
        """
        Expand path replacements in testing text.
        This allows for consistent paths (even absolute paths) in the test text.
        """

        replacements = [
            (DATA_DIR_ID, DATA_DIR),
            (TEMP_DIR_ID, self.temp_dir),
            (REL_DIR_ID, self.base_dir),
        ]

        for (key, target_dir) in replacements:
            text = replace_path_pattern(text, key, target_dir)

        return text

    @staticmethod
    def load_path(path: str, test_name: str, base_temp_dir: str) -> 'CLITestInfo':
        """ Load a CLI test file and extract the test info. """

        options, expected_stdout = read_test_file(path)

        options['expected_stdout'] = expected_stdout

        base_dir = os.path.dirname(os.path.abspath(path))
        temp_dir = os.path.join(base_temp_dir, test_name)

        return CLITestInfo(test_name, base_dir, temp_dir, **options)

def read_test_file(path: str) -> typing.Tuple[typing.Dict[str, typing.Any], str]:
    """ Read a test case file and split the output into JSON data and text. """

    json_lines: typing.List[str] = []
    output_lines: typing.List[str] = []

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

def replace_path_pattern(text: str, key: str, target_dir: str) -> str:
    """ Make any test replacement inside the given string. """

    match = re.search(rf'{key}\(([^)]*)\)', text)
    if (match is not None):
        filename = match.group(1)

        # Normalize any path separators.
        filename = os.path.join(*filename.split('/'))

        if (filename == ''):
            path = target_dir
        else:
            path = os.path.join(target_dir, filename)

        text = text.replace(match.group(0), path)

    return text

def _get_test_method(test_name: str, path: str) -> typing.Callable:
    """ Get a test method that represents the test case at the given path. """

    def __method(self: edq.testing.unittest.BaseTest) -> None:
        test_info = CLITestInfo.load_path(path, test_name, getattr(self, BASE_TEMP_DIR_ATTR))

        if ((test_info.platform_skip is not None) and re.search(test_info.platform_skip, sys.platform)):
            self.skipTest(f"Test is not available on {sys.platform}.")

        old_args = sys.argv
        sys.argv = [test_info.module.__file__] + test_info.arguments

        try:
            with contextlib.redirect_stdout(io.StringIO()) as stdout_output:
                with contextlib.redirect_stderr(io.StringIO()) as stderr_output:
                    test_info.module.main()

            stdout_text = stdout_output.getvalue()
            stderr_text = stderr_output.getvalue()

            if (test_info.error):
                self.fail(f"No error was not raised when one was expected ('{str(test_info.expected_stdout)}').")
        except BaseException as ex:
            if (not test_info.error):
                raise ex

            stdout_text = self.format_error_string(ex)

            stderr_text = ''
            if (isinstance(ex, SystemExit) and (ex.__context__ is not None)):
                stderr_text = self.format_error_string(ex.__context__)
        finally:
            sys.argv = old_args

        if (test_info.stdout_assertion_func is not None):
            test_info.stdout_assertion_func(self, test_info.expected_stdout, stdout_text)

        if (test_info.stderr_assertion_func is not None):
            test_info.stderr_assertion_func(self, test_info.expected_stderr, stderr_text)

    return __method

def add_test_paths(target_class: type, paths: typing.List[str]) -> None:
    """ Add tests from the given test files. """

    # Attach a temp directory to the testing class so all tests can share a common base temp dir.
    if (not hasattr(target_class, BASE_TEMP_DIR_ATTR)):
        setattr(target_class, BASE_TEMP_DIR_ATTR, edq.util.dirent.get_temp_path('edq_cli_test_'))

    for path in sorted(paths):
        test_name = 'test_cli__' + os.path.splitext(os.path.basename(path))[0]

        try:
            setattr(target_class, test_name, _get_test_method(test_name, path))
        except Exception as ex:
            raise ValueError(f"Failed to parse test case '{path}'.") from ex

def discover_test_cases(target_class: type) -> None:
    """ Look in the text cases directory for any test cases and add them as test methods to the test class. """

    paths = list(sorted(glob.glob(os.path.join(TEST_CASES_DIR, "**", "*.txt"), recursive = True)))
    add_test_paths(target_class, paths)
