#
# This is an auto-generated file.  DO NOT EDIT!
#
# pylint: disable=line-too-long

from ansys.fluent.core.services.datamodel_se import (
    PyMenu,
    PyParameter,
    PyTextual,
    PyNumerical,
    PyDictionary,
    PyNamedObjectContainer,
    PyCommand,
    PyQuery
)


class Root(PyMenu):
    """
    Singleton Root.
    """
    def __init__(self, service, rules, path):
        self.TaskObject = self.__class__.TaskObject(service, rules, path + [("TaskObject", "")])
        self.Workflow = self.__class__.Workflow(service, rules, path + [("Workflow", "")])
        self.CreateCompositeTask = self.__class__.CreateCompositeTask(service, rules, "CreateCompositeTask", path)
        self.CreateNewWorkflow = self.__class__.CreateNewWorkflow(service, rules, "CreateNewWorkflow", path)
        self.DeleteTasks = self.__class__.DeleteTasks(service, rules, "DeleteTasks", path)
        self.InitializeWorkflow = self.__class__.InitializeWorkflow(service, rules, "InitializeWorkflow", path)
        self.InsertNewTask = self.__class__.InsertNewTask(service, rules, "InsertNewTask", path)
        self.LoadState = self.__class__.LoadState(service, rules, "LoadState", path)
        self.LoadWorkflow = self.__class__.LoadWorkflow(service, rules, "LoadWorkflow", path)
        self.ResetWorkflow = self.__class__.ResetWorkflow(service, rules, "ResetWorkflow", path)
        self.SaveWorkflow = self.__class__.SaveWorkflow(service, rules, "SaveWorkflow", path)
        super().__init__(service, rules, path)

    class TaskObject(PyNamedObjectContainer):
        """
        .
        """
        class _TaskObject(PyMenu):
            """
            Singleton _TaskObject.
            """
            def __init__(self, service, rules, path):
                self.Arguments = self.__class__.Arguments(service, rules, path + [("Arguments", "")])
                self.CommandName = self.__class__.CommandName(service, rules, path + [("CommandName", "")])
                self.Errors = self.__class__.Errors(service, rules, path + [("Errors", "")])
                self.InactiveTaskList = self.__class__.InactiveTaskList(service, rules, path + [("InactiveTaskList", "")])
                self.ObjectPath = self.__class__.ObjectPath(service, rules, path + [("ObjectPath", "")])
                self.State = self.__class__.State(service, rules, path + [("State", "")])
                self.TaskList = self.__class__.TaskList(service, rules, path + [("TaskList", "")])
                self.TaskType = self.__class__.TaskType(service, rules, path + [("TaskType", "")])
                self.Warnings = self.__class__.Warnings(service, rules, path + [("Warnings", "")])
                self._name_ = self.__class__._name_(service, rules, path + [("_name_", "")])
                self.AddChildAndUpdate = self.__class__.AddChildAndUpdate(service, rules, "AddChildAndUpdate", path)
                self.AddChildToTask = self.__class__.AddChildToTask(service, rules, "AddChildToTask", path)
                self.Execute = self.__class__.Execute(service, rules, "Execute", path)
                self.ExecuteUpstreamNonExecutedAndThisTask = self.__class__.ExecuteUpstreamNonExecutedAndThisTask(service, rules, "ExecuteUpstreamNonExecutedAndThisTask", path)
                self.ForceUptoDate = self.__class__.ForceUptoDate(service, rules, "ForceUptoDate", path)
                self.GetNextPossibleTasks = self.__class__.GetNextPossibleTasks(service, rules, "GetNextPossibleTasks", path)
                self.InsertCompositeChildTask = self.__class__.InsertCompositeChildTask(service, rules, "InsertCompositeChildTask", path)
                self.InsertCompoundChildTask = self.__class__.InsertCompoundChildTask(service, rules, "InsertCompoundChildTask", path)
                self.InsertNextTask = self.__class__.InsertNextTask(service, rules, "InsertNextTask", path)
                self.Rename = self.__class__.Rename(service, rules, "Rename", path)
                self.Revert = self.__class__.Revert(service, rules, "Revert", path)
                self.SetAsCurrent = self.__class__.SetAsCurrent(service, rules, "SetAsCurrent", path)
                self.UpdateChildTasks = self.__class__.UpdateChildTasks(service, rules, "UpdateChildTasks", path)
                super().__init__(service, rules, path)

            class Arguments(PyDictionary):
                """
                Parameter Arguments of value type dict[str, Any].
                """
                pass

            class CommandName(PyTextual):
                """
                Parameter CommandName of value type str.
                """
                pass

            class Errors(PyTextual):
                """
                Parameter Errors of value type list[str].
                """
                pass

            class InactiveTaskList(PyTextual):
                """
                Parameter InactiveTaskList of value type list[str].
                """
                pass

            class ObjectPath(PyTextual):
                """
                Parameter ObjectPath of value type str.
                """
                pass

            class State(PyTextual):
                """
                Parameter State of value type str.
                """
                pass

            class TaskList(PyTextual):
                """
                Parameter TaskList of value type list[str].
                """
                pass

            class TaskType(PyTextual):
                """
                Parameter TaskType of value type str.
                """
                pass

            class Warnings(PyTextual):
                """
                Parameter Warnings of value type list[str].
                """
                pass

            class _name_(PyTextual):
                """
                Parameter _name_ of value type str.
                """
                pass

            class AddChildAndUpdate(PyCommand):
                """
                Command AddChildAndUpdate.


                Returns
                -------
                bool
                """
                pass

            class AddChildToTask(PyCommand):
                """
                Command AddChildToTask.


                Returns
                -------
                bool
                """
                pass

            class Execute(PyCommand):
                """
                Command Execute.

                Parameters
                ----------
                Force : bool

                Returns
                -------
                bool
                """
                pass

            class ExecuteUpstreamNonExecutedAndThisTask(PyCommand):
                """
                Command ExecuteUpstreamNonExecutedAndThisTask.


                Returns
                -------
                bool
                """
                pass

            class ForceUptoDate(PyCommand):
                """
                Command ForceUptoDate.


                Returns
                -------
                bool
                """
                pass

            class GetNextPossibleTasks(PyCommand):
                """
                Command GetNextPossibleTasks.


                Returns
                -------
                bool
                """
                pass

            class InsertCompositeChildTask(PyCommand):
                """
                Command InsertCompositeChildTask.

                Parameters
                ----------
                CommandName : str

                Returns
                -------
                bool
                """
                pass

            class InsertCompoundChildTask(PyCommand):
                """
                Command InsertCompoundChildTask.


                Returns
                -------
                bool
                """
                pass

            class InsertNextTask(PyCommand):
                """
                Command InsertNextTask.

                Parameters
                ----------
                CommandName : str
                Select : bool

                Returns
                -------
                bool
                """
                pass

            class Rename(PyCommand):
                """
                Command Rename.

                Parameters
                ----------
                NewName : str

                Returns
                -------
                bool
                """
                pass

            class Revert(PyCommand):
                """
                Command Revert.


                Returns
                -------
                bool
                """
                pass

            class SetAsCurrent(PyCommand):
                """
                Command SetAsCurrent.


                Returns
                -------
                bool
                """
                pass

            class UpdateChildTasks(PyCommand):
                """
                Command UpdateChildTasks.

                Parameters
                ----------
                SetupTypeChanged : bool

                Returns
                -------
                bool
                """
                pass

        def __getitem__(self, key: str) -> _TaskObject:
            return super().__getitem__(key)

    class Workflow(PyMenu):
        """
        Singleton Workflow.
        """
        def __init__(self, service, rules, path):
            self.CurrentTask = self.__class__.CurrentTask(service, rules, path + [("CurrentTask", "")])
            self.TaskList = self.__class__.TaskList(service, rules, path + [("TaskList", "")])
            super().__init__(service, rules, path)

        class CurrentTask(PyTextual):
            """
            Parameter CurrentTask of value type str.
            """
            pass

        class TaskList(PyTextual):
            """
            Parameter TaskList of value type list[str].
            """
            pass

    class CreateCompositeTask(PyCommand):
        """
        Command CreateCompositeTask.

        Parameters
        ----------
        ListOfTasks : list[str]

        Returns
        -------
        bool
        """
        pass

    class CreateNewWorkflow(PyCommand):
        """
        Command CreateNewWorkflow.


        Returns
        -------
        bool
        """
        pass

    class DeleteTasks(PyCommand):
        """
        Command DeleteTasks.

        Parameters
        ----------
        ListOfTasks : list[str]

        Returns
        -------
        bool
        """
        pass

    class InitializeWorkflow(PyCommand):
        """
        Command InitializeWorkflow.

        Parameters
        ----------
        WorkflowType : str

        Returns
        -------
        bool
        """
        pass

    class InsertNewTask(PyCommand):
        """
        Command InsertNewTask.

        Parameters
        ----------
        CommandName : str

        Returns
        -------
        bool
        """
        pass

    class LoadState(PyCommand):
        """
        Command LoadState.

        Parameters
        ----------
        ListOfRoots : list[str]

        Returns
        -------
        bool
        """
        pass

    class LoadWorkflow(PyCommand):
        """
        Command LoadWorkflow.

        Parameters
        ----------
        FilePath : str

        Returns
        -------
        bool
        """
        pass

    class ResetWorkflow(PyCommand):
        """
        Command ResetWorkflow.


        Returns
        -------
        bool
        """
        pass

    class SaveWorkflow(PyCommand):
        """
        Command SaveWorkflow.

        Parameters
        ----------
        FilePath : str

        Returns
        -------
        bool
        """
        pass

