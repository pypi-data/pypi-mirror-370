import subprocess
from pathlib import Path

from pheval.utils.file_utils import all_files


def run_annotation(input_dir: Path, testdata_dir: Path, phenopacket_path: Path, apptainer: bool) -> None:
    """
    Run the annotation process using Nextflow.
    Args:
        input_dir (Path): The directory containing the necessary Nextflow workflow and
        configuration files for the annotation process.
        testdata_dir (Path): The testdata directory.
        phenopacket_path (Path): The path to the phenopacket.
        apptainer (bool): Whether to use apptainer to run the workflow.
    Returns:
        None
    """
    cmd = [
        "nextflow",
        "-c",
        f"{testdata_dir}/nextflow_config/{phenopacket_path.stem}_annotation.config",
        "run",
        f"{input_dir}/nextflow/annotation.nf",
    ]
    if apptainer:
        cmd += ["-with-singularity", f"{input_dir}/talos.sif"]
    subprocess.run(
        cmd,
        check=False,
        shell=False,
    )


def run_talos(
    input_dir: Path, testdata_dir: Path, phenopacket_path: Path, raw_results_dir: Path, apptainer: bool
) -> None:
    """
    Run the Talos Nextflow pipeline.
    Args:
        input_dir (Path): The directory containing the Talos Nextflow configuration and pipeline script.
        testdata_dir (Path): The directory containing the phenopackets file for the cohort data.
        phenopacket_path (Path): The path to the phenopacket.
        raw_results_dir (Path): The raw results directory.
        apptainer (bool): Whether to use apptainer to run the workflow.
    Returns:
        None
    """
    cmd = [
        "nextflow",
        "-c",
        f"{testdata_dir}/nextflow_config/{phenopacket_path.stem}_talos.config",
        "run",
        f"{input_dir}/nextflow/talos.nf",
        "--matrix_table",
        f"{raw_results_dir}/{phenopacket_path.stem}.mt",
        f"--phenopackets {phenopacket_path}",
    ]
    if apptainer:
        cmd += ["-with-singularity", f"{input_dir}/talos.sif"]
    subprocess.run(
        cmd,
        check=False,
    )


def run_pipeline_per_sample(input_dir: Path, testdata_dir: Path, raw_results_dir: Path, apptainer: bool):
    for cohort_phenopacket_path in all_files(testdata_dir.joinpath("cohort_phenopackets")):
        run_annotation(
            input_dir=input_dir,
            phenopacket_path=cohort_phenopacket_path,
            testdata_dir=testdata_dir,
            apptainer=apptainer,
        )
        run_talos(
            input_dir=input_dir,
            phenopacket_path=cohort_phenopacket_path,
            testdata_dir=testdata_dir,
            raw_results_dir=raw_results_dir,
            apptainer=apptainer,
        )
