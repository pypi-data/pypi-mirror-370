![Moore.io Client Logo](https://mooreio.com/logo.png)

[![PyPI](https://img.shields.io/pypi/v/mooreio_client?label=pypi%20package)](https://pypi.org/project/mooreio-client/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mooreio_client)](https://pypi.org/project/mooreio-client/#files)
[![Documentation Status](https://readthedocs.org/projects/mooreio-client/badge/?version=latest)](https://mooreio-client.readthedocs.io/en/latest/?badge=latest)

# Moore.io Client

The Moore.io Client is an open-source CLI tool designed to automate Electronic Design Automation (EDA) tasks encountered
during the development of ASIC, FPGA and UVM IP. This tool also serves as a client for the Moore.io Web Site
(https://mooreio.com), providing functionalities such as installing IP dependencies, generating UVM code and
packaging/publishing IPs.

## Why?
The EDA (Electronic Design Automation) field clearly lags behind in terms of Free & Open-Source (FOS) developer tools
when compared to the software world. There is no FOS tool that can drive the various CAD software necessary and provide
the kind of automation needed to produce commercial-grade FPGA and ASIC designs. Instead, homebrew (and seldom shared)
Makefiles and Shell scripts rule the field of DevOps in semiconductors.

### The Problem
Writing a Makefile/Shell script that can perform all the tasks required to create a Chip Design is a LARGE job. Since
these languages do not come with any meaningful libraries, the end result is a mess of patched, brittle code painful to
maintain/debug, yet on which every engineering task directly depends. These issues are usually compounded by
copying the project Makefile/Shell script from project to project; thus losing all Git history while commenting
out old code and adding to the mess.

Surely, there must be a better way ...

### The Solution
The Moore.io Client is a FOS Command Line Interface (CLI) tool implemented in Python 3, using Object-Oriented
Practices, strong typing, unit testing, and a modular architecture that will be very familiar to UVM engineers: the
primary target audience of this tool. The Client, invoked via `mio`, has all the features you would expect from a
"Project Makefile" at a high-end Semiconductor engineering firm AND all the best features from Software package
managers:

 * The concept of a Project, which is identified by a `mio.toml` file in its root directory
 * A layered Configuration Space defined with TOML files (`mio.toml`) at the user (`~/.mio/mio.toml`) and project levels
 * Packaging of HDL source file into IPs (Intellectual Property) identified by `ip.yml` descriptors in their root directory
 * Performing tasks at the IP-level, including generating code, specifying and installing dependencies
 * Ability to drive all Logic Simulators (DSim, Vivado, (soon: Questa, VCS, XCelium & Riviera-PRO)) with a single set of commands and parameters
 * A feature-driven Test Suite schema for specifying Regressions in UVM Test Benches, AND the ability to run these Regressions on Job Schedulers (LSF, GRID, etc.)
 * Built-in compatibility with Continuous Integration (CI) tools like Jenkins

## How much does it cost?
The EDA Automation and Package management is Free & Open-Source. Some commands, such as UVM Code Generation, "phone
home" to the Moore.io Server and therefore require a User Account (which can be created at
https://mooreio.com/register) and a license for Datum UVMx. However, the tool operates independently of the site in all
other regards and can be used without authentication to build a Chip from start to finish. 


## Installation

You can install `mio` via `pip`:

```sh
pip install mooreio_client
```

## Usage

```sh
mio <command> [<args>]
mio help <command>
```

For complete list of commands and options, you can use:

```sh
mio --help
```

For quick reference on a specific command:

```sh
mio help <command>
```

## Documentation

Comprehensive documentation is available on [Read the Docs](http://mooreio-client.rtfd.io/).

## Development

### Architecture
The Design Pattern for the Moore.io Client mimics UVM's phases and component structure. A RootManager (RM) class instance
is created by the CLI argument parser and given a Command instance to execute. The RM operates in 3 steps:

1. Discovery: finding the project file, loading/validating the configuration space and finding/loading IP files
2. Main: RM gives control to the Command which invokes Service(s) (simulators, synthesizers, etc.) to perform Task(s) (compilation, simulation, etc.) via a JobScheduler instance (SubProcess, LSF, GRID) which accepts Jobs (shell commands) 
3. Post: RM and Command parse results, generate reports, clean up files, close sockets, stop processes and print out final notes to the user  

Each step is broken up into phases, with each phase having a 'pre' and 'post' phase associated to it:

* The Discovery step is handled by the RM; the Command can participate via pre/post phase hooks
* During the Main phase, control shifts to the Command, which has a selection of Service tasks and JobSchedulers with which to run them
* The post step is shared between the RM and the Command

Each phase method has a Phase instance parameter that can be used to end the program arbitrarily and/or report errors to the RM.

Commands are discovered by `cli.py` and must append their CLI argument subparser to the main `argparse` instance.
If the user selects the command, an instance is created, fed to the RM and execution begins via `RM.run()`.

Errors are handled via the `raise` of Python Exceptions. The RM catches these and exits with the appropriate error message and return code.


### Requirements

- Python 3.11.4
- `pip` package manager
- `make` utility (for convenience in development and CI)

### Setup

0. Print Makefile User Manual:
    ```sh
    make help
    ```

1. Clone the repository:
    ```sh
    git clone https://github.com/Datum-Technology-Corporation/mooreio_client.git
    cd mooreio_client
    ```
   
2. Run 'core' tests (do not require external software):
    ```sh
    make test-core
    ```
   Test reports, including code coverage, are output under ``./reports``

3. (Optional) Run tests that require simulator license(s):
    ```sh
    make test-dsim
    make test-vivado
    ```

4. Lint codebase:
    ```sh
    make lint
    ```
   Linting reports are output under ``./reports``

5. Build documentation:
    ```sh
    make docs
    ```
   The HTML is output under ``./docs/build``

6. Build package:
    ```sh
    make build
    ```

## Continuous Integration

### Supported Continuous Integration Tools
- Jenkins

## Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- Official site: [www.mooreio.com](http://www.mooreio.com)
- Copyright Holder: [Datum Technology Corporation](http://www.datumtc.ca)