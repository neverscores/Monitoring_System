import pytest
from collector.metrics import collect_metrics

def test_collect_metrics_structure():
    data = collect_metrics()

    # Check top-level keys
    assert "timestamp" in data
    assert "hostname" in data
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data

    # Check CPU structure
    cpu = data["cpu"]
    assert "per_core" in cpu
    assert "average" in cpu
    assert isinstance(cpu["per_core"], list)
    assert isinstance(cpu["average"], float)

    # Check memory structure
    memory = data["memory"]
    for key in ["total", "used", "free", "percent"]:
        assert key in memory
        assert isinstance(memory[key], (int, float))

    # Check disk structure
    disk = data["disk"]
    for key in ["total", "used", "free", "percent"]:
        assert key in disk
        assert isinstance(disk[key], (int, float))
