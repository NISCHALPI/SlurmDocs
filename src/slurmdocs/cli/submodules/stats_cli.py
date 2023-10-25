"""CLI for stats module."""


from pathlib import Path
from ...statistics import Statistics, IcpuStats, IgpuStats
import click
from ...database import SlurmClusterDatabase
import pandas as pd
import seaborn as sns

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


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """_summary_.

    Args:
        ctx (click.Context): _description_
        path (Path): _description_
        database (str): _description_
    """
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
    ctx: click.Context,
    database: str,
    path: Path,
    gpu: bool,
    save_dir: Path,
    file_type: str,
    gpu_model_file: Path,
) -> None:
    """_summary_

    Args:
        ctx (click.Context): _description_
    """
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
    node_df.rename(columns={"cpu_tflops": "CPU_TFLOPS"}, inplace=True)

    # Infer relevant data types
    node_df = node_df.infer_objects()
    # Round the values to 2 decimal places
    node_df = node_df.round(2)

    # Save the dataframe to a file
    if file_type == "csv":
        node_df.to_csv(save_dir / "tflops.csv", index=False)
    elif file_type == "json":
        node_df.to_json(save_dir / "tflops.json", orient="records")
    elif file_type == "html":
        node_df.to_html(save_dir / "tflops.html", index=False)

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
def plots(ctx: click.Context, tflops_file: Path) -> None:
    """_summary_

    Args:
        ctx (click.Context): _description_
        tflops_file (Path): _description_
    """
    # Read the tflops file
    if tflops_file.suffix == ".csv":
        tflops_df = pd.read_csv(tflops_file)

    elif tflops_file.suffix == ".json":
        tflops_df = pd.read_json(tflops_file)

    elif tflops_file.suffix == ".html":
        tflops_df = pd.read_html(tflops_file)[0]

    else:
        raise click.ClickException("Invalid file type. Must be csv, json or html.")

    # Visualize the data using seaborn
    sns.figsize = (20, 10)
    sns.axes_style("whitegrid")

    # Plot the CPU TFLOPS vs NodeName
    import matplotlib.pyplot as plt
    sns.barplot(x="NodeName", y="CPU_TFLOPS", data=tflops_df, palette="viridis")
    plt.xticks(rotation=90)
    plt.show()
