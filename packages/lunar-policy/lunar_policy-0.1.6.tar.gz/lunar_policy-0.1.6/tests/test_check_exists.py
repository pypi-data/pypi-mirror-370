import json

from src.lunar_policy import Check, ComponentData


class TestCheckExists:
    def test_exists_valid_path_workflows_finished(self):
        data = ComponentData.from_component_json(json.dumps({
            "hi": "there"
        }), bundle_info={"workflows_finished": True})

        with Check("test", data=data) as c:
            assert c.exists(".hi")

    def test_exists_valid_path_workflows_not_finished(self):
        data = ComponentData.from_component_json(json.dumps({
            "hi": "there"
        }), bundle_info={"workflows_finished": False})

        with Check("test", data=data) as c:
            assert c.exists(".hi")

    def test_exists_missing_path_workflows_finished(self):
        data = ComponentData.from_component_json(
            "{}",
            bundle_info={"workflows_finished": True}
        )

        with Check("test", data=data) as c:
            assert not c.exists(".missing")

    def test_exists_missing_path_workflows_not_finished(self, capsys):
        data = ComponentData.from_component_json(
            "{}",
            bundle_info={"workflows_finished": False}
        )

        with Check("test", data=data) as c:
            c.exists(".missing")
            c.assert_equals("should not run", "should not run")

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no-data"
        assert ".missing" in results[0]["failure_message"]
        assert results[0]["op"] == "fail"
