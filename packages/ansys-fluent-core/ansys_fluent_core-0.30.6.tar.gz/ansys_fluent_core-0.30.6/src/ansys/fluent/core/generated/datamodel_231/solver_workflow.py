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
        self.GlobalSettings = self.__class__.GlobalSettings(service, rules, path + [("GlobalSettings", "")])
        self.JournalCommand = self.__class__.JournalCommand(service, rules, "JournalCommand", path)
        self.TWF_AssociateMesh = self.__class__.TWF_AssociateMesh(service, rules, "TWF_AssociateMesh", path)
        self.TWF_BasicMachineDescription = self.__class__.TWF_BasicMachineDescription(service, rules, "TWF_BasicMachineDescription", path)
        self.TWF_BladeRowAnalysisScope = self.__class__.TWF_BladeRowAnalysisScope(service, rules, "TWF_BladeRowAnalysisScope", path)
        self.TWF_CompleteWorkflowSetup = self.__class__.TWF_CompleteWorkflowSetup(service, rules, "TWF_CompleteWorkflowSetup", path)
        self.TWF_CreateCFDModel = self.__class__.TWF_CreateCFDModel(service, rules, "TWF_CreateCFDModel", path)
        self.TWF_ImportMesh = self.__class__.TWF_ImportMesh(service, rules, "TWF_ImportMesh", path)
        self.TWF_MapRegionInfo = self.__class__.TWF_MapRegionInfo(service, rules, "TWF_MapRegionInfo", path)
        self.TWF_ReportDefMonitors = self.__class__.TWF_ReportDefMonitors(service, rules, "TWF_ReportDefMonitors", path)
        self.TWF_TurboPhysics = self.__class__.TWF_TurboPhysics(service, rules, "TWF_TurboPhysics", path)
        self.TWF_TurboRegionsZones = self.__class__.TWF_TurboRegionsZones(service, rules, "TWF_TurboRegionsZones", path)
        self.TWF_TurboSurfaces = self.__class__.TWF_TurboSurfaces(service, rules, "TWF_TurboSurfaces", path)
        self.TWF_TurboTopology = self.__class__.TWF_TurboTopology(service, rules, "TWF_TurboTopology", path)
        super().__init__(service, rules, path)

    class GlobalSettings(PyMenu):
        """
        Singleton GlobalSettings.
        """
        def __init__(self, service, rules, path):
            self.EnableTurboMeshing = self.__class__.EnableTurboMeshing(service, rules, path + [("EnableTurboMeshing", "")])
            super().__init__(service, rules, path)

        class EnableTurboMeshing(PyParameter):
            """
            Parameter EnableTurboMeshing of value type bool.
            """
            pass

    class JournalCommand(PyCommand):
        """
        Command JournalCommand.

        Parameters
        ----------
        JournalString : str

        Returns
        -------
        bool
        """
        pass

    class TWF_AssociateMesh(PyCommand):
        """
        Command TWF_AssociateMesh.

        Parameters
        ----------
        AMChildName : str
        AMSelectComponentScope : str
        UseWireframe : bool
        RenameCellZones : str
        DefaultAMRowNumList : list[str]
        DefaultAMCellZonesList : list[str]
        AMRowNumList : list[str]
        OldAMCellZonesList : list[str]
        NewAMCellZonesList : list[str]

        Returns
        -------
        bool
        """
        pass

    class TWF_BasicMachineDescription(PyCommand):
        """
        Command TWF_BasicMachineDescription.

        Parameters
        ----------
        ComponentType : str
        ComponentName : str
        NumRows : int
        RowNumList : list[str]
        OldRowNameList : list[str]
        NewRowNameList : list[str]
        OldRowTypeList : list[str]
        NewRowTypeList : list[str]
        OldNumOfBladesList : list[str]
        NewNumOfBladesList : list[str]
        OldEnableTipGapList : list[str]
        NewEnableTipGapList : list[str]
        CombustorType : str

        Returns
        -------
        bool
        """
        pass

    class TWF_BladeRowAnalysisScope(PyCommand):
        """
        Command TWF_BladeRowAnalysisScope.

        Parameters
        ----------
        ASChildName : str
        ASSelectComponent : str
        ASRowNumList : list[str]
        OldASIncludeRowList : list[str]
        NewASIncludeRowList : list[str]

        Returns
        -------
        bool
        """
        pass

    class TWF_CompleteWorkflowSetup(PyCommand):
        """
        Command TWF_CompleteWorkflowSetup.


        Returns
        -------
        bool
        """
        pass

    class TWF_CreateCFDModel(PyCommand):
        """
        Command TWF_CreateCFDModel.

        Parameters
        ----------
        CFDMChildName : str
        CFDMSelectMeshAssociation : str
        AxisOfRotation : str
        DelayCFDModelCreation : bool
        RestrictToFactors : bool
        EstimateNumBlades : bool
        CFDMRowNumList : list[str]
        OldCFDMNumOfBladesList : list[str]
        NewCFDMNumOfBladesList : list[str]
        OldCFDMModelBladesList : list[str]
        NewCFDMModelBladesList : list[str]
        OldCFDMAngleOffset : list[str]
        NewCFDMAngleOffset : list[str]
        OldCFDMBladesPerSectorList : list[str]
        NewCFDMBladesPerSectorList : list[str]

        Returns
        -------
        bool
        """
        pass

    class TWF_ImportMesh(PyCommand):
        """
        Command TWF_ImportMesh.

        Parameters
        ----------
        AddChild : str
        MeshFilePath : str
        MeshFilePath_old : str
        MeshName : str
        CellZoneNames : list[str]
        ListItemLevels : list[str]
        ListItemTitles : list[str]
        ListOfCellZones : str

        Returns
        -------
        bool
        """
        pass

    class TWF_MapRegionInfo(PyCommand):
        """
        Command TWF_MapRegionInfo.

        Parameters
        ----------
        MRChildName : str
        MRSelectCellZone : str
        UseWireframe : bool
        DefaultMRRegionNameList : list[str]
        DefaultMRFaceZoneList : list[str]
        MRRegionNameList : list[str]
        OldMRFaceZoneList : list[str]
        NewMRFaceZoneList : list[str]

        Returns
        -------
        bool
        """
        pass

    class TWF_ReportDefMonitors(PyCommand):
        """
        Command TWF_ReportDefMonitors.

        Parameters
        ----------
        RDIsoSurfaceNumList : list[str]
        OldCreateContourList : list[str]
        NewCreateContourList : list[str]
        TurboContoursList : list[str]

        Returns
        -------
        bool
        """
        pass

    class TWF_TurboPhysics(PyCommand):
        """
        Command TWF_TurboPhysics.

        Parameters
        ----------
        States : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class TWF_TurboRegionsZones(PyCommand):
        """
        Command TWF_TurboRegionsZones.

        Parameters
        ----------
        States : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class TWF_TurboSurfaces(PyCommand):
        """
        Command TWF_TurboSurfaces.

        Parameters
        ----------
        NumIsoSurfaces : int
        IsoSurfaceNumList : list[str]
        OldIsoSurfaceNameList : list[str]
        NewIsoSurfaceNameList : list[str]
        OldIsoSurfaceValueList : list[str]
        NewIsoSurfaceValueList : list[str]
        SurfacesList : list[str]

        Returns
        -------
        bool
        """
        pass

    class TWF_TurboTopology(PyCommand):
        """
        Command TWF_TurboTopology.

        Parameters
        ----------
        TopologyName : str
        UseWireframe : bool
        DefaultTopologyNameList : list[str]
        DefaultTopologyZoneList : list[str]
        TopologyNameList : list[str]
        OldTopologyZoneList : list[str]
        NewTopologyZoneList : list[str]

        Returns
        -------
        bool
        """
        pass

