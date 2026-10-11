from typing import TypeVar

import allure
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def validate_schema(model: type[T], data: object, description: str) -> T:
    """Валидация данных по Pydantic-модели с шагом Allure."""
    with allure.step(description):
        return model.model_validate(data)
