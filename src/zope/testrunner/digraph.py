##############################################################################
#
# Copyright (c) 2022 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Directed graph
"""

from itertools import count


class DiGraph:
    """Directed graph.

    A directed graph is a set of nodes together with a
    neighboring relation.

    The class makes intensive use of dicts; therefore, hashability
    is important. Therefore, the class usually does not work
    with the nodes directly but transforms them via
    a ``make_hashable`` function, ``id`` by default.
    This works well for object types where equality is identity.
    For other types, you may need to deactive the transformation
    or use a different ``make_hashable``.
    """

    def __init__(self, nodes=None, make_hashable=id):
        self._nodes = set()  # transformed nodes
        self._neighbors = {}  # node --> neighbors  -- transformed
        if make_hashable:
            tr2n = {}  # transform -> node

            tr_node = make_hashable

            def utr_node(node):
                return tr2n[node]

            def tr_nodes(nodes):
                ns = set()
                add = ns.add
                for n in nodes:
                    trn = make_hashable(n)
                    if trn not in tr2n:
                        tr2n[trn] = n
                    add(trn)
                return ns

        else:
            def tr_nodes(nodes): return set(nodes)  # noqa: E731
            utr_node = tr_node = lambda node: node

        self._transform_node = tr_node
        self._transform_nodes = tr_nodes
        self._untransform_node = utr_node

        if nodes is not None:
            self.add_nodes(nodes)

    def add_nodes(self, nodes):
        """add *nodes* (iterator) to the graph's nodes."""
        self._nodes |= self._transform_nodes(nodes)

    def add_neighbors(self, node, neighbors, ignore_unknown=True):
        """add *neighbors* (iterator) as neighbors for *node*.

        if *ignore_unknown*, unknown nodes in *neighbors* are
        ignored, otherwise a ``KeyError`` is raised.
        """
        tr_n = self._transform_node(node)
        nodes = self._nodes
        nbad = tr_n not in nodes
        if nbad:
            if ignore_unknown:
                return
            else:
                raise KeyError(node)
        tr_neighbors = self._transform_nodes(neighbors)
        known_neighbors = tr_neighbors & nodes
        if not ignore_unknown and len(known_neighbors) != len(tr_neighbors):
            raise KeyError(tr_neighbors - known_neighbors)
        nbs = self._neighbors.get(tr_n)
        if nbs is None:
            self._neighbors[tr_n] = known_neighbors
        else:
            nbs |= known_neighbors

    def nodes(self):
        """iterate of the graph's nodes."""
        utr = self._untransform_node
        for n in self._nodes:
            yield utr(n)

    def neighbors(self, node):
        """iterate over *node*'s neighbors."""
        utr = self._untransform_node
        for n in self._neighbors.get(self._transform_node(node), ()):
            yield utr(n)

    def sccs(self, trivial=False):
        """iteratate over the strongly connected components.

        If *trivial*, include the trivial components; otherwise
        only the cycles.

        This is an implementation of the "Tarjan SCC" algorithm.
        """

        # any node is either in ``unvisited`` or in ``state``
        unvisited = self._nodes.copy()
        state = {}  # nodes -> state

        ancestors = []  # the ancestors of the currently processed node
        stack = []  # the nodes which might still be on a cycle

        # the algorithm visits each node twice in a depth first order
        # In the first visit, visits for the unprocessed neighbors
        # are scheduled as well as the second visit to this
        # node after all neighbors have been processed.
        dfs = count()  # depth first search visit order
        rtn_marker = object()  # marks second visit to ``ancestor`` top
        visits = []  # scheduled visits

        while unvisited:
            node = next(iter(unvisited))
            # determine the depth first spanning tree rooted in *node*
            visits.append(node)
            while visits:
                visit = visits[-1]  # ``rtn_marker`` or node
                if visit is rtn_marker:
                    # returned to the top of ``ancestors``
                    visits.pop()
                    node = ancestors.pop()  # returned to *node*
                    nstate = state[node]
                    if nstate.low == nstate.dfs:
                        # SCC root
                        scc = []
                        while True:
                            n = stack.pop()
                            state[n].stacked = False
                            scc.append(n)
                            if n is node:
                                break
                        if len(scc) == 1 and not trivial:
                            # check for triviality
                            n = scc[0]
                            if n not in self._neighbors[n]:
                                continue  # tivial -- ignore
                        utr = self._untransform_node
                        yield [utr(n) for n in scc]
                    if not ancestors:
                        # dfs tree determined
                        assert not visits
                        break
                    pstate = state[ancestors[-1]]
                    nstate = state[node]
                    low = nstate.low
                    if low < pstate.low:
                        pstate.low = low
                else:  # scheduled first visit
                    node = visit
                    nstate = state.get(node)
                    if nstate is not None:
                        # we have already been visited
                        if nstate.stacked:
                            # update parent
                            pstate = state[ancestors[-1]]
                            if nstate.dfs < pstate.low:
                                pstate.low = nstate.dfs
                        visits.pop()
                        continue
                    unvisited.remove(node)
                    nstate = state[node] = _TarjanState(dfs)
                    ancestors.append(node)
                    stack.append(node)
                    nstate.stacked = True
                    visits[-1] = rtn_marker  # schedule return visit
                    # schedule neighbor visits
                    visits.extend(self._neighbors.get(node, ()))


class _TarjanState:
    """representation of a node's processing state."""
    __slots__ = "stacked dfs low".split()

    def __init__(self, dfs):
        self.stacked = False
        self.dfs = self.low = next(dfs)

    def __repr__(self):
        return "dfs=%d low=%d stacked=%s" \
               % (self.dfs, self.low, self.stacked)
