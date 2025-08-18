#!/usr/bin/env amspython
import copy
import multiprocessing

from scm.input_classes import ADF, AMS
from scm.plams import config, JobRunner, from_smiles, Settings, AMSJob

# Run jobs as many jobs as possible in parallel:
config.default_jobrunner = JobRunner(parallel=True, maxjobs=multiprocessing.cpu_count())
config.job.runscript.nproc = 1

# The molecules we want to use in our benchmark:
mol_smiles = {"Methane": "C", "Ethane": "C-C", "Ethylene": "C=C", "Acetylene": "C#C"}
molecules = {}
for name, smiles in mol_smiles.items():
    # Compute 10 conformers, optimize with UFF and pick the lowest in energy.
    molecules[name] = from_smiles(smiles, nconfs=10, forcefield="uff")[0]
    print(name, molecules[name])

# Initialize the common settings:
common_settings = Settings()
common_settings.input = AMS()
common_settings.input.Task = "SinglePoint"
common_settings.input.System.Symmetrize = "Yes"
common_settings.input.Engine = ADF()
common_settings.input.Engine.Basis.Core = "None"

basis = ["QZ4P", "TZ2P", "TZP", "DZP", "DZ", "SZ"]
reference_basis = "QZ4P"

# Set up and run the calculations:
results = {}
for bas in basis:
    for name, molecule in molecules.items():
        settings = copy.deepcopy(common_settings)
        settings.input.Engine.Basis.Type = bas
        job = AMSJob(name=name + "_" + bas, molecule=molecule, settings=settings)
        results[(name, bas)] = job.run()

# Calculate the average absolute error in bond energy per atom for each basis set:
average_errors = {}
for bas in basis:
    if bas != reference_basis:
        errors = []
        for name, molecule in molecules.items():
            reference_energy = results[(name, reference_basis)].get_energy(unit="kcal/mol")
            energy = results[(name, bas)].get_energy(unit="kcal/mol")
            errors.append(abs(energy - reference_energy) / len(molecule))
            print("Energy for {} using {} basis set: {} [kcal/mol]".format(name, bas, energy))
        average_errors[bas] = sum(errors) / len(errors)

print("== Results ==")
print("Average absolute error in bond energy per atom")
for bas in basis:
    if bas != reference_basis:
        print("Error for basis set {:<4}: {:>10.3f} [kcal/mol]".format(bas, average_errors[bas]))
