from datetime import datetime, timedelta

import pandas as pd


def get_date_list(start_date, end_date):
    """
    获取指定起始日期和结束日期之间的所有日期列表。

    Args:
      start_date: 起始日期，格式为 'YYYY-MM-DD'。
      end_date: 结束日期，格式为 'YYYY-MM-DD'。

    Returns:
      一个包含所有日期的列表，格式为 ['YYYY-MM-DD', 'YYYY-MM-DD', ... ]。
      如果起始日期晚于结束日期，则返回 ValueError。
    """
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return ValueError("日期格式错误，请使用'YYYY-MM-DD'格式")

    if start_date > end_date:
        return ValueError("起始日期不能晚于结束日期")

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list


def get_q_end(target_date):
    '''
    获取给定日期所在的季度最后一天
    :param target_date: 6位数日期，例如20211201
    :return: 6位数日期，例如20211231
    '''
    quarter = pd.Period(target_date, 'Q').quarter
    if quarter == 1:
        return datetime(pd.to_datetime(target_date).year, 3, 31).strftime('%Y%m%d')
    elif quarter == 2:
        return datetime(pd.to_datetime(target_date).year, 6, 30).strftime('%Y%m%d')
    elif quarter == 3:
        return datetime(pd.to_datetime(target_date).year, 9, 30).strftime('%Y%m%d')
    else:
        return datetime(pd.to_datetime(target_date).year, 12, 31).strftime('%Y%m%d')


def get_previous_q_first_last(target_date: str, q_num: int) -> list:
    """获得给定的日期前XX个季度的第一天和最后一天的列表
        例如给定日期为20230113，q_num是5，则获取前5个季度的第一天、最后一天和年度季度的日期字符串列表

    Args:
        target_date (str): YYYYMMDD
        q_num (int): 获取前多少个季度

    Returns:
        list: [(firstday, lastday, YYYYQX), (...)...]
    """
    p = pd.Period(target_date, 'Q')
    cq = p.quarter
    cy = p.year
    result_list = []
    for i in range(1, q_num+1):
        cq = cq-1
        if cq <= 0:
            cq = 4
            cy -= 1

        if cq == 1:
            start = datetime(cy, 1, 1).strftime('%Y%m%d')
            end = datetime(cy, 3, 31).strftime('%Y%m%d')
        elif cq == 2:
            start = datetime(cy, 4, 1).strftime('%Y%m%d')
            end = datetime(cy, 6, 30).strftime('%Y%m%d')
        elif cq == 3:
            start = datetime(cy, 7, 1).strftime('%Y%m%d')
            end = datetime(cy, 9, 30).strftime('%Y%m%d')
        elif cq == 4:
            start = datetime(cy, 10, 1).strftime('%Y%m%d')
            end = datetime(cy, 12, 31).strftime('%Y%m%d')
        result_list.append((start, end, f'{cy}Q{cq}'))
    return result_list


def get_q_first_last_by_q_name(qname: str) -> list:
    """给定的季度名称，例如2022q1，返回[20220101, 20220331]

    Args:
        qname (str): _description_

    Returns:
        list: [first_day, last_day]
    """
    year = qname[:4]
    q = qname[4:].lower()
    match q:
        case 'q1':
            first = '0101'
            last = '0331'
        case 'q2':
            first = '0401'
            last = '0630'
        case 'q3':
            first = '0701'
            last = '0930'
        case 'q4':
            first = '1001'
            last = '1231'
    return [year+first, year+last]
