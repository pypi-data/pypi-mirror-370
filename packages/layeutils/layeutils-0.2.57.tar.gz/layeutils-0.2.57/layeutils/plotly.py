import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


def dual_axis_plotly_line(data_df: pd.DataFrame, l1_col: str, l2_col: str, title: str = None):
    """双坐标轴plotly图，调用show()显示

    Args:
        data_df (pd.DataFrame): _description_
        l1_col (str): _description_
        l2_col (str): _description_
        title (str, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    trace1 = go.Scatter(
        x=data_df.index,
        y=data_df[l1_col],
        name=data_df[l1_col].name
    )
    trace2 = go.Scatter(
        x=data_df.index,
        y=data_df[l2_col],
        name=data_df[l2_col].name,
        xaxis='x',
        yaxis='y2'  # 标明设置一个不同于trace1的一个坐标轴
    )
    data = [trace1, trace2]
    layout = go.Layout(
        yaxis2=dict(anchor='x', overlaying='y', side='right'),
        template='plotly_dark',
        title=title if title else f'{data_df[l1_col].name} VS {data_df[l2_col].name}'
    )
    return go.Figure(data=data, layout=layout)


def plotly_simple_line(df: pd.DataFrame, x_series: str, y_series: str, title: str = '', template: str = 'plotly_dark'):
    """最简单的线图，调用show()显示，或者继续增加设置- fig.update_traces然后调用show()显示

    Args:
        df (pd.DataFrame): _description_
        x_series (_type_): _description_
        y_series (_type_): _description_
        title (str, optional): _description_. Defaults to ''.
        template (str, optional): _description_. Defaults to 'plotly_dark'.

    Returns:
        _type_: _description_
    """
    return px.line(
        data_frame=df,
        x=x_series,
        y=y_series,
        title=title,
        template=template)


def plotly_simple_bar(df: pd.DataFrame, x_series: str, y_series: str, title: str = '', template: str = 'plotly_dark'):
    """最简单的柱状图，调用show()显示，或者继续增加设置- fig.update_traces然后调用show()显示

    Args:
        df (pd.DataFrame): _description_
        x_series (_type_): _description_
        y_series (_type_): _description_
        title (str, optional): _description_. Defaults to ''.
        template (str, optional): _description_. Defaults to 'plotly_dark'.

    Returns:
        _type_: _description_
    """
    return px.bar(
        data_frame=df,
        x=x_series,
        y=y_series,
        title=title,
        template=template)


def plotly_simple_pie(
        df: pd.DataFrame, value_series: str, by_series: str, title: str = '', template: str = 'plotly_dark'):
    """最简单的饼图，调用show()显示，或者继续增加设置- fig.update_traces然后调用show()显示

    Args:
        df (pd.DataFrame): _description_
        value_series (str): _description_
        by_series (str): _description_
        title (str, optional): _description_. Defaults to ''.
        template (str, optional): _description_. Defaults to 'plotly_dark'.

    Returns:
        _type_: _description_
    """
    return px.pie(
        data_frame=df,
        values=value_series,
        names=by_series,
        title=title,
        template=template)
