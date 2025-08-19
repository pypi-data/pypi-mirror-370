import logging
from typing import Any, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, model_serializer
from pydantic.alias_generators import to_camel

from .locale import Locale
from .mixin import SerializerMixin

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class CustomerRecord(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "id": "ID",
                "short_name": "Nome",
                "full_name": "NomeCompleto",
                "description": "Descricao",
            },
        },
    )

    id: str
    short_name: str
    full_name: Optional[str | None] = None
    description: Optional[str | None] = None

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class ChildRecord(SerializerMixin, BaseModel, Generic[T]):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "record": "Registro",
            },
        },
    )

    record: T

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

        if isinstance(self.record, SerializerMixin):
            self.record.set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class ChildID(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "id": "ID",
            },
        },
    )

    id: str

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class ChildrenIDs(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "ids": "IDs",
            },
        },
    )

    ids: List[str]

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class Tag(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "id": "ID",
                "value": "Valor",
                "meta": "Metadados",
            },
        },
    )

    id: str
    value: str
    meta: Any

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

        if isinstance(self.meta, SerializerMixin):
            self.meta.set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class Artifact(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "id": "ID",
                "result_set": "IdentificadoresDosResultados",
                "name": "Nome",
                "url": "URL",
                "artifact_type": "TipoDeArtefato",
                "public_object": "ObjetoPublico",
                "updated_at": "AtualizadoEm",
            },
        },
    )

    id: str
    result_set: ChildID
    name: str
    url: str
    artifact_type: str
    public_object: bool
    updated_at: str

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

        self.result_set.set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class Group(SerializerMixin, BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)


class Sample(SerializerMixin, BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)


class Metadata(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "group": "Grupo",
                "sample": "Amostra",
            },
        },
    )

    group: Group
    sample: Sample

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

        self.group._set_locale(locale)
        self.sample._set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class Analysis(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "id": "ID",
                "customer": "Cliente",
                "parent": "ResultadoPai",
                "result_type": "TipoDeResultado",
                "name": "Nome",
                "tags": "Etiquetas",
                "hash": "Hash",
                "version": "Versao",
                "updated_at": "AtualizadoEm",
                "collection_date": "DataDeColeta",
                "crop": "Cultura",
                "taxa": "Taxa",
                "was_frozen": "FoiCongelado",
                "was_approved": "FoiAprovado",
                "was_evaluated": "FoiAvaliado",
                "was_rejected": "FoiRejeitado",
                "upload_completed": "UploadConcluido",
                "verbose_status": "StatusDetalhado",
                "artifacts": "Artefatos",
                "children": "ResultadosFilhos",
                "bioindex": "Bioindices",
            },
        },
    )

    customer: Union[ChildRecord[CustomerRecord], ChildID]
    id: str
    parent: Union[ChildID, Any]
    result_type: str
    name: str
    tags: Optional[List[Tag]] = None
    hash: str
    version: int
    updated_at: str
    collection_date: Optional[Any] = None
    crop: str
    taxa: str
    was_frozen: bool
    was_approved: bool
    was_evaluated: bool
    was_rejected: bool
    upload_completed: bool
    verbose_status: str
    artifacts: Optional[List[Artifact]] = None
    children: Optional[List["Analysis"]] = None
    bioindex: Optional[ChildrenIDs] = None

    def list_bioindex_ids(self) -> List[str]:
        """List the bioindex IDs."""

        bioindex_ids: list[str] = []

        if self.bioindex:
            bioindex_ids.extend(self.bioindex.ids)

        if self.children:
            for child in self.children:
                bioindex_ids.extend(child.list_bioindex_ids())

        return bioindex_ids

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

        if self.customer:
            if isinstance(self.customer, ChildRecord[CustomerRecord]):
                self.customer.set_locale(locale)

            elif isinstance(self.customer, ChildID):
                self.customer.set_locale(locale)

        if self.tags:
            for tag in self.tags:
                tag.set_locale(locale)

        if self.artifacts:
            for artifact in self.artifacts:
                artifact.set_locale(locale)

        if self.children:
            for child in self.children:
                child.set_locale(locale)

        if self.bioindex:
            self.bioindex.set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)


class AnalysisList(SerializerMixin, BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        _translations={
            Locale.PT_BR.value: {
                "count": "Total",
                "skip": "ResultadosIgnorados",
                "size": "TamanhoDaPagina",
                "records": "Registros",
            },
        },
    )

    count: int
    skip: int
    size: int
    records: List[Analysis]

    def set_locale(self, locale: Locale | None) -> None:
        """Set the locale for translations."""

        super()._set_locale(locale)

        if self.records:
            for record in self.records:
                record.set_locale(locale)

    @model_serializer
    def translate_model(self) -> dict[str, Any]:
        return self._field_serializer(dict(self), self.model_config)
