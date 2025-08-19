import os.path
import time
import docker
import docker.errors
import typer
import subprocess
import tkinter
import questionary
from questionary import Choice
from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Iterator, Annotated
from .utils import *
from .craft import container_craft
from .into import into_container

app = typer.Typer(invoke_without_command=True)
@app.callback()
def main_callback(ctx: typer.Context):
    """
    🚀 dker: A handy tool for docker user! 🐳
    """
    if not ctx.invoked_subcommand:
        print(ctx.get_help())

@app.command(name='craft', help='Craft container interactively')
def craft():
    container_craft()

def completion_into():
    containers = sorted(
        get_docker_client_or_quit().containers.list(all=True),
        key=lambda c: (c.name, c.status != 'running')
    )
    return [(c.name, c.status) for c in containers]

@app.command(name='into', help='Get into a container specified by name')
def into(
        name: str = typer.Argument(
            autocompletion=completion_into,
            help='Container name',
        ),
):
    into_container(name)

def main():
    try:
        app()
    except Exception as e:
        print('Error: {}'.format(e))
        exit(1)

if __name__ == '__main__':
    main()
