import pandas as pd


def z_score_standardization(df: pd.DataFrame, range_: tuple = (0, 1)) -> pd.DataFrame:
    """Z-Score 数据标准化

    Args:
        df (pd.DataFrame): _description_
        range_ (tuple, optional): 标准化后的数据范围，默认是0-1

    Returns:
        pd.DataFrame: _description_
    """
    from sklearn import preprocessing

    values = df.values
    values = values.astype('float32')
    scaled = preprocessing.MinMaxScaler(feature_range=range_)
    scaled_data = scaled.fit_transform(values)
    result_df = pd.DataFrame(scaled_data)
    result_df.columns = df.columns
    result_df.index = df.index
    return result_df


def extract_float_from_str(s: str):
    '''
    给定的字符串中提取其中所有的数字
    :param s:
    :return:
    '''
    import re

    result_list = re.findall(r'-?\d+\.?\d*', s)
    return list(map(float, result_list))


def convert_float_for_dataframe_columns(target_df, columns, number=2, thousands=True):
    """
    给定的dataframe中，指定[列]中的所有数字转换convert_float_format
    :param target_df:
    :param columns: list-> [column1, column2]
    :param number: 保留小数点后几位
    :param thousands:
    :return:
    """
    for column in columns:
        target_df[column] = target_df[column].apply(
            convert_float_format, args=(number, thousands,))
    return target_df


# 转换数字为：保留n位小数；是否使用千分位
def convert_float_format(target, number=2, thousands=True):
    if isinstance(target, str):
        target = float(target.replace(',', ''))
    first_step = round(target, number)
    second_step = format(first_step, ',') if thousands else first_step
    return second_step
