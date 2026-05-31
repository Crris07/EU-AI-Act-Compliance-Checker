import json
import re

from llama_index.llms.ollama import Ollama
from llama_index.llms.mistralai import MistralAI

from src.analysis.prompts import COMPLIANCE_SYSTEM_PROMPT, COMPLIANCE_USER_PROMPT
from src.config import settings


JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> dict:
    match = JSON_BLOCK_PATTERN.search(text)
    raw = match.group(1) if match else text
    raw = raw.strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]
    return json.loads(raw)


def build_context(retrieved_nodes, max_nodes: int = 3, max_chars_per_node: int = 600) -> str:
    blocks = []
    for index, node in enumerate(retrieved_nodes[:max_nodes], start=1):
        metadata = node.metadata
        label = metadata.get("section_number") or metadata.get("article_number") or f"Source {index}"
        source_type = metadata.get("section_type", "EU AI Act")
        blocks.append(
            "\n".join(
                [
                    f"[{index}] {label} ({source_type})",
                    node.get_content()[:max_chars_per_node],
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)


def get_llm():
    provider = settings.llm_provider.lower().strip()
    if provider == "mistral":
        if not settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY is required when LLM_PROVIDER=mistral.")
        return MistralAI(
            model=settings.mistral_model,
            api_key=settings.mistral_api_key,
            temperature=0.1,
            timeout=120,
        )
    if provider == "ollama":
        return Ollama(
            model=settings.ollama_model,
            request_timeout=300.0,
            context_window=2048,
            json_mode=True,
            additional_kwargs={"num_predict": 512, "num_ctx": 2048},
        )
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")


def analyze_with_llm(description: str, retrieved_nodes) -> dict:
    llm = get_llm()
    prompt = COMPLIANCE_USER_PROMPT.format(
        description=description,
        context=build_context(retrieved_nodes),
    )
    response = llm.complete(f"{COMPLIANCE_SYSTEM_PROMPT}\n\n{prompt}")
    return extract_json(str(response))
