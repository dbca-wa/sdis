#!/usr/bin/env python
import sys
import confy

confy.read_environment_file(envfile=".env")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
