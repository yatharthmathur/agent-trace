from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from agenttrace import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "v1" / "trace.schema.json"
FIXTURES = ROOT / "tests" / "fixtures"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validator() -> Draft202012Validator:
    return Draft202012Validator(load_schema(), format_checker=FormatChecker())


def fixture_documents() -> list[tuple[str, dict]]:
    docs = []
    for path in sorted(FIXTURES.glob("*.json")):
        docs.append((path.name, json.loads(path.read_text())))
    return docs


def assert_tree_integrity(document: dict) -> None:
    run_id = document["run"]["id"]
    spans = document["spans"]
    ids = {span["id"] for span in spans}
    assert len(ids) == len(spans), "span ids must be unique"
    for span in spans:
        assert span["run_id"] == run_id
        parent = span["parent_id"]
        if parent is not None:
            assert parent in ids, f"parent_id {parent} is not in this run"
            assert parent != span["id"], "span cannot parent itself"


@pytest.mark.parametrize("name,document", fixture_documents())
def test_fixtures_match_schema(name: str, document: dict) -> None:
    validator().validate(document)


@pytest.mark.parametrize("name,document", fixture_documents())
def test_fixtures_have_a_valid_span_tree(name: str, document: dict) -> None:
    assert_tree_integrity(document)


def test_package_schema_version_matches_export_contract() -> None:
    assert SCHEMA_VERSION == load_schema()["properties"]["schema_version"]["const"]


def test_successful_fixture_records_llm_and_tool_spans() -> None:
    document = json.loads((FIXTURES / "successful_run.json").read_text())
    kinds = [span["kind"] for span in document["spans"]]
    assert kinds.count("llm") == 2
    assert kinds.count("tool") == 1
    assert document["run"]["status"] == "succeeded"


def test_failed_fixture_keeps_the_error_on_the_tool_span() -> None:
    document = json.loads((FIXTURES / "failed_tool_run.json").read_text())
    errors = [span for span in document["spans"] if span["status"] == "error"]
    assert document["run"]["status"] == "failed"
    assert len(errors) == 1
    assert errors[0]["kind"] == "tool"
    assert errors[0]["error"]["type"] == "TimeoutError"


def test_tree_integrity_rejects_a_span_from_another_run() -> None:
    document = _valid_document()
    document["spans"][1]["run_id"] = "99999999-9999-4999-8999-999999999999"
    with pytest.raises(AssertionError):
        assert_tree_integrity(document)


def test_tree_integrity_rejects_a_missing_parent() -> None:
    document = _valid_document()
    document["spans"][1]["parent_id"] = "99999999-9999-4999-8999-999999999999"
    with pytest.raises(AssertionError):
        assert_tree_integrity(document)


def _valid_document() -> dict:
    return copy.deepcopy(json.loads((FIXTURES / "successful_run.json").read_text()))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda doc: doc.pop("schema_version"),
        lambda doc: doc.update(schema_version="0.0.1"),
        lambda doc: doc["spans"][1]["attributes"].pop("model"),
        lambda doc: doc["spans"][2]["attributes"].pop("tool_name"),
        lambda doc: doc["spans"][1].update(kind="error"),
        lambda doc: doc["spans"][2].update(status="error", error=None),
        lambda doc: doc["spans"][1].update(error={"type": "Oops", "message": "nope"}),
        lambda doc: doc["run"].update(status="ok"),
        lambda doc: doc["spans"][0].update(id="not-a-uuid"),
    ],
)
def test_schema_rejects_invalid_documents(mutate) -> None:
    document = _valid_document()
    mutate(document)
    errors = list(validator().iter_errors(document))
    assert errors, "expected the mutated document to be invalid"
