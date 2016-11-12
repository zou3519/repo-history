#!/usr/bin/python3
import cPickle as pickle
import bisect
import difflib
import networkx as nx
import json

# Models individual insertions and deletions as Patches, revisions as
#   PatchSets, and the history of ownership of text as a PatchModel


class PatchType:
    """
        Add if text was inserted. Delete if text was removed
    """
    ADD = 0
    DELETE = 1


class Patch:
    """
        A Patch is a contiguous block of added or deleted words
            representing a single edit.
    """

    def __init__(self, pid, ptype, start, end, content, revision):
        assert ptype == PatchType.ADD or ptype == PatchType.DELETE
        assert start >= 0
        assert end > start

        self.pid = pid
        self.ptype = ptype
        self.start = start
        self.end = end
        self.length = end - start
        # "".join([line[1:] for line in content])
        self.content = str([line[2:] for line in content])
        self.revision = revision


def reorder_diff(diff):
    """Preprocess so if there is a contiguous string of only +- (no space), the - comes before +"""
    def is_plus(line):
        return line[0] == '+'

    def is_minus(line):
        return line[0] == '-'

    def is_land(line):
        return line[0] != ' '

    def at_world_edge(index, diff):
        return index + 1 == len(diff)

    def record_land(line, minus, plus):
        if is_plus(line):
            plus.append(line)
        elif is_minus(line):
            minus.append(line)

    in_island = False
    start = 0
    minus, plus = [], []
    for index in xrange(0, len(diff)):
        unit = diff[index]
        if not in_island:
            if not is_land(unit):
                continue
            in_island = True
            start = index

        # Currently on island
        if is_land(unit):
            record_land(unit, minus, plus)

        # Next unit is not island anymore
        if not is_land(unit) or at_world_edge(index, diff):
            end = index + (1 if at_world_edge(index, diff) else 0)
            minus.extend(plus)
            for i in xrange(start, end):
                diff[i] = minus[i - start]
            in_island = False
            plus, minus = [], []


class PatchSet:
    """
        A PatchSet is a list of Patches (edits) that belong to the
        same revision.

        Each Patch implicitly depend on preceding Patches.
    """

    def __init__(self):
        self.patches = []

    @classmethod
    def psdiff(cls, startid, old, new, rvid):
        """
            Compares 2 vesions of text at a word level to identify 
                the individual edits (insertions and deletions).
        """
        ptype = None
        ps = cls()
        start = None
        pid = startid

        # Obtain a list of differences between the texts
        diff = difflib.ndiff(old, new)

        # debugging
        diff = [line for line in diff]
        # ignore helper lines
        diff = [line for line in diff if not line.startswith('?')]
        reorder_diff(diff)
        print("diffset: \n%s" % '\n'.join(diff))

        # print("")
        # print("old: %s" % '\n'.join(old))
        # print("new: %s" % '\n'.join(new))
        # print("diffset: %s" % '\n'.join(diff))
        # print("")

        # Split the differences into Patches
        index = 0
        deletes = 0
        for line in diff:

            if line[0] == ' ':
                # If equal, terminate any current patch.
                if ptype is not None:
                    ps.append_patch(
                        Patch(pid, ptype, start, index, diff[start + deletes:index + deletes], rvid))
                    pid += 1
                    if ptype == PatchType.DELETE:
                        deletes += index - start
                        index = start
                    ptype = None
                index += 1
            elif line[0] == '+':
                # If addition, terminate any current DELETE patch.
                if ptype == PatchType.DELETE:
                    ps.append_patch(
                        Patch(pid, ptype, start, index, diff[start + deletes:index + deletes], rvid))
                    pid += 1
                    deletes += index - start
                    index = start
                    ptype = None
                # Begin a new ADD patch, or extend an existing one.
                if ptype is None:
                    ptype = PatchType.ADD
                    start = index
                index += 1
            elif line[0] == '-':
                # If deletion, terminate any current ADD patch.
                if ptype == PatchType.ADD:
                    ps.append_patch(
                        Patch(pid, ptype, start, index, diff[start + deletes:index + deletes], rvid))
                    pid += 1
                    ptype = None
                # Begin a new DELETE patch, or extend an existing one.
                if ptype is None:
                    ptype = PatchType.DELETE
                    start = index
                index += 1
            # Skip line[0] == '?' completely.

        # Terminate and add any remaining patch.
        if ptype is not None:
            ps.append_patch(Patch(pid, ptype, start, index, diff[
                            start + deletes:index + deletes], rvid))

        # print "Patch: "
        # print "".join([line[1:] for line in diff[start:index]])
        return ps

    def append_patch(self, p):
        self.patches.append(p)


class PatchModel:
    """
        A PatchModel model gives ownership of indices of the current text to
            the Patch that last modified that section of text.
    """

    def __init__(self):
        self.model = []
        self.graph = nx.DiGraph()

    @classmethod
    def read_from_file(cls, filename):
        return pickle.load(open(filename, 'rb'))

    def save_to_file(self, filename):
        pickle.dump(self, open(filename, 'wb'))

    def apply_patch(self, p, timestamp):
        """
            Adds Patch, p, to the model and graph
        """
        # print("Insert patch: " + str(p.__dict__))
        self.graph.add_node(p.pid, time=timestamp, size=p.length)
        self.graph.node[p.pid]['patch'] = json.dumps(p.__dict__)
        if not self.model:
            self.model.append((p.end, p.pid))

        elif p.ptype == PatchType.ADD:
            # Find indices that share a range with p
            sin = bisect.bisect_left(
                [end for (end, pid) in self.model], p.start)
            ein = bisect.bisect_right(
                [end for (end, pid) in self.model], p.start)

            # Add dependencies

            # Case 1: Insertion into the middle of one edit
            if sin == ein:  # startindex == endindex
                pid = self.model[sin][1]
                if sin == 0:
                    start = 0
                else:
                    start = self.model[sin - 1][0]
                length = self.model[sin][0] - start
                self.graph.add_edge(p.pid, pid, prob=1.0)

            # Case 2: Insertion between 2 edits or at the end of the document
            elif (ein - sin) == 1:
                total = 0
                if sin == 0:
                    start = 0
                else:
                    start = self.model[sin - 1][0]

                total = 0
                nstart = start
                for (end, pid) in self.model[sin:(ein + 1)]:
                    total += end - nstart
                    nstart = end
                nstart = start
                for (end, pid) in self.model[sin:(ein + 1)]:
                    length = end - nstart
                    nstart = end
                    prob = float(length) / total
                    self.graph.add_edge(p.pid, pid, prob=prob)

            # Case 3: Replacement, insertion depends on deletions
            else:

                # Get total size of dependencies to find weight of dependence
                # Only include deletes in range
                start = p.start
                total = 0
                for (end, pid) in self.model[sin:(ein + 1)]:
                    if p.end < end:
                        length = p.end - start
                    else:
                        length = end - start
                        start = end
                    # Delete patches act like invisible text
                    if length == 0:
                        total += self.graph.node[pid]['size']

                # Add dependencies to graph with weights
                start = p.start
                for (end, pid) in self.model[sin:(ein + 1)]:
                    if p.end < end:
                        length = p.end - start
                    else:
                        length = end - start
                        start = end
                    if length == 0:
                        length = self.graph.node[pid]['size']
                        prob = float(length) / total
                        self.graph.add_edge(p.pid, pid, prob=prob)

            # Remove intermediates if present.
            # Leave the first preceeding Patch
            if sin != ein:
                del self.model[(sin + 1):ein]
            # Else, split the surrounding span.
            else:
                (end, pid) = self.model[sin]
                self.model.insert(sin, (p.start, pid))
            ein = sin + 1

            # Insert.
            self.model.insert(ein, (p.end, p.pid))

            # Update proceeding spans.
            self.model[(ein + 1):] = \
                [(end + p.length, pid) for (end, pid)
                 in self.model[(ein + 1):]]

        elif p.ptype == PatchType.DELETE:
            # Find indices of Patches who fall in the deleted range.
            sin = bisect.bisect_right(
                [end for (end, pid) in self.model], p.start)
            ein = bisect.bisect_left(
                [end for (end, pid) in self.model], p.end)

            # Get total size of dependencies to find weight of dependence
            start = p.start
            total = 0
            for (end, pid) in self.model[sin:(ein + 1)]:
                if p.end < end:
                    length = p.end - start
                else:
                    length = end - start
                    start = end
                # Delete patches act like invisible text
                if length == 0:
                    total += self.graph.node[pid]['size']
                else:
                    total += length

            # Add dependencies to graph with weights
            start = p.start
            for (end, pid) in self.model[sin:(ein + 1)]:
                if p.end < end:
                    length = p.end - start
                else:
                    length = end - start
                    start = end
                if length == 0:
                    length = self.graph.node[pid]['size']
                prob = float(length) / total

                self.graph.add_edge(p.pid, pid, prob=prob)

            # Adjust indices to include Patches that end where p starts
            #   or end where p ends.
            if sin != bisect.bisect_left(
               [end for (end, pid) in self.model], p.start):
                sin -= 1
            if ein != bisect.bisect_right(
                    [end for (end, pid) in self.model], p.end):
                ein += 1

            # Shrink the preceding span and remove intermediates if present
            (end, pid) = self.model[sin]
            if sin != ein:
                self.model[sin] = (p.start, pid)
                del self.model[(sin + 1):ein]
            # Else, split the surrounding span.
            else:
                self.model.insert(sin, (p.start, pid))
            ein = sin + 1

            # Insert.
            self.model.insert(ein, (p.start, p.pid))

            # Update the proceeding spans.
            self.model[(ein + 1):] = \
                [(end - p.length, pid) for (end, pid)
                 in self.model[(ein + 1):]]

        else:
            assert False
