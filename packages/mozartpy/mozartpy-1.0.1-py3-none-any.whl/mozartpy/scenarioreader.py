import os
import sys
import mozartpy.dataconverter as dc
import mozartpy.modelreader as mr

filedir = os.path.dirname(os.path.abspath(__file__))
dllFolder = os.path.join(filedir, r'netcore')

from clr_loader import get_coreclr
from pythonnet import set_runtime

rt = get_coreclr(runtime_config=os.path.join(dllFolder, "ProcessHost.runtimeconfig.json"))
set_runtime(rt)
sys.path.append(dllFolder)

import clr

clr.AddReference("Mozart.Task.Analyzer")

from Mozart.Task.Analyzer import ScenarioEngine


class Scenario:
    """
    Base class for mozart scenario object.

    properties
    name(string): File name of the vscenario file
    baseModel(Model): Mozart model object
    path(stringh): Full path for the sscenario file
    factors(list<string>): String list of the factor names
    kpis(list<string>): String list of the kpi names
    executions(list<string>): String list of the execution names
    """

    def __init__(self, scenario_path):
        self.__scenarioEngine = None
        self.__baseModel = None
        self.name = ''
        self.scenario_path = scenario_path
        self.factors = []
        self.kpis = []
        self.executions = []
        self.arg = {}
        self.__readScenario()

    def __readScenario(self):
        """ Initialize by reading the Scenario
        """
        self.__scenarioEngine = ScenarioEngine.Load(self.scenario_path)
        self.name = self.__scenarioEngine.Name
        self.__baseModel = mr.Model(self.__scenarioEngine.ModelPath)

        for factor in self.__scenarioEngine.Factors.Values:
            self.factors.append(factor.Name)

        for kpi in self.__scenarioEngine.KPIs.Values:
            self.kpis.append(kpi.Name)

        for exec_name in self.__scenarioEngine.Executions.Keys:
            self.executions.append(exec_name)

    def PrintExecutionArgs(self, exec_name='Execution 0'):
        args = self.__scenarioEngine.GetExecution(exec_name).Option
        print(args)

    def ExportExecutionArgs(self, file_path, exec_name='Execution 0'):
        drive, path = os.path.splitdrive(file_path)
        if drive == None:
            file_path = os.path.join(self.path, file_path)
        
        args = self.__scenarioEngine.GetExecution(exec_name).Option

        with open(file_path, "w") as file:
            file.write(str(args))

    def GetReport(self, exec_name='Execution 0'):
        df = None

        if exec_name == '':
            print('{0} is not found exec_name'.format(exec_name))
            pass

        if not self.executions.__contains__(exec_name):
            print('{0} is not found execution name'.format(exec_name))
            pass

        try:
            execution = self.__scenarioEngine.GetExecution(exec_name)
            df = dc.ExcRunToDataFrame(execution)
            return df

        except Exception as err:
            print(str(err))

    def GetExecutionModel(self, exec_name="Execution 0", run_name="Run 0"):
        execution = self.__scenarioEngine.GetExecution(exec_name)

        for run in execution.Runs:
            if run_name == run.Name:
                run_model_path = run.ModelPath
                run_model = mr.Model(run_model_path)
                return run_model
