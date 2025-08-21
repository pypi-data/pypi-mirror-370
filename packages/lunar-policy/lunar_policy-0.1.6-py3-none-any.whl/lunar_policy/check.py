import json
import os
import re
from typing import Any, Callable, List, Optional
from pathlib import Path as FSPath

from .data import Path, ComponentData
from .result import AssertionResult, Op, CheckStatus, NoDataError


class Check:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        data: Optional[ComponentData] = None
    ):
        self._name = name
        self._description = description
        self._accessed_paths = []
        self._used_vars = []
        self._results = []
        self._submitted = False

        if data is None:
            try:
                path = os.environ["LUNAR_BUNDLE_PATH"]
            except KeyError:
                raise ValueError(
                    "LUNAR_BUNDLE_PATH is not set"
                )

            try:
                data = ComponentData.from_file(FSPath(path))
            except ValueError as e:
                raise ValueError(
                    "invalid LUNAR_BUNDLE_PATH"
                ) from e
            except FileNotFoundError:
                raise ValueError(
                    f"LUNAR_BUNDLE_PATH does not exist: {path}"
                )

        if not isinstance(data, ComponentData):
            raise ValueError(
                f"Data must be a ComponentData instance, got {data}"
            )
        self._data = data

    # Context Manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        suppressable_no_data = (isinstance(exc_value, NoDataError) and
                                not self._data.workflows_finished())

        if exc_value is not None:
            if suppressable_no_data:
                self._results.append(
                    AssertionResult(
                        op=Op.FAIL,
                        args=[],
                        result=CheckStatus.NO_DATA,
                        failure_message=str(exc_value)
                    )
                )
            else:
                self._results.append(
                    AssertionResult(
                        op=Op.FAIL,
                        args=[],
                        result=CheckStatus.ERROR,
                        failure_message=f"Unexpected error: {exc_value}"
                    )
                )

        self._submit()
        return suppressable_no_data

    # Properties

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> CheckStatus:
        if not self._results:
            return CheckStatus.PASS

        has_no_data = False
        has_fail = False
        has_error = False

        for result in self._results:
            if result.result == CheckStatus.ERROR:
                has_error = True
            if result.result == CheckStatus.NO_DATA:
                has_no_data = True
            if result.result == CheckStatus.FAIL:
                has_fail = True

        if has_error:
            return CheckStatus.ERROR
        if has_no_data:
            return CheckStatus.NO_DATA
        elif has_fail:
            return CheckStatus.FAIL

        return CheckStatus.PASS

    @property
    def failure_reasons(self) -> list:
        failure_messages = [
            result.failure_message
            for result in self._results
            if (result.result == CheckStatus.FAIL and
                result.failure_message is not None)
        ]
        return failure_messages

    # JSON Path value getters

    def get(self, path: str) -> Any:
        try:
            jsonPath = Path(path)
        except ValueError as e:
            raise ValueError(f"Invalid JSON path: {path}") from e

        result = self._data.get_merged(jsonPath)
        self._accessed_paths.extend(result.paths)
        return result.value

    def get_all(self, path: str) -> List[Any]:
        try:
            jsonPath = Path(path)
        except ValueError as e:
            raise ValueError(f"Invalid JSON path: {path}") from e

        results = self._data.get_all(jsonPath)
        self._accessed_paths.extend(p for r in results for p in r.paths)
        return [r.value for r in results]

    def exists(self, path: str) -> bool:
        jsonPath = Path(path)

        try:
            result = self._data.get_merged(jsonPath)
            self._accessed_paths.extend(result.paths)
        except ValueError:
            return False

        return True

    # Assertions

    def fail(
        self,
        failure_message: Optional[str] = None
    ) -> None:
        self._make_assertion(
            Op.FAIL,
            lambda v: False,
            False,
            False,
            failure_message or "Policy Forced Failure"
        )

    def assert_true(
        self,
        value: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.TRUE,
            lambda v: v is True,
            value,
            all_instances,
            failure_message or f"{value} is not true",
        )

    def assert_false(
        self,
        value: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.FALSE,
            lambda v: v is False,
            value,
            all_instances,
            failure_message or f"{value} is not false",
        )

    def assert_equals(
        self,
        value: Any,
        expected: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.EQUALS,
            lambda v: v == expected,
            value,
            all_instances,
            failure_message or f"{value} is not equal to {expected}",
        )

    def assert_contains(
        self,
        value: Any,
        expected: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.CONTAINS,
            lambda v: expected in v,
            value,
            all_instances,
            failure_message or f"{value} does not contain {expected}",
        )

    def assert_greater(
        self,
        value: Any,
        expected: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ):
        self._make_assertion(
            Op.GREATER,
            lambda v: v > expected,
            value,
            all_instances,
            failure_message or f"{value} is not greater than {expected}",
        )

    def assert_greater_or_equal(
        self,
        value: Any,
        expected: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.GREATER_OR_EQUAL,
            lambda v: v >= expected,
            value,
            all_instances,
            failure_message or
            f"{value} is not greater than or equal to {expected}",
        )

    def assert_less(
        self,
        value: Any,
        expected: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.LESS,
            lambda v: v < expected,
            value,
            all_instances,
            failure_message or f"{value} is not less than {expected}",
        )

    def assert_less_or_equal(
        self,
        value: Any,
        expected: Any,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.LESS_OR_EQUAL,
            lambda v: v <= expected,
            value,
            all_instances,
            failure_message or
            f"{value} is not less than or equal to {expected}",
        )

    def assert_match(
        self,
        value: Any,
        pattern: str,
        failure_message: Optional[str] = None,
        all_instances: bool = False
    ) -> None:
        self._make_assertion(
            Op.MATCH,
            lambda v: re.match(pattern, v) is not None,
            value,
            all_instances,
            failure_message or f"{value} does not match {pattern}",
        )

    def assert_exists(
        self,
        value: Any,
        failure_message: Optional[str] = None
    ) -> None:
        # This assertion behaves differently than the others, so it gets its
        # own implementation. Does not support all_instances. Normal no-data
        # behavior before workflows completed, fail afterward.

        try:
            self._make_assertion(
                Op.EXISTS,
                lambda v: v is not None,
                value,
                False,
                failure_message or f"{value} does not exist",
            )
        except ValueError:
            self._results.append(
                AssertionResult(
                    op=Op.FAIL,
                    args=[],
                    result=CheckStatus.FAIL,
                    failure_message=(
                        failure_message
                        or f"{value} does not exist"
                    )
                )
            )

    # Private methods

    def _submit(self):
        if not self._submitted:
            output = {
                "name": self._name,
                "assertions": [
                    result.toJson()
                    for result in self._results
                ]
            }

            output["paths"] = list(dict.fromkeys(
                p if p.startswith('.') else f'.{p}'
                for p in self._accessed_paths
            ))

            if self._description is not None:
                output["description"] = self._description

            prefix = os.environ.get("LUNAR_LOG_PREFIX", "")
            print(f"{prefix}{json.dumps(output)}")

            self._submitted = True

    def _get_query_result(
        self,
        value: Any,
        all_instances: bool
    ) -> tuple[Any, list[str]]:
        if not isinstance(value, Path):
            return value, []

        if self._data is None:
            return None, []

        if all_instances:
            results = self._data.get_all(value)
            if not results:
                return None, []
            values = [r.value for r in results]
            paths = [p for r in results for p in r.paths]
            return values, paths
        else:
            result = self._data.get_merged(value)
            if result is None:
                return None, []
            return result.value, result.paths

    def _make_assertion(
        self,
        op: Op,
        check_fn: Callable[[Any], bool],
        value: Any,
        all_instances: bool,
        failure_message: str,
    ):
        actual_value, paths = self._get_query_result(value, all_instances)
        self._accessed_paths.extend(paths)

        if actual_value is None:
            raise NoDataError("Value was None")

        if all_instances:
            if not isinstance(actual_value, list):
                actual_value = [actual_value]
            ok = all(check_fn(v) for v in actual_value)
        else:
            ok = check_fn(actual_value)

        try:
            # We don't care about the actual value,
            # we just want to make sure its serializable at submission time
            serialized_value = str(actual_value)
        except Exception as e:
            type_name = type(actual_value).__name__
            serialized_value = f"<typename {type_name}: {e}>"

        self._results.append(
            AssertionResult(
                op=op,
                args=[serialized_value],
                result=CheckStatus.PASS if ok else CheckStatus.FAIL,
                failure_message=failure_message if not ok else None,
            )
        )
