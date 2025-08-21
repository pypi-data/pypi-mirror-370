import argparse
import numpy as np
import matplotlib.pyplot as plt
import sys
from .handlers import SHIK, BUCK, BUCK_EXT, TETER
from .handlers import TRUNC3B, SW_3B
from . import constants
from . import utils

def parse_args():
    parser = utils.ErrorHandlingParser(prog = "tablegen")


    subparsers = parser.add_subparsers(dest="command", required=True, metavar = "style", action = utils.StrictSubParsersAction)

    teter = subparsers.add_parser("teter", help = "Argument parser for generating tables based on TETER potentials.", description = "Non-Coulomic part of Teter potential.\n\nRef:\n\tDeng L, Du J. \"Development of boron oxide potentials for computer simulations of multicomponent oxide glasses.\" J Am Ceram Soc. 2019; 102: 2482–2505. https://doi.org/10.1111/jace.16082\n\nNote: Boron parameter calculation not yet implemented.", formatter_class = utils.NoMetavarHelpFormatter)

    teter.add_argument("species", nargs = "+", type = str, default = [], help = "Atoms for potential energy and force curve generation. Example: Si O Na.")

    teter.add_argument("-c", "--cutoff", type = float, default = constants.TETER_CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.TETER_CUTOFF} Å")
    teter.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}")
    teter.add_argument("-t", "--table_name", type = str, default = "TETER.table", help = f"Name of the created table file. Default: TETER.table")
    teter.add_argument("-p", "--plot", nargs=2, type = float, default = None, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib with lower and upper bound specified. Example: -p -10 10.")
    teter.add_argument("-s", "--support", action = utils.SupportAction, default = False, help = "Switch to show all currently supported elements of the potential. When specified all other arguments will be ignored. Dafault: False")
    teter.add_argument("-f", "--file",  nargs = "?", const = "in.TETER", help = "A switch for generating a LAMMPS formatted input file incorporating all of the information that could be implied from the potential selected. Desired file name can be provided as a positional argument. Default: in.TETER")

    teter.set_defaults(handler_class = TETER)

    shik = subparsers.add_parser("shik", help = "Argument parser for generating tables based on SHIK potentials.", description = "Ref:\n\tYueh-Ting Shih, Siddharth Sundararaman, Simona Ispas, and Liping Huang. \"New interaction potentials for alkaline earth silicate and borate glasses.\" Journal of non-crystalline solids 565 (2021): 120853.", formatter_class = utils.NoMetavarHelpFormatter)

    shik.add_argument("species", nargs = "+", type = str, default = [], help = "Map of species types and their stoichiometric coefficients with colons as separators. Example: Si:1 O:2. Coefficients of 1 can be ommited. Previous example is analogous to Si O:2.")
    shik.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF} Å")
    shik.add_argument("-w", "--wolf_cutoff", type = float, default = constants.WOLF_CUTOFF, help = f"Wolf cutoff used for generation of the potential functions. Default: {constants.WOLF_CUTOFF} Å")
    shik.add_argument("-b", "--buck_cutoff", type = float, default = constants.BUCK_CUTOFF, help = f"Buckingham cutoff that specifies past which distance only wolf interactions are considered. Default: {constants.BUCK_CUTOFF} Å")
    shik.add_argument("-g", "--gamma", type = float, default = constants.GAMMA, help = f"Smoothing function width. Default: {constants.GAMMA} Å")
    shik.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}")
    shik.add_argument("-t", "--table_name", type = str, default = "SHIK.table", help = f"Name of the created table file. Default: SHIK.table")
    shik.add_argument("-p", "--plot", nargs=2, type = float, default = None, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib with lower and upper bound specified. Example: -p -10 10.")
    shik.add_argument("-s", "--support", action = utils.SupportAction, default = False, help = "Switch to show all currently supported elements of the potential. When specified all other arguments will be ignored. Dafault: False")
    shik.add_argument("-f", "--file",  nargs = "?", const = "in.SHIK", help = "A switch for generating a LAMMPS formatted input file incorporating all of the information that could be implied from the potential selected. Desired file name can be provided as a positional argument. Default: in.SHIK")

    shik.set_defaults(handler_class = SHIK)


    buck = subparsers.add_parser("buck", help = "Argument parser for generating tables based on Buckingham potentials.", formatter_class = utils.NoMetavarHelpFormatter)

    buck.add_argument("pairs", nargs = "+", type = str, default = [], help = "Pairs of atoms for potential energy and force curve generation. Example: Na-O Si-Na Si-O O-O.")
    buck.add_argument("-t", "--table_name", type = str, default = "BUCK.table", help = f"Name of the created table file. Default: BUCK.table")
    buck.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF} Å")
    buck.add_argument("-p", "--plot", nargs=2, type = float, default = None, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib with lower and upper bound specified. Example: -p -10 10.")
    buck.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}")
    buck.add_argument("-f", "--file",  nargs = "?", const = "in.BUCK", help = "A switch for generating a LAMMPS formatted input file incorporating all of the information that could be implied from the potential selected. Desired file name can be provided as a positional argument. Default: in.BUCK")

    buck.set_defaults(handler_class = BUCK)


    buck_ext = subparsers.add_parser("buck_ext", help = "Argument parser for generating tables based on extended Buckingham potentials.", formatter_class = utils.NoMetavarHelpFormatter)

    buck_ext.add_argument("pairs", nargs = "+", type = str, default = [], help = "Pairs of atoms for potential energy and force curve generation. Example: Na-O Si-Na Si-O O-O.")
    buck_ext.add_argument("-t", "--table_name", type = str, default = "BUCKEXT.table", help = f"Name of the created table file. Default: BUCK.table")
    buck_ext.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF} Å")
    buck_ext.add_argument("-p", "--plot", nargs=2, type = float, default = None, help = f"Plotting switch. When included the potential functions will be plotted in matplotlib with lower and upper bound specified. Example: -p -10 10.")
    buck_ext.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS, help = f"Number of points used in the table definition of the potential function. Default: {constants.DATAPOINTS}")
    buck_ext.add_argument("-f", "--file",  nargs = "?", const = "in.BUCKEXT", help = "A switch for generating a LAMMPS formatted input file incorporating all of the information that could be implied from the potential selected. Desired file name can be provided as a positional argument. Default: in.BUCKEXT")


    buck_ext.set_defaults(handler_class = BUCK_EXT)

    trunc3b = subparsers.add_parser("3b_trunc", help = "Argument parser for generating tables based on three-body truncated harmonic potentials.", formatter_class = utils.NoMetavarHelpFormatter)

    trunc3b.add_argument("triplets", nargs = "+", type = str, default = [], help = "Ttiplets of atoms in the format B-A-C where A is the central atom.")
    trunc3b.add_argument("-t", "--table_name", type = str, default = "TRUNC", help = f"Name (no extension) of two files that will be created - three-body + tabulated files. Default: TRUNC.3b, TRUNC.table")
    trunc3b.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS3B, help = f"Number of steps used in tabulating interatomic separation distances. Angle is tabulated with 2N entries. In symmetric case the number of table entries will be M = (N+1)N^2 and in asymmetric 2N^3. Default: {constants.DATAPOINTS3B}")
    trunc3b.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF3B, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF3B} Å")
    trunc3b.add_argument("-f", "--file",  nargs = "?", const = "in.TRUNC3B", help = "A switch for generating a LAMMPS formatted input file incorporating all of the information that could be implied from the potential selected. Desired file name can be provided as a positional argument. Default: in.TRUNC3B")

    trunc3b.set_defaults(handler_class = TRUNC3B)

    sw_3b = subparsers.add_parser("3b_sw", help = "Argument parser for generating tables based on Stilinger-Webber potentials.", formatter_class = utils.NoMetavarHelpFormatter)

    sw_3b.add_argument("triplets", nargs = "+", type = str, default = [], help = "Ttiplets of atoms in the format B-A-C where A is the central atom.")
    sw_3b.add_argument("-t", "--table_name", type = str, default = "SW", help = f"Name (no extension) of two files that will be created - three-body + tabulated files. Default: SW.3b, SW3B.table")
    sw_3b.add_argument("-d", "--data_points", type = int, default = constants.DATAPOINTS3B, help = f"Number of steps used in tabulating interatomic separation distances. Angle is tabulated with 2N entries. In symmetric case the number of table entries will be M = (N+1)N^2 and in asymmetric 2N^3. Default: {constants.DATAPOINTS3B}")
    sw_3b.add_argument("-c", "--cutoff", type = float, default = constants.CUTOFF3B, help = f"Table cutoff beyond which no potentials or forces will be generated. Default: {constants.CUTOFF3B} Å")
    sw_3b.add_argument("-f", "--file",  nargs = "?", const = "in.SW3B", help = "A switch for generating a LAMMPS formatted input file incorporating all of the information that could be implied from the potential selected. Desired file name can be provided as a positional argument. Default: in.SW3B")

    sw_3b.set_defaults(handler_class = SW_3B)

    return parser.parse_args()

def two_body(handler):
    file = open(handler.get_table_name(), "w")
    file.write(constants.GENERATION_COMMENT)
    datapoints = handler.get_datapoints()
    radius = np.linspace(0, handler.get_cutoff(), datapoints + 1)[1:]
    num_digits = len(str(datapoints))

    pairs = handler.get_pairs()

    for pair_name in pairs:
            print(f"Generating interaction parameters for {pair_name}")
            file.write(pair_name + "\n")
            file.write(f"N {datapoints}\n\n")
            potential = []
            force = []
            for i, r in enumerate(radius):
                force_val = handler.eval_force(pair_name, r)
                force.append(force_val)
                pot_val = handler.eval_pot(pair_name, r)
                potential.append(pot_val)
                file.write(str(i + 1).rjust(num_digits) + "  " + f"{r:.6E}".center(16) + f"{potential[i]:.6E}".center(16) + f"{force[i]:.6E}".rjust(14) + "\n")
            file.write("\n\n")
            if handler.to_plot():
                plt.plot(radius, potential, label = pair_name)

    handler.comment_message_call()

    file.close()
    if handler.to_plot():
        plt.axhline(0, color="black", linewidth=1, linestyle = "--")
        plt.xlabel("Separation Distance (Å)")
        plt.ylabel("Potential Energy (eV)")
        plt.ylim(*handler.to_plot())
        plt.legend()
        plt.show()

        plt.savefig("potentials.png", dpi = 300, bbox_inches = "tight")

    if handler.lammps_file_needed():
        handler.gen_file()



def three_body(handler, symcase = False):

    table_name = handler.get_table_name()
    table3b = handler.get_3b_tablename()
    
    tb_file = open(table3b, "w")
    tab_file = open(table_name, "w")

    tb_file.write(constants.GENERATION_COMMENT)
    tab_file.write(constants.GENERATION_COMMENT)

    cutoff = handler.get_cutoff()
    datapoints = handler.get_datapoints()
    is_symmetric = handler.is_symmetric()

    all_combos = handler.get_all_atom_combos()

    for orig, triplet in handler.get_triplets():
        triplet_name = "-".join(triplet)
        all_combos.remove(triplet_name)

        tb_file.write(f"{triplet[1]}\n{triplet[0]}\n{triplet[2]}\n")
        tb_file.write(f"{cutoff}\n")
        tb_file.write(f"{table_name}\n")

        if orig or not is_symmetric:
            tb_file.write("-".join(triplet) + "\n")
        else:
            tb_file.write(f"{triplet[2]}-{triplet[1]}-{triplet[0]}\n")
            
        tb_file.write("linear\n")
        tb_file.write(f"{datapoints}\n\n")


        if orig or not is_symmetric: #If not original triplet (two non-central elements swapped) and potential is symmetric existing table will be reused
            tab_file.write(triplet_name + "\n")
            tab_file.write(f"N {datapoints} rmin {cutoff/datapoints} rmax {cutoff}\n\n")

            ctr = 0
            if triplet[0] == triplet[2]:
                print(f"Triplet {triplet_name} is symmetric. Working on generating a table of {(datapoints**2) * (datapoints + 1)} entries")
                for step, rij in enumerate(np.linspace(0, cutoff, datapoints + 1)[1:]):
                    for rik in np.linspace(rij, cutoff, datapoints - step):
                        for theta in np.linspace(np.pi/(4*datapoints), np.pi - np.pi/(4*datapoints), 2*datapoints):
                            ctr += 1
                            poteng = handler.get_pot(triplet_name, rij, rik, theta)
                            forces = handler.get_force_coeffs(triplet_name, rij, rik, theta, poteng)
                            force_porj = " ".join(map(str, forces))
                            tab_file.write(f"{ctr} {rij} {rik} {theta * 180 / np.pi} {force_porj} {poteng}\n")

                    print(f"Progress: {round(100*(step + 1)/datapoints, 3)}%")

            else:
                print(f"Triplet {triplet_name} is asymmetric. Working on generating a table of {2*(datapoints**3)} entries")
                for step, rij in enumerate(np.linspace(0, cutoff, datapoints + 1)[1:]):
                    for rik in np.linspace(0, cutoff, datapoints + 1)[1:]:
                        for theta in np.linspace(np.pi/(4*datapoints), np.pi - np.pi/(4*datapoints), 2*datapoints):
                            ctr += 1
                            poteng = handler.get_pot(triplet_name, rij, rik, theta)
                            forces = handler.get_force_coeffs(triplet_name, rij, rik, theta, poteng)
                            force_porj = " ".join(map(str, forces))
                            tab_file.write(f"{ctr} {rij} {rik} {theta * 180 / np.pi} {force_porj} {poteng}\n")

                    print(f"Progress: {round(100*(step + 1)/datapoints, 3)}%")

            tab_file.write("\n")

    #Placeholder for symmetric pairs
    tab_file.write("SYMPH\nN 2 rmin 0.1 rmax 0.2\n\n")
    tab_file.write("1 0.1 0.1 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("2 0.1 0.2 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("3 0.2 0.2 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("4 0.1 0.1 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("5 0.1 0.2 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("6 0.2 0.2 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("7 0.1 0.1 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("8 0.1 0.2 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("9 0.2 0.2 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("10 0.1 0.1 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("11 0.1 0.2 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("12 0.2 0.2 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")

    #Placeholder for asymmetric pairs
    tab_file.write("ASYMPH\nN 2 rmin 0.1 rmax 0.2\n\n")
    tab_file.write("1 0.1 0.1 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("2 0.1 0.2 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("3 0.2 0.1 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("4 0.2 0.2 22.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("5 0.1 0.1 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("6 0.1 0.2 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("7 0.2 0.1 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("8 0.2 0.2 67.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("9 0.1 0.1 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("10 0.1 0.2 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("11 0.2 0.1 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("12 0.2 0.2 112.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("13 0.1 0.1 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("14 0.1 0.2 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("15 0.2 0.1 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    tab_file.write("16 0.2 0.2 157.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")

    for triplet in all_combos:
        elements = triplet.split("-")
        tb_file.write(f"{elements[1]}\n{elements[0]}\n{elements[2]}\n")
        tb_file.write("0.2\n")
        tb_file.write(f"{table_name}\n")

        if elements[0] == elements[2]:
            tb_file.write("SYMPH\n")
        else:
            tb_file.write("ASYMPH\n")

        tb_file.write("linear\n")
        tb_file.write("2\n\n")

        

    tb_file.close()
    tab_file.close()

    if handler.lammps_file_needed():
        handler.gen_file()


def main():
    args = parse_args()

    handler = args.handler_class(args)

    (two_body if handler.is_2b() else three_body)(handler)


if __name__ == "__main__":
    main()
