import typing
import unittest

import edq.util.json
import edq.util.reflection

FORMAT_STR: str = "\n--- Expected ---\n%s\n--- Actual ---\n%s\n---\n"

class BaseTest(unittest.TestCase):
    """
    A base class for unit tests.
    """

    maxDiff = None
    """ Don't limit the size of diffs. """

    def assertJSONDictEqual(self, a: typing.Dict[str, typing.Any], b: typing.Dict[str, typing.Any]) -> None:  # pylint: disable=invalid-name
        """
        Call assertDictEqual(), but supply a message containing the full JSON representation of the arguments.
        """

        a_json = edq.util.json.dumps(a, indent = 4)
        b_json = edq.util.json.dumps(b, indent = 4)

        super().assertDictEqual(a, b, FORMAT_STR % (a_json, b_json))

    def assertJSONListEqual(self, a: typing.List[typing.Any], b: typing.List[typing.Any]) -> None:  # pylint: disable=invalid-name
        """
        Call assertListEqual(), but supply a message containing the full JSON representation of the arguments.
        """

        a_json = edq.util.json.dumps(a, indent = 4)
        b_json = edq.util.json.dumps(b, indent = 4)

        super().assertListEqual(a, b, FORMAT_STR % (a_json, b_json))

    def format_error_string(self, ex: typing.Union[BaseException, None]) -> str:
        """
        Format an error string from an exception so it can be checked for testing.
        The type of the error will be included,
        and any nested errors will be joined together.
        """

        parts = []

        while (ex is not None):
            type_name = edq.util.reflection.get_qualified_name(ex)
            message = str(ex)

            parts.append(f"{type_name}: {message}")

            ex = ex.__cause__

        return "; ".join(parts)
