from unittest import TestCase

from ..digraph import DiGraph


class Tests(TestCase):
    def test_int_digraph(self):
        self.check(lambda nodes: DiGraph(nodes, False))

    def test_obj_diraph(self):
        self.check(DiGraph)

    def check(self, digraph_factory):
        ints = list(range(100))
        g = digraph_factory(ints)
        self.assertEqual(sorted(g.nodes()), ints)
        nb0 = [ints[0], ints[1]]
        g.add_neighbors(ints[0], nb0)
        self.assertEqual(sorted(g.neighbors(ints[0])), nb0)
        self.assertEqual(list(g.neighbors(ints[1])), [])
        # unknown neighbors
        with self.assertRaises(KeyError):
            g.add_neighbors(ints[0], (200,), False)
        g.add_neighbors(ints[0], (200,))  # ignored
        self.assertEqual(sorted(g.neighbors(ints[0])), nb0)
        # unknown node
        with self.assertRaises(KeyError):
            g.add_neighbors(200, (ints[0],), False)
        g.add_neighbors(200, (ints[0],))  # ignored

        # additional neighbors
        nb0.append(ints[2])
        g.add_neighbors(ints[0], nb0)
        self.assertEqual(sorted(g.neighbors(ints[0])), nb0)

    def test_scc_linear(self):
        ints = list(range(100))
        g = DiGraph(ints)
        for i in range(99):
            g.add_neighbors(ints[i], (ints[i + 1], ))
        self.assertEqual(sorted(g.sccs(True)), [[i] for i in ints])

    def test_trivial_cycle(self):
        g = dig_from_dict({1: 2, 2: (2, 3), 3: ()})
        sccs = list(g.sccs())
        self.assertEqual(len(sccs), 1)
        cy = sccs[0]
        self.assertEqual(len(cy), 1)
        self.assertEqual(cy[0], 2)

    def test_forest(self):
        g = dig_from_dict({1: (), 2: ()})
        sccs = list(g.sccs(True))
        self.assertEqual(sorted(sccs), [[1], [2]])

    def test_complex(self):
        g = dig_from_dict({0: 1, 1: 2, 2: (3, 4), 3: (0, 4),
                           4: (5, 2), 5: (6, 9), 6: (5, 7),
                           7: 8, 8: 9, 9: (5, 6)})
        sccs = list(g.sccs())
        self.assertEqual(len(sccs), 2)
        for c in sccs:
            self.assertEqual(len(c), 5)
            self.assertEqual(max(c) - min(c), 4)
        self.assertEqual(sorted(sccs[0] + sccs[1]), list(range(10)))


def dig_from_dict(d):
    g = DiGraph(list(d), False)
    for e in d.items():
        n, nbs = e
        if not hasattr(nbs, "__len__"):
            nbs = nbs,
        g.add_neighbors(n, nbs, False)
    return g
