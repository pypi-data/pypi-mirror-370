# coding: utf-8
u"""
Основной регистр сведений Платформы М3.

@author: akvarats
"""

from __future__ import absolute_import
import datetime

from django.db import models
from m3_django_compat import atomic

from .core import PeriodEnum, normdate


class BaseDataStoreModel(models.Model):
    u"""
    Базовый класс для всех моделей, которые используются для хранения
    записей в регистрах сведений.
    """
    # левый конец интервала
    drg_left = models.DateTimeField()
    # правый конец интервала
    drg_right = models.DateTimeField()
    # момент времени, на который происходит сохранение значения
    drg_center = models.DateTimeField()

    class Meta:
        abstract = True


class DataRegistry(object):
    u"""
    Базовый класс для регистров сведений.

    Создание прикладного регистра выполняется следующим образом:
    <code>
    # myapp/models.py
    from m3.core.registry import DataRegistry, BaseDataStoreModel

    class MyDataModel(BaseDataStoreModel):
        # данная модель используется для хранения информации в регистре
        field1 = ...
        field2 = ...

    class MyDataRegistry(DataRegistry):
        model = MyDataModel
        dimentions = ['field1',]
        resources = ['field2',]
        period = DataRegistry.PERIOD_DAY
    </code>
    """

    # =========================================================================
    # Атрибуты для работы конкретного регистра
    # =========================================================================
    model = None
    dimentions = []
    resources = []
    period = PeriodEnum.INFTY

    @classmethod
    @atomic
    def insert(cls, data, date=None):
        u"""
        Выполняет сохранение данных в регистре сведений.

        @param data: объект с данными для сохранения в регистр, может быть:
             - объектом модели хранения данных регистра,
             - или словарем, ключами которого являются имена полей
             из модели хранения,
             - или объектом любого класса, у которого есть атрибуты с именами
        @param date: дата/время актуальности сведений
        """
        if cls.period != PeriodEnum.INFTY and not date:
            raise Exception(
                u'Не задана дата при вставке данных в периодический регистр')

        # нормализуем переданные дату и время
        reg_date = normdate(cls.period, date)

        # временный объект для корректного хранения вставляемых данных
        query_model = cls._get_model_object(
            data, model=DataRegistry.QueryDataHolder())

        query_affected_models = cls.model.objects
        for dim_field in cls.dimentions:
            dim_field_value = getattr(query_model, dim_field, None)
            if dim_field_value:
                query_affected_models = query_affected_models.filter(
                    dim_field=dim_field_value)

        if cls.period != PeriodEnum.INFTY:
            query_affected_models = query_affected_models.filter(
                drg_left__lte=reg_date, drg_right__gte=reg_date)
        query_affected_models = query_affected_models.order_by('drg_center')

        affected_models = list(query_affected_models)

        if cls.period != PeriodEnum.INFTY:
            left_bound = datetime.datetime.min
            right_bound = datetime.datetime.max
            model_to_save = None
            for affected_model in affected_models:
                if affected_model.drg_center < reg_date:
                    affected_model.drg_right = reg_date
                    affected_model.save()
                    left_bound = (affected_model.drg_center
                                  if affected_model.drg_center > left_bound
                                  else left_bound)
                elif affected_model.drg_center > reg_date:
                    affected_model.drg_left = reg_date
                    affected_model.save()
                    right_bound = (affected_model.drg_center
                                   if affected_model.drg_center < right_bound
                                   else right_bound)
                else:
                    model_to_save = affected_model

            model_to_save = cls._get_model_object(data, model_to_save)
            model_to_save.drg_left = left_bound
            model_to_save.drg_center = reg_date
            model_to_save.drg_right = right_bound
            model_to_save.save()
        else:
            # регистр у нас непериодический
            if affected_models:
                for affected_model in affected_models:
                    affected_model = cls._get_model_object(
                        data, affected_model
                    )
                    affected_model.save()
            else:
                affected_model = cls._get_model_object(data)
                affected_model.drg_left = datetime.datetime.min
                affected_model.drg_center = datetime.datetime.min
                affected_model.drg_right = datetime.datetime.max
                affected_model.save()

    @classmethod
    def query(cls, dimentions, date=None, next=False):
        u"""
        Возвращает данные из регистра

        :param dict dimentions: значения полей-измерений
        :param date: если регистр с периодичностью, то будет учитываться и дата
        :param bool next: данные беруться справа или слева от даты
        """
        # временный объект для корректного хранения данных
        query_model = cls._get_model_object(dimentions)

        query = cls.model.objects
        for dim_field in cls.dimentions:
            dim_field_value = getattr(query_model, dim_field, None)
            if dim_field_value:
                query = query.filter(dim_field=dim_field_value)

        if cls.period != PeriodEnum.INFTY and date:
            reg_date = normdate(cls.period, date)
            if next:
                query = query.filter(
                    drg_left__lt=reg_date, drg_center__gte=reg_date)
            else:
                query = query.filter(
                    drg_center__lte=reg_date, drg_right__gt=reg_date)

        query = query.order_by('drg_center')

        return query

    @classmethod
    @atomic
    def remove(cls, dimentions, date=None):
        u"""
        Удаление записей на основе переданных в dimentions ключевых значений
        разрезов. В случае периодичности регистра производится удаление данных,
        действительных на переданную дату.

        @param dimentions: словарь, либо объект, атрибуты которого
                           характеризуют удаляемые сведения
        @param date: дата, на которую удаляются сведения
        """
        if cls.period == PeriodEnum.INFTY:
            # в случае непериодического регистра просто удаляем записи
            cls._get_query_by_dimentions(dimentions).delete()
        else:
            # в случае периодического регистра помимо удаления указанных
            # записей пересчитываем даты начала и окончания у смежных записей
            reg_date = normdate(cls.period, date)

            if cls.period != PeriodEnum.INFTY and not reg_date:
                raise Exception(
                    u'Не указана дата при удалении данных из '
                    u'периодического регистра')

            # получаем список записей для удаления
            query_delete = cls._get_query_by_dimentions(dimentions).filter(
                drg_center=reg_date)

            for model in query_delete:
                # обновляем правую границу у смежной слева записью
                cls._get_query_by_dimentions(dimentions).filter(
                    drg_right=reg_date).update(drg_right=model.drg_right)
                # обновляем левую границу у смежной справа записью
                cls._get_query_by_dimentions(dimentions).filter(
                    drg_left=reg_date).update(drg_left=model.drg_left)

            cls._get_query_by_dimentions(dimentions).filter(
                drg_center=reg_date).delete()

    @classmethod
    def change(cls, dimentions, date=None, new_resources=None, new_date=None):
        pass

    @classmethod
    def _get_model_object(cls, data, model=None):
        u"""
        Возвращает экземпляр модели с установленными значениями атрибутов
        из объекта data
        """
        model_obj = model if model else cls.model()

        fields = []
        fields.extend(cls.dimentions)
        fields.extend(cls.resources)

        if isinstance(data, dict):
            for field_name in fields:
                if field_name in data:
                    setattr(model_obj, field_name, data[field_name])
        else:
            for field_name in fields:
                if hasattr(data, field_name):
                    setattr(model_obj, field_name, getattr(data, field_name))

        return model_obj

    @classmethod
    def _get_query_by_dimentions(cls, dimentions):
        u"""
        Возвращает запрос данных из регистра

        :param dimentions: объект, по которому будет строиться фильтр
        """
        result_query = cls.model.objects

        query_model = cls._get_model_object(dimentions)

        for dim_field in cls.dimentions:
            dim_field_value = getattr(query_model, dim_field, None)
            if dim_field_value:
                result_query = result_query.filter(dim_field=dim_field_value)

        return result_query
