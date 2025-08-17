from abc import ABC
from typing import Any
from ..base import VannaBase


class MockLLM(VannaBase, ABC):
    def __init__(self, config=None):
        pass

    def system_message(self, message: str) -> Any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> Any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> Any:
        return {"role": "assistant", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        return "Mock LLM response"
