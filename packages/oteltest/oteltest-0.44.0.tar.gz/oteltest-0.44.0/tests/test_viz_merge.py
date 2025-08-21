import json
from pathlib import Path

import pytest

from oteltest.viz import normalize_telemetry, normalize_traces, normalize_metrics

# Use pathlib to construct the fixture path robustly
TEST_JSON_PATH = Path(__file__).parent / "fixtures" / "agent_with_tools.json"


@pytest.fixture
def trace_data():
    with open(TEST_JSON_PATH) as f:
        return json.load(f)


def test_merge_resource_spans(trace_data):
    merged_data = normalize_telemetry(trace_data)
    merged = merged_data["traces"]
    seen = set()
    for resource_span in merged:
        attrs = resource_span.get("resource", {}).get("attributes", [])
        key = tuple(sorted((a["key"], json.dumps(a["value"], sort_keys=True)) for a in attrs))
        assert key not in seen, f"Duplicate resource found: {key}"
        seen.add(key)
    assert len(merged) > 0
    for resource_span in merged:
        assert "scopeSpans" in resource_span
        for scope_span in resource_span["scopeSpans"]:
            assert "spans" in scope_span
            assert isinstance(scope_span["spans"], list)


def test_scope_merge():
    resource_attrs = [{"key": "service.name", "value": {"stringValue": "test-service"}}]

    trace_req1 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "test-scope", "version": "1.0"},
                            "spans": [{"spanId": "1", "name": "span-1"}],
                        }
                    ],
                }
            ]
        }
    }

    trace_req2 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "test-scope", "version": "1.0"},
                            "spans": [{"spanId": "2", "name": "span-2"}],
                        }
                    ],
                }
            ]
        }
    }

    trace_req3 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "test-scope-2", "version": "1.0"},
                            "spans": [{"spanId": "3", "name": "span-3"}],
                        }
                    ],
                }
            ]
        }
    }

    merged = normalize_traces([trace_req1, trace_req2, trace_req3])

    assert len(merged) == 1
    resource_span = merged[0]

    assert len(resource_span["scopeSpans"]) == 2

    scope1 = None
    scope2 = None
    for scope in resource_span["scopeSpans"]:
        if scope["scope"]["name"] == "test-scope":
            scope1 = scope
        elif scope["scope"]["name"] == "test-scope-2":
            scope2 = scope

    assert scope1 is not None
    assert scope2 is not None

    spans1 = scope1["spans"]
    assert len(spans1) == 2
    span_ids = {span["spanId"] for span in spans1}
    assert span_ids == {"1", "2"}

    spans2 = scope2["spans"]
    assert len(spans2) == 1
    assert spans2[0]["spanId"] == "3"


def test_multiple_resources_with_scopes():
    resource1_attrs = [{"key": "service.name", "value": {"stringValue": "service-1"}}]
    resource2_attrs = [{"key": "service.name", "value": {"stringValue": "service-2"}}]

    trace_req1 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource1_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "scope-A", "version": "1.0"},
                            "spans": [{"spanId": "1", "name": "res1-scopeA-span1"}],
                        }
                    ],
                }
            ]
        }
    }

    trace_req2 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource1_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "scope-B", "version": "1.0"},
                            "spans": [{"spanId": "2", "name": "res1-scopeB-span1"}],
                        }
                    ],
                }
            ]
        }
    }

    trace_req3 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource1_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "scope-A", "version": "1.0"},
                            "spans": [{"spanId": "3", "name": "res1-scopeA-span2"}],
                        }
                    ],
                }
            ]
        }
    }

    trace_req4 = {
        "pbreq": {
            "resourceSpans": [
                {
                    "resource": {"attributes": resource2_attrs},
                    "scopeSpans": [
                        {
                            "scope": {"name": "scope-A", "version": "1.0"},
                            "spans": [{"spanId": "4", "name": "res2-scopeA-span1"}],
                        }
                    ],
                }
            ]
        }
    }

    merged = normalize_traces([trace_req1, trace_req2, trace_req3, trace_req4])

    assert len(merged) == 2

    res1 = None
    res2 = None
    for resource in merged:
        attrs = resource.get("resource", {}).get("attributes", [])
        service_name = None
        for attr in attrs:
            if attr.get("key") == "service.name":
                service_name = attr.get("value", {}).get("stringValue")
        if service_name == "service-1":
            res1 = resource
        elif service_name == "service-2":
            res2 = resource

    assert res1 is not None
    assert res2 is not None

    assert len(res1["scopeSpans"]) == 2
    scope_map_res1 = {}
    for scope in res1["scopeSpans"]:
        scope_name = scope["scope"]["name"]
        scope_map_res1[scope_name] = scope

    assert "scope-A" in scope_map_res1
    scope_a_res1 = scope_map_res1["scope-A"]
    spans_a_res1 = scope_a_res1["spans"]
    assert len(spans_a_res1) == 2
    span_ids_a_res1 = {span["spanId"] for span in spans_a_res1}
    assert span_ids_a_res1 == {"1", "3"}

    assert "scope-B" in scope_map_res1
    scope_b_res1 = scope_map_res1["scope-B"]
    spans_b_res1 = scope_b_res1["spans"]
    assert len(spans_b_res1) == 1
    assert spans_b_res1[0]["spanId"] == "2"

    assert len(res2["scopeSpans"]) == 1
    scope_a_res2 = res2["scopeSpans"][0]
    assert scope_a_res2["scope"]["name"] == "scope-A"
    spans_a_res2 = scope_a_res2["spans"]
    assert len(spans_a_res2) == 1
    assert spans_a_res2[0]["spanId"] == "4"


def test_normalize_metrics_empty():
    # Should return an empty list or dict when given empty input
    result = normalize_metrics([])
    assert result == [] or result == {}  # Accept either, depending on implementation


def test_normalize_metrics_single_metric():
    metric_req = {
        "pbreq": {
            "resourceMetrics": [
                {
                    "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "svc"}}]},
                    "scopeMetrics": [
                        {
                            "scope": {"name": "test-scope", "version": "1.0"},
                            "metrics": [
                                {"name": "metric1", "sum": 42}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    result = normalize_metrics([metric_req])
    assert isinstance(result, list)
    assert len(result) == 1
    res = result[0]
    assert "resource" in res
    assert "scopeMetrics" in res
    assert len(res["scopeMetrics"]) == 1
    scope = res["scopeMetrics"][0]
    assert "metrics" in scope
    assert len(scope["metrics"]) == 1
    assert scope["metrics"][0]["name"] == "metric1"


def test_normalize_metrics_merge_resources_and_scopes():
    resource1 = [{"key": "service.name", "value": {"stringValue": "svc1"}}]
    resource2 = [{"key": "service.name", "value": {"stringValue": "svc2"}}]
    metric_req1 = {
        "pbreq": {
            "resourceMetrics": [
                {
                    "resource": {"attributes": resource1},
                    "scopeMetrics": [
                        {
                            "scope": {"name": "scopeA", "version": "1.0"},
                            "metrics": [
                                {"name": "m1", "sum": 1}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    metric_req2 = {
        "pbreq": {
            "resourceMetrics": [
                {
                    "resource": {"attributes": resource1},
                    "scopeMetrics": [
                        {
                            "scope": {"name": "scopeA", "version": "1.0"},
                            "metrics": [
                                {"name": "m2", "sum": 2}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    metric_req3 = {
        "pbreq": {
            "resourceMetrics": [
                {
                    "resource": {"attributes": resource2},
                    "scopeMetrics": [
                        {
                            "scope": {"name": "scopeB", "version": "1.0"},
                            "metrics": [
                                {"name": "m3", "sum": 3}
                            ]
                        }
                    ]
                }
            ]
        }
    }
    merged = normalize_metrics([metric_req1, metric_req2, metric_req3])
    assert isinstance(merged, list)
    assert len(merged) == 2  # Two resources
    svc_names = set()
    for res in merged:
        attrs = res.get("resource", {}).get("attributes", [])
        for attr in attrs:
            if attr.get("key") == "service.name":
                svc_names.add(attr.get("value", {}).get("stringValue"))
    assert svc_names == {"svc1", "svc2"}
    # Check that metrics are merged by scope
    for res in merged:
        for scope in res["scopeMetrics"]:
            assert "metrics" in scope
            assert isinstance(scope["metrics"], list)
