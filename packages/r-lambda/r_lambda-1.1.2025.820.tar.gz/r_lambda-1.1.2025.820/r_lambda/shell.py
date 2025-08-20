import os

from r_lambda import docker
from abc import ABC, abstractmethod


class shell(ABC):
    """Abstract base class for executing R# lambda functions in different environments
    
    Attributes:
        argv (list): CLI arguments passed to the script
        options (dict): Configuration options for runtime
        workdir (str): Target working directory path
    """
        
    def __init__(self, argv, options, workdir):
        """Initialize shell executor
        
        Args:
            argv (list): Command line arguments
            options (dict): Runtime configuration options
            workdir (str): Working directory path
        """
                
        self.argv = argv
        self.options = options
        self.workdir = workdir

    @abstractmethod
    def commandline(self, func):
        """Generate command line string for executing R# lambda function
        
        Args:
            func (str): Target R# lambda function name
            
        Returns:
            str: Complete command line string
        """
        pass

    def call_lambda(self, func, run_debug=False):
        """Execute the generated command line
        
        Args:
            func (str): Target R# lambda function name
            run_debug (bool): Debug mode flag. If True, skips actual execution
            
        Returns:
            int: Exit code of the shell command
        """
                
        print(" -> r_lambda: {}".format(func))
        print("")

        shell = 0
        shell_command = self.commandline(func)

        print("")
        print("Run shell commandline:")
        print(shell_command)
        print(" ------- start -------")
        print("")

        if not run_debug:
            shell = os.system(shell_command)
        else:
            print("[debug] skip of run shell command for debug test!")

        print("[pipeline_done] run R# lambda job done!")
        print("exit={0}".format(shell))
        print("")

        return shell


class local_shell(shell):
    """Concrete executor for running R# lambda functions in local environment"""

    def __init__(self, argv, options, workdir):
        """Initialize local shell executor
        
        Args: See base class
        """

        super().__init__(argv, options, workdir)

    def commandline(self, func):
        """Build local execution command line using dotnet Rscript
        
        Args:
            func (str): Target R# lambda function name
            
        Returns:
            str: Formatted dotnet command string
        """

        # run rscript command
        # Rscript host executable
        RSCRIPT_HOST = "/usr/local/bin/Rscript.dll"
        # Lambda specific args
        RSCRIPT_LAMBDA = "--lambda {} --SetDllDirectory /usr/local/bin/".format(func)

        shell = []
        shell.append("dotnet")
        shell.append(RSCRIPT_HOST)
        shell.append(RSCRIPT_LAMBDA)

        return " ".join(shell)

    def call_lambda(self, func, run_debug=False):
        """Execute command in target working directory
        
        Args: See base class
        
        Returns:
            int: Exit code from base class execution
        """
                
        pwd = os.getcwd()
        os.chdir(self.workdir)
        exitcode = super().call_lambda(func, run_debug=run_debug)
        os.chdir(pwd)

        return exitcode


class docker_run(shell):
    """Docker-based executor for running R# lambda functions in containerized environment
    
    Attributes:
        docker (dict): Docker configuration parameters
        local (local_shell): Local executor instance for command generation
    """

    def __init__(self, argv, options, docker, workdir):
        """Initialize docker executor
        
        Args:
            docker_config (dict): Docker settings including:
                - image (str): Docker image ID
                - shm_size (str): Shared memory size (e.g., '2g')
                - name (str): Container name
                - tty (bool): Allocate pseudo-TTY
            Other args: See base class
        """
                
        self.docker = docker
        self.local = local_shell(argv, options, workdir)

        super().__init__(argv, options, workdir)

    def commandline(self, func):
        """Build docker run command with volume mounts and parameters
        
        Args:
            func (str): Target R# lambda function name
            
        Returns:
            str: Complete docker run command string
        """
                
        image_id = self.docker["image"]

        run_pipeline = []
        run_pipeline.append("docker run --rm -e WINEDEBUG=-all")

        if not self.docker["shm_size"] is None:
            run_pipeline.append('--shm-size={}'.format(self.docker["shm_size"]))

        if not self.docker["name"] is None:
            run_pipeline.append('--name "{}"'.format(self.docker["name"]))

        if not self.docker["tty"] is None:
            if self.docker["tty"]:
                run_pipeline.append('-it')

        if not self.docker["host_net"] is None:
            if self.docker["host_net"]:
                run_pipeline.append("--net=host")

        run_pipeline = docker.mount_volumn(
            docker_run=run_pipeline,
            argv=self.argv,
            workdir=self.workdir,
            docker_config=self.docker,
        )
        run_pipeline.append("--privileged=true")
        run_pipeline.append(image_id)
        run_pipeline.append(self.local.commandline(func))

        return " ".join(run_pipeline)
