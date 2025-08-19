#!/usr/bin/env python3
"""
LAMMPS Input File Generator
A versatile class-based system for creating LAMMPS input files for different MLIP frameworks.
"""

import os
import sys
import argparse
import datetime
import numpy as np
import subprocess
from typing import Dict, Any, Optional, Union
from ase.io import read, write

# Import utilities from the existing workflow
from ..utils import (
    print_logo, string_to_dict, cite_amaceing_toolkit,
    ask_for_float_int, ask_for_int, ask_for_yes_no, ask_for_yes_no_pbc,
    ask_for_non_cubic_pbc
)
from amaceing_toolkit.runs.run_logger import run_logger1
from amaceing_toolkit.default_configs import configs_mace, lammps_runscript


class LAMMPSInputGeneratorWrapper:
    """
    Wrapper class for generating LAMMPS input files for different run types and MLIP frameworks.
    """
    
    SUPPORTED_RUN_TYPES = ['GEO_OPT', 'CELL_OPT', 'MD', 'RECALC']
    SUPPORTED_FRAMEWORKS = ['mace', 'sevennet']
    
    def __init__(self, run_type: str, framework: str, config: Dict[str, Any]):
        if run_type not in self.SUPPORTED_RUN_TYPES:
            raise ValueError(f"Unsupported run type: {run_type}. Supported: {self.SUPPORTED_RUN_TYPES}")
        
        if framework not in self.SUPPORTED_FRAMEWORKS:
            raise ValueError(f"Unsupported framework: {framework}. Supported: {self.SUPPORTED_FRAMEWORKS}")
        
        self.run_type = run_type
        self.framework = framework
        self.config = config

        # If Q&A session: config is only containing the keys (no values) -> start interactive mode
        if not config:
            print_logo()
            print(f"Interactive mode for {run_type} input generation with {framework}.")
            print("Please provide the required parameters interactively.")
            return

        # Build the Input file from the config
        self.input_generator = LAMMPSInputGenerator(framework, config)
        
        if run_type == 'GEO_OPT':
            self.build_input_file = self.input_generator.generate_geoopt_input
        elif run_type == 'CELL_OPT':
            self.build_input_file = self.input_generator.generate_cellopt_input
        elif run_type == 'MD':
            self.build_input_file = self.input_generator.generate_md_input
        elif run_type == 'RECALC':
            self.build_input_file = self.input_generator.generate_recalc_input

        # Generate and save the input
        self.run_and_save()

    def run_and_save(self) -> str:
        """Generate and save the LAMMPS input file."""
        # Validate the configuration
        self._validate_config()

        # Generate the input file content
        input_content = self.build_input_file()
        
        # Write to file
        filenames = {
            'GEO_OPT': f'lammps_geoopt_{self.framework}.inp',
            'CELL_OPT': f'lammps_cellopt_{self.framework}.inp',
            'MD': f'lammps_md_{self.framework}.inp',
            'RECALC': f'lammps_recalc_{self.framework}.inp'
        }

        filename = filenames.get(self.run_type)

        with open(filename, 'w') as f:
            f.write(input_content)
        
        print(f"LAMMPS input file written to: {filename}")
        
        # Write runscript
        self._write_runscript(filename)
        
        return filename

    def _validate_config(self):
        """Validate that all required configuration parameters are present."""
        
        required_params = {
            'GEO_OPT': ['project_name', 'coord_file', 'pbc_list', 'max_iter', 'foundation_model'],
            'CELL_OPT': ['project_name', 'coord_file', 'pbc_list', 'max_iter', 'foundation_model'],
            'MD': ['project_name', 'coord_file', 'pbc_list', 'foundation_model', 'temperature', 'thermostat', 'nsteps', 'timestep', 'write_interval', 'log_interval', 'print_ext_traj'],
            'RECALC': ['project_name', 'coord_file', 'pbc_list', 'foundation_model']
        }
        
        explain_params = {
            'project_name': 'Name of the project',
            'coord_file': 'Path to the coordinate file (coord.xyz)',
            'pbc_list': 'Periodic boundary conditions as a 9x1 matrix or path to pbc file',
            'foundation_model': 'Name of foundation model or path to a fine-tuned foundation model file',
            'max_iter': 'Maximum number of optimization iterations',
            'temperature': 'Temperature for MD simulation in Kelvin',
            'nsteps': 'Number of MD steps to run',
            'timestep': 'Timestep for MD simulation in femtoseconds',
            'write_interval': 'Interval for writing output files during MD',
            'log_interval': 'Interval for logging during MD',
            'print_ext_traj': 'Whether to print extended trajectory information during MD',
            'pressure': 'Pressure for NPT MD simulation in bar (only needed for NPT)',
            'thermostat': 'Thermostat type for MD simulation',
        }
        
        # Load the required parameters based on run type
        if self.run_type in required_params:
            for param in required_params[self.run_type]:
                if param not in self.config:
                    raise ValueError(f"Missing required parameter: {param} ({explain_params.get(param, 'No explanation available')})")
        
        # Validate coordinate file exists
        if not os.path.isfile(self.config['coord_file']):
            raise FileNotFoundError(f"Coordinate file not found: {self.config['coord_file']}")
        
        # Ensure pbc_list is a numpy array
        if not isinstance(self.config['pbc_list'], np.ndarray):
            self.config['pbc_list'] = np.array(self.config['pbc_list']).reshape(3, 3)

    def _write_runscript(self, input_filename: str):
        """Write LAMMPS runscript."""
        if self.framework == 'mace':
            cpu_template, gpu_template = lammps_runscript()
        elif self.framework == 'sevennet':
            gpu_template = lammps_runscript(sevennet=True)
            cpu_template = None
        
        # Replace placeholders
        if cpu_template:
            cpu_script = cpu_template.replace("$$PROJECT_NAME$$", self.config['project_name'])
            cpu_script = cpu_script.replace("$$INPUT_FILE$$", input_filename)
            
            with open("runscript.sh", 'w') as f:
                f.write(cpu_script)
            os.chmod("runscript.sh", 0o755)
        
        if gpu_template:
            gpu_script = gpu_template.replace("$$PROJECT_NAME$$", self.config['project_name'])
            gpu_script = gpu_script.replace("$$INPUT_FILE$$", input_filename)
            
            with open("gpu_script.job", 'w') as f:
                f.write(gpu_script)
            os.chmod("gpu_script.job", 0o755)
        
        print("Runscripts created successfully!")


class LAMMPSInputGenerator:
    """
    Main class for generating LAMMPS input files for different MLIP frameworks.
    """
    
    def __init__(self, framework: str, config: Dict[str, Any]):
        self.framework = framework
        self.config = config
        self.mlip_handler = MLIPFrameworkHandler(framework, config)
        
    def _get_element_list(self, list_only: bool = False) -> Union[str, list]:
        """Extract element list from coordinate file."""
        elements_ordered = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
                           "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
                           "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe",
                           "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se",
                           "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo",
                           "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
                           "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce",
                           "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
                           "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W",
                           "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb",
                           "Bi", "Po", "At", "Rn"]

        atoms = read(self.config['coord_file'], format='xyz')
        elements = atoms.get_chemical_symbols()
        unique_elements = [el for el in elements_ordered if el in elements]
        
        if list_only:
            return unique_elements
        else:
            return ' '.join(unique_elements)

    def _prepare_coordinate_file(self) -> str:
        """Prepare coordinate file for LAMMPS."""
        if self.config['coord_file'].endswith('.xyz'):
            # Convert XYZ to LAMMPS data format
            atoms = read(self.config['coord_file'], format='xyz', index=0)
            atoms.set_cell(self.config['pbc_list'])
            atoms.set_pbc([True, True, True])
            
            data_file = self.config['coord_file'].replace('.xyz', '.data')
            write(data_file, atoms, units="metal", masses=True, 
                  specorder=self._get_element_list(list_only=True), 
                  format="lammps-data", atom_style="atomic")
            return data_file
        else:
            return self.config['coord_file']

    def _get_header(self) -> str:
        """Generate LAMMPS header."""
        return f"""# --------- Units and System Setup ---------
units         metal
atom_style    atomic
atom_modify   map yes
newton        on
boundary      p p p
variable      p equal press
variable      v equal vol 
variable      pot_e equal pe"""

    def _get_coordinates_section(self) -> str:
        """Generate coordinates reading section."""
        data_file = self._prepare_coordinate_file()
        return f"\nread_data     {data_file}\n"

    def _get_potential_section(self) -> str:
        """Generate potential section using MLIP handler."""
        return self.mlip_handler.get_potential_section(self._get_element_list())

    def _get_neighbors_section(self) -> str:
        """Generate neighbors section."""
        return """# --------- Neighbors ---------
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes"""

    def _get_footer(self) -> str:
        """Generate footer."""
        return f"""
# INPUT WRITTEN BY AMACEING_TOOLKIT on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""

    def generate_geoopt_input(self) -> str:
        """Generate geometry optimization input."""
        element_list = self._get_element_list()
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}
{self._get_neighbors_section()}

# --------- Minimization ---------
thermo        1
dump          d_go all xyz 1 geoopt_traj.xyz
dump_modify   d_go element {element_list} sort id
fix           log_energy all print {self.config.get('write_interval', 1)} """ + r'"${pot_e}"' + f""" file energies.txt screen no title ""
minimize      1.0e-5 1.0e-7 {int(self.config['max_iter'])} {10*int(self.config['max_iter'])}
undump        d_go
unfix         log_energy

write_dump all xyz {self.config['project_name']}_geoopt.xyz modify sort id element {element_list}
{self._get_footer()}"""
        
        return content

    def generate_cellopt_input(self) -> str:
        """Generate cell optimization input."""
        element_list = self._get_element_list()
        
        # Check if PBC matrix is non-orthogonal
        pbc_matrix = np.array(self.config['pbc_list']).reshape(3, 3)
        if np.any(np.abs(pbc_matrix - np.diag(np.diag(pbc_matrix))) > 1e-6):
            cellopt_fix = "cellopt all box/relax tri 0.0 vmax 0.001"
        else:
            cellopt_fix = "cellopt all box/relax iso 0.0 vmax 0.001"
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}
{self._get_neighbors_section()}

# --------- Minimization ---------
thermo        1
dump          d_co all xyz 1 cellopt_traj.xyz
dump_modify   d_co element {element_list} sort id
fix           log_energy all print {self.config.get('write_interval', 1)} """ + r'"${pot_e}"' + f""" file energies.txt screen no title ""
fix           {cellopt_fix}
minimize      1.0e-5 1.0e-7 {int(self.config['max_iter'])} {10*int(self.config['max_iter'])}
unfix         cellopt
unfix         log_energy
undump        d_co

write_dump all xyz {self.config['project_name']}_cellopt.xyz modify sort id element {element_list}

print "avecx avecy avecz" file pbc_new screen no
print "bvecx bvecy bvecz" append pbc_new screen no
print "cvecx cvecy cvecz" append pbc_new screen no
{self._get_footer()}"""
        
        return content

    def generate_md_input(self) -> str:
        """Generate molecular dynamics input."""
        element_list = self._get_element_list()
        timestep = float(self.config['timestep']) * 0.001  # Convert fs to ps
        
        # Get thermostat-specific content
        thermostat_content = self._get_thermostat_content(element_list)
        
        # Get trajectory printing if requested
        ext_traj_content = self._get_ext_traj_content(element_list)
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}

# --------- Timestep and Neighbors ---------
timestep      {timestep}     # ps
neighbor      2.0 bin
neigh_modify  every 1 delay 0 check yes

# --------- Initial Velocity ---------
velocity      all create {self.config['temperature']} 42 dist uniform rot yes mom yes

# --------- Equilibration ---------
fix           integrator all nve
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        1000
dump          d_equi all xyz 1000 equilibration.xyz
dump_modify   d_equi element {element_list} sort id
fix           equi all langevin {self.config['temperature']} {self.config['temperature']} $(100.0*dt) 42
run           10000
unfix         equi
unfix         fcom
undump        d_equi
unfix         integrator
reset_timestep 0

{thermostat_content}
{ext_traj_content}
{self._get_footer()}"""
        
        return content

    def generate_recalc_input(self) -> str:
        """Generate recalculation input."""
        element_list = self._get_element_list()
        
        # Convert trajectory to LAMMPS format
        self._convert_trajectory_to_lammps()
        
        content = f"""{self._get_header()}
{self._get_coordinates_section()}
{self._get_potential_section()}
{self._get_neighbors_section()}

# --------- Rerun ---------
thermo        1
thermo_style  custom step temp pe ke etotal press vol
dump          d_rerun all xyz 1 rerun.xyz
dump_modify   d_rerun element {element_list} sort id
dump          d_forces all custom 1 md_frc.lammpstrj type fx fy fz
dump_modify   d_forces sort id
fix           log_energy all print 1 """ + r'"${pot_e}"' + f""" file energies.txt screen no title ""

rerun         {self.config['coord_file'].replace('.xyz', '.lammpstrj')} dump x y z

undump        d_rerun
undump        d_forces
unfix         log_energy
{self._get_footer()}"""
        
        return content

    def _get_thermostat_content(self, element_list: str) -> str:
        """Generate thermostat-specific content for MD."""
        thermostat = self.config.get('thermostat', 'Langevin')
        temperature = self.config['temperature']
        nsteps = self.config['nsteps']
        write_interval = self.config['write_interval']
        log_interval = self.config['log_interval']
        
        base_content = f"""# --------- {thermostat} MD ---------
fix           pressavg all ave/time 1 1 1 v_p ave running
fix           fcom all momentum 10000 linear 1 1 1 rescale
thermo        {log_interval}
thermo_style  custom step temp pe ke etotal press vol
dump          d_prod all xyz {write_interval} md_traj.xyz
dump_modify   d_prod element {element_list} sort id
fix           log_energy all print {write_interval} """ + r'"${pot_e}"' + """ file energies.txt screen no title ""
"""
        
        if thermostat == 'Langevin':
            content = f"""{base_content}
fix           integrator all nve
fix           prod all langevin {temperature} {temperature} $(100.0*dt) 42

run           {nsteps}

unfix         prod
unfix         integrator"""
        
        elif thermostat == 'NoseHooverChainNVT':
            content = f"""{base_content}
fix           prod all nvt temp {temperature} {temperature} $(100.0*dt)

run           {nsteps}

unfix         prod"""
        
        elif thermostat == 'Bussi':
            content = f"""{base_content}
fix           integrator all nve
fix           prod all temp/csvr {temperature} {temperature} $(100.0*dt) 42

run           {nsteps}

unfix         prod
unfix         integrator"""
        
        elif thermostat == 'NPT':
            pressure = self.config.get('pressure', 1.0)
            # Check if PBC matrix is non-orthogonal
            pbc_matrix = np.array(self.config['pbc_list']).reshape(3, 3)
            if np.any(np.abs(pbc_matrix - np.diag(np.diag(pbc_matrix))) > 1e-6):
                npt_fix = f"tri {pressure} {pressure} $(1000.0*dt)"
            else:
                npt_fix = f"iso {pressure} {pressure} $(1000.0*dt)"
            
            content = f"""{base_content}
fix           integrator all npt temp {temperature} {temperature} $(100.0*dt) {npt_fix}

run           {nsteps}

unfix         integrator"""
        
        else:
            raise ValueError(f"Unsupported thermostat: {thermostat}")
        
        content += f"""
undump        d_prod
unfix         log_energy
""" + r"""
variable      apre equal f_pressavg
print         ">>> Average pressure is ${apre} bar."
unfix         fcom 
unfix         pressavg"""
        
        return content

    def _get_ext_traj_content(self, element_list: str) -> str:
        """Generate extended trajectory content if requested."""
        if self.config.get('print_ext_traj', 'n') == 'y':
            write_interval = self.config['write_interval']
            return f"""
# --------- Extended Trajectory ---------
dump          d_prod_frc all custom {write_interval} md_frc.lammpstrj type fx fy fz
dump_modify   d_prod_frc sort id"""
        return ""

    def _convert_trajectory_to_lammps(self):
        """Convert XYZ trajectory to LAMMPS format."""
        from ase.data import atomic_numbers
        
        traj_file = self.config['coord_file']
        cell = self.config['pbc_list']
        element_list = self._get_element_list(list_only=True)
        
        # Load trajectory
        frames = read(traj_file, index=":")
        
        # Set periodic cell for each frame
        for atoms in frames:
            atoms.set_cell(cell)
            atoms.set_pbc([True, True, True])
        
        # Atom element to type mapping
        element_to_type = {el: i + 1 for i, el in enumerate(element_list)}
        
        # Write LAMMPS-style trajectory
        with open(traj_file.replace('.xyz', '.lammpstrj'), "w") as f:
            for i, atoms in enumerate(frames):
                positions = atoms.get_positions()
                symbols = atoms.get_chemical_symbols()
                cell_params = atoms.get_cell()
                
                f.write(f"ITEM: TIMESTEP\n{i}\n")
                f.write(f"ITEM: NUMBER OF ATOMS\n{len(atoms)}\n")
                f.write("ITEM: BOX BOUNDS pp pp pp\n")
                f.write(f"0.0 {cell_params[0][0]}\n")
                f.write(f"0.0 {cell_params[1][1]}\n")
                f.write(f"0.0 {cell_params[2][2]}\n")
                f.write("ITEM: ATOMS id type x y z\n")
                
                for j, (symbol, pos) in enumerate(zip(symbols, positions)):
                    atom_type = element_to_type[symbol]
                    f.write(f"{j+1} {atom_type} {pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")


class MLIPFrameworkHandler:
    """
    Handler for different MLIP frameworks - makes it easy to add new frameworks.
    """
    
    def __init__(self, framework: str, config: Dict[str, Any]):
        self.framework = framework
        self.config = config
        
    def get_potential_section(self, element_list: str) -> str:
        """Get potential section based on framework."""
        if self.framework == 'mace':
            return self._get_mace_potential_section(element_list)
        elif self.framework == 'sevennet':
            return self._get_sevennet_potential_section(element_list)
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
    
    def _get_mace_potential_section(self, element_list: str) -> str:
        """Generate MACE potential section."""
        model_file = self._prepare_mace_model()
        
        return f"""# --------- MACE Potential Setup ---------
pair_style    mace no_domain_decomposition
pair_coeff    * * {model_file} {element_list}
"""
    
    def _get_sevennet_potential_section(self, element_list: str) -> str:
        """Generate SevenNet potential section."""
        model_file = self._prepare_sevennet_model()
        
        dispersion = self.config.get('dispersion_via_simenv', 'n')
        
        if dispersion == 'n':
            return f"""# --------- SevenNet Potential Setup ---------
pair_style    e3gnn
pair_coeff    * * {model_file} {element_list}
"""
        else:
            functional = self.config.get('functional', 'PBE')
            if functional == 'BLPY':
                functional = 'b-lyp'  # Correct LAMMPS name
            
            return f"""# --------- SevenNet Potential Setup (with dispersion) ---------
pair_style    hybrid/overlay e3gnn d3 9000 1600 damp_bj {functional}
pair_coeff    * * e3gnn {model_file} {element_list}
pair_coeff    * * d3 {element_list}
"""
    
    def _prepare_mace_model(self) -> str:
        """Prepare MACE model file for LAMMPS."""
        foundation_model = self.config['foundation_model']
        
        if foundation_model.endswith('.pt'):
            return foundation_model
        
        # Handle model conversion
        try:
            import mace
            converter_script_path = mace.__file__.replace('__init__.py', 'cli/create_lammps_model.py')
        except ImportError:
            raise ImportError("MACE package not found. Please install mace-torch.")
        
        if foundation_model.endswith('.model'):
            # Convert custom model
            convert_command = f"python {converter_script_path} {foundation_model}"
            print(f"Converting model {foundation_model} to LAMMPS format...")
            
            try:
                subprocess.run(convert_command, shell=True, check=True, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Model conversion failed with exit code {e.returncode}")
            
            return f"{foundation_model}-lammps.pt"
        
        else:
            # Handle foundation models
            download_model_dict = {
                'mp_small': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2023-12-10-mace-128-L0_energy_epoch-249.model',
                'mp_medium': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2023-12-03-mace-128-L1_epoch-199.model',
                'mp_large': 'https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/2024-01-07-mace-128-L2_epoch-199.model',
                'off_small': 'https://github.com/ACEsuit/mace-off/releases/download/mace_off_0/MACE-OFF23_small.model',
                'off_medium': 'https://github.com/ACEsuit/mace-off/releases/download/mace_off_0/MACE-OFF23_medium.model',
                'off_large': 'https://github.com/ACEsuit/mace-off/releases/download/mace_off_0/MACE-OFF23_large.model'
            }
            
            # Build model key
            model_size = self.config.get('model_size', 'medium')
            model_key = f"{foundation_model.split('_')[-1]}_{model_size}"
            
            if model_key not in download_model_dict:
                raise ValueError(f"Unknown model combination: {model_key}")
            
            model_url = download_model_dict[model_key]
            model_file = f"{model_key}.model"
            
            # Download model if not exists
            if not os.path.exists(model_file):
                print(f"Downloading model {model_key} from {model_url}...")
                subprocess.run(f"wget -O {model_file} {model_url}", shell=True, check=True)
            
            # Convert to LAMMPS format
            convert_command = f"python {converter_script_path} {model_file}"
            print(f"Converting model {model_file} to LAMMPS format...")
            subprocess.run(convert_command, shell=True, check=True)
            
            return f"{model_file}-lammps.pt"
    
    def _prepare_sevennet_model(self) -> str:
        """Prepare SevenNet model file for LAMMPS."""
        foundation_model = self.config['foundation_model']
        
        if foundation_model.endswith('.pt'):
            print(f"Model {foundation_model} is already in LAMMPS format.")
            return foundation_model
        
        # Convert model to LAMMPS format
        if "." not in foundation_model:
            # Foundation model name
            modal = self.config.get('modal', '')
            if modal:
                convert_command = f"sevennnet_get_model {foundation_model} --modal {modal}"
            else:
                convert_command = f"sevennnet_get_model {foundation_model}"
            
            model_file = f"{foundation_model}.pt"
            
        elif foundation_model.endswith('.pth'):
            # Convert .pth to .pt
            modal = self.config.get('modal', '')
            if modal:
                convert_command = f"sevennnet_get_model {foundation_model} --modal {modal}"
            else:
                convert_command = f"sevennnet_get_model {foundation_model}"
            
            model_file = foundation_model.replace('.pth', '.pt')
        else:
            raise ValueError("SevenNet model file must be .pt, .pth, or a foundation model name")
        
        print(f"Converting SevenNet model {foundation_model} to LAMMPS format...")
        
        try:
            subprocess.run(convert_command, shell=True, check=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SevenNet model conversion failed with exit code {e.returncode}")
        
        return model_file


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate LAMMPS input files for MLIP calculations",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-rt", "--run_type",
        choices=['GEO_OPT', 'CELL_OPT', 'MD', 'RECALC'],
        help="Type of calculation to run"
    )
    
    parser.add_argument(
        "-f", "--framework",
        choices=['mace', 'sevennet'],
        help="MLIP framework to use"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Configuration dictionary as string or path to config file"
    )
    
    args = parser.parse_args()
    
    if args.run_type and args.framework and args.config:
        # Command-line mode
        try:
            if os.path.isfile(args.config):
                # Load from file
                with open(args.config, 'r') as f:
                    config_str = f.read()
                config = eval(config_str)
            else:
                # Parse as string
                config = string_to_dict(args.config)
            
            # Ensure PBC is numpy array
            if 'pbc_list' in config:
                if not isinstance(config['pbc_list'], np.ndarray):
                    pbc_data = config['pbc_list']
                    if len(pbc_data) == 3:  # Cubic case
                        config['pbc_list'] = np.array([[pbc_data[0], 0, 0], [0, pbc_data[1], 0], [0, 0, pbc_data[2]]])
                    else:
                        config['pbc_list'] = np.array(pbc_data).reshape(3, 3)
            
            generator = LAMMPSInputGeneratorWrapper(args.run_type, args.framework, config)
            
            # Log the run
            run_logger1(args.run_type, os.getcwd())
            
            print(f"✓ LAMMPS input file created successfully")
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        # Interactive mode would go here
        print("Interactive mode not yet implemented. Please use command-line mode.")
        print("Example: python input_lammps.py -rt MD -f mace -c \"{'project_name': 'test', ...}\"")


if __name__ == "__main__":
    main()