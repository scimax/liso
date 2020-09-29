"""
Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE, distributed with this software.

Copyright (C) Jun Zhu. All rights reserved.
"""
from .file_access import FileAccess


class DataCollection:
    """A collection of simulated data."""
    def __init__(self, files):
        """Initialization

        :param list files: a list of FileAccess instances.
        """
        self._files = list(files)

        self.control_sources = set()
        self.phasespace_sources = set()
        for fa in self._files:
            self.control_sources.update(fa.control_sources)
            self.phasespace_sources.update(fa.phasespace_sources)

        self.control_sources = frozenset(self.control_sources)
        self.phasespace_sources = frozenset(self.phasespace_sources)

        # this returns a list!
        self.sim_ids = sorted(set().union(*(f.sim_ids for f in files)))

    @classmethod
    def from_path(cls, path):
        files = [FileAccess(path)]
        return cls(files)


def open_sim(filepath):
    return DataCollection.from_path(filepath)
