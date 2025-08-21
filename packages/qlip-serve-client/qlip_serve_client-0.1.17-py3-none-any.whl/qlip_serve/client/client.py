import json
from typing import Any, Dict, NoReturn, Optional, Union

import numpy as np
import requests

from ..common.model_config.utils import (
    TRITON_NUMERAL_NP_TYPES,
    deserialize_bytes_tensor,
    np_to_triton_dtype,
    serialize_byte_tensor,
    triton_to_np_dtype,
)
from ..common.payload import (
    FilePayload,
    ImagePayload,
    TensorPayload,
    TextPayload,
)
from ..common.signature import (
    FileSignature,
    ImageSignature,
    TensorSignature,
    TextSignature,
)

__all__ = ["send_triton_request"]


def send_triton_request(
    request_dict: Dict[str, Any],
    metadata_dict: Dict,
    triton_url: str,
    is_sagemaker: bool = False,
    authorization: Optional[str] = None,
) -> Union[Dict[str, Any], NoReturn]:
    """
    Send a request to Triton Inference Server (or SageMaker endpoint).

    :param request_dict: The data to send to Triton, keyed by input signature names.
    :param metadata_dict: Dictionary containing model metadata (including input/output signatures).
    :param triton_url: The full URL of the Triton (or SageMaker) endpoint.
    :param is_sagemaker: If True, the request will be formatted for a SageMaker Triton endpoint.
    :param authorization: Optional authorization header (e.g. 'Basic <base64-encoded-credentials>')
                         or any other token you want to pass along in the 'Authorization' header.
    :return: A dictionary of output payloads, keyed by output signature name.
    :raises ValueError: If the request fails or if data types are unsupported.
    """

    model_metadata = metadata_dict["model"]

    # TODO: refactor Payload(Signature and make it more generic with DRY
    # Prepare input payload objects
    input_payload_dict = {}
    for input_signature in metadata_dict["inputs"]:
        if input_signature["signature_type"] == "image":
            input_payload_dict[input_signature["name"]] = ImagePayload(
                signature=ImageSignature(
                    shape=input_signature["shape"],
                    dtype=triton_to_np_dtype(input_signature["dtype"]),
                    name=input_signature["name"],
                    optional=input_signature["optional"],
                    allow_ragged_batch=input_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        elif input_signature["signature_type"] == "text":
            input_payload_dict[input_signature["name"]] = TextPayload(
                signature=TextSignature(
                    shape=input_signature["shape"],
                    dtype=triton_to_np_dtype(input_signature["dtype"]),
                    name=input_signature["name"],
                    optional=input_signature["optional"],
                    allow_ragged_batch=input_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        elif input_signature["signature_type"] == "tensor":
            input_payload_dict[input_signature["name"]] = TensorPayload(
                signature=TensorSignature(
                    shape=input_signature["shape"],
                    dtype=triton_to_np_dtype(input_signature["dtype"]),
                    name=input_signature["name"],
                    optional=input_signature["optional"],
                    allow_ragged_batch=input_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        elif input_signature["signature_type"] == "file":
            input_payload_dict[input_signature["name"]] = FilePayload(
                signature=FileSignature(
                    shape=input_signature["shape"],
                    dtype=triton_to_np_dtype(input_signature["dtype"]),
                    name=input_signature["name"],
                    optional=input_signature["optional"],
                    allow_ragged_batch=input_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        else:
            raise ValueError(
                f"Unsupported signature type: {input_signature['signature_type']}"
            )

    # Prepare output payload objects
    output_payloads_dict = {}
    for output_signature in metadata_dict["outputs"]:
        if output_signature["signature_type"] == "image":
            output_payloads_dict[output_signature["name"]] = ImagePayload(
                signature=ImageSignature(
                    shape=output_signature["shape"],
                    dtype=triton_to_np_dtype(output_signature["dtype"]),
                    name=output_signature["name"],
                    optional=output_signature["optional"],
                    allow_ragged_batch=output_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        elif output_signature["signature_type"] == "text":
            output_payloads_dict[output_signature["name"]] = TextPayload(
                signature=TextSignature(
                    shape=output_signature["shape"],
                    dtype=triton_to_np_dtype(output_signature["dtype"]),
                    name=output_signature["name"],
                    optional=output_signature["optional"],
                    allow_ragged_batch=output_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        elif output_signature["signature_type"] == "tensor":
            output_payloads_dict[output_signature["name"]] = TensorPayload(
                signature=TensorSignature(
                    shape=output_signature["shape"],
                    dtype=triton_to_np_dtype(output_signature["dtype"]),
                    name=output_signature["name"],
                    optional=output_signature["optional"],
                    allow_ragged_batch=output_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        elif output_signature["signature_type"] == "file":
            output_payloads_dict[output_signature["name"]] = FilePayload(
                signature=FileSignature(
                    shape=output_signature["shape"],
                    dtype=triton_to_np_dtype(output_signature["dtype"]),
                    name=output_signature["name"],
                    optional=output_signature["optional"],
                    allow_ragged_batch=output_signature["allow_ragged_batch"],
                ),
                model_metadata=model_metadata,
            )
        else:
            raise ValueError(
                f"Unsupported signature type: {output_signature['signature_type']}"
            )

    # Serialize inputs
    serialized_bytes = b""
    json_header = {"model_name": model_metadata["name"], "inputs": [], "outputs": []}
    for payload_name, payload in input_payload_dict.items():
        if payload_name not in request_dict:
            raise ValueError(
                # TODO: better input_signature str repr for the error message
                f"Input data for the signature {payload_name} is missing"
            )

        payload.load(request_dict[payload_name])
        # TODO: add different types of serialization (BOOL?)
        # https://github.com/triton-inference-server/client/blob/main/src/python/library/tritonclient/utils/__init__.py
        if payload.signature.dtype in TRITON_NUMERAL_NP_TYPES:
            serialized_bytes_tensor = payload.data.tobytes()
            serialized_bytes += serialized_bytes_tensor
        elif (
            payload.signature.dtype == np.bytes_
            or payload.signature.dtype == np.object_
        ):
            serialized_bytes_tensor = serialize_byte_tensor(payload.data)
            serialized_bytes += serialized_bytes_tensor
        else:
            raise ValueError(
                f"Unsupported dtype for the serialization: {payload.signature.dtype}"
            )

        json_header["inputs"].append(
            {
                "name": payload.signature.name,
                "datatype": np_to_triton_dtype(payload.signature.dtype),
                "shape": list(payload.data.shape),
                "parameters": {"binary_data_size": len(serialized_bytes_tensor)},
            }
        )

    # Prepare output requests
    for output_signature_name, output_signature in output_payloads_dict.items():
        json_header["outputs"].append(
            {
                "name": output_signature.signature.name,
                "parameters": {"binary_data": True},
            }
        )

    # Build final request body
    json_header_str = json.dumps(json_header)
    header_length = str(len(json_header_str))

    request_body = json_header_str.encode() + serialized_bytes

    # Set headers
    if is_sagemaker:
        headers = {
            "Content-Type": (
                f"application/vnd.sagemaker-triton.binary+json;json-header-size={header_length}"
            )
        }
    else:
        headers = {
            "Content-Type": "application/octet-stream",
            "Inference-Header-Content-Length": header_length,
            "Content-Length": str(len(request_body)),
        }

    # # Print without data!
    # print(payload)
    # print(json.dumps(payload, indent=4))

    # Optionally add the Authorization header
    if authorization:
        headers["Authorization"] = authorization

    # Send POST request
    response = requests.post(
        triton_url,
        data=request_body,
        headers=headers,
    )

    # Handle the response (for Triton vs SageMaker)
    if is_sagemaker:
        if (
            response.status_code != 200
            or "application/vnd.sagemaker-triton.binary+json"
            not in response.headers.get("Content-Type", "")
        ):
            raise ValueError(
                f"Failed with status code: {response.status_code}, Response: {response.content}"
            )
        json_header_size = int(
            response.headers["Content-Type"].split(";")[1].split("=")[1]
        )
    else:
        if (
            response.status_code != 200
            or "application/octet-stream"
            not in response.headers.get("Content-Type", "")
        ):
            raise ValueError(
                f"Failed with status code: {response.status_code}, Response: {response.content}"
            )
        json_header_size = int(response.headers["Inference-Header-Content-Length"])

    # Extract JSON header
    json_header = json.loads(response.content[:json_header_size])

    # TODO: when we need +4 ? like in bytes example
    response_content_i = json_header_size

    # TODO: debug add
    # print(json_header)

    # TODO: Check if all outputs are returned?
    # TODO: Check return types!!!
    # for output_payload_name, output_payload in output_payloads_dict.items():
    # print(output_payload_name)
    # print(output_payloads_dict[output_payload_name].data)

    # Parse outputs
    for out in json_header["outputs"]:
        if out["name"] not in output_payloads_dict:
            raise requests.exceptions.HTTPError(
                f"Missing expected output '{out['name']}' in response, "
                f"status code {response.status_code}"
            )

        out_content = response.content[
            response_content_i : response_content_i
            + out["parameters"]["binary_data_size"]
        ]

        if out_content == b"":
            raise ValueError(f"Empty output content for '{out['name']}'")

        out_datatype = triton_to_np_dtype(out["datatype"])
        if out_datatype in TRITON_NUMERAL_NP_TYPES:
            payload = output_payloads_dict[out["name"]]
            payload.data = np.array(
                np.frombuffer(
                    out_content,
                    dtype=out_datatype,
                ).reshape(out["shape"])
            )
        elif out["datatype"] == "BYTES":
            # TODO: add support for the arrays (now only scalars?) to avoid array inputs
            output_payload = output_payloads_dict[out["name"]]
            output_payload.data = deserialize_bytes_tensor(out_content)
        else:
            raise ValueError(
                f"Unsupported dtype for the deserialization: {out['datatype']}"
            )

        response_content_i += out["parameters"]["binary_data_size"]

    # Return the dictionary of output payload objects
    return output_payloads_dict
