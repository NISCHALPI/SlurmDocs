"""CLI for stats module."""


from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


from ...database import SlurmClusterDatabase
from ...statistics import IcpuStats, IgpuStats, Statistics

__all__ = ["stats"]


RELEVENT_COLUMNS = [
    "NodeName",
    "CPUTot",
    "ThreadsPerCore",
    "CoresPerSocket",
    "Sockets",
    "Model name",
    "CPU MHz",
    "CPU max MHz",
    "Partition",
    "Gres",
    "cpu_tflops",
]

GPU_RELEVENT_COLUMNS = [
    "gpu_tflops",
    "gpu_deep_learning_tflops",
    "gpu_memory_in_gb",
    "gpu_cuda_cores",
    "gpu_tensor_cores",
    "gpu_half_precision_tflops",
]

GPU_COLUMN_NAME_REMAPPER = {
    "gpu_tflops": "GPU TFLOPS",
    "gpu_deep_learning_tflops": "GPU Deep Learning TFLOPS",
    "gpu_memory_in_gb": "GPU Memory (GB)",
    "gpu_cuda_cores": "GPU CUDA Cores",
    "gpu_tensor_cores": "GPU Tensor Cores",
    "gpu_half_precision_tflops": "GPU Half Precision TFLOPS",
}


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
@click.pass_context
def stats(ctx: click.Context) -> None:
    "Subcommand for the slurmdocs statistics."  # noqa: D300
    ctx.obj["logger"].debug("Starting stats subcommand.")
    return


@stats.command()
@click.pass_context
@click.option(
    "-db",
    "--database",
    required=True,
    help="The name of the database to use.",
    type=click.STRING,
)
@click.option(
    "-p",
    "--path",
    required=False,
    help="The path to the database.",
    type=click.Path(path_type=Path),
    default=Path.home() / ".slurmdocs",
)
@click.option(
    "-gpu",
    "--gpu",
    is_flag=True,
    default=False,
    help="Compute GPU statistics along with CPU statistics.",
)
@click.option(
    "-s",
    "--save-dir",
    required=False,
    help="Save the statistics to a file.",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
)
@click.option(
    "-ft",
    "--file-type",
    required=False,
    help="The file type to save the statistics to.",
    type=click.Choice(["csv", "json", "html"]),
    default="html",
)
@click.option(
    "-gpu-model-file",
    required=False,
    type=click.Path(file_okay=True, exists=True, path_type=Path),
    help="The path to the GPU model file containing model and flops.",
)
def tflops(
    ctx: click.Context,  # noqa: ARG001
    database: str,
    path: Path,
    gpu: bool,
    save_dir: Path,
    file_type: str,
    gpu_model_file: Path,
) -> None:
    """Calculate the TFLOPS of each node in the cluster."""
    # Create the statistics object
    calculator = Statistics(istats=IcpuStats())

    # Get the databas
    db = SlurmClusterDatabase(
        db_name=database,
        db_path=path,
    )

    # Raise error if database is empty
    if db.is_empty() and not db.check_integrity():
        raise click.ClickException(
            "Database is empty or corrupted. Please run slurmdocs collect and create a databse."
        )

    # Get the node dataframes from the database
    node_df = db.get_node_file()

    flops_list = []
    # Calculate the statistics for each node
    for node in node_df["NodeName"].to_list():
        if db.is_cpu_file_available(node + ".txt"):
            # Get the cpu file from the database
            cpu = db.get_cpu_file(node + ".txt")

            # Calculate the flops
            flops = calculator(cpu)

            # Add Relevant Information to the flops series
            flops["NodeName"] = node
            flops["Model name"] = cpu["Model name"]
            flops["CPU MHz"] = cpu["CPU MHz"]

            # Add the max MHz if available
            if "CPU max MHz" in cpu:
                flops["CPU max MHz"] = cpu["CPU max MHz"]
            else:
                flops["CPU max MHz"] = flops["CPU MHz"]

            flops_list.append(flops)

    # Create a dataframe from the list
    flops_df = pd.DataFrame(flops_list)
    # Add a column to the node dataframe
    node_df = pd.merge(node_df, flops_df, on="NodeName")

    if gpu:
        # Compute GPU statistics if flag is set
        calculator._istats = IgpuStats(gpu_model_tflops_dataframe=gpu_model_file)

        gpu_stat = []
        # Calculate the statistics for each node
        for idx, node in node_df.iterrows():
            stats = calculator(node)
            stats["NodeName"] = node["NodeName"]
            # Add the stats to the list
            gpu_stat.append(stats)

        # Create a dataframe from the list
        gpu_df = pd.DataFrame(gpu_stat)
        # Add a column to the node dataframe
        node_df = pd.merge(node_df, gpu_df, on="NodeName")

    # Extract the partitions of the dataframe
    partition = [
        colname
        for colname in node_df.columns
        if colname.endswith("_PRT") and not colname[:4].isupper()
    ]
    part_dict = pd.Series()
    for idx, node in node_df.iterrows():
        part_dict[node["NodeName"]] = ""
        for part in partition:
            if node[part]:
                part_dict[node["NodeName"]] += part[:-4] + ","

        part_dict[node["NodeName"]] = part_dict[node["NodeName"]][:-1]

    # Add the partition column to the dataframe
    node_df["Partition"] = part_dict.values

    # Filter the dataframe to only include relevent columns
    node_df = node_df[
        RELEVENT_COLUMNS + GPU_RELEVENT_COLUMNS if gpu else RELEVENT_COLUMNS
    ]
    # Fill only GPU columns with 0 if NaN
    if gpu:
        node_df[GPU_RELEVENT_COLUMNS] = node_df[GPU_RELEVENT_COLUMNS].fillna(0)

    # Rename the columns
    node_df.rename(columns=GPU_COLUMN_NAME_REMAPPER if gpu else {}, inplace=True)
    node_df.rename(columns={"cpu_tflops": "CPU TFLOPS"}, inplace=True)

    # Infer relevant data types
    node_df = node_df.infer_objects()
    # Round the values to 2 decimal places
    node_df = node_df.round(2)

    # Save the dataframe to a file
    if file_type == "csv":
        node_df.to_csv(save_dir / f"{database}_tflops.csv", index=False)
    elif file_type == "json":
        node_df.to_json(save_dir / f"{database}_tflops.json", orient="records")
    elif file_type == "html":
        node_df.to_html(save_dir / f"{database}_tflops.html", index=False)

    return


def read_tflops_file_helper_func(tflops_file: Path) -> pd.DataFrame:
    """_summary_.

    Args:
        tflops_file (Path): _description_

    Returns:
        pd.DataFrame: _description_
    """
    if tflops_file.suffix == ".csv":
        tflops_df = pd.read_csv(tflops_file)

    elif tflops_file.suffix == ".json":
        tflops_df = pd.read_json(tflops_file)

    elif tflops_file.suffix == ".html":
        tflops_df = pd.read_html(tflops_file)[0]

    else:
        raise click.ClickException("Invalid file type. Must be csv, json or html.")

    return tflops_df


def barplot_helper_func(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: str,
    ax: plt.Axes,
    palette: str,
    title: str,
    rotation: int = 0,
) -> tuple:
    """Create a barplot using Seaborn.

    Args:
        df (pd.DataFrame): The input DataFrame.
        x (str): The column name for the x-axis.
        y (str): The column name for the y-axis.
        hue (str): The column name for the hue.
        ax (plt.Axes): The matplotlib axes object to plot on.
        palette (str): The color palette to use.
        title (str): The title of the plot.
        rotation (int, optional): The rotation angle of the x-axis labels. Defaults to 0.

    Returns:
        tuple: A tuple containing the matplotlib figure and axes objects.
    """
    # Create fig and ax
    fig, ax = plt.subplots(figsize=(20, 10))

    # Create the barplot
    ax = sns.barplot(x=x, y=y, hue=hue, data=df, ax=ax, palette=palette)

    # Set the x and y labels
    ax.set_xlabel(x)
    ax.set_ylabel(y)

    # Set the title
    ax.set_title(title)

    # Set a fixed number of ticks
    ax.set_xticks(range(len(df[x])))

    # Rotate the xticks if needed
    ax.set_xticklabels(ax.get_xticklabels(), rotation=rotation)

    return fig, ax


def save_fig_helper_func(fig: plt.Figure, save_path: Path) -> None:
    """_summary_.

    Args:
        fig (plt.Figure): _description_
        save_path (Path): _description_
    """
    # Improve the figure layout
    fig.tight_layout()

    # Save the figure
    fig.savefig(save_path, bbox_inches="tight", dpi=300)

    # Close the figure
    plt.close(fig)

    return


@stats.command()
@click.pass_context
@click.option(
    "-t",
    "--tflops-file",
    required=True,
    type=click.Path(file_okay=True, exists=True, path_type=Path),
    help="The path to the tflops file.",
)
@click.option(
    "-s",
    "--save-path",
    required=False,
    type=click.Path(path_type=Path),
    help="The path to save the plot to.",
    default=Path.cwd(),
)
def plots(
    ctx: click.Context, tflops_file: Path, save_path: Path  # noqa: ARG001
) -> None:
    """Generate plots from the tflops file."""
    # Read the tflops file
    tflops_df = read_tflops_file_helper_func(tflops_file)

    # Generate the plots
    # Plot 1: NodeName vs CPU TFLOPS
    fig, ax = barplot_helper_func(
        df=tflops_df,
        x="NodeName",
        y="CPU TFLOPS",
        hue="Partition",
        ax=None,
        palette="magma",
        title="NodeName vs CPU TFLOPS",
        rotation=90,
    )
    save_fig_helper_func(fig, save_path / "NodeName_vs_CPU_TFLOPS.png")

    # Plot 2: NodeName vs GPU TFLOPS
    if "GPU TFLOPS" in tflops_df.columns:
        gpu_nodes = tflops_df[tflops_df["GPU TFLOPS"] != 0]
        fig, ax = barplot_helper_func(
            df=gpu_nodes,
            x="NodeName",
            y="GPU TFLOPS",
            hue="CPUTot",
            ax=None,
            palette="viridis",
            title="NodeName vs GPU TFLOPS",
            rotation=90,
        )
        save_fig_helper_func(fig, save_path / "NodeName_vs_GPU_TFLOPS.png")

    else:
        click.echo("No GPU TFLOPS data available. Skipping GPU Plots.")

    # Plot 3 : Pie Chart of CPU Model Composition with legend
    fig, ax = plt.subplots(figsize=(20, 10))
    cpu_comp = tflops_df["Model name"].value_counts()
    ax.pie(
        cpu_comp.values,
        labels=cpu_comp.index,
        autopct="%1.1f%%",
        shadow=False,
        startangle=90,
    )
    ax.set_title("CPU Model Composition")
    save_fig_helper_func(fig, save_path / "CPU_Model_Composition.png")


@stats.command()
@click.pass_context
@click.option(
    "-t",
    "--tflops-file",
    required=True,
    type=click.Path(file_okay=True, exists=True, path_type=Path),
    help="The path to the tflops file.",
)
def summarize(ctx: click.Context, tflops_file: Path) -> None:
    """Summarize the tflops file to stdout."""
    # Read the tflops file
    tflops_df = read_tflops_file_helper_func(tflops_file)

    # Get Total CPU TFLOPS
    total_cpu_tflops = tflops_df["CPU TFLOPS"].sum()
    # Get Total GPU TFLOPS
    if "GPU TFLOPS" in tflops_df.columns:
        total_gpu_tflops = tflops_df["GPU TFLOPS"].sum()
    else:
        total_gpu_tflops = 0

    # Get Total TFLOPS
    total_tflops = total_cpu_tflops + total_gpu_tflops

    # Get Total CPU Cores
    total_cpu_cores = tflops_df["CPUTot"].sum()

    # Get Total GPU Cores
    if "GPU CUDA Cores" in tflops_df.columns:
        total_gpu_cores = tflops_df["GPU CUDA Cores"].sum()
    else:
        total_gpu_cores = 0

    # Get GPU Memory
    if "GPU Memory (GB)" in tflops_df.columns:
        total_gpu_memory = tflops_df["GPU Memory (GB)"].sum()
    else:
        total_gpu_memory = 0

    # Get Node Count
    num_nodes = tflops_df["NodeName"].__len__()

    # Print the summary
    click.echo(f"Total Nodes: {num_nodes}")
    click.echo(f"Total CPU TFLOPS(Single Precision): {total_cpu_tflops}")
    click.echo(f"Total GPU TFLOPS (Single Precision): {total_gpu_tflops}")
    click.echo(f"Total TFLOPS (Single Precision): {total_tflops}")
    click.echo(f"Total CPU Cores: {int(total_cpu_cores)}")
    click.echo(f"Total GPU Cores: {int(total_gpu_cores)}")
    click.echo(f"Total GPU Memory (GB): {total_gpu_memory:.2f}")

    return
