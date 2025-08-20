"""Parsers for FHI-aims standard output file."""

import numpy as np

from . import converters
from .abc import ChunkParser, FileParser


class RootParser(FileParser):
    """Base parser for output parsing."""

    name = "root"
    initial_chunk = "preamble"


class PreambleParser(ChunkParser):
    """Parse the preamble portion of aims.out file."""

    name = "preamble"
    values = {
        "aims_version": r"FHI-aims version *: (\w*)",
        "start_date": converters.to_date(r"Date *:  (\d*)"),
        "start_time": converters.to_time(r"Time *:  ([\d.]*)"),
    }
    metadata = {
        "aims_version": r"FHI-aims version *: (\w*)",
        "commit_hash": r"Commit number *: (\w*)",
        "aims_uuid": r"aims_uuid : ([^\n]+)$",
        "fortran_compiler": r"Fortran compiler *: ([^\n]+)$",
        "fortran_compiler_flags": r"Fortran compiler flags: ([^\n]+)$",
        "c_compiler": r"C compiler *: ([^\n]+)$",
        "c_compiler_flags": r"C compiler flags *: ([^\n]+)$",
        "cxx_compiler": r"C\+\+ compiler *: ([^\n]+)$",
        "cxx_compiler_flags": r"C\+\+ compiler flags *: ([^\n]+)$",
        "elpa_kernel": r"  ELPA2 kernel *: (\w*)",
        "build_type": converters.to_vector(r"Using (\S+)", dtype=str, multistring=True),
        "linked_against": converters.to_vector(
            r"(?:Linking against:|^ *) (\/\S+)", dtype=str, multistring=True
        ),
        "num_tasks": converters.to_int(r"Using *(\d+) parallel tasks."),
    }
    next_chunks = ["control_in"]
    parsed_key = ""


class ControlInParser(ChunkParser):
    """Parse the control.in portion of aims.out file."""

    name = "control_in"
    title_line = r"Parsing control.in"
    values = {"control_in": r"-{71}\n(.+)  -{71}\n  Completed first pass"}
    next_chunks = ["geometry_in"]
    parsed_key = "input"

    def parse(self):
        """Make additional adjustments to parse results."""
        parse_results = super().parse()
        # get the runtime choices
        choices = {}
        if "control_in" not in parse_results:
            return parse_results
        for line in parse_results["control_in"].split("\n"):
            if "species" in line:
                break
            hash_idx = line.find("#")
            keywords = (line[:hash_idx] if hash_idx >= 0 else line).strip().split()
            if keywords:
                choices[keywords[0]] = " ".join(keywords[1:])
        self.parent.run_metadata.update(choices)
        return parse_results


class GeometryInParser(ChunkParser):
    """Parse the geometry.in portion of aims.out file."""

    name = "geometry_in"
    title_line = r"Parsing geometry.in"
    values = {"geometry_in": r"-{71}\n(.+)  -{71}\n  Completed first pass"}
    metadata = {
        "num_species": converters.to_int(r"Number of species *: *(\d+)"),
        "num_atoms": converters.to_int(r"Number of atoms *: *(\d+)"),
        "num_spins": converters.to_int(r"Number of spin channels *: *(\d+)"),
    }
    next_chunks = ["reading_control_in"]
    parsed_key = "input"


class ReadingControlParser(ChunkParser):
    """Parse the reading control portion of aims.out file."""

    name = "reading_control_in"
    title_line = r"Reading file control.in"
    values = {
        "electronic_temperature": converters.to_float(
            r"broadening, width = *([-+.E\d]+) eV."
        )
    }
    next_chunks = ["reading_geometry_in"]
    parsed_key = "input"
    metadata = {
        "relax": converters.to_bool(r"Geometry relaxation"),
        "md": converters.to_bool(r"Molecular dynamics"),
    }


class ReadingGeometryParser(ChunkParser):
    """Parse the reading geometry portion of aims.out file."""

    name = "reading_geometry_in"
    title_line = r"Reading geometry description geometry.in"
    values = {
        "geometry": converters.to_atoms(r"Input geometry:\n(.*?)$^\n", from_input=True)
    }
    next_chunks = ["consistency_checks"]
    parsed_key = "input"


class ConsistencyChecksParser(ChunkParser):
    """Parse the consistency check portion of aims.out file."""

    name = "consistency_checks"
    title_line = r"Consistency checks .* are next"
    values = {
        "electronic_temperature": converters.to_float(
            r"broadening, width = *([-+.E\d]+) eV."
        )
    }
    metadata = {
        "num_bands": converters.to_int(
            r"Number of Kohn-Sham states \(occupied \+ empty\): *(\d+)"
        ),
    }
    next_chunks = ["fixed_parts"]
    parsed_key = "input"


class FixedPartsParser(ChunkParser):
    """Parse the fixed values portion of aims.out file."""

    name = "fixed_parts"
    title_line = r"Preparing all fixed parts"
    values = {
        "k_points": converters.to_matrix(
            r"(?:  \| k-point: *\d+ at *([-.\d]+) * *([-.\d]+) *([-.\d]+) *, "
            r"weight: *([-.\d]+))+",
            dtype=[float, float, float, float],
        )
    }
    metadata = {
        "num_bands": converters.to_int(
            r"Reducing total number of +Kohn-Sham states to *(\d+)"
        ),
        "num_basis_fns": converters.to_int(r"Total number of basis functions : *(\d+)"),
        "num_k_points": converters.to_int(r"Number of k-points *: *(\d+)"),
    }
    next_chunks = ["scf_init"]
    parsed_key = "input"

    def parse(self) -> dict:
        """Make additional adjustments to fixed-parts parse results."""
        parse_results = super().parse()
        if "k_points" in parse_results:
            parse_results.update(
                {
                    "k_points": [p[:3] for p in parse_results["k_points"]],
                    "k_point_weights": [p[3] for p in parse_results["k_points"]],
                }
            )
            assert len(parse_results["k_points"]) == self.run_metadata["num_k_points"]
        return parse_results


class SCFInitParser(ChunkParser):
    """Parse the SCF Initiation portion of aims.out file."""

    name = "scf_init"
    title_line = r"Begin self-consistency loop"
    next_chunks = ["init_values"]
    parsed_key = "ionic_steps[]"


class ScfInitValuesParser(ChunkParser):
    """Parse the SCF initialization portion of aims.out file."""

    name = "init_values"
    title_line = r"-{60}"
    values = {
        "chemical_potential": converters.to_float(
            r"  \| Chemical potential \(Fermi level\): *([-+.E\d]*) eV"
        ),
        "vbm": converters.to_float(r"Highest occupied state \(VBM\) at *([-.\d]*) eV"),
        "cbm": converters.to_float(r"Lowest unoccupied state \(CBM\) at *([-.\d]*) eV"),
        "gap": converters.to_float(r"HOMO-LUMO gap: *([-+.E\d]*) eV"),
        "total_energy": converters.to_float(
            r"  \| Total energy *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
        "free_energy": converters.to_float(
            r"  \| Electronic free energy *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
    }
    metadata = {
        "num_electrons": converters.to_float(
            r"Formal number of electrons \(from input files\) : *([\d.]+)"
        ),
        "num_k_points": converters.to_int(r"Number of k-points *: *(\d+)"),
    }
    next_chunks = [
        {"runtime_choices": {"output_level": "MD_light"}, "chunk": "mdlight_scf"},
        "scf_init",
        "scf_step",
        "final_values",
    ]
    parsed_key = "ionic_steps.scf_init"


class SCFStepParser(ChunkParser):
    """Parse the SCF step portion of aims.out file."""

    name = "scf_step"
    title_line = r"Begin self-consistency iteration"
    values = {
        "chemical_potential": converters.to_float(
            r"  \| Chemical potential \(Fermi level\): *([-+.E\d]*) eV"
        ),
        "vbm": converters.to_float(r"Highest occupied state \(VBM\) at *([-.\d]*) eV"),
        "cbm": converters.to_float(r"Lowest unoccupied state \(CBM\) at *([-.\d]*) eV"),
        "gap": converters.to_float(r"HOMO-LUMO gap: *([-+.E\d]*) eV"),
        "direct_gap": converters.to_float(r"Smallest direct gap : *([-+.E\d]*) eV"),
        "is_metallic": converters.to_bool(r"this material is metallic"),
        "spin": converters.to_float(
            r"  \| N = N_up - N_down (?:\(sum over all k points\)|): *([-.\d]*)"
        ),
        "total_energy": converters.to_float(
            r"  \| Total energy *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
        "free_energy": converters.to_float(
            r"  \| Electronic free energy *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
        "charge_density_change": converters.to_float(
            r"  \| Change of charge density *: *([-+.E\d]*)"
        ),
        "charge_spin_density_change": converters.to_vector(
            r"  \| Change of charge/spin density *: *([-+.E\d]*)  *([-+.E\d]*)",
            dtype=float,
        ),
        "eigenvalues_sum_change": converters.to_float(
            r"  \| Change of sum of eigenvalues *: *([-+.E\d]*)"
        ),
        "total_energy_change": converters.to_float(
            r"  \| Change of total energy *: *([-+.E\d]*)"
        ),
        "change_of_forces": converters.to_float(
            r"  \| Change of forces *: *([-+.E\d]*) eV/A"
        ),
        "analytical_stress": converters.to_table(
            r"  \| *Analytical stress tensor - Symmetrized *\|",
            header=5,
            num_rows=3,
            dtype=[None, None, float, float, float, None],
        ),
        "pressure": converters.to_float(r"Pressure: *([-+.E\d]*)"),
        "charge_density_status": r"Charge density*: ([^\n]+)$",
        "spin_density_status": r"Spin density*: ([^\n]+)$",
        "estimated_steps_to_convergence": converters.to_int(
            r"Estimated *(\d+)* more steps to reach target accuracy"
        ),
    }
    next_chunks = ["scf_step", "converged_scf", "not_converged_scf", "final_values"]
    parsed_key = "ionic_steps.scf_steps[]"

    def parse(self) -> dict:
        """Make additional adjustments to parse results."""
        parse_results = super().parse()
        if "charge_spin_density_change" in parse_results:
            charge, spin = parse_results.pop("charge_spin_density_change")
            parse_results["charge_density_change"] = charge
            parse_results["spin_density_change"] = spin

        if "charge_density_status" in parse_results:
            if "estimated_steps_to_convergence" in parse_results:
                parse_results["convergence_expected"] = True
            else:
                parse_results["convergence_expected"] = False

        return parse_results


class MDLightSCFParser(ChunkParser):
    """Parse the SCF steps table of aims.out file for `MD_light` output level."""

    name = "mdlight_scf"
    title_line = r"Convergence:"
    next_chunks = ["mdlight_energy"]
    parsed_key = "ionic_steps"

    def parse(self):
        """Make additional adjustments to parse results."""
        content = self.collect()
        step_lines = []
        for line in content.splitlines()[1:-1]:
            if line.startswith("  SCF"):
                step_lines.append(line)
            else:
                step_lines[-1] += line
        # Each step:  q app. | density  | eigen (eV) | Etot (eV) | forces (eV/A) | CPU time | Clock time # noqa: E501
        steps = []
        for step in step_lines:
            results = [val for val in step.split("|") if not val.strip()[0].isalpha()]

            steps.append(
                {
                    "eigenvalues_sum_change": float(results[1]),
                    "total_energy_change": float(results[2]),
                    "cpu_time": float(results[4].split()[0]),
                    "wall_time": float(results[5].split()[0]),
                }
            )
            try:
                charge_spin_change = results[0].split()
                steps[-1]["charge_density_change"] = float(charge_spin_change[0])
                if len(charge_spin_change) > 1:
                    steps[-1]["spin_density_change"] = float(charge_spin_change[1])
                steps[-1]["change_of_forces"] = float(results[3])
            except ValueError:
                pass
        return {"scf_steps": steps}


class MDLightEnergyParser(SCFStepParser):
    """Parse the SCF energy for `MD_light` output level of aims.out file."""

    name = "mdlight_energy"
    title_line = r"Total energy components:"
    values = {
        "chemical_potential": converters.to_float(
            r"  \| Chemical potential \(Fermi level\): *([-+.E\d]*) eV"
        ),
        "vbm": converters.to_float(r"Highest occupied state \(VBM\) at *([-.\d]*) eV"),
        "cbm": converters.to_float(r"Lowest unoccupied state \(CBM\) at *([-.\d]*) eV"),
        "gap": converters.to_float(r"HOMO-LUMO gap: *([-+.E\d]*) eV"),
        "direct_gap": converters.to_float(r"Smallest direct gap : *([-+.E\d]*) eV"),
        "is_metallic": converters.to_bool(r"this material is metallic"),
        "spin": converters.to_float(
            r"  \| N = N_up - N_down (?:\(sum over all k points\)|): *([-.\d]*)"
        ),
        "total_energy": converters.to_float(
            r"  \| Total energy *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
        "free_energy": converters.to_float(
            r"  \| Electronic free energy *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
    }
    next_chunks = [
        "scf_init",
        "converged_scf",
        "mulliken",
        "final_values",
    ]
    parsed_key = "ionic_steps"


class NotConvergedSCFParser(ChunkParser):
    """Parse the non-converged SCF part of aims.out file."""

    name = "not_converged_scf"
    title_line = r"WARNING! SELF-CONSISTENCY CYCLE DID NOT CONVERGE"
    values = {
        "scf_converged": converters.to_bool(r"Self-consistency cycle converged"),
    }
    next_chunks = [
        "hirshfeld",
        "mulliken",
        "final_values",
    ]
    parsed_key = "ionic_steps"


class ConvergedSCFParser(ChunkParser):
    """Parse the converged SCF values of aims.out file."""

    name = "converged_scf"
    title_line = r"Self-consistency cycle converged"
    values = {
        "scf_converged": converters.to_bool(r"Self-consistency cycle converged"),
        "total_energy": converters.to_float(
            r"  \| Total energy uncorrected *: *([-+.E\d]*) eV"
        ),
        "corrected_total_energy": converters.to_float(
            r"  \| Total energy corrected *: *([-+.E\d]*) eV"
        ),
        "free_energy": converters.to_float(
            r"  \| Electronic free energy *: *([-+.E\d]*) eV"
        ),
        "vdw_correction": converters.to_float(
            r"  \| vdW energy correction *: *[-.\d]* Ha *([-.\d]*) eV"
        ),
        # charge / dipole moments
        "total_charge": converters.to_float(r"  \| Total charge \[e\] *: *([-+.E\d]*)"),
        "total_dipole_moment": converters.to_vector(
            r"  \| Total dipole moment \[eAng\] *: "
            r"*([-+.E\d]*) *([-+.E\d]*) *([-+.E\d]*)",
            dtype=float,
        ),
        "absolute_dipole_moment": converters.to_float(
            r"  \| Absolute dipole moment *: *([-+.E\d]*)"
        ),
        "hirshfeld_charges": converters.to_vector(
            r"  \|   Hirshfeld charge *: *([-+.\d]*)", multistring=True
        ),
        # forces and stress
        "atomic_forces": converters.to_table(
            r"Total atomic forces [^\n]* \[eV\/Ang\]:",
            num_rows="num_atoms",
            dtype=[None, None, float, float, float],
        ),
        "analytical_stress": converters.to_table(
            r"  \| *Analytical stress tensor - Symmetrized *\|",
            header=5,
            num_rows=3,
            dtype=[None, None, float, float, float, None],
        ),
        "numerical_stress": converters.to_table(
            r"  \| *Numerical stress tensor *\|",
            header=5,
            num_rows=3,
            dtype=[None, None, float, float, float, None],
        ),
        "pressure": converters.to_float(r"Pressure: *([-+.E\d]*)"),
        "atomic_stresses": converters.to_table(
            r"Per atom stress \(eV\) used for heat flux calculation:",
            header=3,
            num_rows="num_atoms",
            dtype=[None, None, float, float, float, float, float, float],
        ),
    }
    next_chunks = [
        "scf_init",
        "ionic_step_geometry",
        {
            "runtime_choices": {"calculate_atom_bsse": True},
            "chunk": "bsse_ionic_step_geometry",
        },
        {"runtime_choices": {"md": True}, "chunk": "md_values"},
        {"runtime_choices": {"qpe_calc": "gw_expt"}, "chunk": "periodic_gw"},
        "final_geometry",
        "mulliken",
        "hirshfeld",
        "output_polarization",
        "dfpt_dielectric",
        "final_values",
    ]
    parsed_key = "ionic_steps"


class MullikenAnalysisParser(ChunkParser):
    """Parse the Mulliken analysis part of aims.out file."""

    name = "mulliken"
    title_line = r" *Starting Mulliken Analysis"
    values = {
        "mulliken_charges": converters.to_table(
            r"Performing (?:scalar-relativistic )?Mulliken charge[\s\S]*?"
            r"Summary of the per-atom charge analysis:",
            header=3,
            num_rows="num_atoms",
            dtype=[None, None, None, float, None, None, None, None],
        ),
        "mulliken_spins": converters.to_table(
            r"Performing (?:scalar-relativistic )?Mulliken charge[\s\S]*?"
            r"Summary of the per-atom spin analysis:",
            header=3,
            num_rows="num_atoms",
            dtype=[None, None, float, None, None, None],
        ),
        "mulliken_charges_soc": converters.to_table(
            r"Performing spin-orbit-coupled Mulliken charge[\s\S]*?"
            r"Summary of the per-atom charge analysis:",
            header=3,
            num_rows="num_atoms",
            dtype=[None, None, None, float, None, None, None, None],
        ),
        "mulliken_spins_soc": converters.to_table(
            r"Performing spin-orbit-coupled Mulliken charge[\s\S]*?"
            r"Summary of the per-atom spin analysis:",
            header=3,
            num_rows="num_atoms",
            dtype=[None, None, float, None, None, None],
        ),
    }
    next_chunks = [
        "hirshfeld",
        "output_polarization",
        "dfpt_dielectric",
        "final_values",
    ]
    parsed_key = "final"


class DFPTDielectricParser(ChunkParser):
    """Parse the DFPT analysis part of aims.out file."""

    name = "dfpt_dielectric"
    title_line = r"ENTERING DFPT_DIELECTRIC"
    values = {
        "polarizability": converters.to_vector(
            r"  \| Polarizability:---> *([-+.\d]*) *([-+.\d]*) *([-+.\d]*) *([-+.\d]*) *([-+.\d]*) *([-+.\d]*)",  # noqa: E501
            dtype=float,
        ),
        "dielectric_tensor": converters.to_table(
            r"DFPT for dielectric_constant:--->  # PARSE DFPT_dielectric_tensor",
            header=1,
            num_rows=3,
            dtype=[float, float, float],
        ),
    }
    next_chunks = ["output_polarization", "final_values"]
    parsed_key = "dfpt"


class PolarizationParser(ChunkParser):
    """Parse the Polarization calculation part of aims.out file."""

    name = "output_polarization"
    title_line = r"Starting with the calculation of the polarization"
    values = {
        "polarization": converters.to_vector(
            r"  \| Cartesian Polarization *([-+.\d]*) *([-+.\d]*) *([-+.\d]*)",
            dtype=float,
        ),
    }
    next_chunks = ["dfpt_dielectric", "final_values"]
    parsed_key = "polarization"


class HirshfeldAnalysisParser(ChunkParser):
    """Parse the Hirshfeld analysis part of aims.out file."""

    name = "hirshfeld"
    title_line = r"Performing Hirshfeld analysis of fragment charges and moments."
    values = {
        "hirshfeld_charges": converters.to_vector(
            r"  \|   Hirshfeld charge *: *([-+.\d]*)", multistring=True
        ),
        "hirshfeld_spins": converters.to_vector(
            r"  \|   Hirshfeld spin moment *: *([-+.\d]*)", multistring=True
        ),
        "hirshfeld_dipoles": converters.to_vector(
            r"  \|   Hirshfeld dipole moment *: *([-+.\d]*)", multistring=True
        ),
    }
    next_chunks = ["final_values"]
    parsed_key = "final"


class PeriodicGWParser(ChunkParser):
    """Parse the Periodic GW portion of aims.out file."""

    name = "periodic_gw"
    title_line = r"Initializing LVL tricoefficents in reciprocal space for GW ..."
    values = {
        "vbm": converters.to_float(
            r"\"GW Band gap\" of total set of bands:[\s\S]*?"
            r"  \| Highest occupied state : *([-.\d]*) eV"
        ),
        "cbm": converters.to_float(
            r"\"GW Band gap\" of total set of bands:[\s\S]*?"
            r"  \| Lowest unoccupied state: *([-.\d]*) eV"
        ),
        "gap": converters.to_float(
            r"\"GW Band gap\" of total set of bands:[\s\S]*?"
            r"  \| Energy difference      : *([-.\d]*) eV"
        ),
        "se_on_k_grid": r" *GW quasi-particle energy levels\n"
        r"(?:[^\n]*\n){5}([\s\S]*)\n\n"
        r"  Valence band maximum",
        "se_states": converters.to_vector(
            r"states to compute self-energy: *([\d]*) *([\d]*)", dtype=int
        ),
    }
    next_chunks = ["final_values"]
    parsed_key = "gw"

    def parse(self) -> dict:
        """Additionally, parse the table of the self-energy
        on the regular k-point grid.
        """
        parse_results = super().parse()
        # parse the table the usual way
        try:
            se_str = parse_results.pop("se_on_k_grid")
            states = parse_results.pop("se_states")
        except KeyError:
            return parse_results
        se_lines = se_str.split("\n")
        headers = se_lines[0].split()[1:]
        n_states = states[1] - states[0] + 1
        n_k_points = (len(se_lines) - 1) / (n_states + 4)
        se = {
            "states": list(range(states[0], states[1] + 1)),
        }
        result = []
        for i_k in range(int(n_k_points)):
            result.append([])
            for i_line in range(i_k * (n_states + 4) + 4, (i_k + 1) * (n_states + 4)):
                result[i_k].append(list(map(float, se_lines[i_line].split()[1:])))
        result = np.array(result)
        for i_head, head in enumerate(headers):
            se[head] = result[:, :, i_head].T
        parse_results["self_energy"] = se
        return parse_results


class MDValuesParser(ChunkParser):
    """Parse the MD porition of aims.out file."""

    name = "md_values"
    title_line = r"  Complete information for previous time-step:"
    values = {
        "time_step": converters.to_int(r"  \| Time step number *: *(\d+)"),
        "electronic_free_energy": converters.to_float(
            r"  \| Electronic free energy *: *([-+.E\d]*) eV"
        ),
        "temperature": converters.to_float(
            r"  \| Temperature \(nuclei\) *: *([-+.E\d]*) K"
        ),
        "kinetic_energy": converters.to_float(
            r"  \| Nuclear kinetic energy *: *([-+.E\d]*) eV"
        ),
        "total_energy": converters.to_float(
            r"  \| Total energy \(el.+nuc.\) *: *([-+.E\d]*) eV"
        ),
        "gle_H": converters.to_float(r"  \| GLE pseudo hamiltonian *: *([-+.E\d]*) eV"),
    }
    next_chunks = ["ionic_step_geometry"]
    parsed_key = "ionic_steps.md"


class IonicStepGeometry(ChunkParser):
    """Parse the geometry of ionic step in an aims.out file."""

    name = "ionic_step_geometry"
    title_line = (
        r"Atomic structure \(and velocities\) as used in the preceding time step:|"
        r"Final atomic structure \(and velocities\) as used in the preceding time step:|"  # noqa: E501
        r"Atomic structure that was used in the preceding time step of the wrapper:|"
        r"Updated atomic structure:"
    )
    values = {
        "geometry": converters.to_atoms(
            r"Atomic structure \(and velocities\) as used in the preceding time step:|"
            r"Final atomic structure \(and velocities\) as used in the preceding time step:|"  # noqa: E501
            r"Atomic structure that was used in the preceding time step of the wrapper|"
            r"Updated atomic structure:"
        )
    }
    next_chunks = ["scf_init", "mulliken", "final_values"]
    parsed_key = "ionic_steps"


class BSSEIonicStepGeometry(IonicStepGeometry):
    """Parse the geometry of BSSE step in an aims.out file."""

    name = "bsse_ionic_step_geometry"
    title_line = r"Geometry for the next BSSE step"
    values = {"geometry": converters.bsse_to_atoms()}


class FinalGeometry(ChunkParser):
    """Parse the final geometry in a aims.out file."""

    name = "final_geometry"
    title_line = r"Present geometry is converged|Aborting optimization"
    values = {
        "geometry_converged": converters.to_bool(r"Present geometry is converged"),
        "geometry": converters.to_atoms(r"  Final atomic structure:"),
    }
    next_chunks = ["mulliken", "output_polarization", "dfpt_dielectric", "final_values"]
    parsed_key = "final"


class FinalValuesParser(ChunkParser):
    """Parse the final physical values in an aims.out file."""

    name = "final_values"
    title_line = r"Final output of selected total energy values"
    values = {
        "energy": converters.to_float(
            r"  \| Total energy of the DFT / Hartree-Fock s.c.f. "
            r"calculation *: *([-.\d]*)"
        ),
    }
    parsed_key = "final"
    next_chunks = ["final"]


class FinalParser(ChunkParser):
    """Parse the final metadata values in an aims.out file."""

    name = "final"
    title_line = r"Leaving FHI-aims"
    values = {
        "end_date": converters.to_date(r"Date *:  (\d*)"),
        "end_time": converters.to_time(r"Time *:  ([\d.]*)"),
        "num_scf_steps": converters.to_int(
            r"Number of self-consistency cycles *: *(\d+)"
        ),
        "num_ionic_steps": converters.to_int(
            r"Number of SCF \(re\)initializations *: *(\d+)"
        ),
        "num_relax_steps": converters.to_int(r"Number of relaxation steps *: *(\d+)"),
        "num_md_steps": converters.to_int(
            r"Number of molecular dynamics steps *: *(\d+)"
        ),
        "num_force_evals": converters.to_int(r"Number of force evaluations *: *(\d+)"),
    }
    next_chunks = ["final_times"]
    parsed_key = ""


class FinalTimesParser(ChunkParser):
    """Parse the final timing values in an aims.out file."""

    name = "final_times"
    title_line = r"Detailed time accounting"
    values = {
        "total": converters.to_vector(r"Total time *: *([\d.]+) s *([\d.]+) s"),
        "preparation": converters.to_vector(
            r"Preparation time *: *([\d.]+) s *([\d.]+) s"
        ),
        "bc_init": converters.to_vector(
            r"Boundary condition initalization *: *([\d.]+) s *([\d.]+) s"
        ),
        "grid_part": converters.to_vector(
            r"Grid partitioning *: *([\d.]+) s *([\d.]+) s"
        ),
        "preloading_free_atom": converters.to_vector(
            r"Preloading free-atom quantities on grid *: *([\d.]+) s *([\d.]+) s"
        ),
        "free_atom_sp_e": converters.to_vector(
            r"Free-atom superposition energy *: *([\d.]+) s *([\d.]+) s"
        ),
        "integration": converters.to_vector(
            r"Total time for integrations *: *([\d.]+) s *([\d.]+) s"
        ),
        "ks_equations": converters.to_vector(
            r"Total time for solution of K.-S. equations *: *([\d.]+) s *([\d.]+) s"
        ),
        "ev_reortho": converters.to_vector(
            r"Total time for EV reorthonormalization *: *([\d.]+) s *([\d.]+) s"
        ),
        "density_force": converters.to_vector(
            r"Total time for density & force components *: *([\d.]+) s *([\d.]+) s"
        ),
        "mixing": converters.to_vector(
            r"Total time for mixing *: *([\d.]+) s *([\d.]+) s"
        ),
        "hartree_update": converters.to_vector(
            r"Total time for Hartree multipole update *: *([\d.]+) s *([\d.]+) s"
        ),
        "hartree_sum": converters.to_vector(
            r"Total time for Hartree multipole sum *: *([\d.]+) s *([\d.]+) s"
        ),
        "total_energy_eval": converters.to_vector(
            r"Total time for total energy evaluation *: *([\d.]+) s *([\d.]+) s"
        ),
        "nsc_force": converters.to_vector(
            r"Total time NSC force correction *: *([\d.]+) s *([\d.]+) s"
        ),
        "scaled_zora": converters.to_vector(
            r"Total time for scaled ZORA corrections *: *([\d.]+) s *([\d.]+) s"
        ),
        "pert_soc": converters.to_vector(
            r"Total time for perturbative SOC *: *([\d.]+) s *([\d.]+) s"
        ),
        "wannier_evol": converters.to_vector(
            r"Total time for Wannier Center Evolution *: *([\d.]+) s *([\d.]+) s"
        ),
    }
    next_chunks = ["have_a_nice_day"]
    parsed_key = "time"


class HaveANiceDayParser(ChunkParser):
    """Parse if the aims.out file exited properly."""

    name = "have_a_nice_day"
    title_line = r"Have a nice day"
    values = {"is_finished_ok": converters.to_bool(r"(Have a nice day.)")}
    parsed_key = ""
