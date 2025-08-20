"""Runner."""

from dataclasses import dataclass
from pathlib import Path

from pheval.runners.runner import PhEvalRunner

from pheval_talos.prepare.prepare import prepare_for_talos
from pheval_talos.run.run import run_pipeline_per_sample
from pheval_talos.tool_specific_configuration_options import TALOSConfigurations


@dataclass
class TalosPhEvalRunner(PhEvalRunner):
    """Runner class implementation."""

    input_dir: Path
    testdata_dir: Path
    tmp_dir: Path
    output_dir: Path
    config_file: Path
    version: str

    def prepare(self):
        """Prepare."""
        print("preparing")
        prepare_for_talos(
            testdata_dir=self.testdata_dir,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            raw_results_dir=self.raw_results_dir,
        )

    def run(self):
        """Run."""
        print("running")
        configurations = TALOSConfigurations.model_validate(self.input_dir_config.tool_specific_configuration_options)
        run_pipeline_per_sample(
            input_dir=self.input_dir,
            testdata_dir=self.testdata_dir,
            raw_results_dir=self.raw_results_dir,
            apptainer=configurations.apptainer,
        )

    def post_process(self):
        """Post Process."""
        print("post processing")
