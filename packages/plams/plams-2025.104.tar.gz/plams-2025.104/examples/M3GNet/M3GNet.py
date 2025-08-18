#!/usr/bin/env amspython
# coding: utf-8

# ## Requirements
#
# The package m3net can be installed with `amspackages`

# ## Purpose
#
# Use the M3GNet ML potential with AMS.

# ## Initialization

from scm.plams import *

# this line is not required in AMS2025+
init()


# ## Setup and run job

mol = from_smiles("O")
mol.lattice = [
    [
        3.0,
        0.0,
        0.0,
    ],
    [0.0, 3.0, 0.0],
    [0.0, 0.0, 3.0],
]

s = Settings()
s.runscript.nproc = 1
s.input.ams.task = "GeometryOptimization"
s.input.ams.GeometryOptimization.Convergence.Gradients = 0.01  # hartree/ang

s.input.MLPotential.Model = "M3GNet-UP-2022"
# If you have trained a custom M3GNet model yourself, you can use:
# s.input.MLPotential.Model = 'Custom'
# s.input.MLPotential.Backend = 'm3gnet'
# s.input.MLPotential.ParameterDir = '<path to directory containing the M3GNet model>'

job = AMSJob(settings=s, molecule=mol, name="ams_with_m3gnet")
job.run()

energy = job.results.get_energy(unit="eV")
print(f"M3GNet: final energy {energy:.3f} eV")
