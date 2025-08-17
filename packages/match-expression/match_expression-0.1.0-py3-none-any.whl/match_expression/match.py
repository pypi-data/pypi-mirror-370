from __future__ import annotations

import inspect
from typing import Generic, TypeVar, Any, Callable

V = TypeVar("V")  # type of match(value)
P = TypeVar("P")  # type of case(pattern)
UP = TypeVar("UP")  # unionized pattern type of case(pattern)
R = TypeVar("R")  # return type of case(then)
UR = TypeVar("UR")  # unionized return type of case(then)


class Match(Generic[V]):
    def __init__(self, value: V) -> None:
        self.value = value

    def case(
        self,
        pattern: P,
        then: R | Callable[[Any], R] | Callable[[], R],
    ) -> Case[V, P, R]:
        if isinstance(pattern, type):
            # 타입 매칭
            matched = isinstance(self.value, pattern)
            if matched and callable(then):
                result = _call_with_value(self.value, then)
            elif matched:
                result = then
            else:
                result = then
        else:
            # 값 매칭 (리터럴)
            matched = self.value == pattern
            if matched and callable(then):
                # 리터럴 매칭에서도 매칭된 값을 전달
                result = _call_with_value(self.value, then)
            elif matched:
                result = then
            else:
                result = then

        return Case(self.value, result, matched)  # type: ignore


class Case(Generic[V, P, R]):
    def __init__(self, value: V, result: R, matched: bool) -> None:
        self.value = value
        self.result = result
        self.matched = matched

    def case(
        self,
        pattern: UP,
        then: UR | Callable[[Any], UR] | Callable[[], UR],
    ) -> Case[V, P | UP, R | UR]:
        if self.matched:
            return self  # type: ignore

        # 타입 매칭 (isinstance)
        if isinstance(pattern, type):
            matched = isinstance(self.value, pattern)
            if matched and callable(then):
                result = _call_with_value(self.value, then)
            elif matched:
                result = then
            else:
                result = then
        # 값 매칭 (리터럴)
        else:
            matched = self.value == pattern
            if matched and callable(then):
                # 리터럴 매칭에서도 매칭된 값을 전달
                result = _call_with_value(self.value, then)
            elif matched:
                result = then
            else:
                result = then

        return Case(self.value, result, matched)  # type: ignore

    def exhaustive(self) -> R:
        if not self.matched:
            raise ExhaustiveError(self.value)
        return self.result

    def otherwise(self, default: UR | Callable[[], UR]) -> R | UR:
        if self.matched:
            return self.result
        if callable(default):
            return default()  # type: ignore
        return default


def match(value: V) -> Match[V]:
    return Match[V](value)


def _call_with_value(
    value: Any,
    then: Callable[[Any], Any] | Callable[[], Any],
) -> Any:
    if not callable(then):
        return then
    
    try:
        sig = inspect.signature(then)
        if len(sig.parameters) == 0:
            return then()
        else:
            return then(value)
    except TypeError:
        # 인자를 받지 않는 callable인 경우
        return then()


class ExhaustiveError(Exception):
    def __init__(self, value: Any) -> None:
        super().__init__(f"Non-exhaustive match. Unhandled value: {value}")
        self.value = value