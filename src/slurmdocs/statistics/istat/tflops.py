"""Implements CPU And GPU TFLOPS Istat interface for computing TFLOPS given CPU and GPU info.Need to use the parsed data from slurmdocs.parse.iparse.ilscpu.

This module provides a framework for calculating TFLOPS (floating-point operations per second) for CPU devices based on their architecture and clock speed. It includes the `IcpuStats` class, which implements the TFLOPS computation for CPUs using information parsed from slurmdocs.

Classes:
    - IcpuStats: A class that calculates CPU TFLOPS based on CPU architecture, clock speed, and the number of cores.

Usage:
    To use this module, create an instance of the `IcpuStats` class and call it with CPU information parsed from slurmdocs. The `IcpuStats` class calculates TFLOPS based on the detected CPU architecture, clock speed, and the number of CPU cores.

Example:
    ```python
    # Create an instance of IcpuStats
    cpu_stats = IcpuStats()

    # Obtain CPU information using slurmdocs
    cpu_info = slurmdocs.parse.iparse.ilscpu.get_cpu_info()

    # Calculate CPU TFLOPS
    cpu_tflops = cpu_stats(cpu_info)

    print(f"CPU TFLOPS: {cpu_tflops['cpu_tflops']} TFLOPS")
    ```

Note:
    - This module focuses on CPU TFLOPS computation and uses information obtained from slurmdocs. It calculates TFLOPS based on architecture, clock speed, and the number of cores.
    - For GPU TFLOPS computation, you may need to implement a separate class or module.
    - Ensure that you have slurmdocs and the necessary parsing functions available to use this module effectively.
"""
from pathlib import Path
from warnings import warn

import pandas as pd

from .istat import Istat

__all__ = ["IcpuStats", "IgpuStats"]


class IcpuStats(Istat):
    """Computes CPU TFLOPS using architecture and clock speed.

    This class calculates CPU TFLOPS based on the architecture, clock speed, and the number of CPU cores. It uses information parsed from slurmdocs for accurate TFLOPS computation.

    Attributes:
        intel_instruction_set_sp_flops_dp_flops (dict): Mapping of Intel instruction sets to SP (Single Precision) and DP (Double Precision) flops per cycle.
        amd_instruction_set_sp_flops_dp_flops (dict): Mapping of AMD instruction sets to SP (Single Precision) and DP (Double Precision) flops per cycle.

    Methods:
        __init__(self) -> None:
            Initializes an instance of IcpuStats.

        _determine_max_instruction_set_single_precision(self, cpu_info: pd.Series) -> float:
            Determines the maximum instruction set for single precision computation based on CPU flags.

        _compute(self, series: pd.Series) -> pd.Series:
            Computes CPU TFLOPS using architecture, clock speed, and the number of CPU cores.

    Example:
        To calculate CPU TFLOPS:

        ```python
        # Create an instance of IcpuStats
        cpu_stats = IcpuStats()

        # Obtain CPU information using slurmdocs
        cpu_info = slurmdocs.parse.iparse.ilscpu.get_cpu_info()

        # Calculate CPU TFLOPS
        cpu_tflops = cpu_stats(cpu_info)

        print(f"CPU TFLOPS: {cpu_tflops['cpu_tflops']} TFLOPS")
        ```

    Note:
        This class is designed for CPU TFLOPS computation based on CPU architecture and clock speed. It relies on slurmdocs for CPU information.
    """

    # Source : https://en.wikichip.org/wiki/flops
    # Intel Instruction set to the number of flops per cycle (SP, DP)
    intel_instruction_set_sp_flops_dp_flops = {
        "sse": (8, 4),
        "avx": (16, 8),
        "avx2": (32, 16),
        "avx512": (64, 32),
    }

    # AMD Instruction set to the number of flops per cycle (SP, DP)
    amd_instruction_set_sp_flops_dp_flops = {
        "sse": (8, 4),
        "avx": (16, 8),
        "avx2": (16, 8),
        "avx512": (32, 16),
    }

    def __init__(self) -> None:
        """Initializes an instance of IcpuStats."""
        super().__init__(features="cpu_tflops")

    def _determine_max_instruction_set_single_precision(
        self, cpu_info: pd.Series
    ) -> float:
        """Determines the maximum instruction set for single precision computation based on CPU flags.

        Args:
            cpu_info (pd.Series): CPU information parsed from slurmdocs.

        Returns:
            float: Maximum SP flops per cycle.


        Raises:
            ValueError: If the CPU vendor is not supported or if the instruction set is not found in CPU flags.
        """
        # Check CPU Model and Vendor
        is_intel = cpu_info["Vendor ID"] == "GenuineIntel"

        # if non-Intel, check AMD or raise an error
        if not is_intel:
            if cpu_info["Vendor ID"] != "AuthenticAMD":
                raise ValueError(
                    "CPU Vendor not supported. Only Intel and AMD are supported."
                )

        # Check Flags in the following order 'avx512', 'avx2', 'avx', 'sse'
        flags = cpu_info["Flags"].split(" ")

        if "avx512" in flags:
            return (
                self.intel_instruction_set_sp_flops_dp_flops["avx512"][0]
                if is_intel
                else self.amd_instruction_set_sp_flops_dp_flops["avx512"][0]
            )

        if "avx2" in flags:
            return (
                self.intel_instruction_set_sp_flops_dp_flops["avx2"][0]
                if is_intel
                else self.amd_instruction_set_sp_flops_dp_flops["avx2"][0]
            )

        if "avx" in flags:
            return (
                self.intel_instruction_set_sp_flops_dp_flops["avx"][0]
                if is_intel
                else self.amd_instruction_set_sp_flops_dp_flops["avx"][0]
            )

        if "sse" in flags:
            return (
                self.intel_instruction_set_sp_flops_dp_flops["sse"][0]
                if is_intel
                else self.amd_instruction_set_sp_flops_dp_flops["sse"][0]
            )

        raise ValueError(
            f"""CPU Instruction set not supported. 
                        Only SSE, AVX, AVX2, AVX512 are supported.
                        None of these were found in the CPU Flags for the following model {cpu_info['Model name']}."""
        )

    def _compute(self, series: pd.Series) -> pd.Series:
        """Computes CPU TFLOPS using architecture, clock speed, and the number of CPU cores.

        Args:
            series (pd.Series): CPU information parsed from slurmdocs.

        Returns:
            pd.Series: Computed CPU TFLOPS.


        Raises:
            ValueError: If CPU clock speed information is not found.
        """
        # Get No of Cores
        no_of_cores = int(
            series["CPU(s)"]
        )  # CPU(s) is a string of the form "2" or "2-4"

        # Get Max Instruction Set for single precision
        max_instruction_set = self._determine_max_instruction_set_single_precision(
            series
        )

        # Get clock speed
        if "CPU max MHz" in series:
            clock_speed = series["CPU max MHz"]
        elif "CPU MHz" in series:
            clock_speed = series["CPU MHz"]
        elif "CPU min MHz" in series:
            clock_speed = series["CPU min MHz"]
        else:
            raise ValueError("CPU clock speed not found. Please check CPU info.")

        # Convert clock speed to float and THz
        clock_speed = float(clock_speed) / 10**6

        return pd.Series(
            {"cpu_tflops": no_of_cores * max_instruction_set * clock_speed}
        )


class IgpuStats(Istat):
    """Computes GPU statistics including TFLOPS, memory, and core information based on GPU model and counts.

    This class calculates GPU statistics, including TFLOPS (floating-point operations per second), memory capacity, CUDA cores, and more, based on the GPU model and counts provided in the Slurm job's Gres field. It utilizes a GPU model to TFLOPS mapping DataFrame for accurate calculations.

    Attributes:
        _gpu_dataframe (pd.DataFrame): A DataFrame containing GPU model to TFLOPS mapping and additional GPU information.


    Methods:
        __init__(self, gpu_model_tflops_dataframe: str | Path = None) -> None:
            Initializes an instance of IgpuStats.

        _compute(self, series: pd.Series) -> pd.Series:
            Computes GPU statistics based on the GPU model and counts in the Slurm job's Gres field.

    Args:
        gpu_model_tflops_dataframe (str | Path, optional): The path to a CSV file containing GPU model to TFLOPS mapping. If provided, this file will be used for calculations. Defaults to None, which loads a default mapping.

    Example:
        To calculate GPU statistics:

        ```python
        # Create an instance of IgpuStats
        gpu_stats = IgpuStats()

        # Obtain Slurm job information including GPU Gres field
        slurm_job_info = get_slurm_job_info()  # Implement your own function to get job info

        # Calculate GPU statistics
        gpu_statistics = gpu_stats(slurm_job_info)

        print(f"GPU TFLOPS: {gpu_statistics['gpu_tflops']} TFLOPS")
        print(f"GPU Memory: {gpu_statistics['gpu_memory_in_gb']} GB")
        print(f"GPU CUDA Cores: {gpu_statistics['gpu_cuda_cores']}")
        ```

    Note:
        - This class is designed to calculate GPU statistics based on GPU model and counts provided in the Gres field of a Slurm job.
        - It utilizes a GPU model to TFLOPS mapping for accurate TFLOPS calculations.
        - Ensure that you have the necessary GPU model to TFLOPS mapping data or use the default mapping provided in the module.
    """

    default_gpu_model_tflops_dataframe = Path(__file__).parent / "gpu_specs.csv"

    def __init__(self, gpu_model_tflops_dataframe: str | Path = None) -> None:
        """Initializes an instance of IgpuStats.

        Args:
            gpu_model_tflops_dataframe (str | Path, optional): The path to a CSV file containing GPU model to TFLOPS mapping. Defaults to None, which loads a default mapping.
        """
        super().__init__(features="gpu_tflops")

        # Load default GPU model to TFLOPS DataFrame
        self._gpu_dataframe = pd.read_csv(
            Path(__file__).parent / "gpu_specs.csv", index_col="Model"
        )

        # Load GPU model to TFLOPS DataFrame if provided
        if gpu_model_tflops_dataframe is not None:
            # Display format warning and assert DataFrame has correct format
            warn(
                "GPU model to TFLOPS DataFrame provided. Ensure that it has the correct format as printed below."
            )
            print(self._gpu_dataframe.head())

            self._gpu_dataframe = pd.read_csv(gpu_model_tflops_dataframe)

    @staticmethod
    def update_default_gpu_model_tflops_dataframe(
        model: str,
        single_precision_tflops: float,
        double_precision_tflops: float,
        deep_learning_tflops: float,
        memory_in_gb: float,
        cuda_cores: int,
        tensor_cores: int,
        half_precision_tflops: float,
        force: bool = False,
    ) -> None:
        """Updates the default GPU model to TFLOPS DataFrame with new GPU model and TFLOPS values.

        Args:
            model (str): The GPU model.
            single_precision_tflops (float): The TFLOPS value for single precision calculations.
            double_precision_tflops (float): The TFLOPS value for double precision calculations.
            deep_learning_tflops (float): The TFLOPS value for deep learning calculations.
            memory_in_gb (float): The memory capacity in GB.
            cuda_cores (int): The number of CUDA cores.
            tensor_cores (int): The number of Tensor cores.
            half_precision_tflops (float): The TFLOPS value for half precision calculations.
            force (bool, optional): If True, forces the update even if the model already exists in the DataFrame. Defaults to False.


        Returns:
            None: None.
        """
        # Read the default GPU model to TFLOPS DataFrame
        defaut_gpu_model_tflops_dataframe = pd.read_csv(
            IgpuStats.default_gpu_model_tflops_dataframe, index_col="Model"
        )

        # If model is already in the DataFrame, raise a warning if not force
        if model in defaut_gpu_model_tflops_dataframe.index and not force:
            warn(
                f"""GPU model {model} is already in the default GPU model to TFLOPS DataFrame. Skipping the TFLOPS values.
                To force update, set force=True."""
            )
            return

        # Remove the model from the DataFrame if force is True
        if model in defaut_gpu_model_tflops_dataframe.index and force:
            defaut_gpu_model_tflops_dataframe.drop(model, axis=0, inplace=True)

        # Add the New GPU model to TFLOPS DataFrame
        defaut_gpu_model_tflops_dataframe.loc[model] = {
            "SinglePrecisionTFLOPS": single_precision_tflops,
            "DeepLearningTFLOPS": deep_learning_tflops,
            "Memory": memory_in_gb,
            "CUDACores": cuda_cores,
            "TensorCores": tensor_cores,
            "HalfPrecisionTFLOPS": half_precision_tflops,
            "DoublePrecisionTFLOPS": double_precision_tflops,
        }

        # Save the DataFrame
        defaut_gpu_model_tflops_dataframe.to_csv(
            IgpuStats.default_gpu_model_tflops_dataframe,
        )

        return

    def _compute(self, series: pd.Series) -> pd.Series:
        """Computes GPU statistics based on GPU model and counts in the Slurm job's Gres field.

        Args:
            series (pd.Series): Slurm job information, including GPU Gres field.

        Returns:
            pd.Series: Computed GPU statistics, including TFLOPS, memory, CUDA cores, and more.
        """
        # Get the Gres value, which should be of the form <gpu_model>:<gpu_count>, <gpu_model>:<gpu_count> (e.g., "a100:2,rtx8000:4")
        gres_value = series["Gres"]

        if gres_value is None:
            return pd.Series({"gpu_tflops": 0})

        # Split the Gres value into a list of GPU model and count tuples
        gpu_tup = [tuple(gres.split(":")) for gres in gres_value.split(",")]

        # Convert the count to int
        gpu_tup = [(gpu[0], int(gpu[1])) for gpu in gpu_tup]

        # Initialize statistics variables
        single_precision_tflops = 0
        deep_learning_tflops = 0
        memory_in_gb = 0
        cuda_cores = 0
        tensor_cores = 0
        half_precision_tflops = 0

        # Loop and sum the TFLOPS and other statistics for each GPU model
        for gpu, count in gpu_tup:
            for _ in range(count):
                gpu_info = self._gpu_dataframe.loc[gpu]
                single_precision_tflops += gpu_info["SinglePrecisionTFLOPS"]
                deep_learning_tflops += gpu_info["DeepLearningTFLOPS"]
                memory_in_gb += gpu_info["Memory"]
                cuda_cores += gpu_info["CUDACores"]
                tensor_cores += gpu_info["TensorCores"]
                half_precision_tflops += gpu_info["HalfPrecisionTFLOPS"]

        return pd.Series(
            {
                "gpu_tflops": single_precision_tflops,
                "gpu_deep_learning_tflops": deep_learning_tflops,
                "gpu_memory_in_gb": memory_in_gb,
                "gpu_cuda_cores": cuda_cores,
                "gpu_tensor_cores": tensor_cores,
                "gpu_half_precision_tflops": half_precision_tflops,
            }
        )
