from typing import Any

from pydantic import BaseModel, ConfigDict, model_serializer
from pydantic.alias_generators import to_camel

from .locale import Locale
from .mixin import SerializerMixin


class BiotaxResponse(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "tax_id": "TaxaID",
                "tax_name": "NomeCientifico",
                "name_class": "ClasseNome",
                "rank": "Classificacao",
                "division": "Divisao",
                "parent": "Pai",
                "unique_name": "NomeUnico",
            },
        },
    )

    tax_id: int
    tax_name: str
    name_class: str
    rank: str
    division: str
    parent: int | None = None
    unique_name: str | None = None

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class TaxonomyResponse(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "tax_id": "TaxaID",
                "tax_name": "NomeCientifico",
                "name_class": "ClasseNome",
                "other_names": "OutrosNomes",
            },
        },
    )

    tax_id: int
    tax_name: str
    name_class: str

    other_names: list[str]

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)
