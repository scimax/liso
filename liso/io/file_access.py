"""
Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE, distributed with this software.

Copyright (C) Jun Zhu. All rights reserved.
"""
import os.path as osp
import resource

from collections import OrderedDict
from weakref import WeakValueDictionary

import h5py

# Track all FileAccess objects - {path: FileAccess}
_file_access_registry = WeakValueDictionary()


class FileOpenRegistry:

    def __init__(self, n_max):
        """Initialization.

        :param int n_max: maximum number of files.
        """
        self._n_max = n_max

        # key: filepath, value: None (not used)
        self._cache = OrderedDict()

    def n_opened(self):
        """Return the number of opened files."""
        # remove files which are not in the registry
        self._cache = OrderedDict.fromkeys(
            path for path in self._cache if path in _file_access_registry
        )
        return len(self._cache)

    def close_old_files(self):
        """Close old files if the number of opened files exceed the maximum."""
        if len(self._cache) <= self._n_max:
            return

        n = self.n_opened()
        while n > self._n_max:
            path, _ = self._cache.popitem(last=False)
            file_access = _file_access_registry.get(path, None)
            if file_access is not None:
                file_access.close()
            n -= 1

    def touch(self, filepath):
        """Add a new file or move the existing file to the end of the cache."""
        if filepath in self._cache:
            self._cache.move_to_end(filepath)
        else:
            self._cache[filepath] = None
            self.close_old_files()

    def remove(self, filename):
        """Remove a closed file from the cache."""
        self._cache.pop(filename, None)


def _init_file_open_registry():
    # (soft, hard) = (1024, 4096) on the Maxwell cluster
    max_files = resource.getrlimit(resource.RLIMIT_NOFILE)
    return FileOpenRegistry(max_files[0])


_file_open_registry = _init_file_open_registry()


class FileAccess:
    """Access an HDF5 file.

    This does not necessarily keep the real file open, but opens it on demand.
    It assumes that the file is not changing on disk while this object exists.
    """
    _file = None

    def __new__(cls, filepath):
        filepath = osp.abspath(filepath)
        instance = _file_access_registry.get(filepath, None)
        if instance is None:
            instance = super().__new__(cls)
            instance._filepath = filepath
            _file_access_registry[filepath] = instance
        return instance

    def __init__(self, filepath):
        self.control_sources, self.phasespace_sources = \
            self._read_data_sources()

        self.sim_ids = self.file["INDEX/simId"][()]

    @property
    def file(self):
        _file_open_registry.touch(self._filepath)
        if self._file is None:
            self._file = h5py.File(self._filepath, 'r')
        return self._file

    def _read_data_sources(self):
        control_sources, phasespace_sources = set(), set()

        data_sources_path = 'METADATA/SOURCE'
        for src in self.file[data_sources_path]['control'][()]:
            control_sources.add(src)
        for src in self.file[data_sources_path]['phasespace'][()]:
            phasespace_sources.add(src)

        return frozenset(control_sources), frozenset(phasespace_sources)

    def close(self):
        """Close the HDF5 file this refers to.

        The file may not actually be closed if there are still references to
        objects from it, e.g. while iterating over trains. This is what HDF5
        calls 'weak' closing.
        """
        if self._file:
            self._file = None
        _file_open_registry.remove(self._filepath)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(self._filepath))
