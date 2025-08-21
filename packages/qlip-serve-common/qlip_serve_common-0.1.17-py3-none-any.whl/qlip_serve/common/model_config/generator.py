# Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generator class for creating Triton model config.

The class consume the TritonModelConfig object as a constructor argument and produce the Triton model config in form of
dict or file.

    Typical usage example:

        model_config = TritonModelConfig(model_name="simple")
        generator = ModelConfigGenerator(model_config)
        generator.to_file("/path/to/config.pbtxt")
"""
import json
import logging
import pathlib
from typing import Dict, Union

import numpy as np
from google.protobuf import json_format, text_format  # pytype: disable=pyi-error

from .exceptions import PyTritonBadParameterError
from .triton_model_config import (
    DynamicBatcher,
    EnsembleStep,
    TensorSpec,
    TritonModelConfig,
)
from .utils import np_to_triton_dtype

logger = logging.getLogger(__name__)


class ModelConfigGenerator:
    """Generate the protobuf config from ModelConfig object."""

    def __init__(self, config: TritonModelConfig):
        """Initialize generator.

        Args:
            config: model config object
        """
        self._config = config

    def to_file(self, config_path: Union[str, pathlib.Path]) -> str:
        """Serialize ModelConfig to prototxt and save to config_path directory.

        Args:
            config_path: path to configuration file

        Returns:
            A string with generated model configuration
        """
        from .grpc import model_config_pb2  # pytype: disable=import-error

        # https://github.com/triton-inference-server/common/blob/main/protobuf/model_config.proto
        model_config = self.get_config()
        logger.debug(f"Generated Triton config:\n{json.dumps(model_config, indent=4)}")

        config_payload = json_format.ParseDict(
            model_config, model_config_pb2.ModelConfig()
        )
        logger.debug(f"Generated Triton config payload:\n{config_payload}")

        config_path = pathlib.Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        model_config_bytes = text_format.MessageToBytes(config_payload)

        # WAR: triton requires max_batch_size = 0 to be explicit written
        # while this is not stored in payload during MessageToBytes
        if model_config["max_batch_size"] == 0:
            model_config_bytes += b"max_batch_size: 0\n"

        with config_path.open("wb") as cfg:
            cfg.write(model_config_bytes)

        logger.debug(f"Generated config stored in {config_path}")

        return config_payload

    def get_config(self) -> Dict:
        """Create a Triton model config from ModelConfig object.

        Returns:
            Dict with model configuration data
        """
        model_config = {
            "name": self._config.model_name,
        }

        if self._config.ensemble_steps:
            model_config["platform"] = "ensemble"
            self._set_ensemble_scheduling(model_config)
        else:
            model_config["backend"] = self._config.backend
            self._set_instance_group(model_config)

        self._set_batching(model_config)
        self._set_model_signature(model_config)
        self._set_model_transaction_policy(model_config)
        self._set_backend_parameters(model_config)
        self._set_response_cache(model_config)

        return model_config

    def _set_ensemble_scheduling(self, model_config: Dict) -> None:
        def _rewrite_ensemble_step_spec(spec_: EnsembleStep) -> Dict:
            item = {
                "model_name": spec_.model_name,
                "model_version": spec_.model_version,
                "input_map": spec_.input_map,
                "output_map": spec_.output_map,
            }

            return item

        model_config["ensemble_scheduling"] = {
            "step": [
                _rewrite_ensemble_step_spec(spec)
                for spec in self._config.ensemble_steps
            ]
        }

    def _set_batching(self, model_config: Dict) -> None:
        """Configure batching for model deployment on Triton Inference Server.

        Args:
            model_config: Dict with model config for Triton Inference Server
        """
        if not self._config.batching:
            model_config["max_batch_size"] = 0
            logger.debug(
                "Batching for model is disabled. The `max_batch_size` field value set to 0."
            )
            return
        elif self._config.max_batch_size < 1:
            raise PyTritonBadParameterError(
                "The `max_batch_size` must be greater or equal to 1."
            )

        model_config["max_batch_size"] = self._config.max_batch_size
        if (
            isinstance(self._config.batcher, DynamicBatcher)
            and not self._config.ensemble_steps
        ):
            dynamic_batching_config = {}
            if self._config.batcher.max_queue_delay_microseconds > 0:
                dynamic_batching_config["maxQueueDelayMicroseconds"] = int(
                    self._config.batcher.max_queue_delay_microseconds
                )

            if self._config.batcher.preferred_batch_size:
                dynamic_batching_config["preferredBatchSize"] = [
                    int(bs) for bs in self._config.batcher.preferred_batch_size
                ]

            if self._config.batcher.preserve_ordering:
                dynamic_batching_config[
                    "preserveOrdering"
                ] = self._config.batcher.preserve_ordering

            if self._config.batcher.priority_levels:
                dynamic_batching_config[
                    "priorityLevels"
                ] = self._config.batcher.priority_levels

            if self._config.batcher.default_priority_level:
                if (
                    self._config.batcher.default_priority_level
                    > self._config.batcher.priority_levels
                ):
                    raise PyTritonBadParameterError(
                        "The `default_priority_level` must be between 1 and "
                        f"{self._config.batcher.priority_levels}."
                    )
                dynamic_batching_config[
                    "defaultPriorityLevel"
                ] = self._config.batcher.default_priority_level

            if self._config.batcher.default_queue_policy:
                priority_queue_policy_config = {
                    "timeoutAction": self._config.batcher.default_queue_policy.timeout_action.value,
                    "defaultTimeoutMicroseconds": int(
                        self._config.batcher.default_queue_policy.default_timeout_microseconds
                    ),
                    "allowTimeoutOverride": self._config.batcher.default_queue_policy.allow_timeout_override,
                    "maxQueueSize": int(
                        self._config.batcher.default_queue_policy.max_queue_size
                    ),
                }
                dynamic_batching_config[
                    "defaultQueuePolicy"
                ] = priority_queue_policy_config

            if self._config.batcher.priority_queue_policy:
                if not self._config.batcher.priority_levels:
                    raise PyTritonBadParameterError(
                        "Provide the `priority_levels` if you want to define `priority_queue_policy` "
                        "for Dynamic Batching."
                    )

                priority_queue_policy_config = {}
                for (
                    priority,
                    queue_policy,
                ) in self._config.batcher.priority_queue_policy.items():
                    if priority < 0 or priority > self._config.batcher.priority_levels:
                        raise PyTritonBadParameterError(
                            f"Invalid `priority`={priority} provided. The value must be between "
                            f"1 and {self._config.batcher.priority_levels}."
                        )

                    priority_queue_policy_config[priority] = {
                        "timeoutAction": queue_policy.timeout_action.value,
                        "defaultTimeoutMicroseconds": int(
                            queue_policy.default_timeout_microseconds
                        ),
                        "allowTimeoutOverride": queue_policy.allow_timeout_override,
                        "maxQueueSize": int(queue_policy.max_queue_size),
                    }

                dynamic_batching_config[
                    "priorityQueuePolicy"
                ] = priority_queue_policy_config

            model_config["dynamic_batching"] = dynamic_batching_config
        else:
            logger.debug("Default batching used")

    def _set_instance_group(self, model_config: Dict) -> None:
        """Configure instance group for model deployment on Triton Inference Server.

        Args:
            model_config: Dict with model config for Triton Inference Server
        """
        instance_groups = []
        for device_kind, count in self._config.instance_group.items():
            instance_groups.append(
                {
                    "count": count,
                    "kind": device_kind.value,
                }
            )

        if instance_groups:
            model_config["instance_group"] = instance_groups

    def _set_model_transaction_policy(self, model_config: Dict) -> None:
        """Configure model transaction policy for model deployment on Triton Inference Server.

        Args:
            model_config: Dict with model config for Triton Inference Server
        """
        if self._config.decoupled:
            model_config["model_transaction_policy"] = {"decoupled": True}

    def _set_backend_parameters(self, model_config: Dict) -> None:
        """Configure backend parameters for model deployment on Triton Inference Server.

        Args:
            model_config: Dict with model config for Triton Inference Server
        """
        parameters = {}
        for key, value in self._config.backend_parameters.items():
            parameters[key] = {
                "string_value": str(value),
            }

        if parameters:
            model_config["parameters"] = parameters

    def _set_model_signature(self, model_config: Dict) -> None:
        """Configure model signature  for model deployment on Triton Inference Server.

        Args:
            model_config: Dict with model config for Triton Inference Server

        """

        def _rewrite_io_spec(spec_: TensorSpec) -> Dict:
            if spec_.dtype in [np.object_, object, bytes, np.bytes_]:
                dtype = "TYPE_STRING"
            else:
                # pytype: disable=attribute-error
                dtype = spec_.dtype().dtype
                # pytype: enable=attribute-error
                dtype = f"TYPE_{np_to_triton_dtype(dtype)}"

            dims = spec_.shape

            item = {
                "name": spec_.name,
                "dims": list(dims),
                "data_type": dtype,
            }

            if spec_.optional:
                item["optional"] = True

            if spec_.allow_ragged_batch:
                item["allow_ragged_batch"] = True

            return item

        if self._config.inputs:
            model_config["input"] = [
                _rewrite_io_spec(spec) for spec in self._config.inputs
            ]

        if self._config.outputs:
            outputs = [_rewrite_io_spec(spec) for spec in self._config.outputs]
            if outputs:
                optional_outputs = [o for o in outputs if o.get("optional")]
                if optional_outputs:
                    raise PyTritonBadParameterError(
                        "Optional flag for outputs is not supported. "
                        f"Outputs marked as optional: {', '.join([o['name'] for o in optional_outputs])}."
                    )
                model_config["output"] = outputs

    def _set_response_cache(self, model_config: Dict):
        """Configure response cache for model.

        Args:
            model_config: Dictionary where configuration is attached.
        """
        if self._config.response_cache:
            model_config["response_cache"] = {
                "enable": self._config.response_cache.enable,
            }
