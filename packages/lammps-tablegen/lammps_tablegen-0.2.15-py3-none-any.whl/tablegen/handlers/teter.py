import re, sys
import numpy as np
import mpmath as mp

from tablegen import constants
from tablegen import utils

from .base_handler import BASE2B

class TETER(BASE2B):

    def __init__(self, args):
        super().__init__()

        self.TABLENAME = args.table_name
        self.PLOT = args.plot
        self.SPECIES = args.species
        self.CUTOFF = mp.mpf(args.cutoff)
        self.DATAPOINTS = args.data_points

        self.NEED_FILE = not args.file is None
        if self.NEED_FILE:
            self.LAMMPS_FILENAME = args.file

        self.TWO_BODY = True

        self.UNITS = "metal"

        self.CHARGES = constants.TETER_CHARGES

        self.COEFFS = dict()

        visited = list()
        filtered_species = list()
        for spec in self.SPECIES:
            pair_name = None

            for attempt in (f"{spec}-O", f"O-{spec}"):
                if attempt in constants.TETER_COEFFS:
                    pair_name = attempt

            if pair_name is None:
                print(f"\nWARNING: Unsupported atom {spec} will be ignored.\n")
            elif pair_name in visited:
                print(f"\nWARNING: Duplicate entry for atom {spec} will be ignored.\n")
            else:
                filtered_species.append(spec)
                visited.append(pair_name)
                self.COEFFS[pair_name] = constants.TETER_COEFFS[pair_name]

        self.SPECIES = filtered_species

        print("Charges:\n")
        for spec in self.SPECIES:
            if spec in self.CHARGES:
                print(spec, ":", self.CHARGES[spec])
        print()



    def get_pairs(self):
        return self.COEFFS.keys()


    def get_force(self, A, B, C, D, rho, n, r_0, r):
        A =   mp.mpf(A)
        B =   mp.mpf(B)
        C =   mp.mpf(C)
        D =   mp.mpf(D)
        rho = mp.mpf(rho)
        n =   mp.mpf(n)
        r_0 = mp.mpf(r_0)
        r =   mp.mpf(r)

        if r <= r_0:
            return B * n * mp.power(r, -n - 1) - 2 * D * r
        else:
            return (A / rho) * mp.exp(-r / rho) - 6 * C * mp.power(r, -7)


    def get_pot(self, A, B, C, D, rho, n, r_0, r):
        A =   mp.mpf(A)
        B =   mp.mpf(B)
        C =   mp.mpf(C)
        D =   mp.mpf(D)
        rho = mp.mpf(rho)
        n =   mp.mpf(n)
        r_0 = mp.mpf(r_0)
        r =   mp.mpf(r)

        if r <= r_0:
            return B * mp.power(r, -n) + D * mp.power(r, 2)
        else:
            return A * mp.exp(-r / rho) - C * mp.power(r, -6)


    def eval_force(self, pair_name, r):
        if pair_name in self.COEFFS.keys():
            return float(self.get_force(*self.COEFFS[pair_name], r))
        else:
            raise RuntimeError("ERROR: Inconsitent pair_name assignment!")

    def eval_pot(self, pair_name, r):
        if pair_name in self.COEFFS.keys():
            return float(self.get_pot(*self.COEFFS[pair_name], r))
        else:
            raise RuntimeError("ERROR: Inconsitent pair_name assignment!")

    def comment_message_call(self):
        print(f"\nCOMMENT: Only oxygen-cation interactions are specified by Teter.\n One should use Coulombic interactions for the rest.\n")

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

    def is_2b(self):
        return self.TWO_BODY

    @staticmethod
    def display_support():
        print("\nSUPPOTED ELEMENTS AND THEIR CHARGES:\n")

        atom_str_len = max([len(a) for a in constants.TETER_CHARGES.keys()] + [len("ATOM")]) + TETER.SUPPORT_SPACING

        charge_str_len = len("CHARGE")
        max_left = 1
        max_right = 1
        for charge in constants.TETER_CHARGES.values():
            mod_c = utils.format_min_dec(charge, 1).strip()
            charge_str_len = max(charge_str_len, len(mod_c))
            whole, dec = mod_c.split(".")
            max_left = max(max_left, len(whole))
            max_right = max(max_right, len(dec))

        charge_str_len = max(max_left + max_right + 1, charge_str_len)
        dec_pos = int(round(charge_str_len/2))
        dec_pos = max(dec_pos, max_left)
        dec_pos = min(dec_pos, charge_str_len - max_right - 1)
        charge_str_len += TETER.SUPPORT_SPACING

        print("\t" + "ATOM".ljust(atom_str_len) + "CHARGE".ljust(charge_str_len))

        for atom, charge in constants.TETER_CHARGES.items():
            res_str = "\t" + atom.ljust(atom_str_len)
            res_str += utils.align_by_decimal(
                       string = utils.format_min_dec(charge, 1),
                       size = charge_str_len,
                       dec_pos = max_left,
                       )
            print(res_str)

        print("\nPAIRWISE COEFFICIENTS:\n")

        pair_str_len = max([len(p) for p in constants.TETER_COEFFS.keys()] + [len("PAIR")]) + TETER.SUPPORT_SPACING

        num_coeffs = len(constants.TETER_COEFF_HEADINGS)
        column_params = list()

        for i in range(num_coeffs):
            coeff_str_len = len(constants.TETER_COEFF_HEADINGS[i])
            max_left = 1
            max_right = 1
            for coeffs in constants.TETER_COEFFS.values():
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
            coeff_str_len += TETER.SUPPORT_SPACING
            column_params.append((coeff_str_len, dec_pos))

        res_str = "PAIR".ljust(pair_str_len)
        for i in range(num_coeffs):
            res_str += constants.TETER_COEFF_HEADINGS[i].center(column_params[i][0])
        print("  " + res_str)

        for pair, coeffs in constants.TETER_COEFFS.items():
            res_str = "  " + pair.ljust(pair_str_len)
            for i in range(num_coeffs):
                res_str += utils.align_by_decimal(
                    string = utils.format_min_dec(coeffs[i], 1),
                    size = column_params[i][0],
                    dec_pos = column_params[i][1],
                    )

            print(res_str)

    def lammps_file_needed(self):
        return self.NEED_FILE

    def gen_file(self):
        lmp_file = open(self.LAMMPS_FILENAME, "w")

        text = utils.generate_filetext_2b(
            elements = self.SPECIES,
            pairs = self.COEFFS.keys(),
            datapoints = self.DATAPOINTS,
            tablename = self.TABLENAME,
            cutoff = self.CUTOFF,
            units = self.UNITS,
            timestep = "0.001 #1 femtosecond",
            extra_pairstyle = "coul/long 12"
            )

        text += "\n\n#COULOMBIC INTERACTIONS\n\n"

        for i in range(len(self.SPECIES)):
            text += "set".ljust(constants.LAMMPS_FILE_TAB) + f"type {i + 1} charge {self.CHARGES[self.SPECIES[i]]}\n"
        
        text += "\n"
        text += "kspace_style".ljust(constants.LAMMPS_FILE_TAB) + "ewald 0.000001\n\n"
        text += "pair_coeff".ljust(constants.LAMMPS_FILE_TAB) + "* * coul/long\n"


        text += "\n\n#SUGGESTED PROCEDURE\n\n"
        text += "#This procedure follows multiple papers description of a\n"
        text += "#melt-quench process for oxide glasses with Teter potentials.\n\n"

        text += "\n"
        text += "#Frequency of system-wide properties output\n"
        text += "thermo".ljust(constants.LAMMPS_FILE_TAB) + "1000\n"
        text += "thermo_style".ljust(constants.LAMMPS_FILE_TAB) + "custom step temp etotal pe vol density press\n"
        text += "thermo_modify".ljust(constants.LAMMPS_FILE_TAB) + "flush yes\n"
        text += "\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "timestep equal 1.0e-12 #s\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "quenchrate equal 5 #K/ps\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "start_temp equal 6000 #K\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "room_temp equal 300 #K\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "room_equil equal 10 #ps\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "sit_time equal 80 #ps\n"

        text += "\n"

        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "quench_steps equal $(round((v_start_temp - v_room_temp)*1.0e-12/(dt*v_quenchrate*v_timestep)))\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "sit_steps equal $(round(v_sit_time*1.0e-12/(dt*v_timestep)))\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "room_equil_steps equal $(round(v_room_equil*1.0e-12/(dt*v_timestep)))\n"
        text += "\n"

        text += "minimize".ljust(constants.LAMMPS_FILE_TAB) + "1.0e-8 1.0e-8 100000 10000000\n"
        text += "velocity".ljust(constants.LAMMPS_FILE_TAB) + "all create ${room_temp} 12345\n\n"
        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "initial_room_equil all nvt temp ${room_temp} ${room_temp} $(100.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${room_equil_steps}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "initial_room_equil\n\n"

        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "melt all nvt temp ${start_temp} ${start_temp} $(100.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${sit_steps}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "melt\n\n"

        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "melt all npt temp ${start_temp} ${start_temp} $(100.0*dt) iso 0 0 $(1000.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${sit_steps}/2\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "melt\n\n"

        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "quench all npt temp ${start_temp} ${room_temp} $(100.0*dt) iso 0 0 $(1000.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${quench_steps}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "quench\n\n"

        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "room_sit all npt temp ${room_temp} ${room_temp} $(100.0*dt) iso 0 0 $(1000.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${sit_steps}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "room_sit\n\n"

        text += "write_data".ljust(constants.LAMMPS_FILE_TAB) + "glass_" + "".join(self.SPECIES) + ".structure\n"

        lmp_file.write(text)

        lmp_file.close()
