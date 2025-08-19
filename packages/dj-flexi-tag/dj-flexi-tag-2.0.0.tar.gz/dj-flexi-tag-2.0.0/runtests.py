import argparse
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the tests for dj-flexi-tag")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode"
    )
    args = parser.parse_args()

    os.environ["DJANGO_SETTINGS_MODULE"] = "flexi_tag.tests.test_settings"

    if not args.interactive:
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        os.environ["DJANGO_DATABASE_YES_TO_ALL"] = "true"

    django.setup()

    verbosity_level = 2 if args.verbose else 1

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity_level, interactive=args.interactive)

    failures = test_runner.run_tests(["flexi_tag.tests"])
    sys.exit(bool(failures))
