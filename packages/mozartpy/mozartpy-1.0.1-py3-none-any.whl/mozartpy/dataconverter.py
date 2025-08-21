import os
from pythonnet import get_runtime_info
import pandas as pd
import time
import sys
import decimal

import clr
clr.AddReference('System.Data.Common')
clr.AddReference('System.Data')
clr.AddReference("System.Collections")

info = get_runtime_info()

import System
from System import Data, Decimal, DateTime, DateTimeKind, DateTimeOffset, TimeSpan
from datetime import datetime
from System.Data import DataTable
from System.Data import DataColumn

# from System.IO import MemoryStream

def TableToDataFrame(dt):
    ''' Convert DataTable type to DataFrame type '''

    colTempCount = 0
    dic = {}
    # DataFrameToTable 수행 시 사용하기 위한 DotNet 컬럼 타입 정보 별도 저장
    columnTypesForDotNet = {}
    while (colTempCount < dt.Columns.Count):
        li = []
        rowTempCount = 0
        column = dt.Columns[colTempCount]
        colName = column.ColumnName
        typeName = column.DataType.Name
        while (rowTempCount < dt.Rows.Count):
            result = dt.Rows[rowTempCount][colTempCount]
            try:
                if typeName == 'Decimal' and System.DBNull.Value != result:
                    li.append(Decimal.ToDouble(result))
                elif typeName != 'DateTime' and result == System.DBNull.Value:
                    li.append(None)
                else:
                    li.append(result)
            except Exception as err:
                print(err)

            rowTempCount = rowTempCount + 1

        colTempCount = colTempCount + 1
        dic.setdefault(colName, li)
        columnTypesForDotNet[colName] = typeName

    df = pd.DataFrame(dic)
    df.attrs['columnTypesForDotNet'] = columnTypesForDotNet

    return (df)

def DataFrameToDic(df):
    ''' Convert DataFrame data type to dictionary type '''
    dic = df.to_dict(' list ')
    return dic

def TableToDataFrame2(dt):
    # 컬럼 이름 추출
    columns = [column.ColumnName for column in dt.Columns]
    decimal_cols = [column.ColumnName for column in dt.Columns if column.DataType.Name == "Decimal"]

    data = []
    for row in dt.Rows:
        data.append([row[column] for column in columns])

    df = pd.DataFrame(data, columns=columns)
    for dcol in decimal_cols:
        df[dcol] = pd.to_numeric(df[dcol], errors='ignore')
        print(df[dcol])

    return df

def TableToDataFrame_Test(dt):
    import System.Data
    # linq 사용하기 위해서는 다음 추가필요
    clr.AddReference("System.Core")

    sys.path.append(r'<path>')

    # 컬럼 이름 추출
    columns = [column.ColumnName for column in dt.Columns]

    # rows = dt.AsEumerable()
    rows = System.Data.DataTableExtensions.AsEnumerable(dt)
    df = pd.DataFrame.from_records(rows, columns=columns)
    return df


def DataFrameToTable(df, name):
    """ Convert DataFrame data type into DataTable data type """
    dtable = DataTable(name)
    columnTypesForDotNet = df.attrs['columnTypesForDotNet']
    # Add columns to the DataTable based on the columns in the pandas DataFrame
    for column_name in df.columns:
        column = DataColumn(column_name)
        columnTypeForDotNet = columnTypesForDotNet[column_name]
        if df.dtypes[column_name] == 'int64':
            column.DataType = System.Type.GetType('System.Int32')
        elif df.dtypes[column_name] == 'float64':
            column.DataType = System.Type.GetType('System.Single')
        elif column.DataType == 'bool':
            column.DataType = System.Type.GetType('System.Boolean')
        elif columnTypeForDotNet == 'DateTime':
            column.DataType = System.Type.GetType('System.DateTime')
        dtable.Columns.Add(column)

    # Add rows to the DataTable based on the rows in the pandas DataFrame
    for index, row in df.iterrows():
        data_row = dtable.NewRow()
        for column_name in df.columns:
            if columnTypesForDotNet[column_name] == 'DateTime' and isinstance(row[column_name], pd.Timestamp):
                # Pandas Timestamp를 System.DateTime으로 변환
                dt_value = row[column_name]
                ticks = int((dt_value.to_pydatetime() - datetime(1, 1, 1)).total_seconds() * 10**7)
                if dt_value.tz is not None:  # 타임존 정보가 있을 경우
                    # UTC로 변환하여 System.DateTime 생성
                    offset = dt_value.utcoffset()  # timedelta 형태로 오프셋 가져오기
                    if offset is not None:
                        # 오프셋을 초 단위로 변환
                        offset_seconds = offset.total_seconds()
                        # 오프셋을 적용하여 DateTime 저장
                        data_row[column_name] = DateTimeOffset(ticks, TimeSpan(offset_seconds  * 10**7)).DateTime
                    else:
                        data_row[column_name] = DateTime(ticks,DateTimeKind.Unspecified)  # 오프셋이 없다면 Unspecified로 설정
                else:
                    data_row[column_name] = DateTime(ticks, DateTimeKind.Local)  # 로컬 시간으로 설정
            else:
                data_row[column_name] = row[column_name]
        dtable.Rows.Add(data_row)

    return dtable


def DictToArg(cs_dict):
    """
    Convert a C# arguments to a Python dictionary.

    :param cs_dict: C# arguments object
    :return: Python dictionary
    """
    pyth_dict = {}

    # Extract the key and value from the KeyValuePair object
    key = cs_dict.Key
    value = cs_dict.Value

    if isinstance(value, System.Decimal):
        value = float(str(cs_dict.Value))

    elif isinstance(value, System.DateTime):
        value = str(cs_dict.Value)

    else:
        value = cs_dict.Value

    # Add the key-value pair to the Python dictionary
    pyth_dict[key] = value

    return pyth_dict


def ExcRunToDataFrame(execution):
    """
    Convert List of Execution Run DataTypes to Pandas DataFrame
    """

    data = {}

    for run in execution.Runs:
        embedded_data = {
            "Run Index": run.Index,
            "Run Name": run.Name,
            "Start Time": run.StartTime,
            "End Time": run.EndTime,
        }
        elapsed_time = str(run.EndTime - run.StartTime).split('.')[0]
        embedded_data["Elapsed Time"] = elapsed_time

        for factor in run.Factors:
            value = factor.Value

            if isinstance(factor.Key, System.Double):
                value = round(float(value), 3)
            elif isinstance(factor.Key, System.Decimal):
                value = round(decimal.Decimal(value), 3)
            elif isinstance(factor.Key, int):
                value = int(value)

            if factor.Key not in embedded_data:
                embedded_data[factor.Key] = value

        for kpi in run.KPIs:
            kpi_value = round(kpi.Value, 3)

            if kpi.Key not in embedded_data:
                embedded_data[kpi.Key] = kpi_value

        embedded_data["Run State"] = run.State

        if run.IsSuccess:
            embedded_data["Engine Status"] = "Success"
        elif run.ErrorLog:
            embedded_data["Engine Status"] = "Fail"
            embedded_data["Error"] = str(run.ErroLog)
        else:
            embedded_data["Engine Status"] = '-'
        
        data[run.Index] = embedded_data

    df = pd.DataFrame.from_dict(data, orient='index')
    return df