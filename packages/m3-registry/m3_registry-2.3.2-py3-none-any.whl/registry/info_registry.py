# coding: utf-8
from __future__ import (
    absolute_import,
)

import datetime as dt

from django.db import (
    models,
)
from django.db.models.query_utils import (
    Q,
)
from django.db.models.signals import (
    post_delete,
    pre_delete,
)
from registry.core import (
    PeriodEnum,
    normdate,
)


# PERIOD_INFTY = 0 # в регистре нет периодичности и нет динамически хранящихся
# PERIOD_SECOND = 1 # до секунд
# PERIOD_MINUTE = 2
# PERIOD_HOUR = 3
# PERIOD_DAY = 4
# PERIOD_MONTH = 5
# PERIOD_QUARTER = 6
# PERIOD_YEAR = 7

# def normdate(period, date, begin=True):
#     u""" Метод нормализует дату в зависимости от периода.
#
#     :param begin: True - даты выравниваются на начало, иначе на конец
#
#     """
#     if not date:
#         return None
#     if period == PERIOD_SECOND:
#         return datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
#     if period == PERIOD_MINUTE:
#         return datetime(date.year, date.month, date.day, date.hour, date.minute, 0 if begin else 59)
#     if period == PERIOD_HOUR:
#         return datetime(date.year, date.month, date.day, date.hour, 0 if begin else 59, 0 if begin else 59)
#     if period == PERIOD_DAY:
#         return datetime(date.year, date.month, date.day, 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#     if period == PERIOD_MONTH:
#         return datetime(date.year, date.month, 1 if begin else calendar.monthrange(date.year, date.month)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#     if period == PERIOD_QUARTER:
#         if date.month < 4:
#             return datetime(date.year, 1 if begin else 3, 1 if begin else calendar.monthrange(date.year, 1 if begin else 3)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#         if date.month < 7:
#             return datetime(date.year, 4 if begin else 6, 1 if begin else calendar.monthrange(date.year, 4 if begin else 6)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#         if date.month < 10:
#             return datetime(date.year, 7 if begin else 9, 1 if begin else calendar.monthrange(date.year, 7 if begin else 9)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#         return datetime(date.year, 10 if begin else 12, 1 if begin else calendar.monthrange(date.year, 10 if begin else 12)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#     if period == PERIOD_YEAR:
#         return datetime(date.year, 1 if begin else 12, 1 if begin else calendar.monthrange(date.year, 1 if begin else 12)[1], 0 if begin else 23, 0 if begin else 59, 0 if begin else 59)
#     return date


def shift_date(period, date, step=1):
    """Возвращает дату смещенную на заданное кол-во пунктов периода

    :param PeriodEnum period: период смещения
    :param step: смещение
    :rtype: datetime.datetime
    """
    if not date:
        return

    if period == PeriodEnum.SECOND:
        return date + dt.timedelta(seconds=step)
    elif period == PeriodEnum.MINUTE:
        return date + dt.timedelta(minutes=step)
    elif period == PeriodEnum.HOUR:
        return date + dt.timedelta(hours=step)
    elif period == PeriodEnum.DAY:
        return date + dt.timedelta(days=step)
    elif period == PeriodEnum.MONTH:
        # TODO: не знаю пока как быстро изменить дату на месяц,
        # т.к. день может быть 31, а в пред. месяце его нет
        return date
    elif period == PeriodEnum.QUARTER:
        # TODO: не знаю пока как быстро изменить дату
        return date
    elif period == PeriodEnum.YEAR:
        return date.replace(year=date.year + step)
    else:
        return date


class OverlapError(Exception):
    """
    Исключение возникающее при наложении интервалов друг на друга.
    """

    def __init__(self, cls=None):
        self.model_cls = cls


class InvalidIntervalError(Exception):
    """
    Исключение возникающее при неверно заданом интервале,
    например если конечная дата меньше начальной.
    """

    pass


class InfoModelMeta(models.base.ModelBase):
    """
    Магия! Если у модели есть атрибут no_time = True,
    то управляющие поля меняют свой тип с DateTimeField на DateField
    """

    def __new__(cls, name, bases, attrs):
        """
        Если у модели атрибут no_time равен True, то меняем тип управляющих
        полей с DateTimeField на DateField
        """
        new_class = super(InfoModelMeta, cls).__new__(cls, name, bases, attrs)
        no_time = attrs.get('no_time', False)
        if no_time:
            for base in bases:
                if issubclass(base, BaseInfoModel):
                    search_fields = ('info_date', 'info_date_prev', 'info_date_next')
                    break
                elif issubclass(base, BaseIntervalInfoModel):
                    search_fields = (
                        new_class.begin_src,
                        new_class.end_src,
                        'info_date_begin',
                        'info_date_end',
                        'info_date_prev',
                        'info_date_next',
                    )
                    break
            else:
                base = None

            if base:
                for field in list(new_class._meta.local_fields):
                    # найдем наши поля
                    if field.name in search_fields:
                        # заменим поля на новые
                        if field.default == dt.datetime.min:
                            default = dt.date.min
                        elif field.default == dt.datetime.max:
                            default = dt.date.max
                        else:
                            default = field.default
                        new_field = models.DateField(db_index=field.db_index, default=default)
                        new_class.replace_field(field, new_field)

        # Если в модели определены специальные источники
        # для полей, содержащих дату:
        if hasattr(new_class, 'begin_src') and hasattr(new_class, 'end_src') and new_class._meta.local_fields:

            def remove_date_field(field_name, default_field_name):
                """Удаляет дефолтное поле даты в случае, если используем другое имя поля

                Args:
                    field_name: Наименование поля даты в модели
                    default_field_name: Наименование поля даты по умолчанию
                """
                if field_name != default_field_name:
                    try:
                        date_fld = next(
                            filter(
                                lambda x: x.name == default_field_name,
                                list(new_class._meta.local_fields),
                            )
                        )
                    except StopIteration:
                        # Такое может произойти, если поле уже было удалено
                        # в базовой абстрактной модели.
                        # В таком случае можно просто игнорировать
                        pass
                    else:
                        new_class._meta.local_fields.remove(date_fld)

            remove_date_field(new_class.begin_src, new_class.DEFAULT_BEGIN)
            remove_date_field(new_class.end_src, new_class.DEFAULT_END)

        # подключим сигналы к классу
        new_class.connect_to_signals()

        return new_class

    def replace_field(cls, old_field, new_field):
        """
        Замена поля в классе
        """
        cls.add_to_class(old_field.name, new_field)
        model_fields = cls._meta.local_fields

        index = model_fields.index(old_field)
        model_fields.remove(old_field)
        new_index = model_fields.index(new_field)
        model_fields.insert(index, model_fields.pop(new_index))

    def connect_to_signals(cls):
        """
        Подключает обработчики регистра к pre- и post- сигналам удаления
        его записей
        """
        pre_delete.connect(cls.infomodel_pre_delete, cls, dispatch_uid='base_info_model_pre_delete')
        post_delete.connect(cls.infomodel_post_delete, cls, dispatch_uid='base_info_model_post_delete')

    def infomodel_pre_delete(cls, instance, **kwargs):
        """
        Обработчик перед удалением записи регистра. Ищет предыдущую и
        следующую записи и, если такие есть, добавляет их параметрами
        в сигнал
        """
        if instance._signal_params.get('skip_signals'):
            return

        # если объект уже хранится, то найдем записи для изменения
        if instance.pk:

            def get_rec(date, lookup):
                # в зависимости от базовой модели разные фильтры
                if isinstance(instance, BaseInfoModel):
                    q = Q(info_date=date)
                else:
                    q = instance._gen_Q(lookup, '', date)
                try:
                    return instance.query_dimentions(instance).get(q)
                except (instance.DoesNotExist, instance.MultipleObjectsReturned):
                    return

            old_prev_rec = get_rec(instance.info_date_prev, 'end')
            old_next_rec = get_rec(instance.info_date_next, 'bgn')
        else:
            old_prev_rec = None
            old_next_rec = None

        instance._signal_params['old_prev_rec'] = old_prev_rec
        instance._signal_params['old_next_rec'] = old_next_rec

    def infomodel_post_delete(cls, instance, **kwargs):
        """
        Обработчик после удаления записи регистра.
        """
        if instance._signal_params.get('skip_signals'):
            return

        # изменим найденные ранее записи
        # TODO: тут можно оптимизировать сохранение,
        # чтобы не было каскада сохранений
        old_prev_rec = instance._signal_params.get('old_prev_rec')
        old_next_rec = instance._signal_params.get('old_next_rec')

        for old_rec in (old_prev_rec, old_next_rec):
            # нужно проверить что объект есть, т.к. он может быть удален
            if old_rec and cls.objects.filter(pk=old_rec.pk).exists():
                old_rec.save()

    @staticmethod
    def suppress_signals(method):
        """
        Декоратор для выполнения действий над записью регистра
        без срабатывания сигналов
        """

        def inner(instance, *args, **kwargs):
            instance._signal_params['skip_signals'] = True
            res = method(instance, *args, **kwargs)
            instance._signal_params['skip_signals'] = False
            return res

        return inner


class BaseInfoModel(models.Model, metaclass=InfoModelMeta):
    info_date_prev = models.DateTimeField(db_index=True, default=dt.datetime.min)
    info_date_next = models.DateTimeField(db_index=True, default=dt.datetime.max)
    info_date = models.DateTimeField(db_index=True, blank=True)

    dimentions = []  # перечень реквизитов-измерений
    period = PeriodEnum.DAY  # периодичность

    # Константы с минимальной и максимальной датами регистра. Для удобства.
    MAX_DATE = dt.datetime.max
    MIN_DATE = dt.datetime.min

    def __init__(self, *args, **kwargs):
        super(BaseInfoModel, self).__init__(*args, **kwargs)
        # словарь параметров для передачи через сигналы
        self._signal_params = {}

    @classmethod
    def query_dimentions(cls, data):
        """
        Возвращает результаты запроса по ключевым полям.

        :param data: объект, который содержит данные для сохранения в
            регистр. Это может быть:
            - объект модели хранения данных регистра,
            - или словарь, ключами которого являются имена полей из
              модели хранения,
            - или объект любого класса, у которого есть атрибуты с
              именами
        :rtype: django.db.models.query.QuerySet
        """
        # Добавим в запрос фильтр по ключевым полям, со значениями =
        # текущему объекту, переданным данным
        query = cls.objects
        for dim_field in cls.dimentions:
            if isinstance(dim_field, models.Field):
                dim_attr = dim_field.name
            else:
                dim_attr = dim_field

            if isinstance(data, BaseInfoModel):
                if not hasattr(data, dim_attr):
                    continue
                dim_val = getattr(data, dim_attr)
            elif isinstance(data, dict):
                if dim_attr not in data:
                    continue
                dim_val = data[dim_attr]
            elif hasattr(data, dim_attr):
                dim_val = getattr(data, dim_attr)
            else:
                continue

            query = query.filter(**{dim_attr: dim_val})

        return query

    @classmethod
    def query_on_date(cls, data, date=None, next=False):
        """
        Возвращает результат запроса записей регистра на дату

        :param data: объект или словарь с ключевыми данными
        :param date: дата актуальности, по умолчанию текущая
        :param next: False - поиск уже действующих на дату записей,
            иначе ближайших записей, которые будут действовать
        """
        if date is None:
            date = dt.datetime.now()

        query = cls.query_dimentions(data)
        if cls.period != PeriodEnum.INFTY:
            norm_date = normdate(cls.period, date)
            if next:
                params = dict(info_date_prev__lte=norm_date, info_date__gt=norm_date)
            else:
                params = dict(info_date__lte=norm_date)
                if norm_date == normdate(cls.period, dt.datetime.max):
                    params.update(info_date_next__gte=norm_date)
                else:
                    params.update(info_date_next__gt=norm_date)

        return query.filter(**params)

    def _save(self, *args, **kwargs):
        """
        Прямая запись объекта, чтобы можно было записывать без доп. обработки
        """
        super(BaseInfoModel, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Переопределение записи объекта, чтобы изменять соседние записи
        """
        if 'update_fields' in kwargs:
            kwargs['update_fields'] = set(kwargs['update_fields'])
            # Добавляем все поля, которые меняются в save()
            kwargs['update_fields'].update({'info_date', 'info_date_prev', 'info_date_next'})

        # если не указана дата записи
        if self.period != PeriodEnum.INFTY and not self.info_date:
            raise Exception('Attribute info_date is not set!')
        # нормализуем переданные дату и время
        self.info_date = normdate(self.period, self.info_date)

        # проверим на уникальность записи
        if self.period != PeriodEnum.INFTY:
            q = self.__class__.query_dimentions(self).filter(info_date=self.info_date)
            if self.pk:
                q = q.exclude(pk=self.pk)
            if q.count() > 0:
                raise OverlapError()

        # если объект уже хранится, то найдем записи для изменения
        if self.pk:
            q = self.__class__.query_dimentions(self).filter(info_date=self.info_date_prev).exclude(pk=self.pk)
            old_prev_rec = q.get() if q.count() == 1 else None

            q = self.__class__.query_dimentions(self).filter(info_date=self.info_date_next).exclude(pk=self.pk)
            old_next_rec = q.get() if q.count() == 1 else None
        else:
            old_prev_rec = None
            old_next_rec = None

        # вычислим ближайщую запись, которая начинается "левее" текущей
        q = (
            self.__class__.query_dimentions(self)
            .filter(info_date__lt=self.info_date, info_date_next__gte=self.info_date)
            .exclude(pk=self.pk)
        )
        new_prev_rec = q.get() if q.count() == 1 else None

        # вычислим ближайшую запись, которая начинается "правее" текущей
        q = (
            self.__class__.query_dimentions(self)
            .filter(info_date__gt=self.info_date, info_date_prev__lte=self.info_date)
            .exclude(pk=self.pk)
        )
        new_next_rec = q.get() if q.count() == 1 else None

        # изменим даты исходя из соседей
        if new_prev_rec:
            self.info_date_prev = new_prev_rec.info_date
        else:
            self.info_date_prev = normdate(self.period, self.MIN_DATE)

        if new_next_rec:
            self.info_date_next = new_next_rec.info_date
        else:
            self.info_date_next = normdate(self.period, self.MAX_DATE)

        # сохраним запись
        self._save(*args, **kwargs)

        # изменим найденные ранее записи
        # TODO: тут можно оптимизировать сохранение,
        # чтобы не было каскада сохранений
        if old_prev_rec and old_prev_rec != new_prev_rec:
            old_prev_rec.save()
        if old_next_rec and old_next_rec != new_next_rec:
            old_next_rec.save()
        if new_prev_rec and new_prev_rec.info_date_next != self.info_date:
            new_prev_rec.info_date_next = self.info_date
            new_prev_rec._save()
        if new_next_rec and new_next_rec.info_date_prev != self.info_date:
            new_next_rec.info_date_prev = self.info_date
            new_next_rec._save()

    @InfoModelMeta.suppress_signals
    def _delete(self, *args, **kwargs):
        """
        Прямое удаление, без обработки
        """
        super(BaseInfoModel, self).delete(*args, **kwargs)

    class Meta:
        abstract = True


def rebuild_info_model(cls):
    """
    Перестраивает связи между записями в регистре
    """

    def eq_keys(dims, dict1, dict2):
        """
        Возвращает True, если значения полей измерений в двух словарях
        одинаково, иначе False
        """
        for key_attr in dims:
            if dict1[key_attr] != dict2[key_attr]:
                return False
        return True

    def get_key(dims, data):
        """
        Достает из объекта значения ключевых аттрибутов
        """
        result = {}
        for key_attr in dims:
            dim_val = None
            if isinstance(data, BaseInfoModel):
                dim_val = getattr(data, key_attr, None)
            elif isinstance(data, dict):
                if key_attr in data:
                    dim_val = data[key_attr]
            elif hasattr(data, key_attr):
                dim_val = getattr(data, key_attr)
            result[key_attr] = dim_val

        return result

    # Вытащить записи регистра сгруппированные по ключевым полям и
    # отсортированные по дате
    query = cls.objects
    order = []
    dims = []
    period = cls.period
    for dim_field in cls.dimentions:
        dim_attr = dim_field
        if isinstance(dim_field, models.Field):
            dim_attr = dim_field.name
        order.append(dim_attr)
        dims.append(dim_attr)
    order.append('info_date')
    query.order_by(order)

    # начальное значение ключа = пусто
    last_key = get_key(dims, None)
    last_rec = None

    for rec in query:
        # получим ключ тек. записи
        rec_key = get_key(dims, rec)
        # если тек. ключ не совпадает с предыдущим, то... надо что-то делать
        if not eq_keys(dims, rec_key, last_key):
            # отметим что не было предыдущих записей
            rec.info_date_prev = normdate(period, dt.datetime.min)
            # если была старая запись, то меняем ее и запишем
            if last_rec:
                last_rec.info_date_next = normdate(period, dt.datetime.max)
                last_rec._save()
        # если ключ совпал, то будем менять связи
        else:
            last_rec.info_date_next = rec.info_date
            last_rec._save()
            rec.info_date_prev = last_rec.info_date
        last_rec = rec
        last_key = rec_key
    # сохраним оставшуюся запись
    if last_rec:
        last_rec.info_date_next = normdate(period, dt.datetime.max)
        last_rec._save()


class BaseIntervalInfoModel(models.Model, metaclass=InfoModelMeta):
    DEFAULT_BEGIN = 'info_date_begin'
    DEFAULT_END = 'info_date_end'

    # тип управляющих полей по умолчанию остается DateTimeField
    # но может быть изменен на DateField - см. InfoModelMeta
    info_date_prev = models.DateTimeField(db_index=True, default=dt.datetime.min)
    info_date_next = models.DateTimeField(db_index=True, default=dt.datetime.max)
    info_date_begin = models.DateTimeField(db_index=True, blank=True)
    info_date_end = models.DateTimeField(db_index=True, blank=True)

    dimentions = []  # перечень реквизитов-измерений
    period = PeriodEnum.DAY  # тип периодичности

    # тут мы можем переопределить,
    # какое поле нам использовать для хранения даты начала.
    # по умолчанию используется info_date_begin
    begin_src = DEFAULT_BEGIN
    # тут мы можем переопределить,
    # какое поле нам использовать для хранения даты конца.
    # по умолчанию используется info_date_end
    end_src = DEFAULT_END
    # Если мы переопередяем какие поля нам использовать,
    # мы сами берем на себя отвественность
    # за настройку полей(тип, индексы, default, allow_blank и т.д.)

    def __init__(self, *args, **kwargs):
        super(BaseIntervalInfoModel, self).__init__(*args, **kwargs)
        # словарь параметров для передачи через сигналы
        self._signal_params = {}

    def _get_safe_value(self, fld_name):
        """
        Возвращает значение для поля. Если значение None,
        то пытается найти значение по умолчанию в мета-описании поля.
        Если и в поле не указано значение по умолчанию, то возвращает None
        """
        val = getattr(self, fld_name)
        if val is not None:
            return val
        # Если значение пустое, надо попытаться найти значение по умолчанию:
        fld = list(filter(lambda x: x.name == fld_name, self._meta.fields))[0]

        return None if fld.default is models.NOT_PROVIDED else fld.default

    @property
    def _begin(self):
        return self._get_safe_value(self.begin_src)

    @_begin.setter
    def _begin(self, val):
        setattr(self, self.begin_src, val)

    @property
    def _end(self):
        return self._get_safe_value(self.end_src)

    @_end.setter
    def _end(self, val):
        setattr(self, self.end_src, val)

    @classmethod
    def query_dimentions(cls, data):
        """
        Возвращает запрос по ключевым полям.

        :param data: объект, который содержит данные для сохранения в
            регистр. Это может быть:
            - Либо объект модели хранения данных регистра,
            - Либо словарь, ключами которого являются имена полей из
              модели хранения,
            - Либо объект любого класса, у которого есть атрибуты с
              именами
        """
        # Добавим в запрос фильтр по ключевым полям, со значениями =
        # текущему объекту, переданным данным
        query = cls.objects
        for dim_field in cls.dimentions:
            dim_val = None
            dim_attr = dim_field

            if isinstance(dim_field, models.Field):
                dim_attr = dim_field.name

            if isinstance(data, BaseInfoModel):
                if not hasattr(data, dim_attr):
                    continue
                dim_val = getattr(data, dim_attr)
            elif isinstance(data, dict):
                if dim_attr not in data:
                    continue
                dim_val = data[dim_attr]
            elif hasattr(data, dim_attr):
                dim_val = getattr(data, dim_attr)

            query = query.filter(**{dim_attr: dim_val})

        return query

    @classmethod
    def _gen_Q(cls, src, add, val):
        """
        Возвращает Q выражение для динамически состовляемых
        фильтров по дате начала\конца

        :param str src: указывает дату начала или конца
        :param str add: постфикс(gte, lte, ...). Пустая строка для равенства
        :param val: значение, с которым будем сравнивать
        """
        # шаблон фильтра принимает вид:
        # либо имяполя__постфикс(info_date_end__gte например)
        # или имяполя, если нет постфикса(info_date_end)
        _tmpl = '%s__%s' if add else '%s%s'

        if src == 'bgn':
            return Q(**{_tmpl % (cls.begin_src, add): val})
        elif src == 'end':
            return Q(**{_tmpl % (cls.end_src, add): val})

        raise RuntimeError('invalid arg <<src>> for _gen_Q method!')

    @classmethod
    def query_interval(
        cls, data, date_begin=dt.datetime.min, date_end=dt.datetime.max, include_begin=True, include_end=True
    ):
        """
        Возвращает запрос на записи, попадающие в указанный интервал дат.

        :param data: объект или словарь с ключевыми данными
        :param date_begin: начало интервала
        :param date_end: конец интервала
        :param bool include_begin: включать записи попадающие
            на начало интервала
        :param bool include_end: включать записи попадающие на конец интервала
        """
        query = cls.query_dimentions(data)

        if cls.period != PeriodEnum.INFTY:
            date_begin = normdate(cls.period, date_begin, True)
            date_end = normdate(cls.period, date_end, False)
            # попадание в интервал полностью
            _filter = cls._gen_Q('bgn', 'gte', date_begin) & cls._gen_Q('end', 'lte', date_end)

            if include_begin:
                # попадание начала интервала в границы записи
                _filter = _filter | (cls._gen_Q('bgn', 'lte', date_begin) & cls._gen_Q('end', 'gt', date_begin))
                if include_end:
                    # попадание конца интервала в границы записи
                    _filter = _filter | (cls._gen_Q('bgn', 'lt', date_end) & cls._gen_Q('end', 'gte', date_end))

        return query.filter(_filter)

    @classmethod
    def query_on_date(cls, data, date=None, active=True, next=False):
        """
        Запрос записей на дату

        :param data: объект или словарь с ключевыми данными
        :param date: дата актуальности, по-умолчанию текущая
        :param bool active: True - поиск записей, действующие на указанную дату
        :param bool next: False - поиск записей, действовавшие до даты, иначе
            ближайшиие записи которые будут действовать
        """
        if date is None:
            date = dt.datetime.now()

        query = cls.query_dimentions(data)

        if cls.period != PeriodEnum.INFTY:
            q_date_begin = normdate(cls.period, date, True)
            q_date_end = normdate(cls.period, date, False)
            if next:
                # дата попадает в интервал перед записью
                _filter = Q(info_date_prev__lte=q_date_begin) & cls._gen_Q('bgn', 'gt', q_date_end)
            else:
                # дата попадает в интервал после записи
                _filter = Q(info_date_next__gt=q_date_end) & cls._gen_Q('end', 'lte', q_date_begin)

            if active:
                # дата попадает в интервал записи
                _filter = _filter | (cls._gen_Q('bgn', 'lte', q_date_begin) & cls._gen_Q('end', 'gte', q_date_end))

            query = query.filter(_filter)

        return query

    def _save(self, *args, **kwargs):
        """
        Прямая запись объекта, чтобы можно было записывать без доп. обработки
        """
        super(BaseIntervalInfoModel, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Запись объекта с изменением соседних записей
        """
        if 'update_fields' in kwargs:
            kwargs['update_fields'] = set(kwargs['update_fields'])
            # Добавляем все поля, которые меняются в save()
            kwargs['update_fields'].update({'_begin', '_end', 'info_date_prev', 'info_date_next'})

        # если не указана дата записи, то
        if self.period != PeriodEnum.INFTY and not (self._begin and self._end):
            raise Exception('Attribute info_date is not set!')

        self._begin = normdate(self.period, self._begin, True)
        self._end = normdate(self.period, self._end, False)

        if self.period != PeriodEnum.INFTY and self._begin > self._end:
            raise InvalidIntervalError('%s > %s' % (self.__class__.begin_src, self.__class__.end_src))

        # проверим на уникальность записи
        if self.period != PeriodEnum.INFTY:
            q = self.__class__.query_interval(self, self._begin, self._end)
            if self.pk:
                q = q.exclude(pk=self.pk)

            if q.count() > 0:
                raise OverlapError(self.__class__)

        # если объект уже хранится, то найдем записи для изменения
        old_prev_rec = None
        old_next_rec = None

        if self.pk:
            q = (
                self.__class__.query_dimentions(self)
                .filter(self.__class__._gen_Q('end', '', self.info_date_prev))
                .exclude(pk=self.pk)
            )
            old_prev_rec = q.get() if q.count() == 1 else None

            q = (
                self.__class__.query_dimentions(self)
                .filter(self.__class__._gen_Q('bgn', '', self.info_date_next))
                .exclude(pk=self.pk)
            )
            old_next_rec = q.get() if q.count() == 1 else None

        # вычислим ближайщую запись, которая заканчивается "левее" текущей
        q = (
            self.__class__.query_dimentions(self)
            .filter(self.__class__._gen_Q('end', 'lte', self._begin) & Q(info_date_next__gte=self._begin))
            .exclude(pk=self.pk)
        )
        new_prev_rec = q.get() if q.count() == 1 else None

        # вычислим ближайшую запись, которая начинается "правее" текущей
        q = (
            self.__class__.query_dimentions(self)
            .filter(self.__class__._gen_Q('bgn', 'gte', self._end) & Q(info_date_prev__lte=self._end))
            .exclude(pk=self.pk)
        )
        new_next_rec = q.get() if q.count() == 1 else None

        # изменим даты исходя из соседей
        if new_prev_rec:
            self.info_date_prev = new_prev_rec._end
        else:
            self.info_date_prev = normdate(self.period, dt.datetime.min, False)

        if new_next_rec:
            self.info_date_next = new_next_rec._begin
        else:
            self.info_date_next = normdate(self.period, dt.datetime.max, True)

        self._save(*args, **kwargs)

        # изменим найденные ранее записи
        # TODO: можно оптимизировать сохранение, чтобы не было каскада сохранений
        if old_prev_rec and old_prev_rec != new_prev_rec:
            old_prev_rec.save()

        if old_next_rec and old_next_rec != new_next_rec:
            old_next_rec.save()

        if new_prev_rec and new_prev_rec.info_date_next != self._begin:
            new_prev_rec.info_date_next = self._begin
            new_prev_rec._save()

        if new_next_rec and new_next_rec.info_date_prev != self._end:
            new_next_rec.info_date_prev = self._end
            new_next_rec._save()

    @InfoModelMeta.suppress_signals
    def _delete(self, *args, **kwargs):
        """
        Прямое удаление без обработки
        """
        super(BaseIntervalInfoModel, self).delete(*args, **kwargs)

    class Meta:
        abstract = True


def rebuild_interval_info_model(cls, on_overlap_error=0):
    """
    Перестраивает связи между записями в интервальном регистре

    :param int on_overlap_error: действие при возникновении ошибки
        перекрытия диапазонов записей:
        0 - вызвать exception
        1 - изменить интервал записи с ранней датой начала
        2 - выдать список ID некорректных элементов, которые пропущены
            (после исправления придется еще раз запускать пересчет)
    """

    def eq_keys(dims, dict1, dict2):
        for key_attr in dims:
            if dict1[key_attr] != dict2[key_attr]:
                return False

        return True

    def get_key(dims, data):
        key = {}

        for key_attr in dims:
            dim_val = None
            if isinstance(data, BaseIntervalInfoModel):
                dim_val = getattr(data, key_attr, None)
            elif isinstance(data, dict):
                if key_attr in data:
                    dim_val = data[key_attr]
            elif hasattr(data, key_attr):
                dim_val = getattr(data, key_attr)
            key[key_attr] = dim_val

        return key

    # достаем записи регистра сгруппированные по ключевым полям и
    # отсортированные по дате
    query = cls.objects
    order = []
    dims = []
    error_ids = []
    period = cls.period

    for dim_field in cls.dimentions:
        dim_attr = dim_field
        if isinstance(dim_field, models.Field):
            dim_attr = dim_field.name
        order.append(dim_attr)
        dims.append(dim_attr)

    order.append(cls.begin_src)

    for field_name in order:
        query = query.order_by(field_name)

    # начальное значение ключа = пусто
    last_key = get_key(dims, None)
    last_rec = None

    for rec in query:
        # получим ключ тек. записи
        rec_key = get_key(dims, rec)
        # если тек. ключ не совпадает с предыдущим, то... надо что-то делать
        if not eq_keys(dims, rec_key, last_key):
            # отметим что не было предыдущих записей
            rec.info_date_prev = normdate(period, dt.datetime.min, True)
            # если была старая запись, то меняем ее и запишем
            if last_rec:
                last_rec.info_date_next = normdate(period, dt.datetime.max, False)
                last_rec._save()
        else:
            # если ключ совпал, то будем менять связи, и проверим
            # перекрытие интервала
            if rec._begin < last_rec._end:
                # текущая запись попадает в интервал предыдущей
                # изменим пред. запись
                if on_overlap_error == 1:
                    last_rec._end = normdate(period, shift_date(period, rec._begin, -1), False)
                else:
                    # если ведем лог ошибочных записей, то продолжим
                    if on_overlap_error == 2:
                        error_ids.append(rec.id)
                        continue
                    else:
                        raise OverlapError()

            last_rec.info_date_next = rec._begin
            last_rec._save()
            rec.info_date_prev = last_rec._end

        last_rec = rec
        last_key = rec_key

    # сохраним оставшуюся запись
    if last_rec:
        last_rec.info_date_next = normdate(period, dt.datetime.max, False)
        last_rec._save()

    if error_ids and on_overlap_error == 2:
        return error_ids
