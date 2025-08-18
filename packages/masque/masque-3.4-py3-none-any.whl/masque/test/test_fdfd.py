# ruff: noqa: ARG001
import dataclasses
import pytest       # type: ignore
import numpy
from numpy import pi
from numpy.typing import NDArray
#from numpy.testing import assert_allclose, assert_array_equal

from .. import Pattern, Arc



def test_Arc_arclen() -> None:
    max_arclen = 1000

    wedge = Arc(radii=( 50,  50), angles=(-pi/4, pi/4), width=100)
    arc   = Arc(radii=(100, 100), angles=(-pi/4, pi/4), width=1)

    verts_wedge = wedge.to_polygons(max_arclen=max_arclen)[0].vertices
    verts_arc = arc.to_polygons(max_arclen=max_arclen)[0].vertices

    dxy_wedge = numpy.roll(verts_wedge, 1, axis=0) - verts_wedge
    dxy_arc   = numpy.roll(verts_arc, 1, axis=0) - verts_arc

    dl_wedge = numpy.sqrt((dxy_wedge * dxy_wedge).sum(axis=1))
    dl_arc = numpy.sqrt((dxy_arc * dxy_arc).sum(axis=1))

    assert dl_wedge.max() < max_arclen
    assert dl_arc.max() < max_arclen

    print(verts_wedge.shape[0])
    print(verts_arc.shape[0])
    print(dl_wedge, dl_arc)
    Pattern(shapes={(0, 0): [wedge, arc]}).visualize()
    assert False
