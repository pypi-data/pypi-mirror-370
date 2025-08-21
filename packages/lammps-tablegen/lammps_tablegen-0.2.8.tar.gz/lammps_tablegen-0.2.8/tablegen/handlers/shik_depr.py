import sys
import numpy as np
import mpmath as mp

from tablegen import constants
from tablegen import utils

from .base_handler import BASE2B

class SHIK(BASE2B):

    def __init__(self, args):
        super().__init__()

        self.TABLENAME = args.table_name
        self.PLOT = args.plot
        self.SPECIES = args.species
        self.CUTOFF = mp.mpf(args.cutoff)
        self.WOLF_CUTOFF = mp.mpf(args.wolf_cutoff)
        self.BUCK_CUTOFF = mp.mpf(args.buck_cutoff)
        self.GAMMA = mp.mpf(args.gamma)
        self.DATAPOINTS = args.data_points

        for spec in self.SPECIES:
            if spec not in constants.SHIK_SPECIES:
                print(f"ERROR: Unsopported species {spec}. Run tablegen shik -s to view atom support.")
                sys.exit(1)

        self.CHARGES = constants.SHIK_CHARGES
        self.CHARGES["O"] = self.get_oxygen_charge(args.structure_file)

        self.COEFFS = constants.SHIK_coeffs

        print("Charges:\n")
        for spec in self.SPECIES:
            if spec in self.CHARGES:
                print(spec, ":", self.CHARGES[spec])
        print()

        self.TWO_BODY = True

        
    def get_force(self, A, B, C, D, q_a, q_b, r, *args):
        A = mp.mpf(A)
        B = mp.mpf(B)
        C = mp.mpf(C)
        D = mp.mpf(D)
        q_a = mp.mpf(q_a)
        q_b = mp.mpf(q_b)
        r = mp.mpf(r)
        buck = -A*B*mp.exp(-B*r) + 6*C/(r**7) + -24*D/(r**25)
        wolf = ((q_a*q_b)/(4*mp.pi*constants.EPSILON_NAUGHT))*(-1/r**2 + 1/ (self.WOLF_CUTOFF**2))
        if r < self.BUCK_CUTOFF:
            res = -(buck + wolf)*self.smooth(r)
        else:
            res = -wolf*self.smooth(r)

        return float(res)

    def get_pot(self, A, B, C, D, q_a, q_b, r):
        A = mp.mpf(A)
        B = mp.mpf(B)
        C = mp.mpf(C)
        D = mp.mpf(D)
        q_a = mp.mpf(q_a)
        q_b = mp.mpf(q_b)
        r = mp.mpf(r)
        buck = A*mp.exp(-B*r) - C/(r**6) + D/(r**24)
        wolf = ((q_a*q_b)/(4*mp.pi*constants.EPSILON_NAUGHT))*(1/r - 1/self.WOLF_CUTOFF + (r - self.WOLF_CUTOFF)/(self.WOLF_CUTOFF**2))
        if r < self.BUCK_CUTOFF:
            res = (buck + wolf)*self.smooth(r)
        else:
            res = wolf*self.smooth(r)

        return float(res)

    def eval_force(self, spec1, spec2, r):
        pair_name = self.get_pair_name(spec1, spec2)
        return self.get_force(*self.COEFFS[pair_name], self.CHARGES[spec1], self.CHARGES[spec2], r)

    def eval_pot(self, spec1, spec2, r):
        pair_name = self.get_pair_name(spec1, spec2)
        return self.get_pot(*self.COEFFS[pair_name], self.CHARGES[spec1], self.CHARGES[spec2], r)

    def smooth(self, r):
        if r != self.WOLF_CUTOFF:
            return mp.exp(-self.GAMMA/((r - self.WOLF_CUTOFF)**2))
        else:
            return mp.mpf(0)

    def get_pair_name(self, spec1, spec2):
        option1 = spec1 + '-' + spec2
        option2 = spec2 + '-' + spec1
        if option1 in self.COEFFS:
            return option1
        elif option2 in self.COEFFS:
            return option2


    def get_oxygen_charge(self, filename):
        lines = open(filename).readlines()
        #Need to implement reading all types of file
        header_lines = next((i for i, line in enumerate(lines) if "Atoms" in line)) + 1
        atom_lines = np.loadtxt(skiprows = header_lines, fname = filename)
        charge_mapper = np.vectorize(lambda x: self.CHARGES[self.SPECIES[int(x) - 1]])
        try:
            total_positive_charge = np.sum(charge_mapper(atom_lines[:, 1]))
        except IndexError as e:
            raise RuntimeError("ERROR: More species listed in structure file than the names provided.")
        num_oxygens = np.sum(atom_lines[:, 1] == self.SPECIES.index("O") + 1)
        return -total_positive_charge/num_oxygens

    def no_spec_msg(self, spec1, spec2):
        return f"WARNING: No potential exists for species {spec1} and {spec2}."

    def get_table_name(self):
        return self.TABLENAME

    def to_plot(self):
        return self.PLOT

    def get_cutoff(self):
        return float(self.CUTOFF)

    def get_datapoints(self):
        return self.DATAPOINTS

    def get_species(self):
        return self.SPECIES

    @staticmethod
    def display_support():
        print("\nSUPPOTED ELEMENTS AND THEIR CHARGES:\n")

        atom_str_len = max([len(a) for a in constants.SHIK_CHARGES.keys()] + [len("ATOM")]) + SHIK.SUPPORT_SPACING

        charge_str_len = len("CHARGE")
        max_left = 1
        max_right = 1
        for charge in constants.SHIK_CHARGES.values():
            mod_c = utils.format_min_dec(charge, 1).strip()
            charge_str_len = max(charge_str_len, len(mod_c))
            whole, dec = mod_c.split(".")
            max_left = max(max_left, len(whole))
            max_right = max(max_right, len(dec))

        charge_str_len = max(max_left + max_right + 1, charge_str_len)
        dec_pos = int(round(charge_str_len/2))
        dec_pos = max(dec_pos, max_left)
        dec_pos = min(dec_pos, charge_str_len - max_right - 1)
        charge_str_len += SHIK.SUPPORT_SPACING

        print("\t" + "ATOM".ljust(atom_str_len) + "CHARGE".ljust(charge_str_len))


        for atom, charge in constants.SHIK_CHARGES.items():
            res_str = "\t" + atom.ljust(atom_str_len)
            if atom == "O":
                res_str += "??? (composition dependent)".ljust(charge_str_len)
            else:
                res_str += utils.align_by_decimal(
                           string = utils.format_min_dec(charge, 1),
                           size = charge_str_len,
                           dec_pos = dec_pos,
                           )
            print(res_str)

        print("\nPAIRWISE COEFFICIENTS:\n")

        pair_str_len = max([len(p) for p in constants.SHIK_coeffs.keys()] + [len("PAIR")]) + SHIK.SUPPORT_SPACING

        num_coeffs = len(constants.SHIK_COEFF_HEADINGS)
        column_params = list()

        for i in range(num_coeffs):
            coeff_str_len = len(constants.SHIK_COEFF_HEADINGS[i])
            max_left = 1
            max_right = 1
            for coeffs in constants.SHIK_coeffs.values():
                mod_c = utils.format_min_dec(coeffs[i], 1).strip()
                c_len = len(mod_c)
                if c_len > coeff_str_len:
                    coeff_str_len = c_len

                whole, dec = mod_c.split(".")
                max_left = max(max_left, len(whole))
                max_right = max(max_right, len(dec))

            coeff_str_len = max(max_left + max_right + 1, coeff_str_len)
            dec_pos = int(round(coeff_str_len/2))
            dec_pos = max(dec_pos, max_left)
            dec_pos = min(dec_pos, coeff_str_len - max_right - 1)
            coeff_str_len += SHIK.SUPPORT_SPACING
            column_params.append((coeff_str_len, dec_pos))

        res_str = "PAIR".ljust(pair_str_len)
        for i in range(num_coeffs):
            res_str += constants.SHIK_COEFF_HEADINGS[i].center(column_params[i][0])
        print("\t" + res_str)

        for pair, coeffs in constants.SHIK_coeffs.items():
            res_str = "\t" + pair.ljust(pair_str_len)
            for i in range(num_coeffs):
                res_str += utils.align_by_decimal(
                    string = utils.format_min_dec(coeffs[i], 1),
                    size = column_params[i][0],
                    dec_pos = column_params[i][1],
                    )

            print(res_str)

