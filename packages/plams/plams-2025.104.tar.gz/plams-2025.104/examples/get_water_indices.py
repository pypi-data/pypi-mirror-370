import sys
from scm.plams import RKFTrajectoryFile


def main():
    """
    Main body of the script
    """
    filename = sys.argv[1]

    rkf = RKFTrajectoryFile(filename)
    mol = rkf.get_plamsmol()
    rkf.close()

    oxygens = get_water_oxygens(mol)

    outfile = open("indices.txt", "w")
    for i, io in enumerate(oxygens):
        if i % 10 == 0 and i != 0:
            outfile.write("\n")
        outfile.write("%8i " % (io))
    outfile.close()


def get_water_oxygens(mol):
    """
    Select the oxygens in water only
    """
    wo = []
    for iat, at in enumerate(mol.atoms):
        if at.symbol != "O":
            continue
        neighbors = [n.symbol for n in mol.neighbors(at)]
        if neighbors == ["H", "H"]:
            wo.append(iat)
    return wo


if __name__ == "__main__":
    main()
