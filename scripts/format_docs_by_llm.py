import getpass
import json
import os
import sys
from pathlib import Path
from textwrap import dedent

from cost import calculate_cost
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from pydantic import BaseModel, Field
from tqdm import tqdm

from src.constants import SUPPORTED_PENNYLANE_VERSIONS

load_dotenv(verbose=True)
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

OPENAI_MODEL_VERSION = "gpt-4.1-2025-04-14"

REF_DOCS_DIRC = Path(__file__).parent.parent.absolute() / "refdocs" / "pennylane"
RAW_JSON_DIR = REF_DOCS_DIRC / "raw"
FORMATTED_JSON_DIR = REF_DOCS_DIRC / "formatted"


class Arg(BaseModel):
    name: str = Field(..., description="The name of the argument.")
    type: str = Field(..., description="The type of the argument.")
    required: bool = Field(..., description="Whether the argument is required.")
    description: str = Field(..., description="The description of the argument.")


class APIDocResult(BaseModel):
    args: list[Arg] = Field(..., description="The arguments of the method.")
    description: str = Field(..., description="The description of the method.")


def get_prompt_template() -> ChatPromptTemplate:
    system_prompt_template = dedent(
        """
        You are a software engineer with excellent explanatory skills.
        You will be provided with the method name, its arguments and their types, 
        the method's docstring, and the method's source code.

        Your task is to extract each argument's name and type;
        for each argument, generate a description of the values that should be supplied; 
        and produce a detailed explanation of the method's functionality and intended usage.

        When creating all descriptions, use only the provided source code and docstring—prioritizing 
        the source code whenever the docstring may be outdated or conflicting.
        """
    )

    user_prompt_template = """
            Please format the following method information into a structured format.

            # Method Information
            {formatted_method_info}

            # Output Format
            ```json
            {{
            "args": [
                {{
                "name": "argment name",
                "type": "argment type",
                "required": True,
                "description": "The description of the argument."
                }},
                {{
                "name": "argment name",
                "type": "argment type",
                "required": False,
                "description": "The description of the argument."
                }}
            ],
            "description": "detailed description of the method"
            }}
            ```
            """

    return ChatPromptTemplate.from_messages([("system", system_prompt_template), ("user", user_prompt_template)])


def format_method_info(method_name: str, method_info: dict) -> str:
    return f"""
    Method: {method_name}
    Signature: {method_info['signature']}
    Docstring: {method_info['docstring']}
    Source: {method_info['source']}
    """


def format_docs_by_llm(versions: list[str]) -> None:
    model = init_chat_model(
        model_provider="openai", model=OPENAI_MODEL_VERSION, temperature=0.0, timeout=1000
    ).with_structured_output(APIDocResult, include_raw=True)
    prompt_template = get_prompt_template()
    total_cost = 0.0

    for version in versions:
        with open(RAW_JSON_DIR / f"{version}.json", "r") as f:
            api_docs = json.load(f)

        results_dict = {}
        for i, (method_name, method_info) in enumerate(tqdm(api_docs.items())):
            formatted_method_info = format_method_info(method_name, method_info)
            prompt = prompt_template.invoke({"formatted_method_info": formatted_method_info})

            response = model.invoke(prompt)
            metadata = response["raw"].usage_metadata  # type: ignore
            result = response["parsed"].model_dump()  # type: ignore
            results_dict[method_name] = result

            cost = calculate_cost(
                input_tokens=metadata.get("input_tokens", 0),
                cached_tokens=metadata.get("cached_tokens", 0),
                output_tokens=metadata.get("output_tokens", 0),
                model_version=OPENAI_MODEL_VERSION,
            )
            total_cost += cost

            if i % 30 == 0:
                with open(FORMATTED_JSON_DIR / f"{version}.json", "w") as f:
                    json.dump(results_dict, f)
                logger.info(f"Saved {i} methods. Cost: ${total_cost}")

        logger.info(f"All {version} methods processed. Cost: ${total_cost}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            """No version specified. Using default supported versions.
        If you want to specify a version, please use the following format:
        python format_docs_by_llm.py <version1>,<version2>,<version3>
        """
        )
        versions = SUPPORTED_PENNYLANE_VERSIONS
    else:
        versions = sys.argv[1].split(",")

    format_docs_by_llm(versions)
