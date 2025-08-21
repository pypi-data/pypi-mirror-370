#!/usr/bin/env python3
# main.py

from qalita.cli import cli, add_commands_to_cli

add_commands_to_cli()

if __name__ == "__main__":
    cli()
