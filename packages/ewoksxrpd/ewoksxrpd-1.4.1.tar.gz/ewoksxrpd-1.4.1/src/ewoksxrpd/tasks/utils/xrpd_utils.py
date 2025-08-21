import os
from typing import Dict, Iterable, Tuple, List
import pyFAI.units
import pyFAI.calibrant


def energy_wavelength(x: float) -> float:
    """keV to m and vice versa"""
    return pyFAI.units.hc * 1e-10 / x


GEOMETRY_PARAMETERS = {"dist", "poni1", "poni2", "rot1", "rot2", "rot3"}


def validate_geometry(geometry: dict):
    required = GEOMETRY_PARAMETERS
    existing = set(geometry.keys())
    missing = required - existing
    if missing:
        raise ValueError(f"geometry has missing parameters {sorted(missing)}")
    unexpected = existing - required
    if unexpected:
        raise ValueError(f"geometry has unexpected parameters {sorted(unexpected)}")


def calibrant_ring_labels(calibrant: pyFAI.calibrant.Calibrant) -> List[str]:
    path = calibrant.get_filename()
    try:
        # Introduced in pyfai v2023.08
        path = calibrant._get_abs_path(path)
    except AttributeError:
        pass
    if not path or not os.path.isfile(path):
        raise ValueError(f"No such calibrant file: {path}")

    labels = list()
    i = 0
    with open(path, "r") as fd:
        for line in fd:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            label = line.rpartition("#")[-1]
            if not label or label in labels:
                label = f"ring{i}"
            label = label.strip()
            labels.append(label)
            i += 1
    return labels


def points_to_rings(
    points: Iterable[Tuple[float, float, int]], calibrant: pyFAI.calibrant.Calibrant
) -> Dict[int, Dict[str, list]]:
    rings = dict()
    labels = calibrant_ring_labels(calibrant)
    for p0, p1, i in points:
        i = int(i)
        try:
            label = labels[i]
        except IndexError:
            label = f"ring{i}"
        adict = rings.get(label)
        if adict:
            adict["p0"].append(p0)
            adict["p1"].append(p1)
        else:
            rings[label] = {"p0": [p0], "p1": [p1]}
    return rings
