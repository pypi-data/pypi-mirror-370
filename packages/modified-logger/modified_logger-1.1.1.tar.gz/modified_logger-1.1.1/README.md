[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# README for the log module: (last updated 7/26/22)

## Purpose:
The purpose of the module is to provide an abstracted framework for logging that uses the python logging module. This module abstracts away so of the formatting of the logging module so that the code it is added to doesn't have to be verbose. This modules is mainly used in my personal projects and therefore the abstractions are what I find most useful. You may have to modify the code for other uses.

## Using this module:
Typically I just git clone this module into project as a submodule. You can use the command shown below:

```
git submodule add https://github.com/jtb324/log.git
```

If you don't care about having a separate git history than you could just use:

```
git clone https://github.com/jtb324/log.git
```

## Important Note about allowed log levels.
This script allows three log levels: "verbose", "debug", "warning". Others can add more values to this dictionary to customize other logging levels. This values are stored as keys in a dictionary where the values are the corresponding logging integers:

```
level_dict: dict[str, int] = {
    "verbose": logging.INFO,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
}
```

## Important functions.
**configure:**
```
def configure(
    logger: logging.Logger,
    output: str,
    filename: str = "IBDCluster.log",
    loglevel: str = "warning",
    to_console: bool = False,
) -> None:
```
This function abstracts away alot of the creation of the logger and the customization of the logger. The arguments are described below

* logger - This is the initizalized logger object. It has not yet been customized

* output - string that tells what directory the logger should be written to.

* filename - string that gives the name of the log file. This value defaults to IBDCluster.log

* loglevel - string that tells what you want the log level to be. Acceptable values are warning, verbose, debug

* to_console - boolean value where True means write to the stream handler and the file handler, while false means write to only a file and not the console.

* format_str - string value that tells the program how to format the log file

This function set the format for the log message to the filehandler as:

    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

If to_console is True then it sets the format for the streamhandler to be:

    "%(message)s"

This function also sets the loglevel to either the level provided by the user in the cli or it uses the logging.WARNING value of 30.

**create_logger:**

```
def create_logger(
    logger_name: str = "__main__",
) -> logging.Logger:
```

This function creates a logger. The only argument is the logger_name and defaults to "\_\_main__". It returns a Logger object from the logging library in the standard library. This function is only expected to be used in the main function.

**get_logger**

```
def get_logger(module_name: str, main_name: str = "__main__") -> logging.Logger:
```

This function abstracts away how the logging module gets the logger for the script. It can be used to get the main logger or child logger. The first argument is the module name to get the child logger and the second argument is the scripts name (This defaults to "\_\_main__" but the user can provide other names). The function returns a Logger object from the logging standard library.

**get_loglevel**

```
def get_loglevel(loglevel: str) -> int:
```

This function gets the loglevel being used. It takes the log level string as a parameter. This value should be either "verbose", "debug", or "warning". It will return an integer value corresponding to the loglevel

**record_inputs:**

```
record_inputs(logger, **kwargs) -> None:
```

This function is used to write out what the user provided arguments are to the logfile and/or the stream. This function takes the initialized logger object as the first argument and then it takes keyword arguments. 

*Example:*
```
# recording all the user inputs
    log.record_inputs(
        logger,
        ibd_program_used=ibd_program,
        output_path=output,
        environment_file=env_path,
        json_file=json_path,
        gene_info_file=gene_info_file,
        carrier_matrix=carriers,
        centimorgan_threshold=cm_threshold,
        loglevel=loglevel,
    )
```

