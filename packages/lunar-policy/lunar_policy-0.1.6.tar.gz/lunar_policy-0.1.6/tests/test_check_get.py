import json
import pytest

from src.lunar_policy import Check, ComponentData


class TestCheckGet:
    def test_get_valid_path_workflows_finished(self):
        data = ComponentData.from_component_json(json.dumps({
            "hi": "there"
        }), bundle_info={"workflows_finished": True})

        with Check("test", data=data) as c:
            c.get(".hi")

    def test_get_valid_path_workflows_not_finished(self):
        data = ComponentData.from_component_json(json.dumps({
            "hi": "there"
        }), bundle_info={"workflows_finished": False})

        with Check("test", data=data) as c:
            c.get(".hi")

    def test_get_missing_path_workflows_finished(self):
        data = ComponentData.from_component_json(
            "{}",
            bundle_info={"workflows_finished": True}
        )

        with pytest.raises(ValueError):
            with Check("test", data=data) as c:
                c.get(".missing")

    def test_get_missing_path_workflows_not_finished(self, capsys):
        data = ComponentData.from_component_json(
            "{}",
            bundle_info={"workflows_finished": False}
        )

        with Check("test", data=data) as c:
            c.get(".missing")

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no-data"
        assert ".missing" in results[0]["failure_message"]
        assert results[0]["op"] == "fail"

    def test_get_invalid_path(self):
        data = ComponentData.from_component_json("{}")

        with pytest.raises(ValueError):
            with Check("test", data=data) as c:
                c.get("@#$@#$@#$")

    def test_get_all_valid_path_single(self):
        data = ComponentData.from_json(json.dumps({
            "bundle_info": {},
            "merged_blob": {},
            "metadata_instances": [
                {
                    "payload": {
                        "hi": "there"
                    }
                }
            ]
        }))

        all = []
        with Check("test", data=data) as c:
            all = c.get_all(".hi")

        assert all == ["there"]

    def test_get_all_valid_path_multiple(self):
        data = ComponentData.from_json(json.dumps({
            "bundle_info": {},
            "merged_blob": {},
            "metadata_instances": [
                {
                    "payload": {
                        "hi": "there"
                    }
                },
                {
                    "payload": {
                        "hi": "there"
                    }
                }
            ]
        }))

        all = []
        with Check("test", data=data) as c:
            all = c.get_all(".hi")

        assert all == ["there", "there"]

    def test_get_all_invalid_path(self):
        data = ComponentData.from_component_json("{}")

        with pytest.raises(ValueError):
            with Check("test", data=data) as c:
                c.get_all("@#$@#$@#$")
