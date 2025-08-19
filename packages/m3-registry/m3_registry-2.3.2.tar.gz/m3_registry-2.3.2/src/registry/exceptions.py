#coding:utf-8
"""
Created on 13.04.2011

@author: akvarats
"""


class GenericRegisterException(Exception):
    u"""
    Общий класс исключения некорректной работы с регистром
    """
    pass


class WrongRegisterMeta(GenericRegisterException):
    u"""
    Исключительная ситуация некорректной настройки регистра разработчиком
    """
    pass