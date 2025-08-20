import csv
import io
import json
import os
import re
import warnings
import zipfile
from io import BytesIO
import pandas as pd
from requests import request

from smartpush.utils.StringUtils import StringUtils

warnings.simplefilter("ignore")
excel_extensions = ['.xlsb', '.xlsx', '.xlsm', '.xls', '.xltx', '.xltm', '.xlam', None]
csv_extensions = ['.csv']


def read_excel_file_form_local_path(file_path, usecols,sheet_name=None):
    """
    读取Excel文件并返回数据

    参数:
    file_path (str): Excel文件路径
    sheet_name (str, optional): 要读取的工作表名称，默认为None(读取所有表)

    返回:
    dict: 每个工作表的DataFrame字典，或单个DataFrame(如果指定了sheet_name)
    """

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.xlsx', '.xls']:
        raise ValueError(f"不支持的文件格式: {file_ext}，请提供.xlsx或.xls文件")

    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            # 检查是否包含Excel必要的XML文件
            required_files = ['[Content_Types].xml', 'xl/workbook.xml']
            for f in required_files:
                if f not in z.namelist():
                    raise
    except zipfile.BadZipFile:
        return False

    try:
        # 读取所有工作表
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names
        result = {}
        for sheet in sheets:
            df = excel_file.parse(sheet, usecols=usecols)
            #     result[sheet] = df
            #     print(f"成功读取工作表 '{sheet}'，共 {len(df)} 行数据")
            return df
        return result

    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None


def read_excel_from_oss(url="", method="get"):
    """读取oss的excel内容转为io流数据"""
    try:
        result = request(method=method, url=url)
        excel_data = BytesIO(result.content)
        print(f"成功读取oss文件内容: {url}")
        return excel_data
    except Exception as e:
        print(f"读取oss报错 {url} 时出错：{e}")


def read_excel_header(excel_data, return_type='list', **kwargs):
    """
    1、读出excel的头列 list
    """
    try:
        result = []
        result_dict = {}
        skip_rows, skip_flags = (kwargs.pop('skiprows'), True) if 'skiprows' in kwargs else (0, False)
        dfs = read_excel_csv_data(excel_data, **kwargs)
        if kwargs.get('type', None) in excel_extensions:
            for sheet_name, df in dfs.items():
                # if skip_flags:
                #     # 因为单元格合并并且跳过存在动态参数，所以这里简单粗暴set去重
                #     headers = list(set(df.iloc[skip_rows].tolist()))
                # else:
                headers = df.iloc[skip_rows].tolist()
                result.append(headers)
                result_dict[sheet_name] = headers
            if return_type == 'list':
                return result
            else:
                return result_dict
        else:
            # csv的头
            # result = dfs.keys().values.tolist()
            result = dfs.index.tolist()  # csv转置后读取头数据
            return result
    except Exception as e:
        print(f"excel生成header-list出错：{e}")
        raise


def read_excel_csv_data(excel_data, **kwargs):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
        if kwargs.get('type', None) in excel_extensions:
            dfs = pd.read_excel(excel_data, sheet_name=None, na_filter=False, engine='openpyxl',
                                skiprows=kwargs.get('skiprows', None), header=kwargs.get('header', None)) if isinstance(
                excel_data,
                io.BytesIO) \
                else excel_data
        else:
            dfs = pd.read_csv(excel_data, encoding='utf-8', na_filter=False, dtype={'\ufeff姓名': str})
            # 这里替换制表符
            # for col in dfs.columns:
            #     if dfs[col].dtype == 'object':  # 只处理字符串类型的列
            #         dfs[col] = dfs[col].str.replace('\t', '')
            dfs = dfs.transpose()  # 转置
        return dfs


def read_excel_and_write_to_dict(excel_data=None, file_name=None, **kwargs):
    """excel内容并写入到内存dict中
    :param excel_data：excel的io对象, 参数和file_name互斥
    :file_name: excel文件名称，目前读取check_file目录下文件，参数和excel_data互斥
    """
    dfs = None
    try:
        if excel_data is not None and file_name is not None:
            pass
        elif file_name is not None:
            excel_data = os.path.join(os.path.dirname(os.getcwd()) + "/check_file/" + file_name)
        dfs = read_excel_csv_data(excel_data, **kwargs)
        if kwargs.get('type', None) in excel_extensions:
            # 将DataFrame转换为字典，以行为单位存储数据
            row_dict = {}  # 创建一个空字典来存储按行转换的数据
            for sheet_name, row in dfs.items():
                row = row.to_dict(orient='records')
                if kwargs.get("ignore_sort") is not None and StringUtils.to_lower(sheet_name) == \
                        StringUtils.to_lower(kwargs.get("ignore_sort_sheet_name", sheet_name)):  # 可传参指定那个sheet_name
                    sorted_data_asc = sorted(row[1:], key=lambda x: x.get(kwargs.get("ignore_sort"), 0),
                                             reverse=True)  # 内部排序
                    sorted_data_asc = [row[0]] + sorted_data_asc
                    row_dict[sheet_name] = sorted_data_asc
                else:
                    row_dict[sheet_name] = row
        else:
            row_dict = dfs.to_dict()
        return row_dict
    except zipfile.BadZipFile:
        print(f"文件读取错误，请检查文件是否为无效文件：{dfs}")
        raise
    except Exception as e:
        print(f"excel写入dict时出错：{e}")


def read_excel_and_write_to_list(excel_data=None, sheet_name=None, file_name=None, **kwargs):
    """excel内容并写入到内存list中
    :param excel_data：excel的io对象, 参数和file_name互斥
    :file_name: excel文件名称，目前读取check_file目录下文件，参数和excel_data互斥
    """
    try:
        if excel_data is not None and file_name is not None:
            pass
        elif file_name is not None:
            excel_data = os.path.join(os.path.dirname(os.getcwd()) + "/check_file/" + file_name)
        dfs = read_excel_csv_data(excel_data, **kwargs)
        rows_list = []
        excel_header = read_excel_header(dfs, **kwargs)
        index = 0
        # 多sheet处理
        for name, df in dfs.items():
            row_list = df.values.tolist()
            row_list.insert(0, excel_header[index])
            rows_list.append(row_list)
            index += 1
        if len(dfs) <= 1:
            rows_list = rows_list[0]
        # 插入表头
        return rows_list
    except Exception as e:
        print(f"excel写入list时出错：{e}")


def read_excel_and_write_to_csv(excel_data, file_name, **kwargs):
    """excel内容并写入到csv中"""
    try:
        df = pd.read_excel(excel_data, engine="openpyxl")
        local_csv_path = os.path.join(os.path.dirname(os.getcwd()) + "/temp_file/" + file_name)
        df.to_csv(local_csv_path, index=False, **kwargs)
        return local_csv_path
    except Exception as e:
        print(f"excel写入csv时出错：{e}")


def read_excel_data_for_oss_write_to_dict(oss, **kwargs) -> dict:
    """
    1、根据oss link 直接读出 dict-list
    2、支持多sheet，默认sheet_name =None查全部
    3、返回dict结构 {'sheet_name':[rows_list]}
    """
    try:
        dfs = read_excel_csv_data(read_excel_from_oss(oss), **kwargs)
        result = {}
        for sheet_name, df in dfs.items():
            rows_list = df.values.tolist()
            result[sheet_name] = rows_list
        return result
    except Exception as e:
        print(f"excel生成dict出错：{e}")


# 从 URL 中提取文件名
def get_file_suffix_name(url):
    if StringUtils.is_empty(url):
        raise ValueError("Oss Url不允许为空")
    last_filename = ""
    filename = url.split("/")[-1]
    # 从文件名中提取文件后缀
    if '.' in filename:
        last_filename = '.' + filename.split('.')[-1].lower()
    support_types = excel_extensions + csv_extensions
    if last_filename in support_types:
        return last_filename
    else:
        raise Exception(f"[{last_filename}] 该类型暂不支持！目前只支持 {support_types}")
