"""Test the AimsCube interface"""

import numpy as np
import pytest

from pyfhiaims.control.cube import (
    ALLOWED_AIMS_CUBE_FORMATS,
    ALLOWED_AIMS_CUBE_TYPES,
    ALLOWED_AIMS_CUBE_TYPES_STATE,
    AimsCube,
)

content_block = """output cube elf
    cube origin -1.000000000000e-01  2.000000000000e-01  3.000000000000e-01
    cube edge 30  2.000000000000e-01  1.000000000000e-01  5.000000000000e-02
    cube edge 40 -2.000000000000e-01  1.000000000000e-01 -1.000000000000e-02
    cube edge 10  3.000000000000e-01  2.000000000000e-01  1.000000000000e-01
    cube format cube
    cube spinstate 1
    cube kpoint 2
    cube filename cube_file.cub
    cube elf_type 0
"""


def test_cube(tmp_path):
    """Test the AimsCube Interface"""
    cube_1 = AimsCube(
        type="elf",
        origin=[-0.1, 0.2, 0.3],
        edges=[[0.2, 0.1, 0.05], [-0.2, 0.1, -0.01], [0.3, 0.2, 0.1]],
        points=[30, 40, 10],
        spin_state=1,
        kpoint=2,
        filename="cube_file.cub",
        format="cube",
        elf_type=0,
    )

    test_neq = {
        "type": "stm",
        "origin": [0.1, 0.2, 0.3],
        "edges": [[0.1, 0.1, 0.05], [-0.2, 0.1, -0.01], [0.3, 0.2, 0.1]],
        "points": [20, 40, 10],
        "spin_state": 2,
        "kpoint": 1,
        "filename": "test_cube_file.cub",
        "format": "xsf",
        "elf_type": 1,
    }

    assert cube_1.control_block == content_block
    cube_2 = AimsCube.from_dict(cube_1.as_dict())

    assert cube_1 == cube_2
    for key, val in test_neq.items():
        setattr(cube_2, key, val)
        assert cube_1 != cube_2

        setattr(cube_2, key, getattr(cube_1, key))
        assert cube_1 == cube_2

    for typ in ALLOWED_AIMS_CUBE_TYPES:
        _ = AimsCube(type=typ)
        with pytest.raises(
            ValueError,
            match="can not have a state associated with it"
        ):
            _ = AimsCube(type=f"{typ} 0")

        if typ != "elf":
            with pytest.raises(
                ValueError,
                match="elf_type is only used when the cube type is elf"
            ):
                _ = AimsCube(type=typ, elf_type=1)

    for typ in ALLOWED_AIMS_CUBE_TYPES_STATE:
        _ = AimsCube(type=f"{typ} 1")

        with pytest.raises(
            ValueError,
            match="must have a state associated with it"
        ):
            _ = AimsCube(type=f"{typ}")

        with pytest.raises(
            ValueError,
            match="must have a state associated with it"
        ):
            _ = AimsCube(type=f"{typ} 1 1")

        with pytest.raises(
            ValueError,
            match="elf_type is only used when the cube type is elf"
        ):
            _ = AimsCube(type=f"{typ} 1", elf_type=1)

    with pytest.raises(
        ValueError,
        match="Cube type undefined"
    ):
        _ = AimsCube(type="asdfg")

    for cb_format in ALLOWED_AIMS_CUBE_FORMATS:
        _ = AimsCube(type="total_density", format=cb_format)

    with pytest.raises(
        ValueError,
        match="is invalid. Cube files must have a format of"
    ):
        _ = AimsCube(type="total_density", format="asdfg")

    with pytest.raises(
        ValueError,
        match="Spin state must be one of"
    ):
        _ = AimsCube(type="total_density", spin_state=3)

    with pytest.raises(
        ValueError,
        match="he cube origin must have 3 components"
    ):
        _ = AimsCube(type="total_density", origin=[0])

    with pytest.raises(
        ValueError,
        match="The number of points per edge must have 3 components"
    ):
        _ = AimsCube(type="total_density", points=[0])

    with pytest.raises(
        ValueError,
        match="Only three cube edges can be passed"
    ):
        _ = AimsCube(type="total_density", edges=np.eye(4) * 0.1)

    edges = test_neq["edges"]
    edges[2].append(3)
    with pytest.raises(
        ValueError,
        match="Each cube edge must have 3 components"
    ):
        _ = AimsCube(type="total_density", edges=edges)
