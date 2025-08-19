from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from .locale import Locale


class SerializerMixin(BaseModel, ABC):
    @abstractmethod
    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""
        ...

    def _set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        if locale is None:
            return

        if not isinstance(locale, Locale):
            raise ValueError("Locale must be an instance of Locale enum")

        self.model_config.update(
            {
                "_locale": locale,
            }
        )

    @staticmethod
    def _field_serializer(
        target_field: dict[str, Any],
        model_config: ConfigDict,
    ) -> Any:
        locale: Locale | None = model_config.get("_locale")

        if locale is None:
            return target_field

        if (
            translations := (
                model_config.get("_translations", {}).get(locale.value, {})
            )
        ) is None:
            return target_field

        if translations and isinstance(translations, dict):
            return {
                translations.get(key, key): value for key, value in target_field.items()
            }

        return target_field
