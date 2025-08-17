from typing import Literal

from match_expression import match


type Status = Literal["pending", "success", "error"]
type Platform = Literal["web", "mobile", "desktop"]
type Action = Literal["start", "stop", "pause", "resume"]
type Input = Literal["int", "str", "bool"]
type Operation = Literal["double", "square", "negate"]


def test__literal__no_param() -> None:
    platform: Platform = "mobile"
    result = (
        match(platform)
        .case("web", lambda: "Web App")
        .case("mobile", lambda: "Mobile App")
        .case("desktop", lambda: "Desktop App")
        .exhaustive()
    )

    assert result == "Mobile App"


def test__literal__pattern_param() -> None:
    def handle_pending(status: Status) -> str:
        return "Processing..."

    def handle_success(status: Status) -> str:
        return "Completed!"

    def handle_error(status: Status) -> str:
        return "Failed!"

    status: Status = "success"
    result = (
        match(status)
        .case("pending", handle_pending)
        .case("success", handle_success)
        .case("error", handle_error)
        .exhaustive()
    )

    assert result == "Completed!"


def test__type__pattern_param() -> None:
    class Dog:
        def __init__(self, name: str):
            self.name = name

    class Cat:
        def __init__(self, name: str):
            self.name = name

    def handle_dog(dog: str) -> str:
        return f"Dog: {dog.name}"

    def handle_cat(cat: Cat) -> str:
        return f"Cat: {cat.name}"

    animal = Dog("Buddy")
    result = match(animal).case(Dog, handle_dog).case(Cat, handle_cat).exhaustive()

    assert result == "Dog: Buddy"


def test_callable_with_lambda_and_type() -> None:
    class Success:
        def __init__(self, value: int):
            self.value = value

    class Error:
        def __init__(self, message: str):
            self.message = message

    result = Success(42)
    output = (
        match(result)
        .case(Success, lambda s: s.value * 2)
        .case(Error, lambda e: 0)
        .exhaustive()
    )

    assert output == 84


def test_mixed_callable_and_value() -> None:
    def start_action() -> str:
        return "Started"

    action: Action = "pause"
    result = (
        match(action)
        .case("start", start_action)
        .case("stop", lambda: "Stopped")
        .case("pause", "Paused")  # Direct value
        .case("resume", lambda: "Resumed")
        .exhaustive()
    )

    assert result == "Paused"


def test_callable_returning_different_types() -> None:
    def get_int() -> int:
        return 42

    def get_str() -> str:
        return "hello"

    def get_bool() -> bool:
        return True

    input_type: Input = "int"
    result = (
        match(input_type)
        .case("int", get_int)
        .case("str", get_str)
        .case("bool", get_bool)
        .exhaustive()
    )

    assert result == 42
    assert isinstance(result, int)


def test_callable_with_complex_logic() -> None:
    class Calculator:
        def __init__(self, value: int):
            self.value = value

        def double(self) -> int:
            return self.value * 2

        def square(self) -> int:
            return self.value**2

    calc = Calculator(5)
    operation: Operation = "square"

    result = (
        match(operation)
        .case("double", calc.double)
        .case("square", calc.square)
        .case("negate", lambda: -calc.value)
        .exhaustive()
    )

    assert result == 25


def test_callable_with_otherwise() -> None:
    def default_handler() -> str:
        return "Unknown"

    value = 999
    result = (
        match(value)
        .case(1, lambda: "One")
        .case(2, lambda: "Two")
        .case(3, lambda: "Three")
        .otherwise(default_handler)
    )

    assert result == "Unknown"
