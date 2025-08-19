"""
Main CLI application for Flexagg.

This module contains the main Typer application that will be registered
as the 'fa' command.
"""

from flexagg.loader import TyperLoader

app = TyperLoader().create_app()

if __name__ == "__main__":
    app()
