from sys import exc_info
from unittest import TestCase
from warnings import warn


class GcAfterTestTests(TestCase):
    def tearDown(self):
        try:
            del self.cycle
        except AttributeError:
            pass

    def test_okay(self):
        pass

    def test_cycle_without_resource(self):
        self.cycle = _Cycle()

    def test_cycle_with_resource(self):
        self.cycle = _Cycle(resource=_Resource())

    def test_test_holds_cycle(self):
        self.hold_cycle = _Cycle(resource=_Resource())

    def test_failure(self):
        raise AssertionError("failure")

    def test_exception(self):
        1 / 0

    def test_traceback_cycle(self):

        def f():
            try:
                1 / 0
            except Exception:
                # create cycle
                tb = exc_info()[2]  # noqa: F841

        f()


class _Cycle:
    """Auxiliary class creating a reference cycle."""

    def __init__(self, **kw):
        self.self = self  # create reference cycle
        self.__dict__.update(kw)


class _Resource:
    """Auxiliary class emulating a resource."""
    closed = False

    def close(self):
        self.closed = True

    def __del__(self):
        if not self.closed:
            warn(ResourceWarning(
                "not closed"
                " - this is no error: testing ResourceWarning here"))
