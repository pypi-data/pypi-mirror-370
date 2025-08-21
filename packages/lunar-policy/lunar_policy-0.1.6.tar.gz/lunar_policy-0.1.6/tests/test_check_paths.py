import json
import pytest

from src.lunar_policy import Check, Path, ComponentData


class TestCheckPaths:
    def test_path_in_check(self, capsys):
        data = ComponentData.from_component_json(json.dumps({
            "value": True,
        }))

        with Check("test", data=data) as c:
            c.assert_true(Path(".value"))

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".value"]

    def test_multiple_paths_in_check(self, capsys):
        data = ComponentData.from_component_json(json.dumps({
            "true_value": True,
            "false_value": False
        }))

        with Check("test", data=data) as c:
            v = c.get(".false_value")
            c.assert_false(v)
            c.assert_true(Path(".true_value"))

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".false_value", ".true_value"]

    def test_money_path(self, capsys):
        data = ComponentData.from_component_json(json.dumps({
            "true_value": True,
            "false_value": False
        }))

        with Check("test", data=data) as c:
            v = c.get(".false_value")
            c.assert_false(v)
            c.assert_true(Path(".true_value"))

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".false_value", ".true_value"]

    def test_tricky_path(self, capsys):
        data = ComponentData.from_component_json(json.dumps({
            "tricky_value": ".true_value",
            ".true_value": True
        }))

        with Check("test", data=data) as c:
            v = c.get("$.tricky_value")
            c.assert_equals(v, ".true_value")

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == [".tricky_value"]

    def test_paths_not_in_check(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)

        assert result["paths"] == []

    def test_get_invalid_path(self):
        data = ComponentData.from_component_json("{}")

        with pytest.raises(ValueError):
            with Check("test", data=data) as c:
                c.get("@#&*(!%)")
