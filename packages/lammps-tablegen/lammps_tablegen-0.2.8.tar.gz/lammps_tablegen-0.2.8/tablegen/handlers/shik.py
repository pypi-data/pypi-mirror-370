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
        self.CUTOFF = mp.mpf(args.cutoff)
        self.WOLF_CUTOFF = mp.mpf(args.wolf_cutoff)
        self.BUCK_CUTOFF = mp.mpf(args.buck_cutoff)
        self.GAMMA = mp.mpf(args.gamma)
        self.DATAPOINTS = args.data_points
        self.SPECIES = list()
        self.STOICS = list()
        self.COEFFS = dict()

        self.UNITS = "metal"

        self.NEED_FILE = not args.file is None
        if self.NEED_FILE:
            self.LAMMPS_FILENAME = args.file

        for spec in args.species:
            if ":" not in spec:
                stoic = "1"
            else:
                splt_spec_entry = spec.split(":")
                if len(splt_spec_entry) != 2:
                    print(f"\nERROR: Species entry {spec} is formatted incorrectly. Please check help message by running tablegen shik.\n")
                else:
                    spec, stoic = splt_spec_entry

            if spec not in constants.SHIK_SPECIES:
                print(f"ERROR: Unsopported species {spec}. Run tablegen shik -s to view atom support.")
                sys.exit(1)
            else:
                self.SPECIES.append(spec)
                if stoic.isnumeric():
                    self.STOICS.append(int(stoic))
                else:
                    print("\nERROR: Element stoichiometric coefficients have to have integer values.\n")
                    sys.exit(1)

        self.CHARGES = constants.SHIK_CHARGES
        if "O" in self.SPECIES:
            self.CHARGES["O"] = self.get_oxygen_charge()

        visited = list()
        for spec1 in self.SPECIES:
            if not spec1 in visited:
                for spec2 in self.SPECIES:
                    pair_name = f"{spec1}-{spec2}"
                    if pair_name not in constants.SHIK_COEFFS.keys():
                        if f"{spec2}-{spec1}" not in constants.SHIK_COEFFS.keys():
                            print(f"\nWARNING: The {pair_name} interaction is not defined by this potential.\n")
                    else:
                        self.COEFFS[pair_name] = constants.SHIK_COEFFS[pair_name]
            else:
                print(f"\nWARNING: Duplicate entry for species {spec1} will be counted towards the total. Make sure that this behavior is intended.\n")


                

        print("Charges:\n")
        for spec in self.SPECIES:
            if spec in self.CHARGES:
                print(spec, ":", self.CHARGES[spec])
        print()

        self.TWO_BODY = True

    def get_pairs(self):
        return self.COEFFS.keys()

        
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

    def eval_force(self, pair_name, r):
        if pair_name in self.COEFFS.keys():
            spec1, spec2 = pair_name.split("-")
            return self.get_force(*self.COEFFS[pair_name], self.CHARGES[spec1], self.CHARGES[spec2], r)
        else:
            raise RuntimeError("ERROR: Inconsitent pair_name assignment!")

    def eval_pot(self, pair_name, r):
        if pair_name in self.COEFFS.keys():
            spec1, spec2 = pair_name.split("-")
            return self.get_pot(*self.COEFFS[pair_name], self.CHARGES[spec1], self.CHARGES[spec2], r)
        else:
            raise RuntimeError("ERROR: Inconsitent pair_name assignment!")

    def smooth(self, r):
        if r != self.WOLF_CUTOFF:
            return mp.exp(-self.GAMMA/((r - self.WOLF_CUTOFF)**2))
        else:
            return mp.mpf(0)


    def get_oxygen_charge(self):
        num_ox = 0
        total_charge = 0
        for spec, stoic in zip(self.SPECIES, self.STOICS):
            if spec == "O":
                num_ox += stoic
            else:
                total_charge += self.CHARGES[spec]

        return -total_charge/num_ox


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

        pair_str_len = max([len(p) for p in constants.SHIK_COEFFS.keys()] + [len("PAIR")]) + SHIK.SUPPORT_SPACING

        num_coeffs = len(constants.SHIK_COEFF_HEADINGS)
        column_params = list()

        for i in range(num_coeffs):
            coeff_str_len = len(constants.SHIK_COEFF_HEADINGS[i])
            max_left = 1
            max_right = 1
            for coeffs in constants.SHIK_COEFFS.values():
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

        for pair, coeffs in constants.SHIK_COEFFS.items():
            res_str = "\t" + pair.ljust(pair_str_len)
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
            timestep =  "0.0016 #1.6 fs"
            )

        text += "\n\n#SUGGESTED PROCEDURE\n\n"

        for i in range(len(self.SPECIES)):
            text += "set".ljust(constants.LAMMPS_FILE_TAB) + f"type {i + 1} charge {self.CHARGES[self.SPECIES[i]]}\n"

        text += "#This procedure follows multiple papers description of a\n"
        text += "#melt-quench process for oxide glasses with SHIK potentials.\n\n"

        text += "\n"
        text += "#Frequency of system-wide properties output\n"
        text += "thermo".ljust(constants.LAMMPS_FILE_TAB) + "1000\n"
        text += "thermo_style".ljust(constants.LAMMPS_FILE_TAB) + "custom step temp etotal pe vol density press\n"
        text += "thermo_modify".ljust(constants.LAMMPS_FILE_TAB) + "flush yes\n"
        text += "\n"


        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "quench_rate equal 1 #K/ps\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "timestep equal 1.0e-12 #s\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "start_temp equal 4000 #K\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "end_temp equal 300 #K\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "nvt_sit_time equal 1000 #ps\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "npt_sit_time equal 500 #ps\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "npt_press equal 0.1 #GPa\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "room_sit_time equal 100 #ps\n"
        text += "\n"

        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "nvt_sit_timestep equal $(round(v_nvt_sit_time*1.0e-12/(dt*v_timestep)))\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "room_sit_timestep equal $(round(v_room_sit_time*1.0e-12/(dt*v_timestep)))\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "npt_sit_timestep equal $(round(v_npt_sit_time*1.0e-12/(dt*v_timestep)))\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "npt_press_correct equal $(v_npt_press*10000)\n"
        text += "variable".ljust(constants.LAMMPS_FILE_TAB) + "quench_timestep equal $(round((v_start_temp - v_end_temp)*1.0e-12/(dt*v_quench_rate*v_timestep)))\n"

        text += "\n"

        text += "minimize".ljust(constants.LAMMPS_FILE_TAB) + "1.0e-8 1.0e-8 100000 10000000\n"
        text += "velocity".ljust(constants.LAMMPS_FILE_TAB) + "all create ${start_temp} 12345\n"
        text += "\n"
        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "relax all nvt temp ${start_temp} ${start_temp} $(1000.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${nvt_sit_timestep}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "relax\n"
        text += "\n"
        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "npt_sit all npt temp ${start_temp} ${start_temp} $(100.0*dt) iso ${npt_press_correct} ${npt_press_correct} $(1000.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${npt_sit_timestep}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "npt_sit\n"
        text += "\n"
        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "quench all npt temp ${start_temp} ${end_temp} $(100.0*dt) iso 0 0 $(100.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${quench_timestep}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "quench\n"
        text += "\n"
        text += "fix".ljust(constants.LAMMPS_FILE_TAB) + "relax all npt temp ${end_temp} ${end_temp} $(1000.0*dt) iso 0 0 $(1000.0*dt)\n"
        text += "run".ljust(constants.LAMMPS_FILE_TAB) + "${room_sit_timestep}\n"
        text += "unfix".ljust(constants.LAMMPS_FILE_TAB) + "relax\n"
        text += "\n"
        text += "write_data".ljust(constants.LAMMPS_FILE_TAB) + "glass_" + "".join(self.SPECIES) + ".structure\n"


        lmp_file.write(text)

        lmp_file.close()

