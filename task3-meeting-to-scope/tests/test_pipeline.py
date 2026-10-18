from agents.pipeline import estimate_hours, compare_with_baseline

def test_estimate_hours_sums_tasks():
    result = estimate_hours([{"task": "A", "hours": 2}, {"task": "B", "hours": 3}])
    assert result["total_hours"] == 5

def test_scope_comparison_flags_new_work():
    result = compare_with_baseline(["Add contact form"], ["Add contact form", "Build mobile app"])
    assert result["in_scope"] == ["Add contact form"]
    assert result["potential_out_of_scope"] == ["Build mobile app"]
    assert result["requires_human_approval"] is True
