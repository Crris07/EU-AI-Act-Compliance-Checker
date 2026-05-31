import pytest

from src.analysis.llm_client import extract_json


def test_extract_json_from_fenced_block():
    payload = extract_json('```json\n{"summary": "ok", "findings": []}\n```')

    assert payload["summary"] == "ok"
    assert payload["findings"] == []


def test_extract_json_raises_for_invalid_text():
    with pytest.raises(ValueError):
        extract_json("not json")
