import re, sys, copy
import numpy as np
import mpmath as mp
import itertools as it

from tablegen import constants
from tablegen import utils

from .base_handler import BASE3B


class SW_3B(BASE3B):
    
    def __init__(self, args):
        super().__init__()
        self.TWO_BODY = False
        self.SYMMETRIC = False

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
        for i, triplet in enumerate(self.TRIPLET_NAMES):
            try:
                lmbd = float(input(f"({triplet}) lambda: "))
            except ValueError:
                sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
            try:
                epsilon = float(input(f"({triplet}) epsilon: "))
            except ValueError:
                sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
            try:
                theta0 = float(input(f"({triplet}) theta-naught: ")) * mp.pi / 180
            except ValueError:
                sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
            try:
                gammaij = float(input(f"({triplet}) gamma ({self.TRIPLETS[i][1]}-{self.TRIPLETS[i][0]}): "))
            except ValueError:
                sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
            try:
                sigmaij = float(input(f"({triplet}) sigma ({self.TRIPLETS[i][1]}-{self.TRIPLETS[i][0]}): "))
            except ValueError:
                sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
            try:
                aij = float(input(f"({triplet}) a ({self.TRIPLETS[i][1]}-{self.TRIPLETS[i][0]}): "))
            except ValueError:
                sys.exit("Stillinger-Weber potential coefficients should be real numbers.")

            if self.TRIPLETS[i][0] != self.TRIPLETS[i][2] and not self.SYMMETRIC:
                try:
                    gammaik = float(input(f"({triplet}) gamma ({self.TRIPLETS[i][1]}-{self.TRIPLETS[i][2]}): "))
                except ValueError:
                    sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
                try:
                    sigmaik = float(input(f"({triplet}) sigma ({self.TRIPLETS[i][1]}-{self.TRIPLETS[i][2]}): "))
                except ValueError:
                    sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
                try:
                    aik = float(input(f"({triplet}) a ({self.TRIPLETS[i][1]}-{self.TRIPLETS[i][2]}): "))
                except ValueError:
                    sys.exit("Stillinger-Weber potential coefficients should be real numbers.")
            else:
                gammaik = gammaij
                sigmaik = sigmaij
                aik = aij


            self.COEFFS[triplet] = [lmbd, epsilon, theta0, gammaij, sigmaij, aij, gammaik, sigmaik, aik]

        tmp_trp = copy.deepcopy(self.TRIPLET_NAMES)
        for i, trp in enumerate(tmp_trp):
            if self.TRIPLETS[i][0] != self.TRIPLETS[i][2]:
                new_name = f"{self.TRIPLETS[i][2]}-{self.TRIPLETS[i][1]}-{self.TRIPLETS[i][0]}"
                self.TRIPLET_NAMES.append(new_name)
                self.TRIPLETS.append([self.TRIPLETS[i][2], self.TRIPLETS[i][1], self.TRIPLETS[i][0]])
                self.COEFFS[new_name] = self.COEFFS[trp][:3] + self.COEFFS[trp][6:9] + self.COEFFS[trp][3:6]

    def triplet_energy(self, rij, rik, theta, lmbd, epsilon, theta0, gammaij, sigmaij, aij, gammaik, sigmaik, aik):
        rij      = mp.mpf(rij)
        rik      = mp.mpf(rik)
        theta    = mp.mpf(theta)
        lmbd     = mp.mpf(lmbd)
        epsilon  = mp.mpf(epsilon)
        theta0   = mp.mpf(theta0)
        gammaij  = mp.mpf(gammaij)
        sigmaij  = mp.mpf(sigmaij)
        aij      = mp.mpf(aij)
        gammaik  = mp.mpf(gammaik)
        sigmaik  = mp.mpf(sigmaik)
        aik      = mp.mpf(aik)

        if sigmaij*aij <= rij:
            return 0

        if sigmaik*aik <= rik:
            return 0
    
        return lmbd * epsilon * mp.power(mp.cos(theta) - mp.cos(theta0), 2) * mp.exp(gammaij * sigmaij / (rij - aij * sigmaij)) * mp.exp(gammaik * sigmaik / (rik - aik * sigmaik))

    def get_pot(self, triplet, rij, rik, theta):
        return float(self.triplet_energy(rij, rik, theta, *self.COEFFS[triplet]))

    def get_force_coeffs(self, triplet, rij, rik, theta, U):
        return self.projection_coeffs(rij, rik, theta, U, *self.COEFFS[triplet])

    def projection_coeffs(self, rij, rik, theta, U, lmbd, epsilon, theta0, gammaij, sigmaij, aij, gammaik, sigmaik, aik):
        
        U = mp.mpf(U)

        #Partial derivative of potential energy with respect to rij
        if U:
            U_rij = -U * gammaij * sigmaij * mp.power(rij - aij * sigmaij, -2)
        else:
            U_rij = 0

        #Partial derivative of potential energy with respect to rik
        if U:
            U_rik =  -U * gammaik * sigmaik * mp.power(rik - aik * sigmaik, -2)           
        else:
            U_rik = 0

        #Partial derivative of potential energy with respect to theta

        if U:
            U_theta = -2 * mp.sin(theta) * lmbd * epsilon * (mp.cos(theta) - mp.cos(theta0)) * mp.exp(gammaij * sigmaij / (rij - aij * sigmaij)) * mp.exp(gammaik * sigmaik / (rik - aik * sigmaik))
        else:
            U_theta = 0

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

    def is_symmetric(self):
        return self.SYMMETRIC

    def is_2b(self):
        return self.TWO_BODY

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
