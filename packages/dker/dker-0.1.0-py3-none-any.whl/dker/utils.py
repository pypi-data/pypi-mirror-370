import docker
import docker.errors

def get_docker_client_or_quit():
    try:
        client = docker.from_env(timeout=5)
        client.ping()
        return client
    except docker.errors.DockerException as e:
        print('Docker error: {}'.format(e))
        exit(1)
