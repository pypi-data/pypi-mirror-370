#coding:utf-8
"""
Created on 12.04.2011

@author: akvarats
"""
from __future__ import absolute_import
import calendar
import datetime
from six.moves import range


class PeriodEnum:
    u"""
    Перечисление возможных периодов хранения данных в регистре
    """
    INFTY = 1  # в регистре нет периодичности и нет динамически хранящихся
    SECOND = 2  # до секунд
    MINUTE = 3
    HOUR = 4
    DAY = 5
    MONTH = 6
    QUARTER = 7
    YEAR = 8


def normdate(period, date, begin=True):
    u"""
    Метод нормализует дату в зависимости от периода

    :param PeriodEnum period: период, по которому нормализуется дата
    :param date: дата/датавремя для нормализации
    :param bool begin: выравнивание даты на начало периода или на конец
    :return: нормализованная по периоду дата
    :rtype: datetime
    """
    if not date:
        return None

    if period == PeriodEnum.INFTY:
        return date

    year = date.year
    month = date.month
    day = date.day
    hour = 0 if begin else 23
    second = minute = 0 if begin else 59

    if period in (PeriodEnum.YEAR, PeriodEnum.QUARTER, PeriodEnum.MONTH):
        if period == PeriodEnum.YEAR:
            month = 1 if begin else 12
        elif period == PeriodEnum.QUARTER:
            quarters_last_months = list(range(3, 13, 3))
            # проверяем квартал у месяца
            for last_month in quarters_last_months:
                if month <= last_month:
                    month = last_month - 2 if begin else last_month
                    break
        # на конец периода последний день месяца
        day = 1 if begin else calendar.monthrange(year, month)[1]
    elif period != PeriodEnum.DAY:
        hour = date.hour
        if period != PeriodEnum.HOUR:
            minute = date.minute
        if period == PeriodEnum.SECOND:
            second = date.second

    return datetime.datetime(year, month, day, hour, minute, second)