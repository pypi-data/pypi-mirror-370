#!/usr/bin/env amspython
from scm.plams import *

"""
    Script to get and print the first 5 frames as PLAMS Molecules
    from an ams.rkf trajectory.

    The script also shows how to print a specific frame, frame 23.

    Set the correct path to ams.rkf below, and then run as
    $AMSBIN/amspython MoleculesFromRKFTrajectory.py
"""


def main():
    job = AMSJob.load_external("ams.rkf")  # modify to give the path to the ams.rkf file

    trajectory = Trajectory(job.results.rkfpath())
    for i, mol in enumerate(trajectory, 1):
        print(f"frame {i}")
        print(mol)  # mol is a PLAMS Molecule
        if i == 5:
            break

    print("Extracting specific molecule")
    mol = job.results.get_history_molecule(23)
    print("Frame 23")
    print(mol)


if __name__ == "__main__":
    main()
