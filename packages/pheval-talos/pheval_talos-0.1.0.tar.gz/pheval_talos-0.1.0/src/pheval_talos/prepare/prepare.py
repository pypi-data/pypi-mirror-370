from pathlib import Path

from pheval_talos.prepare.create_cohort import create_cohort
from pheval_talos.prepare.edit_next_flow_configs import edit_annotation_config, edit_talos_config


def prepare_for_talos(testdata_dir: Path, input_dir: Path, output_dir: Path, raw_results_dir: Path):
    create_cohort(testdata_dir=testdata_dir)
    edit_annotation_config(
        input_dir=input_dir, testdata_dir=testdata_dir, output_dir=output_dir, raw_results_dir=raw_results_dir
    )
    edit_talos_config(
        input_dir=input_dir, testdata_dir=testdata_dir, output_dir=output_dir, raw_results_dir=raw_results_dir
    )
