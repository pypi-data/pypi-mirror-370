# coding:utf-8
u"""
Регистр накопления (+ остатки)

Created on 12.04.2011

@author: akvarats
"""

from __future__ import absolute_import
from django.db.models import F
from m3_django_compat import atomic

from .core import PeriodEnum, normdate
from .exceptions import GenericRegisterException, WrongRegisterMeta
from six.moves import range


class CumulativeRegister(object):
    u"""
    Базовый управляющий класс для регистров накопления.

    Атрибуты, которые нужно определить при описании прикладного регистра:
    * model - модель хранения записей регистра;
    * date_field - наименование поля, которое является системным полем регистра
        (по умолчанию 'date');
    * period - значение перечисления registry.core.PeriodEnum, которое
        задает периодичность регистра (по умолчанию PeriodEnum.DAY);
    * dim_fields - список наименований полей, которые являются
        измерениями регистра;
    * rest_fields - список наименований полей, которые будут хранить
        суммарные остатки;
    * circ_fields - список наименований полей, которые будут хранить
        суммарные обороты за период;
    """

    model = None
    submodels = []  # дочерние модели
    dim_fields = []
    rest_fields = []
    circ_fields = []
    date_field = 'date'
    period = PeriodEnum.DAY

    @classmethod
    @atomic
    def write(cls, date, **kwargs):
        u"""
        Выполняет запись значений в регистр.

        Параметры, передаваемые через kwargs должны включать в себя
        перечисление значений по всем измерениям, по которым необходимо
        вычислить и сохранить остатки и обороты.

        Здесь же, в параметрах, соответствующих наименованиям
        полей хранения остатков (dim_fields) необходимо указывать значение
        изменения остатка в указанном периоде (это может быть положительное,
        либо отрицательное значение).

        :param date: дата/датавремя для создаваемой записи в регистре
        """

        # проверяем регистр на корректность описания
        cls._check_meta()

        normalized_date = normdate(cls.period, date)
        # формируем единый список обновляемых значений
        allmodels = [cls.model]
        if cls.submodels:
            allmodels.extend(cls.submodels)

        for model in allmodels:
            kw_dims = cls._cleaned_kwargs_by_dims(model, kwargs)
            kw_rests = cls._cleaned_kwargs_by_rests(model, kwargs)

            # =================================================================
            # 1. пытаемся понять, если ли запись в регистре на указанную дату
            # =================================================================

            # получаем данные регистра на указанный период
            kw_dims[cls.date_field] = normalized_date
            query_set = model.objects.filter(**kw_dims)

            del kw_dims[cls.date_field]

            if not query_set.exists():
                # добавляем новую запись регистра с указанной датой
                entry = cls._init_model_instance(model, kwargs)
                setattr(entry, cls.date_field, normalized_date)

                # при создании новой записи обороты равны нулю,
                # а остатки равны остаткам на предыдущий период
                prev_rests = cls.get(normalized_date, model, **kw_dims)

                for i, rest_field in enumerate(cls.rest_fields):
                    setattr(entry, rest_field, prev_rests[i])

                for cicr_field in cls.circ_fields:
                    setattr(entry, cicr_field, 0)

                entry.save()

            # =================================================================
            # 2. Производим обновление записей об оборотах, если такие
            #    параметры заданы в настройке
            # =================================================================
            if cls.circ_fields:
                update_expr = {}

                for i, circ_field in enumerate(cls.circ_fields):
                    circ_value = F(circ_field) + kw_rests[cls.rest_fields[i]]
                    update_expr[circ_field] = circ_value

                query_set.update(**update_expr)

            # =================================================================
            # 3. Производим update записей регистра (с датами, лежащими после
            #    указанного периода)
            # =================================================================
            kw_dims[cls.date_field + '__gte'] = normalized_date
            update_expr = {}

            for field_name in cls.rest_fields:
                update_expr[field_name] = F(field_name) + kw_rests[field_name]

            model.objects.filter(**kw_dims).update(**update_expr)

    @classmethod
    def get(cls, date, model=None, **kwargs):
        u"""
        Возвращает кортеж значений, которые соответствуют записям регистра
        на указанную дату.

        :param model: необходимо передавать либо None (будет использоваться
            основня модель хранения), либо класс модели из списка submodels
            регистра, который используется для получения свернутых значений
        :param dict kwargs: словарь значений полей регистра
        :return: кортеж, в котором сначала идут значения полей-остатков,
            потом значения полей-оборотов
        :rtype: tuple
        :raise: GenericRegisterException
        """
        rest_fields_len = len(cls.rest_fields)
        # полей остатков столько же сколько полей-оборотов
        result = [0] * 2 * rest_fields_len

        if not model:
            model = cls.model
        else:
            if model != cls.model and model not in cls.submodels:
                raise GenericRegisterException(
                    u'Указан недопустимый класс подчиненной модели %s при '
                    u'получении данных из регистра %s.' % (model, cls))

        normalized_date = normdate(cls.period, date)

        kw_dims = cls._cleaned_kwargs_by_dims(model, kwargs)
        kw_dims[cls.date_field + '__lte'] = normalized_date

        values_list = [cls.date_field] + cls.rest_fields + cls.circ_fields
        # самая последняя на дату запись с фильтром по полям-измерениям
        query = model.objects.filter(**kw_dims).order_by(
            '-' + cls.date_field)[:1].values_list(*values_list)

        if query:
            query_rec = query.get()
            dates_are_same = cls._same_dates(normalized_date, query_rec[0])
            for i in range(rest_fields_len):
                result[i] = query_rec[i + 1]
                if dates_are_same:
                    # берем и значения оборотов
                    reg_value = query_rec[rest_fields_len + i + 1]
                else:
                    reg_value = 0
                result[rest_fields_len + i] = reg_value

        return tuple(result)


# ПРИВЕДЕННЫЕ НИЖЕ МЕТОДЫ НЕ ДОПИСАНЫ, ХОТЯ НУЖНЫ В РЕГИСТРАХ
#    @classmethod
#    def get_circs(cls, date_since, date_until, model=None, **kwargs):
#        '''
#        Возвращает значения оборотов по указанным измерениям с начала и
#        по конец указанного периода.
#
#        Значения в концевых датах включаются в результат
#        '''
#
#        if not model:
#            model = cls.model
#        else:
#            if not model == cls.model and not model in cls.submodels:
#                raise GenericRegisterException(
#                    u'Указана недопустимый класс подчиненной модели %s при
#                    получении данных из регистра %s.' % (model, cls))
#
#        nds = normdate(cls.period, date_since)
#        ndu = normdate(cls.period, date_until)
#
#        kw_dims = cls._cleaned_kwargs_by_dims(model, kwargs)
#
#        query = model.objects.filter(**kw_dims).annotate
#
#    #===========================================================================
#    # Вспомогательные и не интересные функции
#    #===========================================================================
#    @classmethod
#    def drop(cls, date_since=datetime.datetime.min,
#             date_until=datetime.datetime.max, **kwargs):
#        '''
#        Очищает регистр от записей по датам, которые находятся в указанном
#        периоде
#        '''
#        pass
#        # TODO: вроде бы нужный метод, но пока не работает
#        # формируем единый список обновляемых значений
#        allmodels = [cls.model,]
#        if cls.submodels:
#            allmodels.extend(cls.submodels)
#
#        for model in allmodels:
#            kw_dims = cls._cleaned_kwargs_by_dims(model, kwargs)
#            # kw_dims.

    # =========================================================================
    # Вспомогательные функции
    # =========================================================================
    @staticmethod
    def _cleaned_kwargs_by_fields(model, check_fields, kwargs):
        u"""
        Фильтрует словарь kwargs по полям модели и переданному списку полей
        и возвращает новый словарь

        :param model: модель, у которой берем названия полей
        :type model: django.db.models.Model
        :param list check_fields: список с названиями полей для фильтра
        :param dict kwargs: словарь значений полей модели
        """
        result = {}

        for field in model._meta.fields:
            field_name = field.name
            if field_name in check_fields and field_name in kwargs:
                result[field_name] = kwargs[field_name]

        return result

    @classmethod
    def _cleaned_kwargs_by_dims(cls, model, kwargs):
        u"""
        Возвращает отфильтрованный по названиям полей модели и
        полей-измерений регистра словарь значений kwargs

        :rtype: dict
        """
        return cls._cleaned_kwargs_by_fields(model, cls.dim_fields, kwargs)

    @classmethod
    def _cleaned_kwargs_by_rests(cls, model, kwargs):
        u"""
        Возвращает отфильтрованный по названиям полей модели и
        полей-остатков регистра словарь значений kwargs

        :rtype: dict
        """
        return cls._cleaned_kwargs_by_fields(model, cls.rest_fields, kwargs)

    @classmethod
    def _cleaned_kwargs_by_circs(cls, model, kwargs):
        u"""
        Возвращает отфильтрованный по названиям полей модели и
        полей-оборотов регистра словарь значений kwargs

        :rtype: dict
        """
        return cls._cleaned_kwargs_by_fields(model, cls.circ_fields, kwargs)

    @classmethod
    def _cleaned_kwargs_by_model(cls, model, kwargs):
        u"""
        Возвращает отфильтрованный по названиям полей модели словарь kwargs

        :param model:
        :type model: django.db.models.Model
        :param dict kwargs:
        :rtype: dict
        """
        result = {}

        for field in model._meta.fields:
            field_name = field.name
            if field_name in kwargs:
                result[field_name] = kwargs[field_name]

        return result

    @classmethod
    def _init_model_instance(cls, model, kwargs):
        u"""
        Создает и возвращает новую запись заданной модели,
        проинициализированную значениями из переданного словаря

        :param model: экземпляр какой модели создавать
        :type model: django.db.models.Model
        :param dict kwargs: значения для инициализации экземпляра
        :return: model()
        """
        entry = model()

        for field in model._meta.fields:
            field_name = field.name
            if field_name in kwargs:
                setattr(entry, field_name, kwargs[field_name])

        return entry

    @classmethod
    def _check_meta(cls):
        u"""
        Проверка описания регистра на корректность

        :raise: WrongRegisterMeta
        """
        msg = None

        if not cls.model:
            msg = u'Не задана модель хранения записей регистра (%s)' % cls
        elif not cls.rest_fields:
            msg = (u'Не заданы поля регистра для хранения остатков (%s)' % cls)
        elif not cls.circ_fields:
            msg = (u'Не заданы поля регистра для хранения оборотов (%s)' % cls)
        elif len(cls.rest_fields) != len(cls.circ_fields):
            msg = (u'Количество полей регистра для хранения остатков и '
                   u'оборотов должно быть одинаково (%s)' % cls)

        if msg:
            raise WrongRegisterMeta(msg)

    @classmethod
    def _same_dates(cls, date1, date2):
        u"""
        Нормализует и сравнивает две даты/датывремени на равенство
        """
        return normdate(cls.period, date1) == normdate(cls.period, date2)
