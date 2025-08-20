# Run ``R#`` lambda function in python workflow

## Overview

This package enables seamless execution of R# lambda functions within Python workflows, supporting both local and Docker containerized environments. It handles configuration serialization, execution environment setup, and cross-platform compatibility.

## Key Features
​
+ Multi-Environment Execution​

  - Local Execution: Direct execution via .NET R# runtime
​  - Docker Execution: Containerized runs with automatic volume management

+ ​Automatic Configuration​

  - Parameter serialization to ``.r_env/run.json``
  - Runtime options serialization to ``.r_env/options.json``

+ Unified Interface​

  - Consistent API for local and containerized execution
  - Support for both dictionary and CLI-style arguments

## Installation

```bash
pip install r-lambda
```
​
### System Requirements:

+ Python ≥3.8
+ .NET Runtime (for local execution)
+ Docker Engine (for containerized execution)

## Core Concepts

### Introduce the ``R#`` lambda

The ``R#`` lambda function is a kind of shell feature function in R# script host. Assuming that there is a function named ``hello_world`` in a ``R#`` package which is named ``demo``, so that we could run this hello world function in R# script file:

```r
# In package "demo"
# function inside package namespace: demo 
const hello_world = function(str) {
    print(`hello: ${str}!`);
}

# call function in another script file
demo::hello_world("world");
```

Via the ``R#`` lambda function feature, that we could run this function without write script file, and we could run this function from commandline directly, example as:

```bash
# call function via R# lambda
Rscript --lambda demo::hello_world
```

and the parameter value of hello world function will be setup via a runtime json file ``./.r_env/run.json`` in the working directory:

```json
{
    "str": "world" 
}
```

If the function invoke contains ``getOption`` function calls, then you could setup the runtime environment via the json file ``./.r_env/options.json`` in the working directory:

```json
{
    "example-var": "1234"
}
```

So, you could get such environment variable value in R# runtime environment by ``getOption``:

```r
print(getOption("example-var"));
# [1] "1234"
```

### Configuration Files

| File                | Purpose                      | Generated From   |
|---------------------|------------------------------|------------------|
| .r_env/run.json     | Function parameters          | argv argument    |
| .r_env/options.json | Runtime environment settings | options argument |

## API Reference

```
call_lambda(func, ​**kwargs)
```
​
### Parameters:

| Parameter | Type      | Description                                    | Default   |
|-----------|-----------|------------------------------------------------|-----------|
| func      | str       | R# function in ``package::function`` format    | ​Required   |
| argv      | dict/list | Function parameters                            | ``{}``    |
| options   | dict      | Runtime configuration for ``getOption()``      | ``{}``    |
| workdir   | str       | Execution working directory                    | ``"./"``  |
| docker    | dict      | Docker configuration (from ``docker_image()``) | ``None``  |
| run_debug | bool      | Dry-run mode (no execution)                    | ``False`` |

## Call R# lambda from a python workflow

For call a R# lambda function from your python workflow, then you could use this python package function. Current package call the R# workflow function running in local machine or running in a docker container already been wrapped into function calls, so that you can call such hello world function in ``R#`` package in python, example like:

```py
import r_lambda
from r_lambda.docker import docker_image

r_lambda.call_lambda("demo::hello_world", 
argv = {"str": "world"}, 
    options = None,
    workdir = "./",
    docker = docker_image(id = "example_image", 
        volumn = ["/home"], name = "test"), 
    run_debug = False
)
```

### Usage Examples

#### Basic Local Execution

```python
from r_lambda import call_lambda

call_lambda(
    func="demo::hello_world",
    argv={"str": "world"},  # Dictionary-style arguments
    options={"verbose": True},
    workdir="./analysis"
)
```

#### CLI-Style Arguments

```python
call_lambda(
    "stats::calculate",
    argv=["--input", "data.csv", "--threshold", "0.05"],  # CLI-style arguments
    options={"parallel": True}
)
```

#### Docker Execution

```python
from r_lambda import call_lambda, docker_image

docker_config = docker_image(
    id="rsharp/runtime:3.2",
    volumn=["/data/inputs", "/data/outputs"],  # Absolute paths required
    shm_size="2g",
    name="analysis_container"
)

call_lambda(
    func="preprocess::clean_data",
    argv={"input_dir": "/data/inputs", "output_dir": "/data/outputs"},
    docker=docker_config
)
```

#### Advanced Configuration

##### Volume Mounting

The package automatically handles:

+ Docker socket mounting (``/var/run/docker.sock``)
+ ``/tmp`` directory sharing
+ Argument-specified volumes from ``docker_image()``
​
Example Mount:

```python
docker_image(
    id="rsharp/runtime:3.2",
    volumn=["/host/path"],  # Mounts to /host/path in container
    ...
)
```

##### Runtime Options

Configure environment variables accessible via ``getOption()`` in R#:

```python
options = {
    "max_memory": "16G",
    "temp_dir": "/tmp/rsharp",
    "threads": 8
}
```

#### Debugging & Testing

##### Dry-run Mode

```python
call_lambda(
    func="demo::test",
    run_debug=True  # Prints command without execution
)
```

​Sample Output:

```markdown
[DEBUG] Generated command:
docker run -v /data:/data ... rsharp/runtime:3.2 dotnet Rscript.dll --lambda demo::test
```

#### Configuration Inspection

Check generated files in ``workdir/.r_env``:

+ ``run.json``: Serialized argv parameters
+ ``options.json``: Serialized runtime configuration

### Best Practices
​
1. Path Handling​

  + Use absolute paths for Docker volumes
  + Avoid spaces in directory names
  + Windows: Use raw strings for paths (``"C:\data"``)

​2. Resource Allocation​

  + Set shm_size for memory-intensive tasks
  + Configure thread limits in options

​3. Container Management​

  + Reuse containers for sequential calls
  + Clean up temporary containers with --rm flag

#### Error Handling
​
Common Exit Codes:

| Code | Description                |
|------|----------------------------|
| 0    | Success                    |
| 127  | R# runtime not found       |
| 139  | Memory allocation error    |
| 255  | Invalid function signature |

## License & Support

MIT License. Report issues at [GitHub Repo](https://github.com/rsharp-lang/IronR).