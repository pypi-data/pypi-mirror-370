"""Test new FHI-aims standard output parser."""

from io import StringIO
from textwrap import dedent

import yaml

from pyfhiaims.outputs.parser import StdoutParser
from tests.simple_parser import SimpleParser
from tests.utils import is_subset


def test_empty_parser():
    # empty string - nothing is parsed
    parser = SimpleParser(StringIO(""))
    result = parser.parse()
    assert result == {}
    # Not a parsable string - nothing is parsed
    parser = SimpleParser(StringIO("asdfghjkl"))
    result = parser.parse()
    assert result == {}


def test_converters():
    file_str = dedent("""\
    Version: 1.2
    --- B CHUNK ---
     | B1 = 1
     | B2 = 2 Ry 3.5 eV
     some useless lines
     B3 = 3.5E-5
    """)
    parser = SimpleParser(StringIO(file_str))
    result = parser.parse()
    assert result["version"] == "1.2"
    assert result["b_values"]["b1"] == 1
    assert result["b_values"]["b2"] == 3.5
    assert result["b_values"]["b3"] == 0.000035
    assert "b4" not in result["b_values"]


def test_results_structure():
    file_str = dedent("""\
    B CHUNK
    some useless lines
     B3 = 3.5E-5
    more useless lines
     | B1 = 2
    --- C 1 ---
    time = 0.01
    --- C 2 ---
    time = 0.02
    Everything is good
    --- Values Converged ---
    End time: 170305.22
    """)
    parser = SimpleParser(StringIO(file_str))
    result = parser.parse()
    assert "version" not in result
    assert result["b_values"]["b1"] == 2
    assert result["b_values"]["b3"] == 0.000035
    assert "b4" not in result["b_values"]
    assert [x["t"] for x in result["b_values"]["c_values"]] == [0.01, 0.02]
    assert [x["all_good"] for x in result["b_values"]["c_values"]] == [False, True]
    assert result["b_values"]["c_values"][-1]["end_time"].second == 5


def test_results_k_points(data_dir):
    """Test parsing of output files."""
    file_name = data_dir / "stdout" / "output_files" / "k_points.out.gz"
    parser = StdoutParser(file_name)
    results = parser.parse()
    assert [0.25, -0.25, 0.333333] in results["input"]["k_points"]
    assert 0.04166667 in results["input"]["k_point_weights"]


def test_metadata(data_dir):
    file_name = data_dir / "stdout" / "output_files" / "Si.output_cbm_vbm.out"
    parser = StdoutParser(file_name)
    _ = parser.parse()
    assert parser.run_metadata["xc"] == "pbesol"
    assert parser.run_metadata["num_tasks"] == 4
    assert parser.run_metadata["num_electrons"] == 28.0
    assert parser.run_metadata["num_bands"] == 24
    assert parser.run_metadata["relax"] is False


def test_stdout_parser_regression(data_dir):
    """Checks parsing given output files against reference values."""
    stdout_data_dir = data_dir / "stdout"
    for file_name in stdout_data_dir.iterdir():
        if file_name.is_file():
            parser = StdoutParser(file_name)
            results = parser.parse()
            with open(stdout_data_dir / "ref" / (file_name.stem + ".yaml")) as f:
                ref_data = yaml.safe_load(f)
            assert is_subset(ref_data, results)


# def test_print_parsed_results(data_dir):
#     """This test is for development purposes only."""
#     file_name = data_dir / "stdout" / "output_files" / "Si.output_cbm_vbm.out"
#     parser = StdoutParser(file_name)
#     results = parser.parse()
#     from pprint import pprint
#     pprint(parser.run_metadata)
