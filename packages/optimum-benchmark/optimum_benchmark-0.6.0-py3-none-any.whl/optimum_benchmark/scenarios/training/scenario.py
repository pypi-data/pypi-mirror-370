from contextlib import ExitStack

from transformers import default_data_collator

from ...backends.base import Backend, BackendConfigT
from ...benchmark.report import BenchmarkReport
from ...generators.dataset_generator import DatasetGenerator
from ...trackers.energy import Efficiency, EnergyTracker
from ...trackers.latency import StepLatencyTrackerTrainerCallback, Throughput
from ...trackers.memory import MemoryTracker
from ..base import Scenario
from .config import TrainingConfig

TRAIN_THROUGHPUT_UNIT = "samples/s"
TRAIN_EFFICIENCY_UNIT = "samples/kWh"


class TrainingScenario(Scenario[TrainingConfig]):
    NAME = "training"

    def __init__(self, config: TrainingConfig) -> None:
        super().__init__(config)

    def run(self, backend: Backend[BackendConfigT]) -> BenchmarkReport:
        self.logger.info("\t+ Creating dataset generator")
        dataset_generator = DatasetGenerator(
            task=backend.config.task, model_shapes=backend.model_shapes, dataset_shapes=self.config.dataset_shapes
        )

        self.logger.info("\t+ Generating training dataset")
        training_dataset = dataset_generator()

        self.logger.info("\t+ Initializing training report")
        self.report = BenchmarkReport.from_list(targets=["overall", "warmup", "train"])

        self.logger.info("\t+ Loading model into backend")
        backend.load()

        training_callbackes = []

        with ExitStack() as context_stack:
            if self.config.latency:
                latency_callback = StepLatencyTrackerTrainerCallback(
                    device=backend.config.device, backend=backend.config.name
                )
                training_callbackes.append(latency_callback)
            if self.config.memory:
                memory_tracker = MemoryTracker(
                    device=backend.config.device, backend=backend.config.name, device_ids=backend.config.device_ids
                )
                context_stack.enter_context(memory_tracker.track())
            if self.config.energy:
                energy_tracker = EnergyTracker(
                    device=backend.config.device, backend=backend.config.name, device_ids=backend.config.device_ids
                )
                context_stack.enter_context(energy_tracker.track(task_name="train"))

            backend.train(
                training_dataset=training_dataset,
                training_callbacks=training_callbackes,
                training_data_collator=default_data_collator,
                training_arguments=self.config.training_arguments,
            )

        if self.config.latency:
            self.report.overall.latency = latency_callback.get_latency()
            self.report.overall.throughput = Throughput.from_latency(
                self.report.overall.latency, volume=self.overall_volume, unit=TRAIN_THROUGHPUT_UNIT
            )
            self.report.warmup.latency = self.report.overall.latency[: self.config.warmup_steps]
            self.report.warmup.throughput = Throughput.from_latency(
                self.report.warmup.latency, volume=self.warmup_volume, unit=TRAIN_THROUGHPUT_UNIT
            )
            self.report.train.latency = self.report.overall.latency[self.config.warmup_steps :]
            self.report.train.throughput = Throughput.from_latency(
                self.report.train.latency, volume=self.train_volume, unit=TRAIN_THROUGHPUT_UNIT
            )

        if self.config.memory:
            # we're supposing that it's the same memory usage for all steps
            self.report.overall.memory = memory_tracker.get_max_memory()
            self.report.warmup.memory = memory_tracker.get_max_memory()
            self.report.train.memory = memory_tracker.get_max_memory()

        if self.config.energy:
            # we can only get overall energy consumption
            self.report.overall.energy = energy_tracker.get_energy()
            self.report.overall.efficiency = Efficiency.from_energy(
                self.report.overall.energy, volume=self.overall_volume, unit=TRAIN_EFFICIENCY_UNIT
            )

        return self.report

    @property
    def overall_volume(self) -> int:
        return (
            self.config.max_steps
            * self.config.training_arguments["per_device_train_batch_size"]
            * self.config.training_arguments["gradient_accumulation_steps"]
        )

    @property
    def warmup_volume(self) -> int:
        return (
            self.config.warmup_steps
            * self.config.training_arguments["per_device_train_batch_size"]
            * self.config.training_arguments["gradient_accumulation_steps"]
        )

    @property
    def train_volume(self) -> int:
        return (
            (self.config.max_steps - self.config.warmup_steps)
            * self.config.training_arguments["per_device_train_batch_size"]
            * self.config.training_arguments["gradient_accumulation_steps"]
        )
