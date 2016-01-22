#!/usr/bin/env python
import confy
import sys

confy.read_environment_file()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

