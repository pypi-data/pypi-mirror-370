#!/usr/bin/env amspython
from ase.optimize import BFGS
from scm.plams import *
from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator


def get_atoms():
    # water in a box
    mol = from_smiles("O")  # PLAMS Molecule
    mol.lattice = [
        [
            3.0,
            0.0,
            0.0,
        ],
        [0.0, 3.0, 0.0],
        [0.0, 0.0, 3.0],
    ]
    return toASE(mol)  # convert PLAMS Molecule to ASE Atoms


def get_settings():
    # PLAMS Settings configuring the calculation
    s = Settings()
    s.input.ams.Task = "SinglePoint"
    s.input.ams.Properties.Gradients = "Yes"
    s.input.ams.Properties.StressTensor = "Yes"

    # Engine definition
    s.input.ForceField.Type = "UFF"

    # run in serial
    s.runscript.nproc = 1
    return s


def singlepoint():
    settings = get_settings()
    atoms = get_atoms()
    atoms.calc = AMSCalculator(settings=settings, name="SinglePoint")
    print("Singlepoint through the ASE calculator")
    print(f"Energy (eV): {atoms.get_potential_energy()}")
    print("Forces (eV/ang):")
    print(atoms.get_forces())
    print("Stress (eV/ang^3):")
    print(atoms.get_stress())


def ams_geoopt():
    print("AMS geo opt run with the ASE calculator")
    settings = Settings()
    settings.input.ams.Task = "GeometryOptimization"
    settings.input.ams.GeometryOptimization.Convergence.Gradients = 0.01  # hartree/ang
    settings.input.ForceField.Type = "UFF"
    settings.runscript.nproc = 1
    atoms = get_atoms()
    atoms.calc = AMSCalculator(settings=settings, name="AMS_GeoOpt")
    print(f"Optimized energy (eV): {atoms.get_potential_energy()}")


def ase_geoopt():
    print("ASE geo opt (ase.optimize.BGFGS) in normal mode: One results dir is saved for every step")
    settings = get_settings()
    atoms = get_atoms()
    atoms.calc = AMSCalculator(settings=settings, name="ASE_GeoOpt")
    dyn = BFGS(atoms)
    dyn.run(fmax=0.27)
    print(f"Optimized energy (eV): {atoms.get_potential_energy()}")


def ase_geoopt_workermode():
    print("ASE geo opt (ase.optimize.FGS) in AMSWorker mode: no output files are saved, minimal overhead")
    settings = get_settings()
    atoms = get_atoms()
    with AMSCalculator(settings=settings, name="ASE_WorkerGeoOpt", amsworker=True) as calc:
        atoms.calc = calc
        dyn = BFGS(atoms)
        dyn.run(fmax=0.27)
        print(f"Optimized energy (eV): {atoms.get_potential_energy()}")


def charged_system():
    print("Define the charge of a system through the ASE atoms object")
    settings = get_settings()
    atoms = get_atoms()
    atoms.set_initial_charges([-0.3, 0.2, 0.2])
    atoms.info["charge"] = 3
    calc = AMSCalculator(settings, name="charge")
    atoms.calc = calc
    atoms.get_potential_energy()
    print(f'Charge is "{atoms.calc.amsresults.get_input_molecule().properties.charge}" for the first system.')
    atoms = atoms * (1, 1, 2)
    atoms.calc = calc
    atoms.get_potential_energy()
    print(f'Charge is "{atoms.calc.amsresults.get_input_molecule().properties.charge}" for the second system.')


def main():
    singlepoint()
    ams_geoopt()
    ase_geoopt()
    ase_geoopt_workermode()
    charged_system()


if __name__ == "__main__":
    main()
