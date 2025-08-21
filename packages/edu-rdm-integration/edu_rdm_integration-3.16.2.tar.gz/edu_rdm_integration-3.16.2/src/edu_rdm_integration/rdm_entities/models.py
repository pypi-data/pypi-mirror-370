from m3_db_utils.models import (
    ModelEnumValue,
    TitledModelEnum,
)


class RDMEntityEnum(TitledModelEnum):
    """Модель-перечисление сущностей выгрузки в Региональная витрина данных.

    Поля:
        entity - data-класс сущности;
        main_model_enum - значение модели-перечисления RegionalDataMartModelEnum основной модели РВД для формирования
            данных сущности. Обычно это модель идентификаторы записей которой соответствуют идентификаторам в записях
            сущности. У этих записей проставляется подэтап выгрузки данных;
        additional_model_enums - кортеж значений модели-перечисления RegionalDataMartModelEnum с дополнительными
            моделями РВД, которые участвуют в формировании записей сущностей. Они показывают, что перед запуском
            экспорта данных сущности по ним и основной модели должен быть запущен сбор данных.
    """

    class Meta:
        db_table = 'rdm_entity'
        extensible = True
        verbose_name = 'Модель-перечисление сущностей "Региональной витрины данных"'
        verbose_name_plural = 'Модели-перечисления сущностей "Региональной витрины данных"'

    @property
    def model_enums(self):
        """Возвращает модели, от которых зависит сущность."""
        value = self.model_enum_value

        return self.get_model_enums_from_value(value=value)

    @staticmethod
    def get_model_enums_from_value(value: ModelEnumValue):
        """Получение значений модели-перечисления моделей по значению модели-перечисления сущностей."""
        model_enums = [value.main_model_enum, *value.additional_model_enums]

        return model_enums

    @classmethod
    def get_entities_model_enums(
        cls,
        entity_enums: list[ModelEnumValue],
        is_sorted: bool = True,
    ) -> list[ModelEnumValue]:
        """Получение списка значений модели-перечисления моделей RegionalDataMartModelEnum.

        Args:
            entity_enums: Список значений модели-перечисления сущностей RegionalDataMartEntityEnum;
            is_sorted: Необходимость сортировки значений модели-перечисления RegionalDataMartModelEnum по полю
                order_number.
        """
        model_enums = set()

        for entity_enum_value in entity_enums:
            model_enums.update(cls.get_model_enums_from_value(value=entity_enum_value))

        model_enums = list(model_enums)

        if is_sorted:
            model_enums = sorted(model_enums, key=lambda value: value.order_number)

        return model_enums
