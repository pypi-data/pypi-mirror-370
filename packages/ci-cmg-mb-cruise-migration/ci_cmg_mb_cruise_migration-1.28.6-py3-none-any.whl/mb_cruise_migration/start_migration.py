import sys
from mb_cruise_migration.migrator import Migrator

if __name__ == '__main__':

    config = "config.yaml"
    arguments = sys.argv
    num_args = len(arguments)

    if num_args > 1:
        if num_args != 2:
            raise RuntimeError("Too many arguments. Usage: `python run_migration.py <config_file>`")
        config = sys.argv[1]

    migrator = Migrator(config)
    migrator.migrate()
