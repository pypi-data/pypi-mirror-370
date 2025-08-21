from django.db.models import (
    CASCADE,
    DateTimeField,
    ForeignKey,
    SmallIntegerField,
)
from m3.db import (
    BaseObjectModel,
)

from educommon.django.db.mixins import (
    ReprStrPreModelMixin,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from m3_db_utils.models import (
    TitledModelEnum,
)


class BaseRDMModel(ReprStrPreModelMixin, BaseObjectModel):
    """Базовая модель РВД."""

    collecting_sub_stage = ForeignKey(
        verbose_name='Подэтап сбора данных',
        to='edu_rdm_integration_collect_data_stage.RDMCollectingDataSubStage',
        on_delete=CASCADE,
    )
    exporting_sub_stage = ForeignKey(
        verbose_name='Подэтап выгрузки данных',
        to='edu_rdm_integration_export_data_stage.RDMExportingDataSubStage',
        blank=True,
        null=True,
        on_delete=CASCADE,
    )
    operation = SmallIntegerField(
        verbose_name='Действие',
        choices=EntityLogOperation.get_choices(),
    )

    created = DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
        blank=True,
        db_index=True,
    )
    modified = DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
        null=True,
        blank=True,
        db_index=True,
    )

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['collecting_sub_stage', 'exporting_sub_stage', 'operation', 'created', 'modified']

    class Meta:
        abstract = True


class RDMModelEnum(TitledModelEnum):
    """Модель-перечисление моделей "Региональная витрина данных"."""

    class Meta:
        db_table = 'rdm_model'
        extensible = True
        verbose_name = 'Модель-перечисление моделей "Региональной витрины данных"'
        verbose_name_plural = 'Модели-перечисления моделей "Региональной витрины данных"'
