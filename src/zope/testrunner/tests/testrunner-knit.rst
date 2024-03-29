Knitting in extra package directories
=====================================

Python packages have __path__ variables that can be manipulated to add
extra directories cntaining software used in the packages.  The
testrunner needs to be given extra information about this sort of
situation.

Let's look at an example.  The testrunner-ex-knit-lib directory
is a directory that we want to add to the Python path, but that we
don't want to search for tests.  It has a sample4 package and a
products subpackage.  The products subpackage adds the
testrunner-ex-knit-products to it's __path__.  We want to run tests
from the testrunner-ex-knit-products directory.  When we import these
tests, we need to import them from the sample4.products package.  We
can't use the --path option to name testrunner-ex-knit-products.
It isn't enough to add the containing directory to the test path
because then we wouldn't be able to determine the package name
properly.  We might be able to use the --package option to run the
tests from the sample4/products package, but we want to run tests in
testrunner-ex that aren't in this package.

We can use the --package-path option in this case.  The --package-path
option is like the --test-path option in that it defines a path to be
searched for tests without affecting the python path.  It differs in
that it supplied a package name that is added a profex when importing
any modules found.  The --package-path option takes *two* arguments, a
package name and file path.

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> sys.path.append(os.path.join(this_directory, 'testrunner-ex-pp-lib'))
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     '--package-path',
    ...     os.path.join(this_directory, 'testrunner-ex-pp-products'),
    ...     'sample4.products',
    ...     ]

    >>> from zope import testrunner
    >>> old_argv = sys.argv

    >>> sys.argv = 'test --layer Layer111 -vv'.split()
    >>> _ = testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer111 tests:
      Set up samplelayers.Layerx in 0.000 seconds.
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer11 in 0.000 seconds.
      Set up samplelayers.Layer111 in 0.000 seconds.
      Running:
        test_x1 (sample1.sampletests.test111.TestA...)
        test_y0 (sample1.sampletests.test111.TestA...)
        ...
        test_y0 (sampletests.test111)
        test_z1 (sampletests.test111)
        testrunner-ex/sampletests/../sampletestsl.rst
        test_extra_test_in_products (sample4.products.sampletests.Test...)
        test_another_test_in_products (sample4.products.more.sampletests.Test...)
      Ran 28 tests with 0 failures, 0 errors and 0 skipped in 0.008 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer111 in 0.000 seconds.
      Tear down samplelayers.Layerx in 0.000 seconds.
      Tear down samplelayers.Layer11 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.

In the example, the last test, test_extra_test_in_products, came from
the products directory.  As usual, we can select the knit-in packages
or individual packages within knit-in packages:

    >>> sys.argv = 'test --package sample4.products -vv'.split()
    >>> _ = testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer111 tests:
      Set up samplelayers.Layerx in 0.000 seconds.
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer11 in 0.000 seconds.
      Set up samplelayers.Layer111 in 0.000 seconds.
      Running:
        test_extra_test_in_products (sample4.products.sampletests.Test...)
        test_another_test_in_products (sample4.products.more.sampletests.Test...)
      Ran 2 tests with 0 failures, 0 errors and 0 skipped in 0.000 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer111 in 0.000 seconds.
      Tear down samplelayers.Layerx in 0.000 seconds.
      Tear down samplelayers.Layer11 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.

    >>> sys.argv = 'test --package sample4.products.more -vv'.split()
    >>> _ = testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer111 tests:
      Set up samplelayers.Layerx in 0.000 seconds.
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer11 in 0.000 seconds.
      Set up samplelayers.Layer111 in 0.000 seconds.
      Running:
        test_another_test_in_products (sample4.products.more.sampletests.Test...)
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in 0.000 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer111 in 0.000 seconds.
      Tear down samplelayers.Layerx in 0.000 seconds.
      Tear down samplelayers.Layer11 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.

Restore the arguments::

    >>> sys.argv = old_argv
