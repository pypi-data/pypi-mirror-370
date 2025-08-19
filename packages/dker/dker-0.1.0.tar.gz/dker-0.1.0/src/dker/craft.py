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


class ContainerGeneralFunctionalities(BaseModel):
    class Unit(BaseModel):
        name: str
        enabled: bool = False
        description: str = ''
        command: str

    def __iter__(self) -> Iterator[Unit]:
        for field_name in ContainerGeneralFunctionalities.model_fields.keys():
            yield getattr(self, field_name)

    interactive: Unit = Unit(
        name='interactive',
        description='Keep STDIN open even if not attached',
        command='-i',
    )

    tty: Unit = Unit(
        name='tty',
        description='Allocate a pseudo-TTY',
        command='-t',
    )

    detach: Unit = Unit(
        name='detach',
        description='Run container in background and print container ID',
        command='-d',
    )

    privileged: Unit = Unit(
        name='privileged',
        description='Give extended privileges to this container',
        command='--privileged',
    )

    restart: Unit = Unit(
        name='restart',
        description='Restart always when a container exits',
        command='--restart always',
    )

    net_host: Unit = Unit(
        name='net_host',
        description='Connect to host network',
        command='--network host',
    )

    ipc_host: Unit = Unit(
        name='ipc host',
        description='IPC host mode',
        command='--ipc host',
    )

    display: Unit = Unit(
        name='display',
        description='Display gui apps with "xhost +"',
        command='-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw',
    )

    igpu_support: Unit = Unit(
        name='iGPU support',
        description='Enable integrated GPU',
        command='-v /dev/dri:/dev/dri',
    )

    nvidia_support: Unit = Unit(
        name='nvidia support',
        description='Enable NVIDIA capabilities in container',
        command='--gpus all --runtime=nvidia -e NVIDIA_DRIVER_CAPABILITIES=all',
    )

    map_input_device: Unit = Unit(
        name='map input device',
        description='Map input device to host device',
        command='-v /dev/input:/dev/input',
    )

    map_all_device: Unit = Unit(
        name='map all device',
        description='Map all device to host device',
        command='-v /dev:/dev',
    )

    timelink: Unit = Unit(
        name='timelink',
        description='Use host time',
        command='-v /etc/localtime:/etc/localtime:ro',
    )

    remove: Unit = Unit(
        name='remove',
        description='Automatically remove the container and its associated anonymous volumes when it exits',
        command='--rm',
    )

    map_autonomous_dir: Unit = Unit(
        name='map autonomous directory',
        description='Map autonomous directory in host home to container home',
        command='-v ~/autonomous:/root/autonomous',
    )

    map_host_home: Unit = Unit(
        name='map host home',
        description='Map host home into container',
        command='-v ~:/root/host_home',
    )

class ContainerOptions(BaseModel):
    image_name: str = Field(min_length=1)
    container_functionalities: list[ContainerGeneralFunctionalities.Unit]
    container_addon_options: Optional[str] = None
    container_name: Optional[str] = None
    container_command: Optional[str] = None

    @property
    def command(self):
        command_parts = ['docker run']
        for f in self.container_functionalities:
            command_parts.append(f.command)
        if self.container_addon_options is not None and len(self.container_addon_options) > 0:
            command_parts.append(self.container_addon_options)
        if self.container_name is not None and len(self.container_name) > 0:
            command_parts.append('--name')
            command_parts.append(self.container_name)
        command_parts.append(self.image_name)
        if self.container_command is not None and len(self.container_command) > 0:
            command_parts.append(self.container_command)
        command_parts = [c.strip() for c in command_parts]
        return ' '.join(command_parts)


def question_image_name():
    client = get_docker_client_or_quit()
    images = client.images.list()
    images_tags = [tag for image in images for tag in image.tags]
    custom_input = 'No choice, enter the image next!'
    if (selected_image := questionary.select(
        'Select an image to use:',
        choices=images_tags + [questionary.Separator(), custom_input],
    ).ask()) is None:
        exit(1)
    if selected_image != custom_input:
        return selected_image
    if (selected_image := questionary.autocomplete(
        'Input the image name you want to use:',
        choices=images_tags,
        validate=lambda value: True if len(value.strip()) > 0 else 'name cannot be empty',
    ).ask()) is None:
        exit(1)
    return selected_image

def question_container_functionalities(functionalities: ContainerGeneralFunctionalities):
    if (selected_functionalities := questionary.checkbox(
        'Select functionalities:',
        choices=[
            Choice(
                title=f.name,
                value=f,
                checked=f.enabled,
            )
            for f in functionalities
        ],
    ).ask()) is None:
        exit(1)
    return selected_functionalities

def question_container_addon_options():
    if (result := questionary.text('Input if any other container options you want to add or leave empty:').ask()) is None:
        exit(1)
    return result.strip()

def question_container_name():
    if (result := questionary.text('Input container name or leave empty for random:').ask()) is None:
        exit(1)
    return result.strip().replace(' ', '_')

def question_container_command():
    if (result := questionary.text(
        'Input container command or leave empty:',
        default='bash',
    ).ask()) is None:
        exit(1)
    return result.strip()

def run_command(command: str):
    result = subprocess.run(command.replace('~', os.path.expanduser('~')), shell=True)
    if result.returncode == 0 and result.stdout is not None:
        print(result.stdout)
    elif result.stderr is not None:
        print(result.stderr)

def copy_command(command: str):
    root = tkinter.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(command)
    root.update()
    time.sleep(0.05)
    root.destroy()
    print('Copied command: \n{}'.format(command))

def question_craft(command: Annotated[str, StringConstraints(min_length=1)]):
    print('The craft container command as follows:')
    print('---')
    print(command)
    print('---')
    run_choice = 'run the command'
    copy_choice = 'copy the command'
    if (choice := questionary.select(
        'Select a way to handle the command:',
        choices=[run_choice, copy_choice, questionary.Separator(), 'Exit'],
    ).ask()) is None:
        exit(1)
    if choice == run_choice:
        run_command(command)
    if choice == copy_choice:
        copy_command(command)

def container_craft():
    container_functionalities = ContainerGeneralFunctionalities()
    container_functionalities.interactive.enabled = True
    container_functionalities.tty.enabled = True
    container_functionalities.detach.enabled = True
    container_functionalities.privileged.enabled = True
    container_functionalities.restart.enabled = True
    container_functionalities.net_host.enabled = True
    container_functionalities.ipc_host.enabled = True
    container_functionalities.display.enabled = True
    container_functionalities.igpu_support.enabled = False
    container_functionalities.nvidia_support.enabled = True
    container_functionalities.map_input_device.enabled = True
    container_functionalities.map_all_device.enabled = False
    container_functionalities.timelink.enabled = True
    container_functionalities.remove.enabled = False
    container_functionalities.map_autonomous_dir.enabled = True
    container_functionalities.map_host_home.enabled = True

    try:
        question_craft(
            ContainerOptions(
                image_name=question_image_name(),
                container_functionalities=question_container_functionalities(container_functionalities),
                container_addon_options=question_container_addon_options(),
                container_name=question_container_name(),
                container_command=question_container_command(),
            ).command
        )
    except KeyboardInterrupt:
        exit(1)
