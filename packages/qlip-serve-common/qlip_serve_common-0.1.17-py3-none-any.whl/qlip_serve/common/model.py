from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import numpy as np

from .model_config import (
    ModelConfig,
)
from .model_config.triton_model_config import (
    EnsembleStep,
)
from .signature import BaseSignature

__all__ = ["BaseModel", "BaseEnsembleModel", "ModelConfig", "EnsembleStep"]


def default_model_config():
    """Factory function for creating a default ModelConfig with customized settings."""
    return ModelConfig(max_batch_size=256, batching=True)


class BaseModel(ABC):
    model_name: Optional[str] = None
    inputs: Optional[List[BaseSignature]] = None
    outputs: Optional[List[BaseSignature]] = None
    device_type: Optional[str] = None
    model_config: ModelConfig = ModelConfig(max_batch_size=256, batching=True)
    model_version: int = 1
    strict: bool = False
    model_count: int = 1

    @abstractmethod
    def forward(self, inputs: Dict[str, List[np.ndarray]]) -> List[Dict[str, Any]]:
        ...

    @classmethod
    def validate(cls):
        if cls.model_name is None:
            raise ValueError("Model name should be provided")
        if not isinstance(cls.model_name, str):
            raise ValueError(
                f"Model name should be of str type, got: {cls.model_name} of {type(cls.model_name)} type."
            )

        if cls.inputs is None or not cls.inputs:
            raise ValueError("Inputs should be provided")
        for input_ in cls.inputs:
            if not isinstance(input_, BaseSignature):
                raise ValueError(
                    f"All inputs should be of BaseSignature type, got: {input_} of {type(input_)} type."
                )

        if cls.outputs is None or not cls.outputs:
            raise ValueError("Outputs should be provided")
        for output_ in cls.outputs:
            if not isinstance(output_, BaseSignature):
                raise ValueError(
                    f"All outputs should be of BaseSignature type, got: {output_} of {type(output_)} type."
                )

        if cls.device_type not in ["cpu", "gpu"]:
            raise ValueError(
                f"Unsupported device type: {cls.device_type}. For triton inference it should be 'cpu' or 'gpu'."
            )

        if not isinstance(cls.model_config, ModelConfig):
            raise ValueError(
                f"Model config should be of ModelConfig type, got: {cls.model_config} of {type(cls.model_config)} type."
            )

        if not isinstance(cls.model_version, int):
            raise ValueError(
                f"Model version should be of int type, got: {cls.model_version} of {type(cls.model_version)} type."
            )

        if not isinstance(cls.strict, bool):
            raise ValueError(
                f"Strict should be of bool type, got: {cls.strict} of {type(cls.strict)} type."
            )

        if not isinstance(cls.model_count, int):
            raise ValueError(
                f"Model count should be of int type, got: {cls.model_count} of {type(cls.model_count)} type."
            )

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def __eq__(self, other: "BaseModel") -> bool:
        return (
            self.model_name == other.model_name
            and self.model_version == other.model_version
            and self.model_count == other.model_count
            and self.device_type == other.device_type
            and self.inputs == other.inputs
            and self.outputs == other.outputs
            and self.model_config == other.model_config
        )


class BaseEnsembleModel:
    model_name: Optional[str] = None
    inputs: Optional[List[BaseSignature]] = None
    outputs: Optional[List[BaseSignature]] = None
    models: Optional[List[BaseModel]] = None
    model_config: ModelConfig = ModelConfig(max_batch_size=256, batching=True)
    model_version: int = 1

    @classmethod
    @property
    def ensemble_steps(cls) -> List[EnsembleStep]:
        raise NotImplementedError("You must use a subclass of BaseEnsembleModel")

    @classmethod
    def validate(cls):
        if cls.model_name is None:
            raise ValueError("Model name should be provided")
        if not isinstance(cls.model_name, str):
            raise ValueError(
                f"Model name should be of str type, got: {cls.model_name} of {type(cls.model_name)} type."
            )

        if cls.inputs is None or not cls.inputs:
            raise ValueError("Inputs should be provided")
        for input_ in cls.inputs:
            if not isinstance(input_, BaseSignature):
                raise ValueError(
                    f"All inputs should be of BaseSignature type, got: {input_} of {type(input_)} type."
                )

        if cls.outputs is None or not cls.outputs:
            raise ValueError("Outputs should be provided")
        for output_ in cls.outputs:
            if not isinstance(output_, BaseSignature):
                raise ValueError(
                    f"All outputs should be of BaseSignature type, got: {output_} of {type(output_)} type."
                )

        if cls.models is None or not cls.models:
            raise ValueError("Models should be provided")
        for model_ in cls.models:
            if not issubclass(model_, ABC):
                raise ValueError(
                    f"All models should be of BaseModel type, got: {model_} of {type(model_)} type."
                )

        if cls.ensemble_steps is None or not cls.ensemble_steps:
            raise ValueError("Ensemble steps should be provided")
        for ensemble_step_ in cls.ensemble_steps:
            if not isinstance(ensemble_step_, EnsembleStep):
                raise ValueError(
                    f"All ensemble steps should be of EnsembleStep type, got: {ensemble_step_} of {type(ensemble_step_)} type."
                )

        if not isinstance(cls.model_config, ModelConfig):
            raise ValueError(
                f"Model config should be of ModelConfig type, got: {cls.model_config} of {type(cls.model_config)} type."
            )

        if not isinstance(cls.model_version, int):
            raise ValueError(
                f"Model version should be of int type, got: {cls.model_version} of {type(cls.model_version)} type."
            )


class SeqEnsembleModel(BaseEnsembleModel):
    @classmethod
    @property
    def ensemble_steps(cls) -> List[EnsembleStep]:
        if not cls.models or not cls.inputs or not cls.outputs:
            raise ValueError("Models, inputs, and outputs must be defined.")

        ensemble_steps = []

        # Check if inputs match the first model's inputs
        if len(cls.inputs) != len(cls.models[0].inputs):
            raise ValueError(
                "Number of ensemble inputs doesn't match the first model's inputs."
            )
        for ensemble_input, model_input in zip(cls.inputs, cls.models[0].inputs):
            if (
                ensemble_input.name != model_input.name
                or ensemble_input.shape != model_input.shape
            ):
                raise ValueError(
                    f"Mismatch in input: {ensemble_input.name} vs {model_input.name}"
                )

        # Check if outputs match the last model's outputs
        if len(cls.outputs) != len(cls.models[-1].outputs):
            raise ValueError(
                "Number of ensemble outputs doesn't match the last model's outputs."
            )
        for ensemble_output, model_output in zip(cls.outputs, cls.models[-1].outputs):
            if (
                ensemble_output.name != model_output.name
                or ensemble_output.shape != model_output.shape
            ):
                raise ValueError(
                    f"Mismatch in output: {ensemble_output.name} vs {model_output.name}"
                )

        for i, model_class in enumerate(cls.models):
            input_map = {}
            output_map = {}

            # Set input map
            if i == 0:
                # For the first model, use the ensemble's input names
                for inp in cls.inputs:
                    input_map[inp.name] = inp.name
            else:
                # For subsequent models, match inputs with previous model's outputs
                prev_model_class = cls.models[i - 1]
                unmatched_inputs = list(model_class.inputs)
                unmatched_outputs = list(prev_model_class.outputs)

                for curr_inp in model_class.inputs:
                    matched = False
                    for prev_out in prev_model_class.outputs:
                        if cls._signatures_match(curr_inp, prev_out):
                            input_map[curr_inp.name] = prev_out.name
                            unmatched_inputs.remove(curr_inp)
                            unmatched_outputs.remove(prev_out)
                            matched = True
                            break
                    if not matched:
                        raise ValueError(
                            f"No matching output found for input {curr_inp.name} in model {model_class.__name__}"
                        )

                if unmatched_inputs or unmatched_outputs:
                    raise ValueError(
                        f"Unmatched inputs/outputs between models {i - 1} and {i}"
                    )

            # Set output map
            if i == len(cls.models) - 1:
                # For the last model, match outputs with ensemble's outputs
                unmatched_model_outputs = list(model_class.outputs)
                unmatched_ensemble_outputs = list(cls.outputs)

                for model_out in model_class.outputs:
                    matched = False
                    for ensemble_out in cls.outputs:
                        if cls._signatures_match(model_out, ensemble_out):
                            output_map[model_out.name] = ensemble_out.name
                            unmatched_model_outputs.remove(model_out)
                            unmatched_ensemble_outputs.remove(ensemble_out)
                            matched = True
                            break
                    if not matched:
                        raise ValueError(
                            f"No matching ensemble output found for model output {model_out.name}"
                        )

                if unmatched_model_outputs or unmatched_ensemble_outputs:
                    raise ValueError(
                        "Unmatched outputs between last model and ensemble outputs"
                    )
            else:
                # For intermediate models, use their own output names
                for out in model_class.outputs:
                    output_map[out.name] = out.name

            step = EnsembleStep(
                model_name=model_class.model_name,
                model_version=-1,
                input_map=input_map,
                output_map=output_map,
            )

            ensemble_steps.append(step)

        return ensemble_steps

    @staticmethod
    def _signatures_match(sig1, sig2):
        """
        Compare two signatures to see if they match based on specific attributes.
        Add or remove attributes as needed for your specific use case.
        """
        return (
            # TODO: do we need strictly name checking?
            # YES WE NEED! Because of possible ambiguity if type/dims are the same
            sig1.name == sig2.name
            and sig1.shape == sig2.shape
            and sig1.dtype == sig2.dtype
            # Add any other relevant comparisons here
        )
