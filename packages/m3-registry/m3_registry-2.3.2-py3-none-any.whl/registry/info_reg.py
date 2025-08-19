# -*- coding: utf-8 -*-

from __future__ import absolute_import
import datetime
import copy

from django.db.models.base import ModelBase
from django.db import models
import six


class InformationRegistryMeta(ModelBase):
    u"""
    Метакласс регистра сведений. Предназначен для создания полей регистра
    на ходу, исходя из указанных в нём управляемых моделей и полей
    """
    def __new__(cls, name, bases, _dict):
        super_new = super(InformationRegistryMeta, cls).__new__
        clazz = super_new(cls, name, bases, _dict)
        
        # создаваемый класс должнен наследоваться от регистра
        for base in bases:
            if base.__name__ == 'BaseInformationRegistry':
                break
        else:
            return clazz
        
        if not clazz.managed_models or hasattr(clazz, '_fields_conformity'):
            return clazz
        
        # Получаем все экземпляры полей, имена моделей и имена полей
        ignored = ['id']
        all_fields = []
        for model in clazz.managed_models:
            for field in model._meta.local_fields:
                if field.attname not in ignored:
                    all_fields.append((field, model.__name__, field.name))
        
        # Формируем список полей которые будут созданы в регистре:
        # Класс, полное имя, соответствие
        fields_to_make = []
        fields_conformity = {}
        managed_fields = clazz.managed_fields
        if not managed_fields:
            # Берем все поля управляемой модели
            for field_obj, model_name, field_name in all_fields:
                fields_to_make.append((field_obj, field_name))
                fields_conformity[field_name] = field_name
        elif isinstance(managed_fields, (tuple, list)):
            # Берем первое попавшееся совпадающее имя
            for name in managed_fields:
                for field_obj, model_name, field_name in all_fields:
                    if name == field_name:
                        fields_to_make.append((field_obj, name))
                        fields_conformity[name] = name
                        break
                else:
                    raise ValueError(
                        u'Поле %s не найдено в указанных моделях '
                        u'%s' % (name, managed_fields))
        elif isinstance(managed_fields, dict):
            # Уже есть строгое соответствие
            for key, value in six.iteritems(managed_fields):
                m_name, f_name = key.split('.')
                for field_obj, model_name, field_name in all_fields:
                    if m_name == model_name and f_name == field_name:
                        fields_to_make.append((field_obj, value))
                        fields_conformity[key] = value
                        break
                else:
                    raise ValueError(
                        u'Имя модели и поля %s.%s указанное в managed_fields'
                        u' не найдены в managed_models %s' % (
                            m_name, f_name, managed_fields))
        else:
            raise TypeError(u'Неверный тип managed_fields')
        
        clazz._fields_conformity = fields_conformity
        
        # Создаем такие же поля, но не клонируем,
        # т.к. нужны лишь некоторые свойства
        for field, name in fields_to_make:
            new_field = copy.copy(field)
            # Нужно удалить уникальность, чтобы не сбивать вставку истории
            new_field.primary_key = False
            new_field._unique = False
            new_field.contribute_to_class(clazz, name)
         
        return clazz


def check_obj(obj):
    u"""
    Проверяет на наличие класса модели Джанго в предках объекта

    :param obj: проверяемый объект
    :raise: TypeError
    """
    if not isinstance(obj, models.Model):
        raise TypeError(
            u'Объект по которому запрашивается история должен быть '
            u'наследником models.Model')


class BaseInformationRegistry(six.with_metaclass(InformationRegistryMeta, models.Model)):
    u"""
    Абстактный базовый класс для создания регистра сведений
    """
    managed_models = []
    managed_fields = []
    
    history_time_stamp = models.DateTimeField(db_index=True)
    history_object_id = models.IntegerField(db_index=True)
    
    def mapping(self, *args, **kwargs):
        u"""
        Раскидывает данные по полям регистра в порядке определенном пользователем
        Предполагается, что в args передаются объекты, а в kwargs отдельные поля

        :param list args: экземпляры моделей managed_models
        """
        # Попробуем получить нужные нам поля из каждого объекта
        for obj in args:
            if not isinstance(obj, tuple(self.managed_models)):
                raise TypeError(u'Нужно передавать экземпляр модели')
            for orig_name, pseudonym in six.iteritems(self._fields_conformity):
                if '.' in orig_name:
                    # Нужно точное соответствие
                    model_name, field_name = orig_name.split('.')
                    if obj.__class__.__name__ == model_name:
                        value = obj.__getattribute__(field_name)
                        self.__setattr__(pseudonym, value)
                elif hasattr(obj, orig_name):
                    # Подойдет любой
                    value = obj.__getattribute__(orig_name)
                    self.__setattr__(pseudonym, value)
        
        # Попробуем заполнить по полям из словаря
        for name, value in six.iteritems(kwargs):
            if not hasattr(self, name):
                raise AttributeError(
                    u'Регистр не содержит атрибут с именем %s' % name)
            if name != 'id':
                self.__setattr__(name, value)
        
        # Откуда-то нужно достать id
        if not self.history_object_id:
            self.history_object_id = args[0].id if args else kwargs['id']

        self.save()
    
    @classmethod
    def add_object(cls, *args, **kwargs):
        u"""
        Создает новую запись регистра и инициализирует ее переданными значениями

        :param args: экземпляры моделей self.managed_models, значениями
                    полей которых будем инициализировать
        :param kwargs: словарь значений отдельный полей для инициализации
        :return: cls()
        """
        new_record = cls()
        new_date = kwargs.pop('date', datetime.datetime.now())
        new_record.history_time_stamp = new_date
        cls.mapping(new_record, *args, **kwargs)

        return new_record
    
    @classmethod
    def get_object(cls, obj, date=None):
        u"""
        Возвращает актуальную запись регистра на дату по объекту

        :return: запись регистра или None
        """
        check_obj(obj)
        date = date or datetime.datetime.now()

        result = cls.objects.filter(
            history_time_stamp__lte=date,
            history_object_id=obj.id
        ).order_by('-history_time_stamp')

        if result.exists():
            return result[0]

    @classmethod
    def get_history(cls, obj, reverse=False):
        u"""
        Возвращает историю регистра по объекту c сортировкой по времени и
        идентификатору

        :param obj: объект, по которому ищутся записи регистра
        :param bool reverse: обратная сортировка или по возрастанию

        :return: django.db.models.query.QuerySet
        """
        check_obj(obj)
        result = cls.objects.filter(history_object_id=obj.id)

        if reverse:
            order_by = ['-history_time_stamp', '-id']
        else:
            order_by = ['history_time_stamp', 'id']

        return result.order_by(*order_by)

    class Meta:
        abstract = True

#FIXME: 
#TODO: Сделать возможность хранения нескольких id моделей
#TODO: Сделать возможность хранения нескольких id моделей
