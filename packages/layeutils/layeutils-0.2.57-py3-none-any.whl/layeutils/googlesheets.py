"""使用gspread库，需要首先安装配置：
    https://docs.gspread.org/en/latest/oauth2.html#service-account
"""
import gspread
import pandas as pd


def get_spreadsheet(file_title: str, folder_id: str = None) -> gspread.Spreadsheet:
    """根据给定的文件名，Sheet名称，返回gspread.Worksheet对象; 如果要获得gspread.Spreadsheet对象，使用get_spreadsheet()方法

    Args:
        file_title (str): _description_
        folder_id (str, optional): 如果有重名文件，则默认返回第一个，否则需要指定folder_id. Defaults to None.. Defaults to None.

    Returns:
        gspread.Worksheet: _description_
    """
    return gspread.service_account().open(title=file_title, folder_id=folder_id)


def get_worksheet(file_title: str, sheet_name: str, folder_id: str = None) -> gspread.Worksheet:
    """根据给定的文件名，Sheet名称，返回gspread.Worksheet对象; 如果要获得gspread.Spreadsheet对象，使用get_spreadsheet()方法

    Args:
        file_title (str): _description_
        sheet_name (str): _description_
        folder_id (str, optional): 如果有重名文件，则默认返回第一个，否则需要指定folder_id. Defaults to None.. Defaults to None.

    Returns:
        gspread.Worksheet: _description_
    """
    spreadsheet = gspread.service_account().open(title=file_title, folder_id=folder_id)
    return spreadsheet.worksheet(title=sheet_name)


def worksheet2df(worksheet: gspread.Worksheet) -> pd.DataFrame:
    """将gspread.Worksheet对象内容提取成为pd.DataFrame

    Args:
        worksheet (gspread.Worksheet): _description_

    Returns:
        pd.DataFrame: _description_
    """
    return pd.DataFrame(worksheet.get_all_records())


def update_worksheet_by_df(worksheet: gspread.Worksheet, content_df: pd.DataFrame) -> None:
    """更新worksheet文件，这里的更新不是追加，而是全量更新

    Args:
        worksheet (gspread.Worksheet): _description_
        content_df (pd.DataFrame): _description_
    """
    worksheet.update(
        [content_df.columns.values.tolist()] + content_df.values.tolist(),
        value_input_option='USER_ENTERED')


def add_worksheet(spreadsheet: gspread.Spreadsheet, worksheet_title: str, rows: int, cols: int):
    added = spreadsheet.add_worksheet(title=worksheet_title, rows=rows, cols=cols)
    return added
