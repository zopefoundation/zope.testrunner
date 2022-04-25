from unittest import TestCase
from warnings import warn


class GcAfterTestTests(TestCase):
    def test_okay(self):
        pass

    def test_cycle_without_resource(self):
        c = _Cycle()

    def test_cycle_with_resource(self):
        c = _Cycle(resource=_Resource())

    def test_failure(self):
        raise AssertionError("failure")

    def test_exception(self):
        1/0


class _Cycle(object):
    """Auxiliary class creating a reference cycle."""
    def __init__(self, **kw):
        self.self = self  # create reference cycle
        self.__dict__.update(kw)


class _Resource(object):
    """Auxiliary class emulating a resource."""
    closed = False
    def close(self):
        self.closed = True

    def __del__(self):
        if not self.closed:
            warn(ResourceWarning("not closed"))
