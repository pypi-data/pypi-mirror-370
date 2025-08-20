"""Tests for IntegrationGrid class."""

from textwrap import dedent

from pyfhiaims.species_defaults.integration_grid import IntegrationGrid


def test_integration_grid():
    """Test integration grids."""
    test_string = dedent(
        """\
    radial_base         24 7.0
    radial_multiplier   8
    angular_grids       specified
    division   0.1930   50
    division   0.3175  110
    division   0.4293  194
    division   0.5066  302
    division   0.5626  434
    division   0.5922  590
    #    division   0.6227  974
    #    division   0.6868 1202
    outer_grid  770
    #    outer_grid  434
    """
    )
    grid = IntegrationGrid.from_string(test_string)
    assert grid.radial_grid.radius == 7.0
    assert len(grid.angular_grid.r) == 6
