import pytest

from src.lunar_policy import Check, CheckStatus, ComponentData, Path


class TestCheckName:
    def test_name(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(True)

        assert c.name == "test"


class TestCheckFailureReasons:
    def test_failure_reasons_single(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.fail("this failed")

        assert c.failure_reasons == ["this failed"]

    def test_failure_reasons_multiple(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.fail("this failed")
            c.fail("this failed too")

        assert c.failure_reasons == ["this failed", "this failed too"]


class TestCheckStatus:
    def test_status_pass(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(True)

        assert c.status == CheckStatus.PASS

    def test_status_fail(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.fail("this failed")

        assert c.status == CheckStatus.FAIL

    def test_status_no_data(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(Path(".not.a.path"))

        assert c.status == CheckStatus.NO_DATA

    def test_status_error(self):
        data = ComponentData.from_component_json("{}")

        with pytest.raises(Exception):
            with Check("test", data=data) as c:
                raise Exception("this is an error")

        assert c.status == CheckStatus.ERROR

    def test_status_no_assertions(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            pass

        assert c.status == CheckStatus.PASS

    def test_fail_before_pass(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(True)
            c.fail("this failed")

        assert c.status == CheckStatus.FAIL

    def test_no_data_before_pass(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(True)
            c.assert_true(Path(".not.a.path"))

        assert c.status == CheckStatus.NO_DATA

    def test_no_data_before_fail(self):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.fail("this failed")
            c.assert_true(Path(".not.a.path"))

        assert c.status == CheckStatus.NO_DATA
