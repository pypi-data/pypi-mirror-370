import json
import os

def save_configs(argv, options, workdir):
    """Save R# runtime configuration files to the specified working directory.

    This function serializes function parameters and runtime configurations into JSON format,
    storing them in a dedicated '.r_env' subdirectory. The generated files are used to configure
    the R# execution environment.

    Args:
        argv (list): A list of parameters/arguments for the target R# function to be invoked.
            Typically contains command-line arguments and parameter values in list format.
        options (dict): Configuration dictionary for the R# runtime environment. 
            Contains settings like package paths, environment variables, and execution options.
        workdir (str): Absolute or relative path to the working directory where configuration
            files will be stored. The directory will be created if it doesn't exist.

    Returns:
        list: Returns the input argv parameter list unchanged for potential downstream processing.

    Side Effects:
        - Creates a '.r_env' subdirectory in the specified workdir
        - Generates two JSON files in the subdirectory:
            * run.json: Contains serialized function parameters from argv
            * options.json: Contains serialized runtime configurations from options
        - Prints runtime environment setup information to stdout

    Example:
        >>> save_configs(
            argv = ["--input", "data.csv", "--threshold", "0.05"],
            options = {"lang": "R#", "debug": True},
            workdir = "./analysis"
        )
        # Creates ./analysis/.r_env/run.json and options.json
    """

    print(
        "*************** setup the R-sharp runtime environment variables *****************"
    )
    print("")
    print("view of your input parameters:")
    print(argv)
    print("config of the R-sharp runtime environment:")
    print(options)

    # Serializing json and setup Rscript envrionment variables
    # at current workspace
    argv_str = json.dumps(argv, indent=2)
    pwd = os.path.abspath(workdir)
    r_env = os.path.join(pwd, ".r_env")

    print("runtime files will be export to location:")
    print(r_env)

    if not os.path.exists(r_env):
        os.makedirs(r_env)

    jsonfile = open("{}/.r_env/run.json".format(pwd), "w")
    jsonfile.write(argv_str)
    jsonfile.close()

    argv_str = json.dumps(options, indent=2)

    jsonfile = open("{}/.r_env/options.json".format(pwd), "w")
    jsonfile.write(argv_str)
    jsonfile.close()

    print("")
    print("*******************  end of runtime environment setup  ***********************")
    print("")

    return argv
