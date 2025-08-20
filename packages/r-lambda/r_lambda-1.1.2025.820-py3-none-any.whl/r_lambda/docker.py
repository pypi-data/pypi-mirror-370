import os
import platform

# --shm-size=512m

def docker_image(id, volumn=[], name=None, tty = False, shm_size=None, host_net = False):
    """
    A helper function to generate configuration for Docker run arguments.

    Parameters:
    id (str):               Required. The Docker image ID or name to run.
    volumn (List[str]):     Optional. List of host paths to mount into the container. Each path will be
                            mounted to the same path inside the container. Default is empty list.
    name (str):             Optional. Name to assign to the container. If None, Docker will assign a random name.
    tty (bool):             Optional. Allocate a pseudo-TTY. Useful for interactive sessions. Default is False.
    shm_size (str):         Optional. Size of /dev/shm (e.g., '512m'). Overrides Docker's default 64MB allocation.

    Returns:
    dict: A dictionary containing Docker configuration parameters for building the 'docker run' command,
          including image ID, volume mounts, container name, TTY allocation, and shared memory size.
    """

    return {"image": id, "volumn": volumn, "name": name,
            "tty": tty,
            "host_net": host_net,
            "shm_size": shm_size}


def mount_volumn(docker_run, argv, workdir, docker_config):
    """
    Constructs volume mount arguments and configures the working directory for a Docker container.

    Processes volume mounts from both the Docker configuration and function arguments. Host paths are
    mounted to identical container paths. Adds standard mounts for Docker socket, CLI tool, and /tmp.

    Parameters:
    docker_run (List[str]): List to accumulate 'docker run' command-line arguments. Modified in-place.
    argv (dict):            Dictionary of function arguments. May contain file paths referenced in
                            'docker_config["volumn"]' entries.
    workdir (str):          Host working directory path. Mounted as the container's working directory.
    docker_config (dict):   Docker configuration from docker_image(), containing 'volumn' list and other params.

    Returns:
    List[str]: Updated docker_run list with volume mount arguments (-v), working directory (-w), and
               standard Docker mounts. The list is modified in-place and returned for chaining.
    """

    docker = "docker"

    # config for run commandline test on windows
    if platform.system() != "Windows":
        docker = os.popen("which docker").read().strip()

    workspace = os.path.abspath(workdir)

    # Add standard Docker mounts
    docker_run.append("-v /var/run/docker.sock:/run/docker.sock")
    docker_run.append('-v "{0}:/bin/docker"'.format(docker))
    docker_run.append('-v "/tmp:/tmp"')

    # Process volume mounts from docker_config
    if not docker_config["volumn"] is None:
        for arg in docker_config["volumn"]:
            if arg in argv:
                # mount volumn from the function argument
                vol = os.path.abspath(argv[arg])
                print("[mount] argv.{} -> {}".format(arg, vol))
            else:
                # mount volumn from the docker volumn property
                vol = os.path.abspath(arg)
                print("[mount] {} -> {}".format(arg, vol))

            # Same host/container path
            docker_run.append('-v "{0}:{0}"'.format(vol))

    # Set container working directory
    docker_run.append('-w "{0}"'.format(workspace))

    return docker_run
