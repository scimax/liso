"""
Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE, distributed with this software.

Copyright (C) Jun Zhu. All rights reserved.
"""
from collections.abc import Mapping

from collections import OrderedDict
from .beamline import create_beamline


class Linac(Mapping):
    """Linac class.

    The linac class is the abstraction of a linear accelerator. It
    consists of one or multiple beamlines. These beamlines can be
    simulated using different codes.
    """
    def __init__(self):
        self._beamlines = OrderedDict()

    def __getitem__(self, item):
        """Override."""
        return self._beamlines[item]

    def __iter__(self):
        """Override."""
        return self._beamlines.__iter__()

    def __len__(self):
        """Override."""
        return self._beamlines.__len__()

    def add_beamline(self, code, *args, **kwargs):
        """Add a beamline.

        :param str code: Code used to simulate the beamline. ASTRA: 'astra'
            or 'a'; IMPACT-T: 'impactt' or 't'. Case Insensitive.
        """
        bl = create_beamline(code, *args, **kwargs)

        name = bl.name
        if name in self._beamlines:
            raise ValueError(f"Beamline {name} already exists!")

        self._beamlines[name] = bl

    def add_watch(self, name, *args, **kwargs):
        """Add a Watch object to a beamline of the Linac.

        :param str name: beamline name.
        """
        try:
            bl = self._beamlines[name]
        except KeyError:
            raise KeyError(f"Beamline {name} does not exist!")

        bl.add_watch(*args, **kwargs)

    def run(self, mapping, *, n_workers=1, timeout=None, cwd=None):
        """Run simulation for all the beamlines.

        :param dict mapping:
        :param int n_workers: Number of processes used in simulation.
        :param float timeout: Maximum allowed duration in seconds of the
            simulation.
        :param str cwd: current working directory. If None, it is set to the
            same directory as the input file.
        """
        for bl in self._beamlines.values():
            bl.reset()

        # Run simulations, and update all the BeamParameters and LineParameters
        for i, bl in enumerate(self._beamlines.values()):
            bl.run(mapping, n_workers, timeout, cwd)

    def __str__(self):
        text = ''
        for i, beamline in enumerate(self._beamlines.values()):
            text += "\nBeamline {:02d}\n".format(i)
            text += "-" * 11 + "\n"
            text += beamline.__str__()
        return text
