#!/usr/bin/env amspython
# Workflow with PLAMS
from scm.plams import AMSResults, Units, add_to_class, Settings, read_molecules, AMSJob

# A couple of useful function for extracting results:


@add_to_class(AMSResults)
def get_excitations(results):
    """Returns excitation energies (in eV) and oscillator strenghts (in Debye)."""
    if results.job.ok():
        exci_energies_au = results.readrkf("Excitations SS A", "excenergies", file="engine")
        oscillator_str_au = results.readrkf("Excitations SS A", "oscillator strengths", file="engine")
        # The results are stored in atomic units. Convert them to more convenient units:
        exci_energies = Units.convert(exci_energies_au, "au", "eV")
        oscillator_str = Units.convert(oscillator_str_au, "au", "Debye")
        return exci_energies, oscillator_str
    else:
        return [], []


@add_to_class(AMSResults)
def has_good_excitations(results, min_energy, max_energy, oscillator_str_threshold=1e-4):
    """Returns True if there is at least one excitation with non-vanishing oscillator strenght
    in the energy range [min_energy, max_energy]. Unit for min_energy and max energy: eV.
    """
    exci_energies, oscillator_str = results.get_excitations()
    for e, o in zip(exci_energies, oscillator_str):
        if min_energy < e < max_energy and o > oscillator_str_threshold:
            return True
    return False


# Calculation settings:
# =====================
from scm.input_classes import ADF, AMS, DFTB


# Settings for geometry optimization with the AMS driver:
def get_go_settings():
    go_sett = Settings()
    go_sett.input = AMS()
    go_sett.input.Task = "GeometryOptimization"
    go_sett.input.GeometryOptimization.Convergence.Gradients = 1.0e-4
    return go_sett


# Settings for single point calculation with the AMS driver
def get_sp_settings():
    sp_sett = Settings()
    sp_sett.input = AMS()
    sp_sett.input.Task = "SinglePoint"
    return sp_sett


# Settings for the DFTB engine (including excitations)
go_dftb_sett = get_go_settings()
go_dftb_sett.input.Engine = DFTB()
go_dftb_sett.input.Engine.Model = "SCC-DFTB"
go_dftb_sett.input.Engine.ResourcesDir = "QUASINANO2015"
go_dftb_sett.input.Engine.Properties.Excitations.TDDFTB.Calc = "Singlet"
go_dftb_sett.input.Engine.Properties.Excitations.TDDFTB.Lowest = 10
go_dftb_sett.input.Engine.Occupation.Temperature = 5.0

# Settings for the geometry optimization with the ADF engine
go_adf_sett = get_go_settings()
go_adf_sett.input.Engine = ADF()
go_adf_sett.input.Engine.Basis.Type = "DZP"
go_adf_sett.input.Engine.NumericalQuality = "Basic"

# Settings for the excitation calculation using the ADF engine
sp_adf_exci_sett = get_sp_settings()
sp_adf_exci_sett.input.Engine = ADF()
sp_adf_exci_sett.input.Engine.Basis.Type = "TZP"
sp_adf_exci_sett.input.Engine.XC.GGA = "PBE"
sp_adf_exci_sett.input.Engine.NumericalQuality = "Basic"
sp_adf_exci_sett.input.Engine.Symmetry = "NOSYM"
sp_adf_exci_sett.input.Engine.Excitations.Lowest = [10]
sp_adf_exci_sett.input.Engine.Excitations.OnlySing = True


# Import all xyz files in the folder 'molecules'

molecules = read_molecules("molecules")


print("Step 1: prescreening with DFTB")
print("==============================")

promising_molecules = {}

for name, mol in molecules.items():
    dftb_job = AMSJob(name="DFTB_" + name, molecule=mol, settings=go_dftb_sett)
    dftb_job.run()

    if dftb_job.results.has_good_excitations(1, 6):
        promising_molecules[name] = dftb_job.results.get_main_molecule()

print(f"Found {len(promising_molecules)} promising molecules with DFTB")


print("Step 2: Optimization and excitations calculation with ADF")
print("=========================================================")

for name, mol in promising_molecules.items():
    adf_go_job = AMSJob(name="ADF_GO_" + name, molecule=mol, settings=go_adf_sett)
    adf_go_job.run()

    optimized_mol = adf_go_job.results.get_main_molecule()

    adf_exci_job = AMSJob(
        name="ADF_exci_" + name,
        molecule=optimized_mol,
        settings=sp_adf_exci_sett,
    )
    adf_exci_job.run()

    if adf_exci_job.results.has_good_excitations(2, 4):
        print(f"Molecule {name} has excitation(s) satysfying our criteria!")
        print(optimized_mol)
        exci_energies, oscillator_str = adf_exci_job.results.get_excitations()
        print("Excitation energy [eV], oscillator strength:")
        for e, o in zip(exci_energies, oscillator_str):
            print(f"{e:8.4f}, {o:8.4f}")
