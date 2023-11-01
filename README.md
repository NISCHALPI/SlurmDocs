[![Static Badge](https://img.shields.io/badge/PyPI-v1.0.0-purple)](https://pypi.org/project/convinence-torch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-v3.4.3-blue)](https://matplotlib.org/)


# SlurmDocs: Automated Slurm Cluster Documentation
<img src="./extra/SlurmDocs.png" alt="SlurmDocs Logo" width="600" height='600'/>

**SlurmDocs** is a Python package and CLI tool designed to streamline the process of documenting Slurm clusters. Whether you're managing a small research cluster or a large-scale HPC system, SlurmDocs automates the documentation process, saving you time and ensuring your cluster information is always up-to-date.

## Features

- **Automated tflops Calculation and Visualization:** SlurmDocs can automatically calculate and visualize tflops (floating-point operations per second), providing valuable insights into your cluster's computational performance.

- **Comprehensive Node Hardware Database:** SlurmDocs creates a database of node hardware compute resources, including detailed CPU and GPU information. This data can be easily exported to formats such as CSV and SQL, and it's conveniently viewable with Pandas for in-depth analysis.

- **Reliable and Well-Documented API:** SlurmDocs offers a robust and well-documented API for programmatic usage, as well as a user-friendly command-line interface (CLI).

- **Cluster Configuration Overview:** SlurmDocs provides an overview of your cluster's configuration, partitions, and nodes, giving you a clear understanding of its current state.

- **One-Command Sync:** Keep your documentation in sync with the current cluster state with a single command, ensuring that your documentation is always up-to-date.

- **Export to Various Formats:** SlurmDocs supports exporting your documentation to various formats, including HTML, PDF, and CSV, making it easy to share and present information about your Slurm cluster.

## Installation

You can install SlurmDocs using `pip`:

```bash
pip install slurmdocs
```
## Usage
SlurmDocs is most easily used as a CLI tool. The `slurmdocs` command can be invoked after installation with the following options:
```bash
Usage: slurmdocs [OPTIONS] COMMAND [ARGS]...

  SlurmDocs CLI for collecting and analyzing SLURM clusters.

Options:
  --version    Show the version and exit.
  -d, --debug  Enable debug logging.
  --help       Show this message and exit.

Commands:
  collect   Subcommand for SlurmDocs database operations.
  database  Subcommand for SlurmDocs database operations.
  stats     Subcommand for SlurmDocs statistics.
```
These subcommands are designed for their respective use cases.

### Collect Subcommand
The collect subcommand is used to gather node and CPU data from each node in the cluster. To use it, you must provide the following options to invoke additional subcommands:
```bash
Usage: slurmdocs collect [OPTIONS] COMMAND [ARGS]...

  Subcommand for SlurmDocs database operations.

Options:
  -u, --username TEXT  The username to use.  [required]
  -s, --server TEXT    The server to use.  [required]
  -p, --port INTEGER   The port to use.
  -k, --key-path PATH  The key to use.
  --help               Show this message and exit.

Commands:
  cpu    Collect CPU information for a specific node.
  node   Collect the node info file from the cluster.
  sweep  Populate the database with all the collected data.
```
#### Cluster Connection and Data Collection
To connect to the cluster, you need to specify the username and server, and you can optionally provide the port (defaulting to a standard port). SlurmDocs supports key-based authentication, and you can specify the path to your SSH keys (default location is `~/.ssh`). This allows for a secure and convenient SSH connection to the cluster. The subcommands are invoked in the following manner,
```bash
slurmdocs collect -u jhondoe -s jhondoe.edu -p 23 -k ~/.ssh cpu -n compute-10-3 -p debug -qos debug -save ~/data
```
This will download the output of the `lscpu` command on the `compute-10-3` as a text file in the `~/data` directory. Similarly, all the data are collected for all of the available nodes. The node command collects the output of the scontrol show node and saves it as a text file.

To automate the process of collecting the data and creating a database automatically, users are recommended to use the sweep command.
```bash
slurmdocs collect -u jhondoe -s jhondoe.edu -p 23 -k ~/.ssh sweep -db doehpc -t 10 
```
This will automatically download the node file and collect all the cpu data from the nodes available. This assumes the partition names in the cluster 
are lower case. Optionally, user can override the partiotion and qos needed to collect the data form each compute node in cluster. This is done by providing,
```bash
slurmdocs collect -u jhondoe -s jhondoe.edu -p 23 -k ~/.ssh sweep -db doehpc -t 10  -p main -qos main --override
```
This assumes that the "main" partition can queue jobs in all nodes with the crossponding user account.


### Database Subcommand
After sweeping the data, by default the data is stored in `~/.slurmdocs` directory. User can use the `database` subcommand to access and maniputlate the data. Each recorded cluster has their own database which can be viewed by,
```bash
slurmdocs database avail
```
Here is a sample output from avail command:

<img src="./extra/output/Avail.png" alt="CPU Model Composition"  style="width: 100%"/>


This will list all the database which are avaible. Additionally, there is a check mark to the side for each uncorroupted or non empty database.
Following additional commands are available,
```bash
Usage: slurmdocs database [OPTIONS] COMMAND [ARGS]...

  Subcommand for the slurmdocs database operations.

Options:
  --version        Show the version and exit.
  -p, --path PATH  The path to the database.
  --help           Show this message and exit.

Commands:
  avail      List the available databases.
  clean      Clean the empty databases.
  coverage   Cover the database.
  create     Create the database subdirectories.
  destroy    Destroy the database including it's subdirectory.
  insert     Insert the file into the database.
  integrity  Check the integrity of the database.
  list       List the databases tree structure.
  query      Query the database.
  remove     Remove the entries from the database.
  update     Update the certan pre-exiting data file.
```
The database hierriecy are arranged in two keys (node and cpu) which is required by few subcommands like query and insert. In addition to the CLI, you can use the Python API to manipulate the data. The data is provided as a pandas.DataFrame object, which you can use for custom data analysis and processing.


### Stat Subcommand
The stat command is used to calculate the statistics for the database after collection process is complete. It has follwing subcommands,
```bash
Usage: slurmdocs stats [OPTIONS] COMMAND [ARGS]...

  Subcommand for the slurmdocs statistics.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  plots      Generate plots from the tflops file.
  summarize  Summarize the tflops file to stdout.
  tflops     Calculate the TFLOPS of each node in the cluster.
```
First the user need to generate the tflops file which process and parse the raw text file in the database and create a good dataframe which can be published in the website or used for further processing. The follwing command shows the usage
```bash
slurmdocs stats tflops -db jhondoe -ft html
```
This will generate the html table of the processed data. Now, this file can be used to generate plots and summary of the cluster.
```bash
slurmdocs stats summarize -t jhondoe_tflops.html
```
The follwing is the sample output of the summary output,
<img src="./extra/output/SummarizeOut.png" alt="Summarize Out" style="width: 100%;" />

```bash
slurmdocs stats tflops plots -ft jhondoe_tflops.html
```
These will generate a summary in stdout and plots files in the cwd. The sample plots are,

#### Plot : NodeName vs TFlops
<img src="./extra/output/plots/chpc/NodeName_vs_CPU_TFLOPS.png" alt="Plot by NodeName"  style="width: 100%"/>

#### Plot : Cpu Model Composition
<img src="./extra/output/plots/chpc/CPU_Model_Composition.png" alt="CPU Model Composition"  style="width: 100%"/>

#### Plot : GPUs vs TFlops
<img src="./extra/output/plots/uahpc/NodeName_vs_GPU_TFLOPS.png" alt="GPU Tflops"  style="width: 100%"/>

## Using the Python API
The SlurmDocs package can be independently used as an API by importing the slurmdocs module after installation. This module is well-documented, making it easy to configure according to your specific requirements. The documentation for collecting and analyzing data using the API is available in the form of a Jupyter notebook located in the `/docs` directory.

This provides flexibility for users who prefer programmatic access to SlurmDocs. The Jupyter notebook serves as a practical guide to help you leverage the API for your specific use cases and data analysis needs.

## Using the Python API
The SlurmDocs package can be independently used as an API by importing the `slurmdocs` module after installation. This module is well-documented, making it easy to configure according to your specific requirements. The documentation for collecting and analyzing data using the API is available in the form of a Jupyter notebook located in the `/docs` directory.

This provides flexibility for users who prefer programmatic access to SlurmDocs. The Jupyter notebook serves as a practical guide to help you leverage the API for your specific use cases and data analysis needs.

## Contributions and License
We welcome contributions from the open-source community to enhance the functionality and features of SlurmDocs. If you're interested in contributing or have ideas for improvement, please consider the following:

- **Feature Enhancements:** You can contribute by enhancing existing features or proposing new ones. Feel free to submit feature requests or pull requests on the [GitHub repository](https://github.com/NISCHALPI/SlurmDocs).

- **Bug Reports:** If you encounter any issues or bugs while using SlurmDocs, please report them on the [issue tracker](https://github.com/NISCHALPI/SlurmDocs/issues). Your feedback is valuable in improving the tool.

- **Documentation:** Contributions to documentation, including corrections, improvements, and additional examples, are highly appreciated. You can directly edit the documentation through the GitHub repository.

- **Spread the Word:** If you find SlurmDocs valuable, consider sharing it with your network, colleagues, or on social media. Your support helps us reach a wider audience.

**License:** SlurmDocs is released under the MIT License, which encourages open-source collaboration. You can find the complete license details on [opensource.org](https://opensource.org/licenses/MIT). By using or contributing to SlurmDocs, you agree to abide by the terms of this license.

We appreciate your contributions and support in making SlurmDocs a valuable resource for the community.
