class BASE2B():
    SUPPORT_SPACING = 3
    TWO_BODY = True

    def __init__(self):
        pass

    def get_table_name(self):
        return "TABLE.table"

    def get_cutoff(self):
        return 0

    def get_datapoints(self):
        return 0

    def get_pairs(self):
        return []

    def eval_force(self, pair_name, r):
        return 0

    def eval_pot(self, pair_name, r):
        return 0

    def to_plot(self):
        return []

    def comment_message_call(self):
        return

    def is_2b(self):
        return self.TWO_BODY

    def lammps_file_needed(self):
        return False

    @staticmethod
    def display_support():
        print("NO SUPPORT MESSAGE IMPLEMENTED")

class BASE3B():
    SUPPORT_SPACING = 3
    TWO_BODY = False

    def __init__(self):
        self.SYMMETRIC = False

    def get_table_name(self):
        return "TABLE.table"

    def get_cutoff(self):
        return 0

    def get_datapoints(self):
        return 0

    def is_symmetric(self):
        return self.SYMMETRIC

    def eval_force(self, spec1, spec2, r):
        return 0

    def eval_pot(self, spec1, spec2, r):
        return 0

    def to_plot(self):
        return []

    def no_spec_msg(self, spec1, spec2):
        return ""

    def is_2b(self):
        return self.TWO_BODY

    def get_all_atom_combos(self):
        return []

    def get_triplets(self):
        return []

    @staticmethod
    def display_support():
        print("NO SUPPORT MESSAGE IMPLEMENTED")
