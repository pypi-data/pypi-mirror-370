from scm.plams.core.basejob import MultiJob, SingleJob
from scm.plams.core.enums import JobStatus
from scm.plams.core.errors import (
    FileError,
    JobError,
    MissingOptionalPackageError,
    MoleculeError,
    PlamsError,
    PTError,
    ResultsError,
    TrajectoryError,
    UnitsError,
)
from scm.plams.core.functions import (
    add_to_class,
    add_to_instance,
    config,
    delete_job,
    finish,
    init,
    load,
    load_all,
    log,
    read_all_molecules_in_xyz_file,
    read_molecules,
)
from scm.plams.core.jobmanager import JobManager
from scm.plams.core.jobrunner import GridRunner, JobRunner
from scm.plams.core.logging import get_logger
from scm.plams.core.results import Results
from scm.plams.core.settings import (
    ConfigSettings,
    JobManagerSettings,
    JobSettings,
    LogSettings,
    RunScriptSettings,
    SafeRunSettings,
    Settings,
)
from scm.plams.interfaces.adfsuite.ams import AMSJob, AMSResults
from scm.plams.interfaces.adfsuite.amsanalysis import (
    AMSAnalysisJob,
    AMSAnalysisResults,
    convert_to_unicode,
)
from scm.plams.interfaces.adfsuite.amsworker import (
    AMSWorker,
    AMSWorkerError,
    AMSWorkerPool,
    AMSWorkerResults,
)
from scm.plams.interfaces.adfsuite.crs import CRSJob, CRSResults
from scm.plams.interfaces.adfsuite.densf import DensfJob, DensfResults
from scm.plams.interfaces.adfsuite.fcf import FCFJob, FCFResults
from scm.plams.interfaces.adfsuite.forcefieldparams import (
    ForceFieldPatch,
    forcefield_params_from_kf,
)
from scm.plams.interfaces.adfsuite.quickjobs import (
    preoptimize,
    refine_density,
    refine_lattice,
)
from scm.plams.interfaces.adfsuite.unifac import UnifacJob, UnifacResults
from scm.plams.interfaces.molecule.ase import fromASE, toASE
from scm.plams.interfaces.molecule.packmol import (
    PackMolError,
    packmol,
    packmol_around,
    packmol_in_void,
    packmol_microsolvation,
    packmol_on_slab,
)
from scm.plams.interfaces.molecule.rdkit import (
    add_Hs,
    apply_reaction_smarts,
    apply_template,
    canonicalize_mol,
    from_rdmol,
    from_sequence,
    from_smarts,
    from_smiles,
    gen_coords_rdmol,
    get_backbone_atoms,
    get_conformations,
    get_substructure,
    modify_atom,
    partition_protein,
    readpdb,
    to_rdmol,
    to_smiles,
    writepdb,
    yield_coords,
    to_image,
    get_reaction_image,
)
from scm.plams.interfaces.thirdparty.cp2k import Cp2kJob, Cp2kResults, Cp2kSettings2Mol
from scm.plams.interfaces.thirdparty.crystal import CrystalJob, mol2CrystalConf
from scm.plams.interfaces.thirdparty.dftbplus import DFTBPlusJob, DFTBPlusResults
from scm.plams.interfaces.thirdparty.dirac import DiracJob, DiracResults
from scm.plams.interfaces.thirdparty.gamess import GamessJob
from scm.plams.interfaces.thirdparty.orca import ORCAJob, ORCAResults
from scm.plams.interfaces.thirdparty.raspa import RaspaJob, RaspaResults
from scm.plams.interfaces.thirdparty.vasp import VASPJob, VASPResults
from scm.plams.mol.atom import Atom
from scm.plams.mol.bond import Bond
from scm.plams.mol.identify import label_atoms
from scm.plams.mol.molecule import Molecule
from scm.plams.mol.pdbtools import PDBHandler, PDBRecord
from scm.plams.recipes.adffragment import ADFFragmentJob, ADFFragmentResults
from scm.plams.recipes.adfnbo import ADFNBOJob
from scm.plams.recipes.md.amsmdjob import AMSMDJob, AMSNPTJob, AMSNVEJob, AMSNVTJob
from scm.plams.recipes.md.nvespawner import AMSNVESpawnerJob
from scm.plams.recipes.md.scandensity import AMSMDScanDensityJob
from scm.plams.recipes.md.trajectoryanalysis import AMSMSDJob, AMSRDFJob, AMSVACFJob
from scm.plams.recipes.numgrad import NumGradJob
from scm.plams.recipes.numhess import NumHessJob
from scm.plams.recipes.pestools.optimizer import Optimizer
from scm.plams.recipes.redox import (
    AMSRedoxDirectJob,
    AMSRedoxScreeningJob,
    AMSRedoxThermodynamicCycleJob,
)
from scm.plams.recipes.reorganization_energy import ReorganizationEnergyJob
from scm.plams.tools.converters import (
    file_to_traj,
    gaussian_output_to_ams,
    qe_output_to_ams,
    rkf_to_ase_atoms,
    rkf_to_ase_traj,
    traj_to_rkf,
    vasp_output_to_ams,
)
from scm.plams.tools.geometry import (
    angle,
    axis_rotation_matrix,
    cell_shape,
    cellvectors_from_shape,
    dihedral,
    distance_array,
    rotation_matrix,
)
from scm.plams.tools.kftools import KFFile, KFHistory, KFReader
from scm.plams.tools.periodic_table import PT, PeriodicTable
from scm.plams.tools.table_formatter import format_in_table
from scm.plams.tools.job_analysis import JobAnalysis
from scm.plams.tools.plot import (
    get_correlation_xy,
    plot_band_structure,
    plot_phonons_band_structure,
    plot_phonons_dos,
    plot_phonons_thermodynamic_properties,
    plot_correlation,
    plot_grid_molecules,
    plot_molecule,
    plot_msd,
    plot_work_function,
)
from scm.plams.tools.reaction import ReactionEquation
from scm.plams.tools.reaction_energies import (
    balance_equation,
    balance_equation_new,
    get_stoichiometry,
    reaction_energy,
)
from scm.plams.tools.units import Units
from scm.plams.trajectories.dcdfile import DCDTrajectoryFile
from scm.plams.trajectories.rkffile import (
    RKFTrajectoryFile,
    write_general_section,
    write_molecule_section,
)
from scm.plams.trajectories.rkfhistoryfile import (
    RKFHistoryFile,
    molecules_to_rkf,
    rkf_filter_regions,
)
from scm.plams.trajectories.sdffile import SDFTrajectoryFile, create_sdf_string
from scm.plams.trajectories.sdfhistoryfile import SDFHistoryFile
from scm.plams.trajectories.trajectory import Trajectory
from scm.plams.trajectories.trajectoryfile import TrajectoryFile
from scm.plams.trajectories.xyzfile import XYZTrajectoryFile, create_xyz_string
from scm.plams.trajectories.xyzhistoryfile import XYZHistoryFile
from scm.plams.version import __version__

__all__ = [
    "Results",
    "JobRunner",
    "GridRunner",
    "init",
    "finish",
    "log",
    "load",
    "load_all",
    "delete_job",
    "add_to_class",
    "add_to_instance",
    "config",
    "read_molecules",
    "read_all_molecules_in_xyz_file",
    "JobManager",
    "Settings",
    "SafeRunSettings",
    "LogSettings",
    "RunScriptSettings",
    "JobSettings",
    "JobManagerSettings",
    "ConfigSettings",
    "get_logger",
    "SingleJob",
    "MultiJob",
    "JobStatus",
    "PlamsError",
    "FileError",
    "ResultsError",
    "JobError",
    "PTError",
    "UnitsError",
    "MoleculeError",
    "TrajectoryError",
    "Bond",
    "label_atoms",
    "PDBRecord",
    "PDBHandler",
    "Molecule",
    "Atom",
    "GamessJob",
    "DiracJob",
    "DiracResults",
    "RaspaJob",
    "RaspaResults",
    "CrystalJob",
    "mol2CrystalConf",
    "DFTBPlusJob",
    "DFTBPlusResults",
    "Cp2kJob",
    "Cp2kResults",
    "Cp2kSettings2Mol",
    "VASPJob",
    "VASPResults",
    "ORCAJob",
    "ORCAResults",
    "CRSResults",
    "CRSJob",
    "MissingOptionalPackageError",
    "ForceFieldPatch",
    "forcefield_params_from_kf",
    "AMSWorker",
    "AMSWorkerResults",
    "AMSWorkerError",
    "AMSWorkerPool",
    "DensfJob",
    "DensfResults",
    "FCFJob",
    "FCFResults",
    "AMSAnalysisJob",
    "AMSAnalysisResults",
    "convert_to_unicode",
    "preoptimize",
    "refine_density",
    "refine_lattice",
    "UnifacJob",
    "UnifacResults",
    "AMSJob",
    "AMSResults",
    "toASE",
    "fromASE",
    "packmol",
    "packmol_around",
    "packmol_on_slab",
    "packmol_microsolvation",
    "packmol_in_void",
    "PackMolError",
    "add_Hs",
    "apply_reaction_smarts",
    "apply_template",
    "gen_coords_rdmol",
    "get_backbone_atoms",
    "modify_atom",
    "to_rdmol",
    "from_rdmol",
    "from_sequence",
    "from_smiles",
    "from_smarts",
    "to_smiles",
    "partition_protein",
    "readpdb",
    "writepdb",
    "get_substructure",
    "get_conformations",
    "yield_coords",
    "canonicalize_mol",
    "KFFile",
    "KFReader",
    "KFHistory",
    "traj_to_rkf",
    "vasp_output_to_ams",
    "qe_output_to_ams",
    "gaussian_output_to_ams",
    "rkf_to_ase_traj",
    "rkf_to_ase_atoms",
    "file_to_traj",
    "Units",
    "rotation_matrix",
    "axis_rotation_matrix",
    "distance_array",
    "angle",
    "dihedral",
    "cell_shape",
    "cellvectors_from_shape",
    "get_stoichiometry",
    "balance_equation",
    "reaction_energy",
    "PeriodicTable",
    "PT",
    "format_in_table",
    "JobAnalysis",
    "plot_band_structure",
    "plot_molecule",
    "plot_grid_molecules",
    "get_correlation_xy",
    "plot_correlation",
    "plot_msd",
    "plot_work_function",
    "SDFTrajectoryFile",
    "create_sdf_string",
    "XYZHistoryFile",
    "Trajectory",
    "TrajectoryFile",
    "RKFTrajectoryFile",
    "write_general_section",
    "write_molecule_section",
    "DCDTrajectoryFile",
    "RKFHistoryFile",
    "molecules_to_rkf",
    "rkf_filter_regions",
    "XYZTrajectoryFile",
    "create_xyz_string",
    "SDFHistoryFile",
    "ReorganizationEnergyJob",
    "ADFFragmentJob",
    "ADFFragmentResults",
    "ADFNBOJob",
    "AMSMDJob",
    "AMSNVEJob",
    "AMSNVTJob",
    "AMSNPTJob",
    "AMSNVESpawnerJob",
    "AMSMDScanDensityJob",
    "AMSRDFJob",
    "AMSMSDJob",
    "AMSVACFJob",
    "NumGradJob",
    "NumHessJob",
    "Optimizer",
    "AMSRedoxDirectJob",
    "AMSRedoxScreeningJob",
    "AMSRedoxThermodynamicCycleJob",
]
