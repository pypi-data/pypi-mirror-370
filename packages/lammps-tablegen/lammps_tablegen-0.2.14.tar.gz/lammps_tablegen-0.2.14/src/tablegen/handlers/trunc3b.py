import re, sys, copy
import numpy as np
import mpmath as mp
import itertools as it

from tablegen import constants
from tablegen import utils

from .base_handler import BASE3B

class TRUNC3B(BASE3B):
    
    def __init__(self, args):
        super().__init__()
        self.TABLENAME = args.table_name
        self.CUTOFF = float(args.cutoff)
        self.DATAPOINTS = args.data_points

        self.TRIPLETS = list()
        self.TRIPLET_NAMES = list()

        self.NEED_FILE = not args.file is None
        if self.NEED_FILE:
            self.LAMMPS_FILENAME = args.file


        elems = set()
        self.ORIG_TRIPLETS = 0
        for triplet in args.triplets:
            self.ORIG_TRIPLETS += 1
            nowhite = re.sub(r'\s+', '', triplet)
            self.TRIPLET_NAMES.append(nowhite)
            split_triplet = nowhite.split("-")
            if len(split_triplet) == 3:
                elems.add(split_triplet[0])
                elems.add(split_triplet[1])
                elems.add(split_triplet[2])
                self.TRIPLETS.append(split_triplet)
            else:
                print("ERROR: Each triplet has to contain three elements (two dashes). Please read the help message for any three-body generator.")
                sys.exit(1)

        self.SPECIES = list(elems)

        self.COEFFS = dict()
        for triplet in self.TRIPLET_NAMES:
            try:
                k = float(input(f"({triplet}) k: "))
            except ValueError:
                sys.exit("Truncated three-body potential coefficients should be real numbers.")
            try:
                rho = float(input(f"({triplet}) rho: "))
            except ValueError:
                sys.exit("Truncated three-body potential coefficients should be real numbers.")
            try:
                theta0 = float(input(f"({triplet}) theta-naught: ")) * mp.pi / 180
            except ValueError:
                sys.exit("Truncated three-body potential coefficients should be real numbers.")

            if not rho:
                sys.exit("Rho cannot be 0. Yields no potential energy. Please simply omit this triplet.")

            self.COEFFS[triplet] = [k, rho, theta0]

        tmp_trp = copy.deepcopy(self.TRIPLET_NAMES)
        for i, trp in enumerate(tmp_trp):
            if self.TRIPLETS[i][0] != self.TRIPLETS[i][2]:
                new_name = f"{self.TRIPLETS[i][2]}-{self.TRIPLETS[i][1]}-{self.TRIPLETS[i][0]}"
                self.TRIPLET_NAMES.append(new_name)
                self.TRIPLETS.append([self.TRIPLETS[i][2], self.TRIPLETS[i][1], self.TRIPLETS[i][0]])
                self.COEFFS[new_name] = self.COEFFS[trp]

    def triplet_energy(self, rij, rik, theta, k, rho, theta0):
        rij      = mp.mpf(rij)
        rik      = mp.mpf(rik)
        theta    = mp.mpf(theta)
        theta0   = mp.mpf(theta0)
        k        = mp.mpf(k)
        rho      = mp.mpf(rho)

        return mp.mpf(0.5) * k * mp.power(theta - theta0, 2) * mp.exp(-(mp.power(rij, 8) + mp.power(rik, 8)) / mp.power(rho, 8))

    def get_pot(self, triplet, rij, rik, theta):
        return float(self.triplet_energy(rij, rik, theta, *self.COEFFS[triplet]))

    def get_force_coeffs(self, triplet, rij, rik, theta, U):
        return self.projection_coeffs(rij, rik, theta, U, *self.COEFFS[triplet])


    def projection_coeffs(self, rij, rik, theta, U, k, rho, theta0):

        U = mp.mpf(U)

        #Partial derivative of potential energy with respect to rij
        U_rij = U * (-8 * mp.power(rij, 7) / mp.power(rho, 8))

        #Partial derivative of potential energy with respect to rik
        U_rik = U * (-8 * mp.power(rik, 7) / mp.power(rho, 8))

        #Partial derivative of potential energy with respect to theta

        U_theta = k * (theta - theta0) * mp.exp(-(mp.power(rij, 8) + mp.power(rik, 8)) / mp.power(rho, 8))

        #True for any potential
        f_i1 = mp.power(rij, -1) * U_rij + U_theta * (rik * mp.cos(theta) - rij)/(mp.power(rij, 2) * rik * mp.sin(theta))
        f_i2 = mp.power(rik, -1) * U_rik + U_theta * (rij * mp.cos(theta) - rik)/(mp.power(rik, 2) * rij * mp.sin(theta))
        f_j2 = U_theta * mp.power(rij * rik * mp.sin(theta), -1)

        #By symetry (and analytically)
        f_j1 = -f_i1
        f_k1 = -f_i2
        f_k2 = -f_j2

        return [float(f_i1), float(f_i2), float(f_j1), float(f_j2), float(f_k1), float(f_k2)]


    def get_table_name(self):
        return self.TABLENAME + "3B.table"

    def get_triplets(self):
        return [(i < self.ORIG_TRIPLETS, trp) for i, trp in enumerate(self.TRIPLETS)]

    def get_cutoff(self):
        return self.CUTOFF

    def get_datapoints(self):
        return self.DATAPOINTS

    def get_all_atom_combos(self):
        elem_set = set()
        for trpl in self.TRIPLETS:
            for el in trpl:
                elem_set.add(el)
        return ["-".join(trpl) for trpl in it.product(elem_set, repeat = 3)]

    def lammps_file_needed(self):
        return self.NEED_FILE

    def gen_file(self):
        lmp_file = open(self.LAMMPS_FILENAME, "w")

        text = utils.generate_filetext_3b(
            elements = self.SPECIES,
            tablename = self.TABLENAME + ".3b",
            )

        lmp_file.write(text)

        lmp_file.close()

    def get_3b_tablename(self):
        return self.TABLENAME + ".3b"

