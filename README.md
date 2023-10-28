# SlurmDocs: Automated Slurm Cluster Documentation
![SlurmDocs Logo](./extra/SlurmDocs.png)

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
