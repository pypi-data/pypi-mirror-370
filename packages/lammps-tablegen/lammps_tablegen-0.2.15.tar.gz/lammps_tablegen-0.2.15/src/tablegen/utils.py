import argparse
import sys

from . import constants

class SupportAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 default=False,
                 required=False,
                 help=None,
                 ):
        super(SupportAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=True,
            required=required,
            help=help,
            default=default)

    def __call__(self, parser, namespace, values, option_strings=None):
        setattr(namespace, self.dest, self.const)
        namespace.handler_class.display_support()
        parser.exit()

class StrictSubParsersAction(argparse._SubParsersAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser_name = values[0]
        arg_strings = values[1:]

        # set the parser name if requested
        if self.dest is not argparse.SUPPRESS:
            setattr(namespace, self.dest, parser_name)

        # select the parser
        try:
            subparser = self._name_parser_map[parser_name]
        except KeyError:
            args = {'parser_name': parser_name,
                    'choices': ', '.join(self._name_parser_map)}
            msg = _('unknown parser %(parser_name)r (choices: %(choices)s)') % args
            raise ArgumentError(self, msg)


        #Parse argse with error calls from subparser instead of delegating
        #unrecognized argument error to the main parser
        subnamespace = subparser.parse_args(arg_strings)
        for key, value in vars(subnamespace).items():
            setattr(namespace, key, value)



class NoMetavarHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def _get_default_metavar_for_optional(self, action):
        return ""

    def _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        return "%s" % get_metavar(1)


class ErrorHandlingParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def error(self, message):
        sys.stderr.write("\n\nERROR: %s\n\n" % message)
        self.print_help()
        sys.exit(2)

def format_min_dec(value, min_decimals):
    string = str(value)
    if "." not in string:
        return string + "." + "0" * min_decimals
    else:
        whole, dec = string.split(".")
        num_dec = len(dec)
        if num_dec >= min_decimals:
            return string
        else:
            return string + "0" * (min_decimals - num_decs)


def align_by_decimal(string, size, dec_pos):
    string = string.strip()

    if "." not in string:
        raise RuntimeError("ERROR: No decimal found in string. Cannot align")

    strlen = len(string)

    if size <= strlen:
        return string

    whole, dec = string.split(".")

    room_left = dec_pos - len(whole)
    room_right = size - dec_pos - 1 - len(dec)

    if room_left < 0:
        return string
    if room_right < 0:
        return string


    return " " * room_left + string + " " * room_right

def generate_filetext_3b(elements, tablename = "???", units = "???", timestep = "???", extra_pairstyle = ""):
    text = constants.GENERATION_COMMENT

    text += "\n\n#REQUIRED USER SPECIFIED DEFINITIONS\n\n"

    text += "#Determines what attributes atoms have\n"
    text += "atom_style".ljust(constants.LAMMPS_FILE_TAB) + "???\n"
    text += "boundary".ljust(constants.LAMMPS_FILE_TAB) + "??? ??? ???\n"

    text += "#Unit set determined by the potential\n"
    text += "units".ljust(constants.LAMMPS_FILE_TAB) + f"{units}\n"

    text += "#Defines initial atomic positions by providing a file\n"
    text += "read_data".ljust(constants.LAMMPS_FILE_TAB) + "???\n"

    text += "\n\n#REQUIRED SECTION\n\n"

    
    for i in range(len(elements)):
        if elements[i] in constants.ATOMIC_MASSES:
            text += "mass".ljust(constants.LAMMPS_FILE_TAB) + f"{i + 1} {constants.ATOMIC_MASSES[elements[i]]}\n"
        else:
            text += "mass".ljust(constants.LAMMPS_FILE_TAB) + f"{i + 1} ???\n"

    text += "\n\n"
    
    text += "pair_style".ljust(constants.LAMMPS_FILE_TAB) + f"hybrid/overlay threebody/table " + extra_pairstyle + "\n\n"

    text += "pair_coeff".ljust(constants.LAMMPS_FILE_TAB) +f"* * threebody/table {tablename} " + " ".join(elements) + "\n"

    text += "\n\n#USEFUL DEFINITIONS\n\n"
    for i in range(len(elements)):
        text += "group".ljust(constants.LAMMPS_FILE_TAB) + f"{elements[i]} type {i + 1}\n"

    return text
    

def generate_filetext_2b(elements, pairs, datapoints, tablename, cutoff, units, timestep = "???", extra_pairstyle = ""):
    text = constants.GENERATION_COMMENT

    text += "\n\n#REQUIRED USER SPECIFIED DEFINITIONS\n\n"

    text += "#Determines what attributes atoms have\n"
    text += "atom_style".ljust(constants.LAMMPS_FILE_TAB) + "???\n"
    text += "boundary".ljust(constants.LAMMPS_FILE_TAB) + "??? ??? ???\n"

    text += "#Unit set determined by the potential\n"
    text += "units".ljust(constants.LAMMPS_FILE_TAB) + f"{units}\n"

    text += "#Defines initial atomic positions by providing a file\n"
    text += "read_data".ljust(constants.LAMMPS_FILE_TAB) + "???\n"

    text += "\n\n#REQUIRED SECTION\n\n"

    
    for i in range(len(elements)):
        if elements[i] in constants.ATOMIC_MASSES:
            text += "mass".ljust(constants.LAMMPS_FILE_TAB) + f"{i + 1} {constants.ATOMIC_MASSES[elements[i]]}\n"
        else:
            text += "mass".ljust(constants.LAMMPS_FILE_TAB) + f"{i + 1} ???\n"

    text += "\n\n"
    
    text += "pair_style".ljust(constants.LAMMPS_FILE_TAB) + f"hybrid/overlay table linear {datapoints} " + extra_pairstyle + "\n\n"
    

    for pair in pairs:
        if "-" in pair:
            elem1, elem2 = pair.split("-")
        else:
            raise RuntimeError("ERROR: Each atomic pair should consist of two atoms separated by a dash.")

        text += "pair_coeff".ljust(constants.LAMMPS_FILE_TAB) +f"{elements.index(elem1) + 1} {elements.index(elem2) + 1} table {tablename} {pair} {cutoff}\n"

    text += "\n"
    text += "timestep".ljust(constants.LAMMPS_FILE_TAB) + f"{timestep}\n"

    text += "\n\n#USEFUL DEFINITIONS\n\n"
    for i in range(len(elements)):
        text += "group".ljust(constants.LAMMPS_FILE_TAB) + f"{elements[i]} type {i + 1}\n"






    return text
