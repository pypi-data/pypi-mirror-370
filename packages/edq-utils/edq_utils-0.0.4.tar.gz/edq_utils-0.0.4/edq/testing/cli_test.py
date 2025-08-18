import edq.testing.cli
import edq.testing.unittest

class CLITest(edq.testing.unittest.BaseTest):
    """ Test CLI invocations. """

# Populate CLITest with all the test methods.
edq.testing.cli.discover_test_cases(CLITest)
