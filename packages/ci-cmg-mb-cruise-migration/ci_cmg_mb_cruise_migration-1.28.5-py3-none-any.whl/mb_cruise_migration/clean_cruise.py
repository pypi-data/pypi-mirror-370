import sys

from mb_cruise_migration.cleaner import Cleaner

if __name__ == '__main__':

    config = "config.yaml"
    arguments = sys.argv
    num_args = len(arguments)

    if num_args > 1:
        if num_args != 2:
            raise RuntimeError("Too many arguments. Usage: `python clean_cruise.py <config_file>`")
        config = sys.argv[1]

    cleaner = Cleaner(config)
    cleaner.delete_multibeam_data_from_cruise()
