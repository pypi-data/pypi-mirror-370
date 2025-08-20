import pandas as pd


def dtale_start(df: pd.DataFrame, **options):
    """利用Vscode端口映射启动dtale，强制指定host为0.0.0.0

    Args:
        df (pd.DataFrame): 目标DF
        options: 其他参数

    Returns:
        dtale.show
    """
    import dtale
    return dtale.show(df, host='0.0.0.0', **options)
