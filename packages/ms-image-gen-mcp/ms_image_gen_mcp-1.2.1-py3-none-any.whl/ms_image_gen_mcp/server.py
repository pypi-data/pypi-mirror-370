import time
import json
import os
import requests

from typing import Annotated, Literal
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


mcp = FastMCP("ms_image_gen_mcp")


@mcp.tool()
def search_models(
    query: Annotated[
        str,
        Field(
            description="Search for models on ModelScope using keywords (e.g., 'Flux' will find models related to Flux). \
                Leave empty to skip keyword matching and get all models based on other filters."
        ),
    ] = "",
    task: Annotated[
        Literal["text-to-image"] | None,
        Field(description="Task category to filter by, only text-to-image is supported now, leave empty to skip task filter"),
    ] = None,
    libraries: Annotated[
        Literal["LoRA"] | None,
        Field(description="Libraries to filter by, only LoRA is supported now, leave empty to skip library filter"),
    ] = None,
    sort: Annotated[
        Literal["Default", "DownloadsCount", "StarsCount", "GmtModified"],
        Field(description="Sort order"),
    ] = "Default",
    limit: Annotated[
        int, Field(description="Number of models to return", ge=1, le=30)
    ] = 10,
) -> list[TextContent]:
    """
    Search for models on ModelScope.
    """
    url = "https://modelscope.cn/api/v1/dolphin/models"

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "modelscope-mcp-server",
    }

    # Build criterion for task filter
    criterion = []
    if task:
        # Map task to API values
        task_mapping = {
            "text-generation": "text-generation",
            "text-to-image": "text-to-image-synthesis",
            "image-to-image": "image-to-image",
        }
        api_task_value = task_mapping.get(task)
        if api_task_value:
            criterion.append(
                {
                    "category": "tasks",
                    "predicate": "contains",
                    "values": [api_task_value],
                    "sub_values": [],
                }
            )

    if libraries:
        criterion.append(
            {
                "category": "libraries",
                "predicate": "equal",
                "values": ["LoRA"],
            }
        )

    # Build single criterion based on filters parameter
    filters = ["support_inference"]
    single_criterion = []
    if filters:
        for filter_type in filters:
            if filter_type == "support_inference":
                single_criterion.append(
                    {
                        "category": "inference_type",
                        "DateType": "int",
                        "predicate": "equal",
                        "IntValue": 1,
                    }
                )

    request_data = {
        "Name": query,
        "Criterion": criterion,
        "SingleCriterion": single_criterion,
        "SortBy": sort,
        "PageNumber": 1,
        "PageSize": limit,
    }

    try:
        response = requests.put(url, json=request_data, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        return [TextContent(type="text", text="Request timeout - please try again later")]

    if response.status_code != 200:
        return [TextContent(type="text", text=f"Server returned non-200 status code: {response.status_code} {response.text}")]

    data = response.json()

    if not data.get("Success", False):
        return [TextContent(type="text", text=f"Server returned error: {data}")]

    models_data = data.get("Data", {}).get("Model", {}).get("Models", [])

    result = []
    for model_data in models_data:
        path = model_data.get("Path", "")
        name = model_data.get("Name", "")

        if not path or not name:
            continue

        model_info = f"ID: {path}/{name}, Name: {model_data.get('ChineseName', name)}, Model Card URL: https://modelscope.cn/models/{path}/{name}, Created By: {model_data.get('CreatedBy', 'Unknown')}, Downloads: {model_data.get('Downloads', 0)}, Stars: {model_data.get('Stars', 0)}"
        result.append(TextContent(type="text", text=model_info))

    return result


@mcp.tool()
def gen_img_url_from_text(
    description: str,
    model: str = "Qwen/Qwen-Image"
) -> list[TextContent]:
    """Generate an image from the input description using ModelScope API, it returns the image URL.

    Args:
        description: the description of the image to be generated, containing the desired elements and visual features.
        model: the model name to be used for image generation, default is "Qwen/Qwen-Image".
    """

    base_url = 'https://api-inference.modelscope.cn/'
    api_key = os.environ.get("MODELSCOPE_API_KEY")
    payload = {
        'model': model,  # ModelScope Model-Id, 必填项
        'prompt': description  # 必填项
    }
    common_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{base_url}v1/images/generations",
        headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
    )

    response.raise_for_status()
    task_id = response.json()["task_id"]

    while True:
        result = requests.get(
            f"{base_url}v1/tasks/{task_id}",
            headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
        )
        result.raise_for_status()
        data = result.json()

        if data["task_status"] == "SUCCEED":
            res = data["output_images"][0]
            break
        elif data["task_status"] == "FAILED":
            res = "Image Generation Failed."
            break

        time.sleep(5)

    return [TextContent(type="text", text=res)]


@mcp.tool()
def gen_img_url_from_text_and_img_url(
    description: str,
    image_url: str,
    model: str = "black-forest-labs/FLUX.1-Kontext-dev"
) -> list[TextContent]:
    """Generate an image from the input description and input image_url using ModelScope API, it returns the image URL.

    Args:
        description: the description of the image to be generated, containing the desired elements and visual features.
        image_url: the image URL to be used as the input image for image generation.
        model: the model name to be used for image generation, default is "black-forest-labs/FLUX.1-Kontext-dev".
    """
    base_url = 'https://api-inference.modelscope.cn/'
    api_key = os.environ.get("MODELSCOPE_API_KEY")
    payload = {
        'model': model,  # ModelScope Model-Id, 必填项
        'prompt': description,  # 必填项
        'image_url': image_url
    }

    common_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{base_url}v1/images/generations",
        headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
    )

    response.raise_for_status()
    task_id = response.json()["task_id"]

    while True:
        result = requests.get(
            f"{base_url}v1/tasks/{task_id}",
            headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
        )
        result.raise_for_status()
        data = result.json()

        if data["task_status"] == "SUCCEED":
            res = data["output_images"][0]
            break
        elif data["task_status"] == "FAILED":
            res = "Image Generation Failed."
            break

        time.sleep(5)

    return [TextContent(type="text", text=res)]


if __name__ == "__main__":
    mcp.run(transport='stdio')

