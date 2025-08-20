"""Some tests for the AimsStdout object."""

from datetime import date
from math import isclose

import pytest

from pyfhiaims import AimsStdout
from pyfhiaims.errors import AimsParseError
from pyfhiaims.outputs.parser import StdoutParser, converters


def test_stdout_empty(data_dir):
    file_name = data_dir / "stdout" / "output_files" / "preamble_fail.out"
    with pytest.raises(AimsParseError, match="is not a valid FHI-aims output file"):
        _ = AimsStdout(file_name)


@pytest.mark.parametrize("file_name", ["no_control_in.out", "low_stack.out"])
def test_stdout_no_start_warnings(data_dir, file_name):
    """Test raising warnings with incomplete control.in."""
    file_path = data_dir / "stdout" / "output_files" / file_name

    with pytest.warns(UserWarning, match="FHI-aims calculation did not start"):
        _ = AimsStdout(file_path)

    # with pytest.warns(UserWarning, match="No SCF steps found"):
    #     _ = AimsStdout(file_path)


def test_stdout_no_control_in(data_dir):
    """Test parsing output without input files."""
    file_name = data_dir / "stdout" / "output_files" / "no_control_in.out"
    stdout = AimsStdout(file_name)
    assert stdout.aims_version == "240910"
    assert stdout.start_date == date(2025, 1, 10)
    assert not stdout.is_finished_ok
    assert len(stdout.errors) == 1
    assert "Input file control.in not found" in stdout.errors[0]
    # no final values
    assert stdout.energy is None
    assert all(v is None for _, v in stdout.results["final"].items())
    # we got to input, but found nothing
    assert not stdout.results["input"]


def test_stdout_low_stack(data_dir):
    """Test parsing output with low stack size."""
    file_name = data_dir / "stdout" / "output_files" / "low_stack.out"
    stdout = AimsStdout(file_name)
    assert stdout.aims_version == "240910"
    assert not stdout.is_finished_ok
    assert len(stdout.errors) == 1
    assert "Current stacksize too low" in stdout.errors[0]
    assert len(stdout.warnings) == 2
    assert stdout.energy is None
    assert all(v is None for _, v in stdout.results["final"].items())
    assert stdout.metadata.k_grid == "10 10 10"


def test_stdout(data_dir):
    """Test stdout."""
    stdout_data_dir = data_dir / "stdout"
    file_name = stdout_data_dir / "relax.out.gz"
    stdout = AimsStdout(file_name)
    assert len(stdout.warnings) == 1
    assert len(stdout.errors) == 0
    assert stdout.is_finished_ok
    assert stdout.geometry_converged
    assert isclose(stdout.energy, -1071304.321815)
    assert stdout.forces is not None
    assert stdout.metadata.num_atoms == 2


def test_stdout_own_values(data_dir):
    """Test stdout with own values."""
    stdout_data_dir = data_dir / "stdout"
    file_name = stdout_data_dir / "relax.out.gz"
    parser = StdoutParser(file_name)
    parser.add_parsed_values(
        "scf_step",
        cpu_time=converters.to_float(r"Time for this iteration *: *([.\d]+) s"),
    )
    stdout = AimsStdout(file_name, parser=parser)
    for ionic_step in stdout.results["ionic_steps"]:
        for scf_step in ionic_step["scf_steps"][:-1]:
            assert "cpu_time" in scf_step
    assert stdout.results["ionic_steps"][0]["scf_steps"][0]["cpu_time"] == 0.165


def test_stdout_scf_analysis(data_dir):
    """Test stdout with own values."""
    file_name = data_dir / "stdout" / "output_files" / "scf_analysis.out"
    stdout = AimsStdout(file_name)
    assert stdout.aims_version == "250626"
    assert stdout.is_finished_ok
    assert stdout.num_scf_steps == 53

    for i, scf_step in enumerate(stdout.results["ionic_steps"][0]["scf_steps"]):
        if "charge_density_status" in scf_step:
            assert i in [24, 49]
            if i == 24:
                assert scf_step["estimated_steps_to_convergence"] == 28
                assert scf_step["convergence_expected"]
                assert (
                    scf_step["charge_density_status"]
                    == "Good convergence trend detected"
                )
            if i == 49:
                assert scf_step["estimated_steps_to_convergence"] == 3
                assert scf_step["convergence_expected"]
                assert (
                    scf_step["charge_density_status"]
                    == "Good convergence trend detected"
                )


def test_stdout_scf_analysis_spin(data_dir):
    """Test stdout with own values."""
    file_name = data_dir / "stdout" / "output_files" / "scf_analysis_spin.out"
    stdout = AimsStdout(file_name)
    assert stdout.aims_version == "250626"
    assert stdout.is_finished_ok
    assert stdout.num_scf_steps == 53

    for i, scf_step in enumerate(stdout.results["ionic_steps"][0]["scf_steps"]):
        if "charge_density_status" and "spin_density_status" in scf_step:
            assert i in [24, 49]
            if i == 24:
                assert scf_step["estimated_steps_to_convergence"] == 28
                assert scf_step["convergence_expected"]
                assert (
                    scf_step["charge_density_status"]
                    == "Good convergence trend detected"
                )
                assert scf_step["spin_density_status"] == "Already converged"
            if i == 49:
                assert scf_step["estimated_steps_to_convergence"] == 3
                assert scf_step["convergence_expected"]
                assert (
                    scf_step["charge_density_status"]
                    == "Good convergence trend detected"
                )
                assert scf_step["spin_density_status"] == "Already converged"
