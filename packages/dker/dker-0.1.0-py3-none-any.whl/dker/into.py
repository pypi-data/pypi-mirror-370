import subprocess
from .utils import *


def into_container(name: str):
    if not name:
        return
    try:
        container = get_docker_client_or_quit().containers.get(name)
    except docker.errors.DockerException as e:
        print('Docker error: {}'.format(e))
        exit(1)
    if container.status != 'running':
        print('Container {} not running'.format(name))
        print('Restarting...')
        try:
            container.restart()
        except docker.errors.DockerException as e:
            print('Docker error: {}'.format(e))
            exit(1)
    subprocess.run('docker exec -it {} bash'.format(name), shell=True)
