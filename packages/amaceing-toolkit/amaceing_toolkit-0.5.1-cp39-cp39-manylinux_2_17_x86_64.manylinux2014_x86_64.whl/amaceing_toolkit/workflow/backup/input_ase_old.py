#!/usr/bin/env python3
"""
ASE Input File Generator
A versatile class-based system for creating GEOOPT, CELLOPT, MD and RECALC input files for ASE.
"""

import os
import sys
import argparse
import datetime
import numpy as np
from typing import Dict, Any, Optional, Union

# Import utilities from the existing workflow
from ..utils import (
    print_logo, string_to_dict, cite_amaceing_toolkit,
    ask_for_float_int, ask_for_int, ask_for_yes_no, ask_for_yes_no_pbc,
    ask_for_non_cubic_pbc
)
from amaceing_toolkit.runs.run_logger import run_logger1
from amaceing_toolkit.default_configs import configs_mace


class ASECalculatorConfig:
    """Configuration class for ASE calculators."""
    
    def __init__(self, foundation_model: str, model_size: str = "", dispersion_via_ase: str = "n"):
        self.foundation_model = foundation_model
        self.model_size = model_size
        self.dispersion_via_ase = dispersion_via_ase
    
    def get_import_code(self) -> str:
        """Return the import code for the foundation model."""
        if self.foundation_model == 'mace_off':
            return "from mace.calculators import mace_off"
        elif self.foundation_model == 'mace_anicc':
            return "from mace.calculators import mace_anicc"
        elif self.foundation_model == 'mace_mp':
            return "from mace.calculators import mace_mp"
        else:
            return "from mace.calculators import MACECalculator"
    
    def get_calculator_code(self) -> str:
        """Return the calculator instantiation code."""
        dispersion = ", dispersion=True" if self.dispersion_via_ase == 'y' else ", dispersion=False"
        cuequiv = self._get_cuequivariance_setting()
        
        if self.foundation_model == 'mace_off':
            model_param = f"model='{self.model_size}'" if self.model_size else "model='medium'"
            return f"mace_off({model_param}{dispersion}{cuequiv})"
        elif self.foundation_model == 'mace_anicc':
            return f"mace_anicc({dispersion}{cuequiv})"
        elif self.foundation_model == 'mace_mp':
            model_param = f"model='{self.model_size}'" if self.model_size else "model='medium'"
            return f"mace_mp({model_param}{dispersion}{cuequiv})"
        else:
            # Custom model path
            if os.path.isfile(self.foundation_model) and self.foundation_model.endswith('.model'):
                return f"MACECalculator(model_paths='{self.foundation_model}'{dispersion})"
            else:
                raise ValueError(f"Invalid foundation model: {self.foundation_model}")
    
    def _get_cuequivariance_setting(self) -> str:
        """Check if cuequivariance is available and return setting."""
        try:
            import cuequivariance
            return ", enable_cueq=True"
        except ImportError:
            return ", enable_cueq=False"


class ASEInputGenerator:
    """Main class for generating ASE input files for different run types."""
    
    SUPPORTED_RUN_TYPES = ['GEO_OPT', 'CELL_OPT', 'MD', 'RECALC']
    
    def __init__(self, run_type: str, config: Dict[str, Any]):
        if run_type not in self.SUPPORTED_RUN_TYPES:
            raise ValueError(f"Unsupported run type: {run_type}. Supported: {self.SUPPORTED_RUN_TYPES}")
        
        self.run_type = run_type
        self.config = config
        self.calc_config = ASECalculatorConfig(
            config['foundation_model'],
            config.get('model_size', ''),
            config.get('dispersion_via_ase', 'n')
        )
        
        # Validate required parameters
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration parameters are present."""
        required_params = ['project_name', 'coord_file', 'pbc_list', 'foundation_model']
        
        # Add run-type specific required parameters
        if self.run_type in ['GEO_OPT', 'CELL_OPT']:
            required_params.append('max_iter')
        elif self.run_type == 'MD':
            required_params.extend(['temperature', 'nsteps', 'timestep', 'write_interval'])
        
        for param in required_params:
            if param not in self.config:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Validate coordinate file exists
        if not os.path.isfile(self.config['coord_file']):
            raise FileNotFoundError(f"Coordinate file not found: {self.config['coord_file']}")
        
        # Ensure pbc_list is a numpy array
        if not isinstance(self.config['pbc_list'], np.ndarray):
            self.config['pbc_list'] = np.array(self.config['pbc_list']).reshape(3, 3)
    
    def _get_cell_matrix_code(self) -> str:
        """Generate the cell matrix code."""
        pbc = self.config['pbc_list']
        return f"np.array([[{pbc[0,0]:.6f}, {pbc[0,1]:.6f}, {pbc[0,2]:.6f}], " \
               f"[{pbc[1,0]:.6f}, {pbc[1,1]:.6f}, {pbc[1,2]:.6f}], " \
               f"[{pbc[2,0]:.6f}, {pbc[2,1]:.6f}, {pbc[2,2]:.6f}]])"
    
    def generate_geoopt_input(self) -> str:
        """Generate geometry optimization input."""
        return f"""# Geometry Optimization with ASE and MACE
# Generated by aMACEing Toolkit on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{self.calc_config.get_import_code()}
import numpy as np
from ase.io import read, write
from ase.optimize import BFGS

# Load the foundation model
calc = {self.calc_config.get_calculator_code()}
print("Loading of MACE model completed: {self.config['foundation_model']}")

# Load the coordinates
atoms = read('{self.config['coord_file']}')

# Set the periodic boundary conditions
atoms.pbc = (True, True, True)
atoms.set_cell({self._get_cell_matrix_code()})

# Attach calculator
atoms.calc = calc

# Set up the optimizer
optimizer = BFGS(atoms, trajectory='{self.config['project_name']}_geoopt.traj', 
                logfile='{self.config['project_name']}_geoopt.log')

# Define callback to save intermediate structures
def save_positions(atoms):
    write('{self.config['project_name']}_geoopt_progress.xyz', atoms, append=True)

optimizer.attach(save_positions, interval=10)

# Run the optimization
print("Starting geometry optimization...")
optimizer.run(fmax=0.01, steps={self.config['max_iter']})

# Write final structure
write('{self.config['project_name']}_geoopt_final.xyz', atoms)

print("Geometry optimization completed!")
print(f"Final energy: {{atoms.get_potential_energy():.6f}} eV")
print(f"Final positions saved to: {self.config['project_name']}_geoopt_final.xyz")
"""
    
    def generate_cellopt_input(self) -> str:
        """Generate cell optimization input."""
        return f"""# Cell Optimization with ASE and MACE
# Generated by aMACEing Toolkit on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{self.calc_config.get_import_code()}
import numpy as np
from ase.io import read, write
from ase.optimize import LBFGS
from ase.constraints import ExpCellFilter

# Load the foundation model
calc = {self.calc_config.get_calculator_code()}
print("Loading of MACE model completed: {self.config['foundation_model']}")

# Load the coordinates
atoms = read('{self.config['coord_file']}')

# Set the periodic boundary conditions
atoms.pbc = (True, True, True)
atoms.set_cell({self._get_cell_matrix_code()})

# Attach calculator
atoms.calc = calc

print("Initial cell:")
print(atoms.cell)

# Apply cell filter for cell optimization
cell_filter = ExpCellFilter(atoms, hydrostatic_strain=True)

# Set up the optimizer
optimizer = LBFGS(cell_filter, trajectory='{self.config['project_name']}_cellopt.traj',
                 logfile='{self.config['project_name']}_cellopt.log')

# Define callback functions
def print_cell_info():
    step = optimizer.get_number_of_steps()
    print(f"Step {{step:3d}}: Cell = {{atoms.cell.diagonal()}}")

def save_positions():
    write('{self.config['project_name']}_cellopt_progress.xyz', atoms, append=True)

optimizer.attach(print_cell_info, interval=1)
optimizer.attach(save_positions, interval=10)

# Run the optimization
print("Starting cell optimization...")
optimizer.run(fmax=0.01, steps={self.config['max_iter']})

print("\\nOptimization completed!")
print("Final cell:")
print(atoms.cell)
print(f"Final energy: {{atoms.get_potential_energy():.6f}} eV")

# Write final structure
write('{self.config['project_name']}_cellopt_final.xyz', atoms)
print(f"Final structure saved to: {self.config['project_name']}_cellopt_final.xyz")
"""
    
    def generate_md_input(self) -> str:
        """Generate molecular dynamics input."""
        thermostat_code = self._get_thermostat_code()
        
        return f"""# Molecular Dynamics with ASE and MACE
# Generated by aMACEing Toolkit on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{self.calc_config.get_import_code()}
import numpy as np
import os
import time
from ase.io import read, write
from ase.io.trajectory import Trajectory
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units
from ase.md import MDLogger
{thermostat_code['import']}

# Load the foundation model
calc = {self.calc_config.get_calculator_code()}
print("Loading of MACE model completed: {self.config['foundation_model']}")

# Load coordinates (restart capability)
restart_file = '{self.config['project_name']}_restart.traj'
if os.path.isfile(restart_file):
    print("Restarting from previous trajectory...")
    atoms = read(restart_file)
else:
    print("Starting new MD simulation...")
    atoms = read('{self.config['coord_file']}')
    
    # Set the periodic boundary conditions
    atoms.pbc = (True, True, True)
    atoms.set_cell({self._get_cell_matrix_code()})
    
    # Initialize velocities
    temperature_K = {self.config['temperature']}
    MaxwellBoltzmannDistribution(atoms, temperature_K=temperature_K)

# Attach calculator
atoms.calc = calc

# Set up dynamics
{thermostat_code['dynamics']}
dyn.fixcm = True

# Set up logging
logger = MDLogger(dyn, atoms, '{self.config['project_name']}_md.log',
                 header=True, stress=False, peratom=False,
                 mode='a')
dyn.attach(logger, interval={self.config.get('log_interval', 100)})

# Set up trajectory writing
traj = Trajectory('{self.config['project_name']}_md.traj', 'a', atoms)
dyn.attach(traj.write, interval={self.config['write_interval']})

# Set up XYZ writing
def write_xyz():
    write('{self.config['project_name']}_md.xyz', atoms, append=True)

dyn.attach(write_xyz, interval={self.config['write_interval']})

# Run MD
print(f"Starting MD simulation: {{self.config['nsteps']}} steps at {{self.config['temperature']}} K")
start_time = time.time()

try:
    dyn.run({self.config['nsteps']})
except KeyboardInterrupt:
    print("\\nMD simulation interrupted by user")

end_time = time.time()
runtime = end_time - start_time

print(f"\\nMD simulation completed!")
print(f"Runtime: {{runtime:.2f}} seconds")
print(f"Final temperature: {{atoms.get_temperature():.2f}} K")

# Save runtime and final state
np.savetxt('{self.config['project_name']}_runtime.txt', [runtime])
write(restart_file, atoms)

print(f"Final state saved to: {{restart_file}}")
print(f"Trajectory saved to: {self.config['project_name']}_md.traj")
"""
    
    def generate_recalc_input(self) -> str:
        """Generate recalculation input."""
        return f"""# Trajectory Recalculation with ASE and MACE
# Generated by aMACEing Toolkit on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{self.calc_config.get_import_code()}
import numpy as np
from ase.io import read, write

# Load the foundation model
calc = {self.calc_config.get_calculator_code()}
print("Loading of MACE model completed: {self.config['foundation_model']}")

# Load the reference trajectory
print("Loading trajectory...")
trajectory = read('{self.config['coord_file']}', index=':')
print(f"Loaded {{len(trajectory)}} frames")

# Initialize storage for results
all_forces = []
all_energies = []

print("Starting recalculation...")
for i, atoms in enumerate(trajectory):
    if i % 25 == 0:
        print(f"Processing frame {{i}}/{{len(trajectory)}}")
    
    # Set periodic boundary conditions
    atoms.pbc = (True, True, True)
    atoms.set_cell({self._get_cell_matrix_code()})
    
    # Attach calculator and compute properties
    atoms.calc = calc
    
    try:
        energy = atoms.get_potential_energy()
        forces = atoms.get_forces()
        
        all_energies.append(energy)
        all_forces.append(forces)
        
    except Exception as e:
        print(f"Error calculating frame {{i}}: {{e}}")
        continue

# Convert to numpy arrays
all_forces = np.array(all_forces)
all_energies = np.array(all_energies)

# Save results
energy_file = f'energies_recalc_{self.config['project_name']}.txt'
forces_file = f'forces_recalc_{self.config['project_name']}.xyz'

np.savetxt(energy_file, all_energies)
print(f"Energies saved to: {{energy_file}}")

# Save forces in XYZ format
symbols = trajectory[0].get_chemical_symbols()
with open(forces_file, 'w') as f:
    for i, frame_forces in enumerate(all_forces):
        f.write(f"{{len(symbols)}}\\n")
        f.write(f"# Frame {{i}}, Energy: {{all_energies[i]:.6f}} eV\\n")
        for atom, force in zip(symbols, frame_forces):
            f.write(f"{{atom}} {{force[0]:12.6f}} {{force[1]:12.6f}} {{force[2]:12.6f}}\\n")

print(f"Forces saved to: {{forces_file}}")
print("Recalculation completed!")
"""
    
    def _get_thermostat_code(self) -> Dict[str, str]:
        """Get thermostat-specific code."""
        thermostat = self.config.get('thermostat', 'Langevin')
        temperature = self.config['temperature']
        timestep = self.config['timestep']
        
        if thermostat == 'Langevin':
            return {
                'import': 'from ase.md.langevin import Langevin',
                'dynamics': f'dyn = Langevin(atoms, {timestep} * units.fs, temperature_K={temperature}, friction=0.002)'
            }
        elif thermostat == 'NoseHooverChainNVT':
            return {
                'import': 'from ase.md.nvtberendsen import NVTBerendsen',
                'dynamics': f'dyn = NVTBerendsen(atoms, {timestep} * units.fs, temperature_K={temperature}, taut=100*units.fs)'
            }
        elif thermostat == 'Bussi':
            return {
                'import': 'from ase.md.bussi import Bussi',
                'dynamics': f'dyn = Bussi(atoms, {timestep} * units.fs, temperature_K={temperature}, nu=0.01)'
            }
        elif thermostat == 'NPT':
            pressure = self.config.get('pressure', 1.0)
            return {
                'import': 'from ase.md.npt import NPT',
                'dynamics': f'dyn = NPT(atoms, {timestep} * units.fs, temperature_K={temperature}, externalstress={pressure}*units.bar)'
            }
        else:
            # Default to Langevin
            return {
                'import': 'from ase.md.langevin import Langevin',
                'dynamics': f'dyn = Langevin(atoms, {timestep} * units.fs, temperature_K={temperature}, friction=0.002)'
            }
    
    def generate_input(self) -> str:
        """Generate input file based on run type."""
        if self.run_type == 'GEO_OPT':
            return self.generate_geoopt_input()
        elif self.run_type == 'CELL_OPT':
            return self.generate_cellopt_input()
        elif self.run_type == 'MD':
            return self.generate_md_input()
        elif self.run_type == 'RECALC':
            return self.generate_recalc_input()
        else:
            raise ValueError(f"Unsupported run type: {self.run_type}")
    
    def write_input_file(self) -> str:
        """Write the input file to disk and return filename."""
        content = self.generate_input()
        filename = f"{self.config['project_name']}_{self.run_type.lower()}.py"
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"Input file written to: {filename}")
        return filename


class ASEInputInterface:
    """Interface class providing both Q&A and command-line functionality."""
    
    def __init__(self):
        self.mace_config = configs_mace('default')
    
    def interactive_mode(self):
        """Interactive Q&A mode for input generation."""
        print_logo()
        print("\\n=== ASE Input File Generator ===")
        print("This tool helps you create ASE input files for MACE calculations.")
        print("Please answer the following questions:")
        print()
        
        # Get coordinate file
        coord_file = input(f"Coordinate file [{self.mace_config['coord_file']}]: ").strip()
        if not coord_file:
            coord_file = self.mace_config['coord_file']
        
        if not os.path.isfile(coord_file):
            raise FileNotFoundError(f"Coordinate file not found: {coord_file}")
        
        # Get PBC information
        pbc_mat = self._get_pbc_interactive()
        
        # Get run type
        run_type = self._get_run_type_interactive()
        
        # Get project name
        project_name = input("Project name: ").strip()
        if not project_name:
            project_name = f"{run_type}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get foundation model
        foundation_model, model_size = self._get_foundation_model_interactive()
        
        # Get dispersion setting
        dispersion_via_ase = ask_for_yes_no("Include dispersion correction? (y/n)", 'n')
        
        # Build base config
        config = {
            'project_name': project_name,
            'coord_file': coord_file,
            'pbc_list': pbc_mat,
            'foundation_model': foundation_model,
            'model_size': model_size,
            'dispersion_via_ase': dispersion_via_ase
        }
        
        # Get run-type specific parameters
        if run_type in ['GEO_OPT', 'CELL_OPT']:
            config['max_iter'] = ask_for_int("Maximum iterations", self.mace_config[run_type]['max_iter'])
        
        elif run_type == 'MD':
            config.update(self._get_md_parameters_interactive())
        
        # Generate and write input
        generator = ASEInputGenerator(run_type, config)
        filename = generator.write_input_file()
        
        # Log the run
        run_logger1(run_type, os.getcwd())
        
        print(f"\\n✓ Input file created: {filename}")
        print(f"✓ Run logged successfully")
        
        cite_amaceing_toolkit()
    
    def _get_pbc_interactive(self) -> np.ndarray:
        """Get PBC information interactively."""
        box_type = ask_for_yes_no_pbc("Is the box cubic? (y/n/pbc)", self.mace_config['box_cubic'])
        
        if box_type == 'y':
            box_size = ask_for_float_int("Box size in Å", "10.0")
            return np.array([[box_size, 0.0, 0.0], [0.0, box_size, 0.0], [0.0, 0.0, box_size]])
        elif box_type == 'n':
            return ask_for_non_cubic_pbc()
        else:
            return np.loadtxt(box_type)
    
    def _get_run_type_interactive(self) -> str:
        """Get run type interactively."""
        print("\\nAvailable run types:")
        print("1. GEO_OPT - Geometry optimization")
        print("2. CELL_OPT - Cell optimization")
        print("3. MD - Molecular dynamics")
        print("4. RECALC - Trajectory recalculation")
        
        while True:
            choice = input("Select run type (1-4): ").strip()
            if choice == '1':
                return 'GEO_OPT'
            elif choice == '2':
                return 'CELL_OPT'
            elif choice == '3':
                return 'MD'
            elif choice == '4':
                return 'RECALC'
            else:
                print("Invalid choice. Please enter 1-4.")
    
    def _get_foundation_model_interactive(self) -> tuple:
        """Get foundation model and size interactively."""
        print("\\nAvailable foundation models:")
        print("1. mace_mp - Materials Project MACE")
        print("2. mace_off - OFF MACE")
        print("3. mace_anicc - ANI-CC MACE")
        print("4. custom - Custom model path")
        
        while True:
            choice = input("Select foundation model (1-4): ").strip()
            if choice == '1':
                foundation_model = 'mace_mp'
                break
            elif choice == '2':
                foundation_model = 'mace_off'
                break
            elif choice == '3':
                foundation_model = 'mace_anicc'
                return 'mace_anicc', ''
            elif choice == '4':
                foundation_model = input("Enter custom model path: ").strip()
                if not os.path.isfile(foundation_model):
                    print("Model file not found!")
                    continue
                return foundation_model, ''
            else:
                print("Invalid choice. Please enter 1-4.")
        
        if foundation_model in ['mace_mp', 'mace_off']:
            print("\\nAvailable model sizes:")
            print("1. small")
            print("2. medium")
            print("3. large")
            
            while True:
                size_choice = input("Select model size (1-3): ").strip()
                if size_choice == '1':
                    return foundation_model, 'small'
                elif size_choice == '2':
                    return foundation_model, 'medium'
                elif size_choice == '3':
                    return foundation_model, 'large'
                else:
                    print("Invalid choice. Please enter 1-3.")
        
        return foundation_model, ''
    
    def _get_md_parameters_interactive(self) -> Dict[str, Any]:
        """Get MD-specific parameters interactively."""
        config = {}
        
        config['temperature'] = ask_for_float_int("Temperature (K)", str(self.mace_config['MD']['temperature']))
        config['nsteps'] = ask_for_int("Number of MD steps", self.mace_config['MD']['nsteps'])
        config['timestep'] = ask_for_float_int("Timestep (fs)", str(self.mace_config['MD']['timestep']))
        config['write_interval'] = ask_for_int("Write interval", self.mace_config['MD']['write_interval'])
        config['log_interval'] = ask_for_int("Log interval", self.mace_config['MD'].get('log_interval', 100))
        
        # Thermostat selection
        print("\\nAvailable thermostats:")
        print("1. Langevin")
        print("2. NoseHooverChainNVT")
        print("3. Bussi")
        print("4. NPT")
        
        while True:
            thermo_choice = input("Select thermostat (1-4): ").strip()
            if thermo_choice == '1':
                config['thermostat'] = 'Langevin'
                break
            elif thermo_choice == '2':
                config['thermostat'] = 'NoseHooverChainNVT'
                break
            elif thermo_choice == '3':
                config['thermostat'] = 'Bussi'
                break
            elif thermo_choice == '4':
                config['thermostat'] = 'NPT'
                config['pressure'] = ask_for_float_int("Pressure (bar)", "1.0")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
        
        return config


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate ASE input files for MACE calculations",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-rt", "--run_type",
        choices=['GEO_OPT', 'CELL_OPT', 'MD', 'RECALC'],
        help="Type of calculation to run"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Configuration dictionary as string or path to config file"
    )
    
    args = parser.parse_args()
    
    interface = ASEInputInterface()
    
    if args.run_type and args.config:
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
            
            generator = ASEInputGenerator(args.run_type, config)
            filename = generator.write_input_file()
            
            # Log the run
            run_logger1(args.run_type, os.getcwd())
            
            print(f"✓ Input file created: {filename}")
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        # Interactive mode
        interface.interactive_mode()


if __name__ == "__main__":
    main()
