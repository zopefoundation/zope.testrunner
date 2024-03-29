Running Without Source Code
===========================

The ``--usecompiled`` option allows running tests in a tree without .py
source code, provided compiled .pyc or .pyo files exist (without
``--usecompiled``, .py files are necessary).

We have a very simple directory tree, under ``usecompiled/``, to test
this.  Because we're going to delete its .py files, we want to work
in a copy of that:

    >>> import os.path, shutil, sys, tempfile
    >>> directory_with_tests = tempfile.mkdtemp()

    >>> NEWNAME = "unlikely_package_name"
    >>> src = os.path.join(this_directory, 'testrunner-ex', 'usecompiled')
    >>> os.path.isdir(src)
    True
    >>> dst = os.path.join(directory_with_tests, NEWNAME)
    >>> os.path.isdir(dst)
    False

Have to use our own copying code, to avoid copying read-only SVN files that
can't be deleted later.

    >>> n = len(src) + 1
    >>> for root, dirs, files in os.walk(src):
    ...     dirs[:] = [d for d in dirs if d == "package"] # prune cruft
    ...     os.mkdir(os.path.join(dst, root[n:]))
    ...     for f in files:
    ...         _ = shutil.copy(os.path.join(root, f),
    ...                         os.path.join(dst, root[n:], f))

Now run the tests in the copy:

    >>> from zope import testrunner

    >>> mydefaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^compiletest$',
    ...     '--package', NEWNAME,
    ...     '-vv',
    ...     ]
    >>> sys.argv = ['test']
    >>> testrunner.run_internal(mydefaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test1 (unlikely_package_name.compiletest.Test...)
     test2 (unlikely_package_name.compiletest.Test...)
     test1 (unlikely_package_name.package.compiletest.Test...)
     test2 (unlikely_package_name.package.compiletest.Test...)
      Ran 4 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


If we delete the source files, it's normally a disaster:  the test runner
doesn't believe any test files, or even packages, exist.  Note that we pass
``--keepbytecode`` this time, because otherwise the test runner would
delete the compiled Python files too:

    >>> for root, dirs, files in os.walk(dst):
    ...    for f in files:
    ...        if f.endswith(".py"):
    ...            os.remove(os.path.join(root, f))
    >>> testrunner.run_internal(mydefaults, ["test", "--keepbytecode"])
    Running tests at level 1
    Total: 0 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    False

Finally, passing ``--usecompiled`` asks the test runner to treat .pyc
and .pyo files as adequate replacements for .py files.  Note that the
output is the same as when running with .py source above.  The absence
of "removing stale bytecode ..." messages shows that ``--usecompiled``
also implies ``--keepbytecode``:

    >>> # PEP-3147: pyc files in __pycache__ directories cannot be
    ... # imported; legacy source-less imports need to use the legacy
    ... # layout
    ... for root, dirs, files in os.walk(dst):
    ...     for f in files:
    ...         if f.endswith((".pyc", ".pyo")):
    ...             # "root/f" is "dirname/__pycache__/name.magic.ext"
    ...             dirname = os.path.dirname(os.path.abspath(root))
    ...             namewmagic, ext = os.path.splitext(os.path.basename(f))
    ...             newname = os.path.splitext(namewmagic)[0] + ext
    ...             os.rename(os.path.join(root, f),
    ...                       os.path.join(dirname, newname))

    >>> testrunner.run_internal(mydefaults, ["test", "--usecompiled"])
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test1 (unlikely_package_name.compiletest.Test...)
     test2 (unlikely_package_name.compiletest.Test...)
     test1 (unlikely_package_name.package.compiletest.Test...)
     test2 (unlikely_package_name.package.compiletest.Test...)
      Ran 4 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Remove the temporary directory:

    >>> shutil.rmtree(directory_with_tests)
