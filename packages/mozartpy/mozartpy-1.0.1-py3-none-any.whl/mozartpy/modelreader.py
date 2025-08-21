import os
import sys
import collections
from datetime import datetime
import time

import pandas as pd
import pathlib

import clr

clr.AddReference('Mozart.Task.Model')
clr.AddReference('Mozart.DataActions')
clr.AddReference('System.Collections')

from Mozart.Task.Model import ModelEngine
from Mozart.DataActions import ILocalAccessor
import mozartpy.dataconverter as dc
from System.IO import StreamWriter


class Model:
    """
    Baseclass for mozart model object. Return the Input/Output DataItem with Pandas DataFrame object

    properties
    name(string) : File name of the vmodel file
    inputs(list<string>) : String list of the Input DataItem names(from input data schema)
    outputs(list<string>) : String list of the Output DataItem names(from output data schema)
    path(string) : Full path for the vmodel file
    experiments(list<string>) : String list of the output Experiment names
    results : Dictionary of output result for each experiment

    """

    def __init__(self, path, usecsv=True):
        self.__engine = None
        self.name = ''
        self.results = []
        self.inputs = []
        self.outputs = []
        self.path = path
        self.resultDic = collections.defaultdict(list)
        self.args = collections.defaultdict(list)
        self.argsByResult = {}
        self.usecsv = usecsv
        self.__readModel()

    def __readModel(self):
        """ Initialize by reading the model
        """
        self.__engine = ModelEngine.Load(self.path)
        self.name = self.__engine.Name

        for item in self.__engine.Inputs.ItemArray:
            self.inputs.append(item.Name)

        for experiment in self.__engine.Experiments:
            for result in experiment.ResultList:
                self.resultDic[experiment.Name].append(result.Key)

        for result in self.__engine.Experiments[0].ResultList:
            self.results.append(result.Key)

        for item in self.__engine.Outputs.ItemArray:
            self.outputs.append(item.Name)

        for experiment in self.__engine.Experiments:
            for args in experiment.Arguments:
                pyth_args = dc.DictToArg(args)
                self.args[experiment.Name].append(pyth_args)

        # if not self.usecsv:
        #     pass
        #
        # else:
        #     csvpath = os.path.join(self.__engine.ModelDirectory, 'csv')
        #     if not os.path.exists(csvpath):
        #         starttime = time.time()  # 함수 실행 시작 시간 기록
        #         self.__engine.ExportCsv(csvpath)
        #         endtime = time.time()  # 함수 실행 종료 시간 기록
        #         elapsed_time = endtime - starttime
        #         print(f"csv 파일 변환에 걸린 시간: {elapsed_time} 초")

    def __ParseParameters(self, desc):
        if desc == '':
            return

        self.argsByResult.clear()
        self.argsByResult = self.__GetParseParameters(desc)
        return self.argsByResult

    def __GetParseParameters(self, desc):
        if desc == '':
            return
        parameter = {}
        datetime_format_list = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]
        lst = desc.splitlines()

        for textline in lst[3:]:
            idx = textline.find(' = ')
            if idx < 0:
                continue
            # key = textline[:idx].replace('#','')
            key = textline[:idx]
            value = textline[idx + 3:]

            if key == 'start-time' or key == 'end-time':
                datetime_result = datetime.min
                for fmt in datetime_format_list:
                    try:
                        datetime_result = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue  # 실패하면 다음 형식으로 시도
                value = datetime_result

            parameter[key] = value
        return parameter

    def __GetResult(self, exp_name, key):
        for exp in self.__engine.Experiments:
            if exp.Name != exp_name:
                continue
            for result in exp.ResultList:
                self.__ParseParameters(result.Description)
                if result.Key == key:
                    return result
        # for result in self.__engine.Experiments[0].ResultList:
        #     if result.Key == key:
        #         return result

    def __getInputItemByModelItem(self, key):
        """
        Return the Input DataItem with Pandas DataFrame object

        :param key: Input DataItem name which is the same as vdat file name under Data folder
        :return: Converted Pandas DataFrame from Input DataItem whose table name is the parameter (key)
        """
        acc = ILocalAccessor(self.__engine.LocalAccessorFor(key))
        dt = acc.QueryTable('', -1, -1)
        df = dc.TableToDataFrame(dt)
        return df

    def __getInputItemByCsvfile(self, key, chunksize=None, usecols=None, dtype=None):
        acc = ILocalAccessor(self.__engine.LocalAccessorFor(key))

        csvdir = os.path.join(self.__engine.ModelDirectory, 'csv')
        if not os.path.exists(csvdir):
            os.mkdir(csvdir)

        csvpath = os.path.join(csvdir, f"{key}.csv")

        exportCsv = not os.path.exists(csvpath)
        if not exportCsv:
            datadir = acc.DataDirectory
            vdatpath = os.path.join(datadir, f"{key}.vdat")
            exportCsv = datetime.fromtimestamp(pathlib.Path(vdatpath).stat().st_mtime) > datetime.fromtimestamp(
                pathlib.Path(csvpath).stat().st_mtime)

        if exportCsv:
            stream = StreamWriter(csvpath)
            acc.ExportCsv(stream)

        item = self.__engine.Inputs.GetItem(key)
        schema = item.GetSchema()
        parse_dates = []
        columnTypesForDotNet = {}
        for col in schema.Columns:
            if col.DataType.Name == 'DateTime':
                if usecols == None:
                    parse_dates.append(col.ColumnName)
                elif col.ColumnName in usecols:
                    parse_dates.append(col.ColumnName)
            columnTypesForDotNet[col.ColumnName] = col.DataType.Name

        df = pd.read_csv(csvpath, parse_dates=parse_dates, low_memory=False, chunksize=chunksize, usecols=usecols,
                         dtype=dtype)
        df.attrs['columnTypesForDotNet'] = columnTypesForDotNet
        return df

    def __getOutputItemByModelItem(self, key, exp_name='Experiment 1', rst_name='Result 0'):
        """
        Return the Output DataItem with Pandas DataFrame object for a given table name (key) under Experiment (
        exp_name) and Result (rst_name)

        :param key: Output DataItem name(string) :param exp_name: Output Experiment name(string, defaultValue =
        'Experiment 1') :param rst_name: Output Result name(string, defaultvalue='Result 0') :return: Converted
        Pandas DataFrame from Output DataItem whose table name is the parameter (key) under Experiment (exp_name) and
        Result (rst_name)
        """

        if key == '':
            print('{0} is not found key'.format(key))
            pass

        if not self.outputs.__contains__(key):
            print('{0} is not found output item name'.format(key))
            pass

        result = self.__GetResult(exp_name, rst_name)
        if result is None:
            print('{0} is not found result'.format(rst_name))
            pass

        try:
            acc = ILocalAccessor(result.LocalAccessorFor(key))
            dt = acc.QueryTable('', -1, -1)
            df = dc.TableToDataFrame(dt)
            return df
        except Exception as err:
            print(str(err))

    def __getOutputItemByCsvfile(self, key, exp_name='Experiment 1', rst_name='Result 0', chunksize=None, usecols=None,
                                 dtype=None):
        result = self.__GetResult(exp_name, rst_name)
        acc = ILocalAccessor(result.LocalAccessorFor(key))

        nested_directories = ['csv', exp_name, rst_name]
        csvdir = os.path.join(self.__engine.ModelDirectory, *nested_directories)
        if not os.path.exists(csvdir):
            os.makedirs(csvdir)

        csvpath = os.path.join(csvdir, f"{key}.csv")

        exportCsv = not os.path.exists(csvpath)
        if not exportCsv:
            datadir = acc.DataDirectory
            vdatpath = os.path.join(datadir, f"{key}.vdat")
            exportCsv = datetime.fromtimestamp(pathlib.Path(vdatpath).stat().st_mtime) > datetime.fromtimestamp(
                pathlib.Path(csvpath).stat().st_mtime)

        if exportCsv:
            stream = StreamWriter(csvpath)
            acc.ExportCsv(stream)

        item = self.__engine.Outputs.GetItem(key)
        schema = item.GetSchema()
        parse_dates = []
        columnTypesForDotNet = {}
        for col in schema.Columns:
            if col.DataType.Name == 'DateTime':
                if usecols == None:
                    parse_dates.append(col.ColumnName)
                elif col.ColumnName in usecols:
                    parse_dates.append(col.ColumnName)
            columnTypesForDotNet[col.ColumnName] = col.DataType.Name

        df = pd.read_csv(csvpath, parse_dates=parse_dates, low_memory=False, chunksize=chunksize, usecols=usecols,
                         dtype=dtype)
        df.attrs['columnTypesForDotNet'] = columnTypesForDotNet
        return df

    def GetInputItem(self, key, chunksize=None, usecols=None, dtype=None):
        df = None
        if self.usecsv:
            df = self.__getInputItemByCsvfile(key, chunksize, usecols, dtype)
        else:
            df = self.__getInputItemByModelItem(key)
        return df

    def GetOutputItem(self, key, exp_name='Experiment 1', rst_name='Result 0', chunksize=None, usecols=None,
                      dtype=None):
        df = None
        if self.usecsv:
            df = self.__getOutputItemByCsvfile(key, exp_name, rst_name, chunksize, usecols, dtype)
        else:
            df = self.__getOutputItemByModelItem(key, exp_name, rst_name)
        return df

    def SetInputItem(self, key, df):
        acc = ILocalAccessor(self.__engine.LocalAccessorFor(key))
        dt = dc.DataFrameToTable(df, key)
        acc.Save(dt)

    def SetOutputItem(self, key, df, exp_name='Experiment 1', rst_name="Result 0"):
        result = self.__GetResult(exp_name, rst_name)
        acc = ILocalAccessor(result.LocalAccessorFor(key))
        dt = dc.DataFrameToTable(df, key)
        acc.Save(dt)

    def GetArgsByResult(self, exp_name='Experiment 1', rst_name="Result 0"):
        for exp in self.__engine.Experiments:
            if exp.Name != exp_name:
                continue
            for result in exp.ResultList:
                if result.Key != rst_name:
                    continue
                self.__ParseParameters(result.Description)
                return self.argsByResult

    def GetArgs(self):
        totalArgs = {}
        for exp in self.__engine.Experiments:
            totalArgs[exp.Name] = {}
            for result in exp.ResultList:
                totalArgs[exp.Name][result.Key] = self.__GetParseParameters(result.Description)
        return totalArgs

    def ExportArgs(self, file_path, exp_name='Experiment 1'):
        """"
        Saves model's exp_name arguments into a text file in a folder given as 'file_path'
        """

        drive, path = os.path.splitdrive(file_path)
        if drive == None:
            file_path = os.path.join(self.path, file_path)

        args = self.args[exp_name]

        with open(file_path, "w") as file:
            for argument in args:
                key, value = list(argument.items())[0]
                file.write(f"{key} = {value}\n")
