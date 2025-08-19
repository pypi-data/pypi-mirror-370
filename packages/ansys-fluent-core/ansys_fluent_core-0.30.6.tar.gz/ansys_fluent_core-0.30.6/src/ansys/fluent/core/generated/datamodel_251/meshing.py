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
        self.Diagnostics = self.__class__.Diagnostics(service, rules, path + [("Diagnostics", "")])
        self.File = self.__class__.File(service, rules, path + [("File", "")])
        self.GlobalSettings = self.__class__.GlobalSettings(service, rules, path + [("GlobalSettings", "")])
        self.Graphics = self.__class__.Graphics(service, rules, path + [("Graphics", "")])
        self.Add2DBoundaryLayers = self.__class__.Add2DBoundaryLayers(service, rules, "Add2DBoundaryLayers", path)
        self.AddBoundaryLayers = self.__class__.AddBoundaryLayers(service, rules, "AddBoundaryLayers", path)
        self.AddBoundaryLayersForPartReplacement = self.__class__.AddBoundaryLayersForPartReplacement(service, rules, "AddBoundaryLayersForPartReplacement", path)
        self.AddBoundaryType = self.__class__.AddBoundaryType(service, rules, "AddBoundaryType", path)
        self.AddLocalSizingFTM = self.__class__.AddLocalSizingFTM(service, rules, "AddLocalSizingFTM", path)
        self.AddLocalSizingWTM = self.__class__.AddLocalSizingWTM(service, rules, "AddLocalSizingWTM", path)
        self.AddMultiZoneControls = self.__class__.AddMultiZoneControls(service, rules, "AddMultiZoneControls", path)
        self.AddShellBoundaryLayerControls = self.__class__.AddShellBoundaryLayerControls(service, rules, "AddShellBoundaryLayerControls", path)
        self.AddThickness = self.__class__.AddThickness(service, rules, "AddThickness", path)
        self.AddThinVolumeMeshControls = self.__class__.AddThinVolumeMeshControls(service, rules, "AddThinVolumeMeshControls", path)
        self.AddVirtualTopology = self.__class__.AddVirtualTopology(service, rules, "AddVirtualTopology", path)
        self.Capping = self.__class__.Capping(service, rules, "Capping", path)
        self.CheckMesh = self.__class__.CheckMesh(service, rules, "CheckMesh", path)
        self.CheckSurfaceQuality = self.__class__.CheckSurfaceQuality(service, rules, "CheckSurfaceQuality", path)
        self.CheckVolumeQuality = self.__class__.CheckVolumeQuality(service, rules, "CheckVolumeQuality", path)
        self.ChooseMeshControlOptions = self.__class__.ChooseMeshControlOptions(service, rules, "ChooseMeshControlOptions", path)
        self.ChoosePartReplacementOptions = self.__class__.ChoosePartReplacementOptions(service, rules, "ChoosePartReplacementOptions", path)
        self.CloseLeakage = self.__class__.CloseLeakage(service, rules, "CloseLeakage", path)
        self.ComplexMeshingRegions = self.__class__.ComplexMeshingRegions(service, rules, "ComplexMeshingRegions", path)
        self.ComputeSizeField = self.__class__.ComputeSizeField(service, rules, "ComputeSizeField", path)
        self.CreateBackgroundMesh = self.__class__.CreateBackgroundMesh(service, rules, "CreateBackgroundMesh", path)
        self.CreateCollarMesh = self.__class__.CreateCollarMesh(service, rules, "CreateCollarMesh", path)
        self.CreateComponentMesh = self.__class__.CreateComponentMesh(service, rules, "CreateComponentMesh", path)
        self.CreateContactPatch = self.__class__.CreateContactPatch(service, rules, "CreateContactPatch", path)
        self.CreateExternalFlowBoundaries = self.__class__.CreateExternalFlowBoundaries(service, rules, "CreateExternalFlowBoundaries", path)
        self.CreateGapCover = self.__class__.CreateGapCover(service, rules, "CreateGapCover", path)
        self.CreateLocalRefinementRegions = self.__class__.CreateLocalRefinementRegions(service, rules, "CreateLocalRefinementRegions", path)
        self.CreateMeshObjects = self.__class__.CreateMeshObjects(service, rules, "CreateMeshObjects", path)
        self.CreateOversetInterfaces = self.__class__.CreateOversetInterfaces(service, rules, "CreateOversetInterfaces", path)
        self.CreatePorousRegions = self.__class__.CreatePorousRegions(service, rules, "CreatePorousRegions", path)
        self.CreateRegions = self.__class__.CreateRegions(service, rules, "CreateRegions", path)
        self.DefineGlobalSizing = self.__class__.DefineGlobalSizing(service, rules, "DefineGlobalSizing", path)
        self.DefineLeakageThreshold = self.__class__.DefineLeakageThreshold(service, rules, "DefineLeakageThreshold", path)
        self.DescribeGeometryAndFlow = self.__class__.DescribeGeometryAndFlow(service, rules, "DescribeGeometryAndFlow", path)
        self.DescribeOversetFeatures = self.__class__.DescribeOversetFeatures(service, rules, "DescribeOversetFeatures", path)
        self.ExtractEdges = self.__class__.ExtractEdges(service, rules, "ExtractEdges", path)
        self.ExtrudeVolumeMesh = self.__class__.ExtrudeVolumeMesh(service, rules, "ExtrudeVolumeMesh", path)
        self.GenerateInitialSurfaceMesh = self.__class__.GenerateInitialSurfaceMesh(service, rules, "GenerateInitialSurfaceMesh", path)
        self.GenerateMapMesh = self.__class__.GenerateMapMesh(service, rules, "GenerateMapMesh", path)
        self.GeneratePrisms = self.__class__.GeneratePrisms(service, rules, "GeneratePrisms", path)
        self.GenerateShellBoundaryLayerMesh = self.__class__.GenerateShellBoundaryLayerMesh(service, rules, "GenerateShellBoundaryLayerMesh", path)
        self.GenerateTheMultiZoneMesh = self.__class__.GenerateTheMultiZoneMesh(service, rules, "GenerateTheMultiZoneMesh", path)
        self.GenerateTheSurfaceMeshFTM = self.__class__.GenerateTheSurfaceMeshFTM(service, rules, "GenerateTheSurfaceMeshFTM", path)
        self.GenerateTheSurfaceMeshWTM = self.__class__.GenerateTheSurfaceMeshWTM(service, rules, "GenerateTheSurfaceMeshWTM", path)
        self.GenerateTheVolumeMeshFTM = self.__class__.GenerateTheVolumeMeshFTM(service, rules, "GenerateTheVolumeMeshFTM", path)
        self.GenerateTheVolumeMeshWTM = self.__class__.GenerateTheVolumeMeshWTM(service, rules, "GenerateTheVolumeMeshWTM", path)
        self.GeometrySetup = self.__class__.GeometrySetup(service, rules, "GeometrySetup", path)
        self.IdentifyConstructionSurfaces = self.__class__.IdentifyConstructionSurfaces(service, rules, "IdentifyConstructionSurfaces", path)
        self.IdentifyDeviatedFaces = self.__class__.IdentifyDeviatedFaces(service, rules, "IdentifyDeviatedFaces", path)
        self.IdentifyOrphans = self.__class__.IdentifyOrphans(service, rules, "IdentifyOrphans", path)
        self.IdentifyRegions = self.__class__.IdentifyRegions(service, rules, "IdentifyRegions", path)
        self.ImportBodyOfInfluenceGeometry = self.__class__.ImportBodyOfInfluenceGeometry(service, rules, "ImportBodyOfInfluenceGeometry", path)
        self.ImportGeometry = self.__class__.ImportGeometry(service, rules, "ImportGeometry", path)
        self.ImproveSurfaceMesh = self.__class__.ImproveSurfaceMesh(service, rules, "ImproveSurfaceMesh", path)
        self.ImproveVolumeMesh = self.__class__.ImproveVolumeMesh(service, rules, "ImproveVolumeMesh", path)
        self.LinearMeshPattern = self.__class__.LinearMeshPattern(service, rules, "LinearMeshPattern", path)
        self.LoadCADGeometry = self.__class__.LoadCADGeometry(service, rules, "LoadCADGeometry", path)
        self.LocalScopedSizingForPartReplacement = self.__class__.LocalScopedSizingForPartReplacement(service, rules, "LocalScopedSizingForPartReplacement", path)
        self.ManageZones = self.__class__.ManageZones(service, rules, "ManageZones", path)
        self.MeshFluidDomain = self.__class__.MeshFluidDomain(service, rules, "MeshFluidDomain", path)
        self.ModifyMeshRefinement = self.__class__.ModifyMeshRefinement(service, rules, "ModifyMeshRefinement", path)
        self.PartManagement = self.__class__.PartManagement(service, rules, "PartManagement", path)
        self.PartReplacementSettings = self.__class__.PartReplacementSettings(service, rules, "PartReplacementSettings", path)
        self.RemeshSurface = self.__class__.RemeshSurface(service, rules, "RemeshSurface", path)
        self.RunCustomJournal = self.__class__.RunCustomJournal(service, rules, "RunCustomJournal", path)
        self.SeparateContacts = self.__class__.SeparateContacts(service, rules, "SeparateContacts", path)
        self.SetUpPeriodicBoundaries = self.__class__.SetUpPeriodicBoundaries(service, rules, "SetUpPeriodicBoundaries", path)
        self.SetupBoundaryLayers = self.__class__.SetupBoundaryLayers(service, rules, "SetupBoundaryLayers", path)
        self.ShareTopology = self.__class__.ShareTopology(service, rules, "ShareTopology", path)
        self.SizeControlsTable = self.__class__.SizeControlsTable(service, rules, "SizeControlsTable", path)
        self.SwitchToSolution = self.__class__.SwitchToSolution(service, rules, "SwitchToSolution", path)
        self.TransformVolumeMesh = self.__class__.TransformVolumeMesh(service, rules, "TransformVolumeMesh", path)
        self.UpdateBoundaries = self.__class__.UpdateBoundaries(service, rules, "UpdateBoundaries", path)
        self.UpdateRegionSettings = self.__class__.UpdateRegionSettings(service, rules, "UpdateRegionSettings", path)
        self.UpdateRegions = self.__class__.UpdateRegions(service, rules, "UpdateRegions", path)
        self.UpdateTheVolumeMesh = self.__class__.UpdateTheVolumeMesh(service, rules, "UpdateTheVolumeMesh", path)
        self.WrapMain = self.__class__.WrapMain(service, rules, "WrapMain", path)
        self.Write2dMesh = self.__class__.Write2dMesh(service, rules, "Write2dMesh", path)
        self.WriteSkinMesh = self.__class__.WriteSkinMesh(service, rules, "WriteSkinMesh", path)
        super().__init__(service, rules, path)

    class Diagnostics(PyMenu):
        """
        Singleton Diagnostics.
        """
        def __init__(self, service, rules, path):
            self.Close = self.__class__.Close(service, rules, "Close", path)
            self.Compute = self.__class__.Compute(service, rules, "Compute", path)
            self.DiagOptions = self.__class__.DiagOptions(service, rules, "DiagOptions", path)
            self.Draw = self.__class__.Draw(service, rules, "Draw", path)
            self.First = self.__class__.First(service, rules, "First", path)
            self.Histogram = self.__class__.Histogram(service, rules, "Histogram", path)
            self.Ignore = self.__class__.Ignore(service, rules, "Ignore", path)
            self.List = self.__class__.List(service, rules, "List", path)
            self.Mark = self.__class__.Mark(service, rules, "Mark", path)
            self.Next = self.__class__.Next(service, rules, "Next", path)
            self.Previous = self.__class__.Previous(service, rules, "Previous", path)
            self.Restore = self.__class__.Restore(service, rules, "Restore", path)
            self.Summary = self.__class__.Summary(service, rules, "Summary", path)
            self.Update = self.__class__.Update(service, rules, "Update", path)
            super().__init__(service, rules, path)

        class Close(PyCommand):
            """
            Command Close.


            Returns
            -------
            None
            """
            pass

        class Compute(PyCommand):
            """
            Command Compute.


            Returns
            -------
            None
            """
            pass

        class DiagOptions(PyCommand):
            """
            Command DiagOptions.

            Parameters
            ----------
            Option : str
            Measure : str
            Average : float
            Minimum : float
            Maximum : float
            MarkRangeType : str
            MarkMin : float
            MarkMax : float
            Selected : str
            MarkedCount : int
            CurrentCount : int
            ExtentsUpdateBounds : bool
            ExtentsXMin : float
            ExtentsYMin : float
            ExtentsZMin : float
            ExtentsXMax : float
            ExtentsYMax : float
            ExtentsZMax : float

            Returns
            -------
            None
            """
            pass

        class Draw(PyCommand):
            """
            Command Draw.


            Returns
            -------
            None
            """
            pass

        class First(PyCommand):
            """
            Command First.


            Returns
            -------
            None
            """
            pass

        class Histogram(PyCommand):
            """
            Command Histogram.


            Returns
            -------
            None
            """
            pass

        class Ignore(PyCommand):
            """
            Command Ignore.


            Returns
            -------
            None
            """
            pass

        class List(PyCommand):
            """
            Command List.


            Returns
            -------
            None
            """
            pass

        class Mark(PyCommand):
            """
            Command Mark.


            Returns
            -------
            None
            """
            pass

        class Next(PyCommand):
            """
            Command Next.


            Returns
            -------
            None
            """
            pass

        class Previous(PyCommand):
            """
            Command Previous.


            Returns
            -------
            None
            """
            pass

        class Restore(PyCommand):
            """
            Command Restore.


            Returns
            -------
            None
            """
            pass

        class Summary(PyCommand):
            """
            Command Summary.


            Returns
            -------
            None
            """
            pass

        class Update(PyCommand):
            """
            Command Update.


            Returns
            -------
            None
            """
            pass

    class File(PyMenu):
        """
        Singleton File.
        """
        def __init__(self, service, rules, path):
            self.ReadCase = self.__class__.ReadCase(service, rules, "ReadCase", path)
            self.ReadJournal = self.__class__.ReadJournal(service, rules, "ReadJournal", path)
            self.ReadMesh = self.__class__.ReadMesh(service, rules, "ReadMesh", path)
            self.StartJournal = self.__class__.StartJournal(service, rules, "StartJournal", path)
            self.StopJournal = self.__class__.StopJournal(service, rules, "StopJournal", path)
            self.WriteCase = self.__class__.WriteCase(service, rules, "WriteCase", path)
            self.WriteMesh = self.__class__.WriteMesh(service, rules, "WriteMesh", path)
            super().__init__(service, rules, path)

        class ReadCase(PyCommand):
            """
            Command ReadCase.

            Parameters
            ----------
            FileName : str

            Returns
            -------
            None
            """
            pass

        class ReadJournal(PyCommand):
            """
            Command ReadJournal.

            Parameters
            ----------
            FileName : list[str]
            ChangeDirectory : bool

            Returns
            -------
            None
            """
            pass

        class ReadMesh(PyCommand):
            """
            Command ReadMesh.

            Parameters
            ----------
            FileName : str

            Returns
            -------
            None
            """
            pass

        class StartJournal(PyCommand):
            """
            Command StartJournal.

            Parameters
            ----------
            FileName : str

            Returns
            -------
            None
            """
            pass

        class StopJournal(PyCommand):
            """
            Command StopJournal.


            Returns
            -------
            None
            """
            pass

        class WriteCase(PyCommand):
            """
            Command WriteCase.

            Parameters
            ----------
            FileName : str

            Returns
            -------
            None
            """
            pass

        class WriteMesh(PyCommand):
            """
            Command WriteMesh.

            Parameters
            ----------
            FileName : str

            Returns
            -------
            None
            """
            pass

    class GlobalSettings(PyMenu):
        """
        Singleton GlobalSettings.
        """
        def __init__(self, service, rules, path):
            self.FTMRegionData = self.__class__.FTMRegionData(service, rules, path + [("FTMRegionData", "")])
            self.AreaUnit = self.__class__.AreaUnit(service, rules, path + [("AreaUnit", "")])
            self.EnableCleanCAD = self.__class__.EnableCleanCAD(service, rules, path + [("EnableCleanCAD", "")])
            self.EnableComplexMeshing = self.__class__.EnableComplexMeshing(service, rules, path + [("EnableComplexMeshing", "")])
            self.EnableOversetMeshing = self.__class__.EnableOversetMeshing(service, rules, path + [("EnableOversetMeshing", "")])
            self.EnablePrime2dMeshing = self.__class__.EnablePrime2dMeshing(service, rules, path + [("EnablePrime2dMeshing", "")])
            self.EnablePrimeMeshing = self.__class__.EnablePrimeMeshing(service, rules, path + [("EnablePrimeMeshing", "")])
            self.InitialVersion = self.__class__.InitialVersion(service, rules, path + [("InitialVersion", "")])
            self.LengthUnit = self.__class__.LengthUnit(service, rules, path + [("LengthUnit", "")])
            self.NormalMode = self.__class__.NormalMode(service, rules, path + [("NormalMode", "")])
            self.UseAllowedValues = self.__class__.UseAllowedValues(service, rules, path + [("UseAllowedValues", "")])
            self.VolumeUnit = self.__class__.VolumeUnit(service, rules, path + [("VolumeUnit", "")])
            super().__init__(service, rules, path)

        class FTMRegionData(PyMenu):
            """
            Singleton FTMRegionData.
            """
            def __init__(self, service, rules, path):
                self.AllOversetNameList = self.__class__.AllOversetNameList(service, rules, path + [("AllOversetNameList", "")])
                self.AllOversetSizeList = self.__class__.AllOversetSizeList(service, rules, path + [("AllOversetSizeList", "")])
                self.AllOversetTypeList = self.__class__.AllOversetTypeList(service, rules, path + [("AllOversetTypeList", "")])
                self.AllOversetVolumeFillList = self.__class__.AllOversetVolumeFillList(service, rules, path + [("AllOversetVolumeFillList", "")])
                self.AllRegionFilterCategories = self.__class__.AllRegionFilterCategories(service, rules, path + [("AllRegionFilterCategories", "")])
                self.AllRegionLeakageSizeList = self.__class__.AllRegionLeakageSizeList(service, rules, path + [("AllRegionLeakageSizeList", "")])
                self.AllRegionLinkedConstructionSurfaceList = self.__class__.AllRegionLinkedConstructionSurfaceList(service, rules, path + [("AllRegionLinkedConstructionSurfaceList", "")])
                self.AllRegionMeshMethodList = self.__class__.AllRegionMeshMethodList(service, rules, path + [("AllRegionMeshMethodList", "")])
                self.AllRegionNameList = self.__class__.AllRegionNameList(service, rules, path + [("AllRegionNameList", "")])
                self.AllRegionOversetComponenList = self.__class__.AllRegionOversetComponenList(service, rules, path + [("AllRegionOversetComponenList", "")])
                self.AllRegionSizeList = self.__class__.AllRegionSizeList(service, rules, path + [("AllRegionSizeList", "")])
                self.AllRegionSourceList = self.__class__.AllRegionSourceList(service, rules, path + [("AllRegionSourceList", "")])
                self.AllRegionTypeList = self.__class__.AllRegionTypeList(service, rules, path + [("AllRegionTypeList", "")])
                self.AllRegionVolumeFillList = self.__class__.AllRegionVolumeFillList(service, rules, path + [("AllRegionVolumeFillList", "")])
                super().__init__(service, rules, path)

            class AllOversetNameList(PyTextual):
                """
                Parameter AllOversetNameList of value type list[str].
                """
                pass

            class AllOversetSizeList(PyTextual):
                """
                Parameter AllOversetSizeList of value type list[str].
                """
                pass

            class AllOversetTypeList(PyTextual):
                """
                Parameter AllOversetTypeList of value type list[str].
                """
                pass

            class AllOversetVolumeFillList(PyTextual):
                """
                Parameter AllOversetVolumeFillList of value type list[str].
                """
                pass

            class AllRegionFilterCategories(PyTextual):
                """
                Parameter AllRegionFilterCategories of value type list[str].
                """
                pass

            class AllRegionLeakageSizeList(PyTextual):
                """
                Parameter AllRegionLeakageSizeList of value type list[str].
                """
                pass

            class AllRegionLinkedConstructionSurfaceList(PyTextual):
                """
                Parameter AllRegionLinkedConstructionSurfaceList of value type list[str].
                """
                pass

            class AllRegionMeshMethodList(PyTextual):
                """
                Parameter AllRegionMeshMethodList of value type list[str].
                """
                pass

            class AllRegionNameList(PyTextual):
                """
                Parameter AllRegionNameList of value type list[str].
                """
                pass

            class AllRegionOversetComponenList(PyTextual):
                """
                Parameter AllRegionOversetComponenList of value type list[str].
                """
                pass

            class AllRegionSizeList(PyTextual):
                """
                Parameter AllRegionSizeList of value type list[str].
                """
                pass

            class AllRegionSourceList(PyTextual):
                """
                Parameter AllRegionSourceList of value type list[str].
                """
                pass

            class AllRegionTypeList(PyTextual):
                """
                Parameter AllRegionTypeList of value type list[str].
                """
                pass

            class AllRegionVolumeFillList(PyTextual):
                """
                Parameter AllRegionVolumeFillList of value type list[str].
                """
                pass

        class AreaUnit(PyTextual):
            """
            Parameter AreaUnit of value type str.
            """
            pass

        class EnableCleanCAD(PyParameter):
            """
            Parameter EnableCleanCAD of value type bool.
            """
            pass

        class EnableComplexMeshing(PyParameter):
            """
            Parameter EnableComplexMeshing of value type bool.
            """
            pass

        class EnableOversetMeshing(PyParameter):
            """
            Parameter EnableOversetMeshing of value type bool.
            """
            pass

        class EnablePrime2dMeshing(PyParameter):
            """
            Parameter EnablePrime2dMeshing of value type bool.
            """
            pass

        class EnablePrimeMeshing(PyParameter):
            """
            Parameter EnablePrimeMeshing of value type bool.
            """
            pass

        class InitialVersion(PyTextual):
            """
            Parameter InitialVersion of value type str.
            """
            pass

        class LengthUnit(PyTextual):
            """
            Parameter LengthUnit of value type str.
            """
            pass

        class NormalMode(PyParameter):
            """
            Parameter NormalMode of value type bool.
            """
            pass

        class UseAllowedValues(PyParameter):
            """
            Parameter UseAllowedValues of value type bool.
            """
            pass

        class VolumeUnit(PyTextual):
            """
            Parameter VolumeUnit of value type str.
            """
            pass

    class Graphics(PyMenu):
        """
        Singleton Graphics.
        """
        def __init__(self, service, rules, path):
            self.Bounds = self.__class__.Bounds(service, rules, path + [("Bounds", "")])
            self.ClippingPlane = self.__class__.ClippingPlane(service, rules, "ClippingPlane", path)
            self.GetClippingZoneIDs = self.__class__.GetClippingZoneIDs(service, rules, "GetClippingZoneIDs", path)
            self.GetVisibleDomainBounds = self.__class__.GetVisibleDomainBounds(service, rules, "GetVisibleDomainBounds", path)
            super().__init__(service, rules, path)

        class Bounds(PyMenu):
            """
            Singleton Bounds.
            """
            def __init__(self, service, rules, path):
                self.BoundX = self.__class__.BoundX(service, rules, path + [("BoundX", "")])
                self.BoundY = self.__class__.BoundY(service, rules, path + [("BoundY", "")])
                self.BoundZ = self.__class__.BoundZ(service, rules, path + [("BoundZ", "")])
                self.Delta3D = self.__class__.Delta3D(service, rules, path + [("Delta3D", "")])
                self.Selection = self.__class__.Selection(service, rules, path + [("Selection", "")])
                self.ResetBounds = self.__class__.ResetBounds(service, rules, "ResetBounds", path)
                self.SetBounds = self.__class__.SetBounds(service, rules, "SetBounds", path)
                super().__init__(service, rules, path)

            class BoundX(PyParameter):
                """
                Parameter BoundX of value type bool.
                """
                pass

            class BoundY(PyParameter):
                """
                Parameter BoundY of value type bool.
                """
                pass

            class BoundZ(PyParameter):
                """
                Parameter BoundZ of value type bool.
                """
                pass

            class Delta3D(PyNumerical):
                """
                Parameter Delta3D of value type float.
                """
                pass

            class Selection(PyTextual):
                """
                Parameter Selection of value type str.
                """
                pass

            class ResetBounds(PyCommand):
                """
                Command ResetBounds.


                Returns
                -------
                None
                """
                pass

            class SetBounds(PyCommand):
                """
                Command SetBounds.


                Returns
                -------
                None
                """
                pass

        class ClippingPlane(PyCommand):
            """
            Command ClippingPlane.

            Parameters
            ----------
            InsertClippingPlane : bool
            DrawCellLayer : bool
            FreezeCellLayer : bool
            FlipClippingPlane : bool
            PointCoordinates : list[float]
            PlaneNormal : list[float]
            SliderPosition : int
            CutDirection : str

            Returns
            -------
            None
            """
            pass

        class GetClippingZoneIDs(PyCommand):
            """
            Command GetClippingZoneIDs.


            Returns
            -------
            None
            """
            pass

        class GetVisibleDomainBounds(PyCommand):
            """
            Command GetVisibleDomainBounds.


            Returns
            -------
            None
            """
            pass

    class Add2DBoundaryLayers(PyCommand):
        """
        Command Add2DBoundaryLayers.

        Parameters
        ----------
        AddChild : str
        BLControlName : str
        OffsetMethodType : str
        NumberOfLayers : int
        FirstAspectRatio : float
        TransitionRatio : float
        LastAspectRatio : float
        Rate : float
        FirstLayerHeight : float
        MaxLayerHeight : float
        Addin : str
        FaceLabelList : list[str]
        GrowOn : str
        EdgeLabelList : list[str]
        EdgeZoneList : list[str]
        ShellBLAdvancedOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class AddBoundaryLayers(PyCommand):
        """
        Command AddBoundaryLayers.

        Parameters
        ----------
        AddChild : str
        ReadPrismControlFile : str
        BLControlName : str
        OffsetMethodType : str
        NumberOfLayers : int
        FirstAspectRatio : float
        TransitionRatio : float
        Rate : float
        FirstHeight : float
        MaxLayerHeight : float
        FaceScope : dict[str, Any]
        RegionScope : list[str]
        BlLabelList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LocalPrismPreferences : dict[str, Any]
        BLZoneList : list[str]
        BLRegionList : list[str]
        InvalidAdded : str
        CompleteRegionScope : list[str]
        CompleteBlLabelList : list[str]
        CompleteBLZoneList : list[str]
        CompleteBLRegionList : list[str]
        CompleteZoneSelectionList : list[str]
        CompleteLabelSelectionList : list[str]

        Returns
        -------
        bool
        """
        pass

    class AddBoundaryLayersForPartReplacement(PyCommand):
        """
        Command AddBoundaryLayersForPartReplacement.

        Parameters
        ----------
        AddChild : str
        ReadPrismControlFile : str
        BLControlName : str
        OffsetMethodType : str
        NumberOfLayers : int
        FirstAspectRatio : float
        TransitionRatio : float
        Rate : float
        FirstHeight : float
        MaxLayerHeight : float
        FaceScope : dict[str, Any]
        RegionScope : list[str]
        BlLabelList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LocalPrismPreferences : dict[str, Any]
        BLZoneList : list[str]
        BLRegionList : list[str]
        CompleteRegionScope : list[str]
        CompleteBlLabelList : list[str]
        CompleteBLZoneList : list[str]
        CompleteBLRegionList : list[str]
        CompleteZoneSelectionList : list[str]
        CompleteLabelSelectionList : list[str]

        Returns
        -------
        bool
        """
        pass

    class AddBoundaryType(PyCommand):
        """
        Command AddBoundaryType.

        Parameters
        ----------
        MeshObject : str
        NewBoundaryLabelName : str
        NewBoundaryType : str
        SelectionType : str
        BoundaryFaceZoneList : list[str]
        TopologyList : list[str]
        Merge : str
        ZoneLocation : list[str]

        Returns
        -------
        bool
        """
        pass

    class AddLocalSizingFTM(PyCommand):
        """
        Command AddLocalSizingFTM.

        Parameters
        ----------
        LocalSettingsName : str
        SelectionType : str
        ObjectSelectionList : list[str]
        LabelSelectionList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        EdgeSelectionList : list[str]
        LocalSizeControlParameters : dict[str, Any]
        ValueChanged : str
        CompleteZoneSelectionList : list[str]
        CompleteLabelSelectionList : list[str]
        CompleteObjectSelectionList : list[str]
        CompleteEdgeSelectionList : list[str]

        Returns
        -------
        bool
        """
        pass

    class AddLocalSizingWTM(PyCommand):
        """
        Command AddLocalSizingWTM.

        Parameters
        ----------
        AddChild : str
        BOIControlName : str
        BOIGrowthRate : float
        BOIExecution : str
        AssignSizeUsing : str
        BOISize : float
        NumberofLayers : int
        SmallestHeight : float
        GrowthPattern : str
        GrowthMethod : str
        BiasFactor : float
        BOIMinSize : float
        BOIMaxSize : float
        BOICurvatureNormalAngle : float
        BOICellsPerGap : float
        BOIScopeTo : str
        IgnoreOrientation : str
        BOIZoneorLabel : str
        BOIFaceLabelList : list[str]
        BOIFaceZoneList : list[str]
        EdgeLabelList : list[str]
        EdgeZoneList : list[str]
        TopologyList : list[str]
        ReverseEdgeZoneOrientation : bool
        ReverseEdgeZoneList : list[str]
        BOIPatchingtoggle : bool
        DrawSizeControl : bool
        ZoneLocation : list[str]
        CompleteFaceZoneList : list[str]
        CompleteFaceLabelList : list[str]
        CompleteEdgeLabelList : list[str]
        CompleteTopologyList : list[str]
        PrimeSizeControlId : int

        Returns
        -------
        bool
        """
        pass

    class AddMultiZoneControls(PyCommand):
        """
        Command AddMultiZoneControls.

        Parameters
        ----------
        ControlType : str
        MultiZName : str
        MeshMethod : str
        FillWith : str
        UseSweepSize : str
        MaxSweepSize : float
        RegionScope : list[str]
        TopologyList : list[str]
        SourceMethod : str
        ParallelSelection : bool
        ShowEdgeBiasing : str
        LabelSourceList : list[str]
        ZoneSourceList : list[str]
        ZoneLocation : list[str]
        AssignSizeUsing : str
        Intervals : int
        Size : float
        SmallestHeight : float
        BiasMethod : str
        GrowthMethod : str
        GrowthRate : float
        BiasFactor : float
        EdgeLabelSelection : list[str]
        EdgeLabelList : list[str]
        CFDSurfaceMeshControls : dict[str, Any]
        CompleteRegionScope : list[str]
        CompleteEdgeScope : list[str]

        Returns
        -------
        bool
        """
        pass

    class AddShellBoundaryLayerControls(PyCommand):
        """
        Command AddShellBoundaryLayerControls.

        Parameters
        ----------
        AddChild : str
        BLControlName : str
        OffsetMethodType : str
        NumberOfLayers : int
        FirstAspectRatio : float
        LastAspectRatio : float
        Rate : float
        FirstLayerHeight : float
        MaxLayerHeight : float
        GrowOn : str
        FaceLabelList : list[str]
        FaceZoneList : list[str]
        EdgeSelectionType : str
        EdgeLabelList : list[str]
        EdgeZoneList : list[str]
        ShellBLAdvancedOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class AddThickness(PyCommand):
        """
        Command AddThickness.

        Parameters
        ----------
        ZeroThicknessName : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        ObjectSelectionList : list[str]
        LabelSelectionList : list[str]
        Distance : float

        Returns
        -------
        bool
        """
        pass

    class AddThinVolumeMeshControls(PyCommand):
        """
        Command AddThinVolumeMeshControls.

        Parameters
        ----------
        ThinMeshingName : str
        AssignSizeUsing : str
        Intervals : int
        Size : float
        GrowthRate : float
        RemeshOverlapping : bool
        DoubleBiasing : bool
        SideImprints : bool
        StackedPlates : bool
        AutoControlCreation : bool
        RegionScope : list[str]
        SelectSourceBy : str
        ParallelSource : bool
        LabelSourceList : list[str]
        ZoneSourceList : list[str]
        SelectTargetBy : str
        ParallelTarget : bool
        LabelTargetList : list[str]
        ZoneTargetList : list[str]
        ThinVolRegs : list[str]
        CompleteRegionScope : list[str]
        CompleteLabelSourceList : list[str]
        CompleteZoneSourceList : list[str]
        CompleteLabelTargetList : list[str]
        CompleteZoneTargetList : list[str]
        ThinVolumePreferences : dict[str, Any]
        ZoneLocation : list[str]
        ZoneLocation2 : list[str]

        Returns
        -------
        bool
        """
        pass

    class AddVirtualTopology(PyCommand):
        """
        Command AddVirtualTopology.

        Parameters
        ----------
        AddChild : str
        ControlName : str
        SelectionType : str
        FaceLabelList : list[str]
        FaceZoneList : list[str]
        NewFaces : list[int]

        Returns
        -------
        bool
        """
        pass

    class Capping(PyCommand):
        """
        Command Capping.

        Parameters
        ----------
        PatchName : str
        ZoneType : str
        PatchType : str
        SelectionType : str
        LabelSelectionList : list[str]
        ZoneSelectionList : list[str]
        TopologyList : list[str]
        CreatePatchPreferences : dict[str, Any]
        ObjectAssociation : str
        NewObjectName : str
        PatchObjectName : str
        CapLabels : list[str]
        ZoneLocation : list[str]
        CompleteZoneSelectionList : list[str]
        CompleteLabelSelectionList : list[str]
        CompleteTopologyList : list[str]

        Returns
        -------
        bool
        """
        pass

    class CheckMesh(PyCommand):
        """
        Command CheckMesh.


        Returns
        -------
        None
        """
        pass

    class CheckSurfaceQuality(PyCommand):
        """
        Command CheckSurfaceQuality.


        Returns
        -------
        None
        """
        pass

    class CheckVolumeQuality(PyCommand):
        """
        Command CheckVolumeQuality.


        Returns
        -------
        None
        """
        pass

    class ChooseMeshControlOptions(PyCommand):
        """
        Command ChooseMeshControlOptions.

        Parameters
        ----------
        ReadOrCreate : str
        SizeControlFileName : str
        WrapSizeControlFileName : str
        CreationMethod : str
        ViewOption : str
        GlobalMin : float
        GlobalMax : float
        GlobalGrowthRate : float
        MeshControlOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class ChoosePartReplacementOptions(PyCommand):
        """
        Command ChoosePartReplacementOptions.

        Parameters
        ----------
        AddPartManagement : str
        AddPartReplacement : str
        AddLocalSizing : str
        AddBoundaryLayer : str
        AddUpdateTheVolumeMesh : str

        Returns
        -------
        bool
        """
        pass

    class CloseLeakage(PyCommand):
        """
        Command CloseLeakage.

        Parameters
        ----------
        CloseLeakageOption : bool

        Returns
        -------
        bool
        """
        pass

    class ComplexMeshingRegions(PyCommand):
        """
        Command ComplexMeshingRegions.

        Parameters
        ----------
        ComplexMeshingRegionsOption : bool

        Returns
        -------
        bool
        """
        pass

    class ComputeSizeField(PyCommand):
        """
        Command ComputeSizeField.

        Parameters
        ----------
        ComputeSizeFieldControl : str

        Returns
        -------
        bool
        """
        pass

    class CreateBackgroundMesh(PyCommand):
        """
        Command CreateBackgroundMesh.

        Parameters
        ----------
        RefinementRegionsName : str
        CreationMethod : str
        BOIMaxSize : float
        BOISizeName : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionList : list[str]
        ZoneSelectionSingle : list[str]
        ObjectSelectionSingle : list[str]
        TopologyList : list[str]
        BoundingBoxObject : dict[str, Any]
        OffsetObject : dict[str, Any]
        CylinderObject : dict[str, Any]
        Axis : dict[str, Any]
        VolumeFill : str
        CylinderMethod : str
        CylinderLength : float

        Returns
        -------
        bool
        """
        pass

    class CreateCollarMesh(PyCommand):
        """
        Command CreateCollarMesh.

        Parameters
        ----------
        RefinementRegionsName : str
        CreationMethod : str
        BOIMaxSize : float
        BOISizeName : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionList : list[str]
        ZoneSelectionSingle : list[str]
        ObjectSelectionSingle : list[str]
        TopologyList : list[str]
        BoundingBoxObject : dict[str, Any]
        OffsetObject : dict[str, Any]
        CylinderObject : dict[str, Any]
        Axis : dict[str, Any]
        VolumeFill : str
        CylinderMethod : str
        CylinderLength : float

        Returns
        -------
        bool
        """
        pass

    class CreateComponentMesh(PyCommand):
        """
        Command CreateComponentMesh.

        Parameters
        ----------
        RefinementRegionsName : str
        CreationMethod : str
        BOIMaxSize : float
        BOISizeName : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionList : list[str]
        ZoneSelectionSingle : list[str]
        ObjectSelectionSingle : list[str]
        TopologyList : list[str]
        BoundingBoxObject : dict[str, Any]
        OffsetObject : dict[str, Any]
        CylinderObject : dict[str, Any]
        Axis : dict[str, Any]
        VolumeFill : str
        CylinderMethod : str
        CylinderLength : float

        Returns
        -------
        bool
        """
        pass

    class CreateContactPatch(PyCommand):
        """
        Command CreateContactPatch.

        Parameters
        ----------
        ContactPatchName : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        ObjectSelectionList : list[str]
        LabelSelectionList : list[str]
        GroundZoneSelectionList : list[str]
        Distance : float
        ContactPatchDefeaturingSize : float
        FeatureAngle : float
        PatchHole : bool
        FlipDirection : bool

        Returns
        -------
        bool
        """
        pass

    class CreateExternalFlowBoundaries(PyCommand):
        """
        Command CreateExternalFlowBoundaries.

        Parameters
        ----------
        ExternalBoundariesName : str
        CreationMethod : str
        ExtractionMethod : str
        SelectionType : str
        ObjectSelectionList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionSingle : list[str]
        ZoneSelectionSingle : list[str]
        LabelSelectionSingle : list[str]
        OriginalObjectName : str
        BoundingBoxObject : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class CreateGapCover(PyCommand):
        """
        Command CreateGapCover.

        Parameters
        ----------
        GapCoverName : str
        SizingMethod : str
        GapSizeRatio : float
        GapSize : float
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionList : list[str]
        GapCoverBetweenZones : str
        GapCoverRefineFactor : float
        GapCoverRefineFactorAtGap : float
        RefineWrapperBeforeProjection : str
        AdvancedOptions : bool
        MaxIslandFaceForGapCover : int
        GapCoverFeatureImprint : str

        Returns
        -------
        bool
        """
        pass

    class CreateLocalRefinementRegions(PyCommand):
        """
        Command CreateLocalRefinementRegions.

        Parameters
        ----------
        RefinementRegionsName : str
        CreationMethod : str
        BOIMaxSize : float
        BOISizeName : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionList : list[str]
        ZoneSelectionSingle : list[str]
        ObjectSelectionSingle : list[str]
        TopologyList : list[str]
        BoundingBoxObject : dict[str, Any]
        OffsetObject : dict[str, Any]
        CylinderObject : dict[str, Any]
        Axis : dict[str, Any]
        VolumeFill : str
        CylinderMethod : str
        CylinderLength : float

        Returns
        -------
        bool
        """
        pass

    class CreateMeshObjects(PyCommand):
        """
        Command CreateMeshObjects.

        Parameters
        ----------
        MergeZonesBasedOnLabels : bool
        CreateAFaceZonePerBody : bool

        Returns
        -------
        bool
        """
        pass

    class CreateOversetInterfaces(PyCommand):
        """
        Command CreateOversetInterfaces.

        Parameters
        ----------
        OversetInterfacesName : str
        ObjectSelectionList : list[str]

        Returns
        -------
        bool
        """
        pass

    class CreatePorousRegions(PyCommand):
        """
        Command CreatePorousRegions.

        Parameters
        ----------
        InputMethod : str
        PorousRegionName : str
        WrapperSize : float
        FileName : str
        Location : str
        CellSizeP1P2 : float
        CellSizeP1P3 : float
        CellSizeP1P4 : float
        BufferSizeRatio : float
        P1 : list[float]
        P2 : list[float]
        P3 : list[float]
        P4 : list[float]
        NonRectangularParameters : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class CreateRegions(PyCommand):
        """
        Command CreateRegions.

        Parameters
        ----------
        NumberOfFlowVolumes : int
        RetainDeadRegionName : str
        MeshObject : str

        Returns
        -------
        bool
        """
        pass

    class DefineGlobalSizing(PyCommand):
        """
        Command DefineGlobalSizing.

        Parameters
        ----------
        MinSize : float
        MaxSize : float
        GrowthRate : float
        SizeFunctions : str
        CurvatureNormalAngle : float
        CellsPerGap : float
        ScopeProximityTo : str
        Mesher : str
        PrimeSizeControlIds : list[int]
        EnableMultiThreading : bool
        NumberOfMultiThreads : int

        Returns
        -------
        bool
        """
        pass

    class DefineLeakageThreshold(PyCommand):
        """
        Command DefineLeakageThreshold.

        Parameters
        ----------
        AddChild : str
        LeakageName : str
        SelectionType : str
        DeadRegionsList : list[str]
        RegionSelectionSingle : list[str]
        DeadRegionsSize : float
        PlaneClippingValue : int
        PlaneDirection : str
        FlipDirection : bool

        Returns
        -------
        bool
        """
        pass

    class DescribeGeometryAndFlow(PyCommand):
        """
        Command DescribeGeometryAndFlow.

        Parameters
        ----------
        FlowType : str
        GeometryOptions : bool
        AddEnclosure : str
        CloseCaps : str
        LocalRefinementRegions : str
        DescribeGeometryAndFlowOptions : dict[str, Any]
        AllTaskList : list[str]

        Returns
        -------
        bool
        """
        pass

    class DescribeOversetFeatures(PyCommand):
        """
        Command DescribeOversetFeatures.

        Parameters
        ----------
        AdvancedOptions : bool
        ComponentGrid : str
        CollarGrid : str
        BackgroundMesh : str
        OversetInterfaces : str

        Returns
        -------
        bool
        """
        pass

    class ExtractEdges(PyCommand):
        """
        Command ExtractEdges.

        Parameters
        ----------
        ExtractEdgesName : str
        ExtractMethodType : str
        SelectionType : str
        ObjectSelectionList : list[str]
        GeomObjectSelectionList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        FeatureAngleLocal : int
        IndividualCollective : str
        SharpAngle : int
        CompleteObjectSelectionList : list[str]
        CompleteGeomObjectSelectionList : list[str]
        NonExtractedObjects : list[str]

        Returns
        -------
        bool
        """
        pass

    class ExtrudeVolumeMesh(PyCommand):
        """
        Command ExtrudeVolumeMesh.

        Parameters
        ----------
        MExControlName : str
        Method : str
        SelectionType : str
        ExtendToPeriodicPair : bool
        ExtrudeNormalBased : bool
        ExternalBoundaryZoneList : list[str]
        TopologyList : list[str]
        TotalHeight : float
        FirstHeight : float
        NumberofLayers : int
        GrowthRate : float
        VMExtrudePreferences : dict[str, Any]
        ZoneLocation : list[str]

        Returns
        -------
        bool
        """
        pass

    class GenerateInitialSurfaceMesh(PyCommand):
        """
        Command GenerateInitialSurfaceMesh.

        Parameters
        ----------
        GenerateQuads : bool
        ProjectOnGeometry : bool
        EnableMultiThreading : bool
        NumberOfMultiThreads : int
        Prism2DPreferences : dict[str, Any]
        Surface2DPreferences : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class GenerateMapMesh(PyCommand):
        """
        Command GenerateMapMesh.

        Parameters
        ----------
        AddChild : str
        ControlName : str
        SizingOption : str
        ConstantSize : float
        GrowthRate : float
        ShortSideDivisions : int
        SplitQuads : bool
        ProjectOnGeometry : bool
        SelectionType : str
        FaceLabelList : list[str]
        FaceZoneList : list[str]

        Returns
        -------
        bool
        """
        pass

    class GeneratePrisms(PyCommand):
        """
        Command GeneratePrisms.

        Parameters
        ----------
        GeneratePrismsOption : bool

        Returns
        -------
        bool
        """
        pass

    class GenerateShellBoundaryLayerMesh(PyCommand):
        """
        Command GenerateShellBoundaryLayerMesh.

        Parameters
        ----------
        GapFactor : float
        MaxAspectRatio : float
        MinAspectRatio : float
        LocalRemesh : str
        RemeshGrowthRate : float
        RefineStretchedQuads : str
        SplitQuads : str
        nOrthogonalLayers : int
        MaxFaceSkew : float

        Returns
        -------
        bool
        """
        pass

    class GenerateTheMultiZoneMesh(PyCommand):
        """
        Command GenerateTheMultiZoneMesh.

        Parameters
        ----------
        OrthogonalQualityLimit : float
        SelectionType : str
        RegionScope : list[str]
        NonConformal : str
        SizeFunctionScaleFactor : float
        MeshingStrategy : str
        ReMergeZones : str
        MergeBodyLabels : str
        CFDSurfaceMeshControls : dict[str, Any]
        BodyLabelList : list[str]
        CellZoneList : list[str]
        CompleteRegionScope : list[str]

        Returns
        -------
        bool
        """
        pass

    class GenerateTheSurfaceMeshFTM(PyCommand):
        """
        Command GenerateTheSurfaceMeshFTM.

        Parameters
        ----------
        SurfaceQuality : float
        SaveSurfaceMesh : bool
        AdvancedOptions : bool
        SaveIntermediateFiles : str
        IntermediateFileName : str
        SeparateSurface : str
        UseSizeFieldForPrimeWrap : str
        AutoPairing : str
        MergeWrapperAtSolidConacts : str
        ParallelSerialOption : str
        NumberOfSessions : int
        MaxIslandFace : int
        SpikeRemovalAngle : float
        DihedralMinAngle : float
        ProjectOnGeometry : str
        AutoAssignZoneTypes : str
        AdvancedInnerWrap : str
        GapCoverZoneRecovery : str
        GlobalMin : float
        ShowSubTasks : str

        Returns
        -------
        bool
        """
        pass

    class GenerateTheSurfaceMeshWTM(PyCommand):
        """
        Command GenerateTheSurfaceMeshWTM.

        Parameters
        ----------
        CFDSurfaceMeshControls : dict[str, Any]
        SeparationRequired : str
        SeparationAngle : float
        RemeshSelectionType : str
        RemeshZoneList : list[str]
        RemeshLabelList : list[str]
        SurfaceMeshPreferences : dict[str, Any]
        ImportType : str
        AppendMesh : bool
        CadFacetingFileName : str
        Directory : str
        Pattern : str
        LengthUnit : str
        TesselationMethod : str
        OriginalZones : list[str]
        ExecuteShareTopology : str
        CADFacetingControls : dict[str, Any]
        CadImportOptions : dict[str, Any]
        ShareTopologyPreferences : dict[str, Any]
        PreviewSizeToggle : bool

        Returns
        -------
        bool
        """
        pass

    class GenerateTheVolumeMeshFTM(PyCommand):
        """
        Command GenerateTheVolumeMeshFTM.

        Parameters
        ----------
        MeshQuality : float
        OrthogonalQuality : float
        EnableParallel : bool
        SaveVolumeMesh : bool
        EditVolumeSettings : bool
        RegionNameList : list[str]
        RegionVolumeFillList : list[str]
        RegionSizeList : list[str]
        OldRegionNameList : list[str]
        OldRegionVolumeFillList : list[str]
        OldRegionSizeList : list[str]
        AllRegionNameList : list[str]
        AllRegionVolumeFillList : list[str]
        AllRegionSizeList : list[str]
        AdvancedOptions : bool
        SpikeRemovalAngle : float
        DihedralMinAngle : float
        QualityMethod : str
        AvoidHangingNodes : str
        OctreePeelLayers : int
        FillWithSizeField : str
        OctreeBoundaryFaceSizeRatio : float
        GlobalBufferLayers : int
        TetPolyGrowthRate : float
        ConformalPrismSplit : str
        TetPrismStairstepExposedQuads : str
        PrismNormalSmoothRelaxationFactor : float
        ShowSubTasks : str

        Returns
        -------
        bool
        """
        pass

    class GenerateTheVolumeMeshWTM(PyCommand):
        """
        Command GenerateTheVolumeMeshWTM.

        Parameters
        ----------
        Solver : str
        VolumeFill : str
        MeshFluidRegions : bool
        MeshSolidRegions : bool
        SizingMethod : str
        VolumeFillControls : dict[str, Any]
        RegionBasedPreferences : bool
        ReMergeZones : str
        ParallelMeshing : bool
        VolumeMeshPreferences : dict[str, Any]
        PrismPreferences : dict[str, Any]
        GlobalThinVolumePreferences : dict[str, Any]
        InvokePrimsControl : str
        OffsetMethodType : str
        NumberOfLayers : int
        FirstAspectRatio : float
        TransitionRatio : float
        Rate : float
        FirstHeight : float
        MeshObject : str
        MeshDeadRegions : bool
        BodyLabelList : list[str]
        PrismLayers : bool
        QuadTetTransition : str
        MergeCellZones : bool
        FaceScope : dict[str, Any]
        RegionTetNameList : list[str]
        RegionTetMaxCellLengthList : list[str]
        RegionTetGrowthRateList : list[str]
        RegionHexNameList : list[str]
        RegionHexMaxCellLengthList : list[str]
        OldRegionTetMaxCellLengthList : list[str]
        OldRegionTetGrowthRateList : list[str]
        OldRegionHexMaxCellLengthList : list[str]
        CFDSurfaceMeshControls : dict[str, Any]
        ShowSolidFluidMeshed : bool

        Returns
        -------
        bool
        """
        pass

    class GeometrySetup(PyCommand):
        """
        Command GeometrySetup.

        Parameters
        ----------
        SetupType : str
        CappingRequired : str
        WallToInternal : str
        InvokeShareTopology : str
        NonConformal : str
        Multizone : str
        SetupInternals : list[str]
        SetupInternalTypes : list[str]
        OldZoneList : list[str]
        OldZoneTypeList : list[str]
        RegionList : list[str]
        EdgeZoneList : list[str]
        EdgeLabels : list[str]
        Duplicates : bool
        SMImprovePreferences : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class IdentifyConstructionSurfaces(PyCommand):
        """
        Command IdentifyConstructionSurfaces.

        Parameters
        ----------
        MRFName : str
        CreationMethod : str
        SelectionType : str
        ObjectSelectionSingle : list[str]
        ZoneSelectionSingle : list[str]
        LabelSelectionSingle : list[str]
        ObjectSelectionList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        DefeaturingSize : float
        OffsetHeight : float
        Pivot : dict[str, Any]
        Axis : dict[str, Any]
        Rotation : dict[str, Any]
        CylinderObject : dict[str, Any]
        CylinderMethod : str
        BoundingBoxObject : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class IdentifyDeviatedFaces(PyCommand):
        """
        Command IdentifyDeviatedFaces.

        Parameters
        ----------
        DisplayGridName : str
        SelectionType : str
        ObjectSelectionList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        AdvancedOptions : bool
        DeviationMinValue : float
        DeviationMaxValue : float
        Overlay : str
        IncludeGapCoverGeometry : str

        Returns
        -------
        bool
        """
        pass

    class IdentifyOrphans(PyCommand):
        """
        Command IdentifyOrphans.

        Parameters
        ----------
        NumberOfOrphans : str
        ObjectSelectionList : list[str]
        EnableGridPriority : bool
        DonorPriorityMethod : str
        OverlapBoundaries : str
        CheckOversetInterfaceIntersection : str
        RegionNameList : list[str]
        RegionSizeList : list[str]
        OldRegionNameList : list[str]
        OldRegionSizeList : list[str]

        Returns
        -------
        bool
        """
        pass

    class IdentifyRegions(PyCommand):
        """
        Command IdentifyRegions.

        Parameters
        ----------
        AddChild : str
        MaterialPointsName : str
        MptMethodType : str
        NewRegionType : str
        LinkConstruction : str
        SelectionType : str
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        LabelSelectionList : list[str]
        ObjectSelectionList : list[str]
        GraphicalSelection : bool
        ShowCoordinates : bool
        X : float
        Y : float
        Z : float
        OffsetX : float
        OffsetY : float
        OffsetZ : float

        Returns
        -------
        bool
        """
        pass

    class ImportBodyOfInfluenceGeometry(PyCommand):
        """
        Command ImportBodyOfInfluenceGeometry.

        Parameters
        ----------
        Type : str
        GeometryFileName : str
        MeshFileName : str
        ImportedObjects : list[str]
        LengthUnit : str
        CadImportOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class ImportGeometry(PyCommand):
        """
        Command ImportGeometry.

        Parameters
        ----------
        FileFormat : str
        ImportType : str
        LengthUnit : str
        MeshUnit : str
        UseBodyLabels : str
        ImportCadPreferences : dict[str, Any]
        FileName : str
        FileNames : str
        MeshFileName : str
        NumParts : float
        AppendMesh : bool
        Directory : str
        Pattern : str
        CadImportOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class ImproveSurfaceMesh(PyCommand):
        """
        Command ImproveSurfaceMesh.

        Parameters
        ----------
        MeshObject : str
        FaceQualityLimit : float
        SQMinSize : float
        ScopeImproveTo : str
        SMImprovePreferences : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class ImproveVolumeMesh(PyCommand):
        """
        Command ImproveVolumeMesh.

        Parameters
        ----------
        QualityMethod : str
        CellQualityLimit : float
        AddMultipleQualityMethods : str
        QualityMethodList : list[str]
        QualityCriteriaList : list[str]
        OldQualityMethodList : list[str]
        OldQualityCriteriaList : list[str]
        VMImprovePreferences : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class LinearMeshPattern(PyCommand):
        """
        Command LinearMeshPattern.

        Parameters
        ----------
        ChildName : str
        ObjectList : list[str]
        AutoPopulateVector : str
        PatternVector : dict[str, Any]
        Pitch : float
        NumberOfUnits : int
        CheckOverlappingFaces : str
        BatteryModelingOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class LoadCADGeometry(PyCommand):
        """
        Command LoadCADGeometry.

        Parameters
        ----------
        FileName : str
        LengthUnit : str
        Route : str
        UsePrimeGeometryKernel : bool
        FacetingTolerance : float
        CreateObjectPer : str
        NumParts : float
        Refaceting : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class LocalScopedSizingForPartReplacement(PyCommand):
        """
        Command LocalScopedSizingForPartReplacement.

        Parameters
        ----------
        LocalSettingsName : str
        SelectionType : str
        ObjectSelectionList : list[str]
        LabelSelectionList : list[str]
        ZoneSelectionList : list[str]
        ZoneLocation : list[str]
        EdgeSelectionList : list[str]
        LocalSizeControlParameters : dict[str, Any]
        ValueChanged : str
        CompleteZoneSelectionList : list[str]
        CompleteLabelSelectionList : list[str]
        CompleteObjectSelectionList : list[str]
        CompleteEdgeSelectionList : list[str]

        Returns
        -------
        bool
        """
        pass

    class ManageZones(PyCommand):
        """
        Command ManageZones.

        Parameters
        ----------
        Type : str
        ZoneFilter : str
        SizeFilter : str
        Area : float
        Volume : float
        EqualRange : float
        ZoneOrLabel : str
        LabelList : list[str]
        ManageFaceZoneList : list[str]
        ManageCellZoneList : list[str]
        BodyLabelList : list[str]
        Operation : str
        OperationName : str
        MZChildName : str
        AddPrefixName : str
        FaceMerge : str
        Angle : float
        ZoneList : list[str]
        CompleteZoneList : list[str]
        CompleteLabelList : list[str]
        ZoneLocation : list[str]

        Returns
        -------
        bool
        """
        pass

    class MeshFluidDomain(PyCommand):
        """
        Command MeshFluidDomain.

        Parameters
        ----------
        MeshFluidDomainOption : bool

        Returns
        -------
        bool
        """
        pass

    class ModifyMeshRefinement(PyCommand):
        """
        Command ModifyMeshRefinement.

        Parameters
        ----------
        MeshObject : str
        RemeshExecution : str
        RemeshControlName : str
        LocalSize : float
        FaceZoneOrLabel : str
        RemeshFaceZoneList : list[str]
        RemeshFaceLabelList : list[str]
        SizingType : str
        LocalMinSize : float
        LocalMaxSize : float
        RemeshGrowthRate : float
        RemeshCurvatureNormalAngle : float
        RemeshCellsPerGap : float
        CFDSurfaceMeshControls : dict[str, Any]
        RemeshPreferences : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class PartManagement(PyCommand):
        """
        Command PartManagement.

        Parameters
        ----------
        FileLoaded : str
        FMDFileName : str
        AppendFileName : str
        Append : bool
        LengthUnit : str
        CreateObjectPer : str
        FileLengthUnit : str
        FileLengthUnitAppend : str
        Route : str
        RouteAppend : str
        JtLOD : str
        JtLODAppend : str
        PartPerBody : bool
        PrefixParentName : bool
        RemoveEmptyParts : bool
        FeatureAngle : float
        OneZonePer : str
        Refaceting : dict[str, Any]
        IgnoreSolidNames : bool
        IgnoreSolidNamesAppend : bool
        Options : dict[str, Any]
        EdgeExtraction : str
        Context : int
        ObjectSetting : str
        RefacetOptions : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class PartReplacementSettings(PyCommand):
        """
        Command PartReplacementSettings.

        Parameters
        ----------
        PartReplacementName : str
        ManagementMethod : str
        CreationMethod : str
        OldObjectSelectionList : list[str]
        NewObjectSelectionList : list[str]
        AdvancedOptions : bool
        ScalingFactor : float
        MptMethodType : str
        GraphicalSelection : bool
        ShowCoordinates : bool
        X : float
        Y : float
        Z : float

        Returns
        -------
        bool
        """
        pass

    class RemeshSurface(PyCommand):
        """
        Command RemeshSurface.

        Parameters
        ----------
        RemeshSurfaceOption : bool

        Returns
        -------
        bool
        """
        pass

    class RunCustomJournal(PyCommand):
        """
        Command RunCustomJournal.

        Parameters
        ----------
        JournalString : str
        PythonJournal : bool
        PrimeJournal : bool

        Returns
        -------
        bool
        """
        pass

    class SeparateContacts(PyCommand):
        """
        Command SeparateContacts.

        Parameters
        ----------
        SeparateContactsOption : bool

        Returns
        -------
        bool
        """
        pass

    class SetUpPeriodicBoundaries(PyCommand):
        """
        Command SetUpPeriodicBoundaries.

        Parameters
        ----------
        MeshObject : str
        Type : str
        Method : str
        PeriodicityAngle : float
        LCSOrigin : dict[str, Any]
        LCSVector : dict[str, Any]
        TransShift : dict[str, Any]
        SelectionType : str
        ZoneList : list[str]
        LabelList : list[str]
        TopologyList : list[str]
        RemeshBoundariesOption : str
        ZoneLocation : list[str]
        ListAllLabelToggle : bool
        AutoMultiplePeriodic : str
        MultipleOption : str

        Returns
        -------
        bool
        """
        pass

    class SetupBoundaryLayers(PyCommand):
        """
        Command SetupBoundaryLayers.

        Parameters
        ----------
        AddChild : str
        PrismsSettingsName : str
        AspectRatio : float
        GrowthRate : float
        OffsetMethodType : str
        LastRatioPercentage : float
        FirstHeight : float
        PrismLayers : int
        RegionSelectionList : list[str]

        Returns
        -------
        bool
        """
        pass

    class ShareTopology(PyCommand):
        """
        Command ShareTopology.

        Parameters
        ----------
        GapDistance : float
        GapDistanceConnect : float
        STMinSize : float
        InterfaceSelect : str
        EdgeLabels : list[str]
        ShareTopologyPreferences : dict[str, Any]
        SMImprovePreferences : dict[str, Any]
        SurfaceMeshPreferences : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class SizeControlsTable(PyCommand):
        """
        Command SizeControlsTable.

        Parameters
        ----------
        GlobalMin : float
        GlobalMax : float
        TargetGrowthRate : float
        DrawSizeControl : bool
        InitialSizeControl : bool
        TargetSizeControl : bool
        SizeControlInterval : float
        SizeControlParameters : dict[str, Any]

        Returns
        -------
        bool
        """
        pass

    class SwitchToSolution(PyCommand):
        """
        Command SwitchToSolution.


        Returns
        -------
        None
        """
        pass

    class TransformVolumeMesh(PyCommand):
        """
        Command TransformVolumeMesh.

        Parameters
        ----------
        MTControlName : str
        Type : str
        Method : str
        SelectionType : str
        TopoBodyList : list[str]
        CellZoneList : list[str]
        LCSOrigin : dict[str, Any]
        LCSVector : dict[str, Any]
        TransShift : dict[str, Any]
        Angle : float
        Copy : str
        NumOfCopies : int
        Merge : str
        Rename : str
        MergeBoundaries : list[str]

        Returns
        -------
        bool
        """
        pass

    class UpdateBoundaries(PyCommand):
        """
        Command UpdateBoundaries.

        Parameters
        ----------
        MeshObject : str
        SelectionType : str
        BoundaryLabelList : list[str]
        BoundaryLabelTypeList : list[str]
        BoundaryZoneList : list[str]
        BoundaryZoneTypeList : list[str]
        OldBoundaryLabelList : list[str]
        OldBoundaryLabelTypeList : list[str]
        OldBoundaryZoneList : list[str]
        OldBoundaryZoneTypeList : list[str]
        OldLabelZoneList : list[str]
        ListAllBoundariesToggle : bool
        ZoneLocation : list[str]
        TopologyList : list[str]
        TopologyTypeList : list[str]
        OldTopologyList : list[str]
        OldTopologyTypeList : list[str]
        BoundaryCurrentList : list[str]
        BoundaryCurrentTypeList : list[str]
        BoundaryAllowedTypeList : list[str]

        Returns
        -------
        bool
        """
        pass

    class UpdateRegionSettings(PyCommand):
        """
        Command UpdateRegionSettings.

        Parameters
        ----------
        MainFluidRegion : str
        FilterCategory : str
        RegionNameList : list[str]
        RegionMeshMethodList : list[str]
        RegionTypeList : list[str]
        RegionVolumeFillList : list[str]
        RegionLeakageSizeList : list[str]
        RegionOversetComponenList : list[str]
        OldRegionNameList : list[str]
        OldRegionMeshMethodList : list[str]
        OldRegionTypeList : list[str]
        OldRegionVolumeFillList : list[str]
        OldRegionLeakageSizeList : list[str]
        OldRegionOversetComponenList : list[str]
        AllRegionNameList : list[str]
        AllRegionMeshMethodList : list[str]
        AllRegionTypeList : list[str]
        AllRegionVolumeFillList : list[str]
        AllRegionLeakageSizeList : list[str]
        AllRegionOversetComponenList : list[str]
        AllRegionLinkedConstructionSurfaceList : list[str]
        AllRegionSourceList : list[str]
        AllRegionFilterCategories : list[str]

        Returns
        -------
        bool
        """
        pass

    class UpdateRegions(PyCommand):
        """
        Command UpdateRegions.

        Parameters
        ----------
        MeshObject : str
        RegionNameList : list[str]
        RegionTypeList : list[str]
        OldRegionNameList : list[str]
        OldRegionTypeList : list[str]
        RegionInternals : list[str]
        RegionInternalTypes : list[str]
        RegionCurrentList : list[str]
        RegionCurrentTypeList : list[str]
        NumberOfListedRegions : int

        Returns
        -------
        bool
        """
        pass

    class UpdateTheVolumeMesh(PyCommand):
        """
        Command UpdateTheVolumeMesh.

        Parameters
        ----------
        EnableParallel : bool

        Returns
        -------
        bool
        """
        pass

    class WrapMain(PyCommand):
        """
        Command WrapMain.

        Parameters
        ----------
        WrapRegionsName : str

        Returns
        -------
        bool
        """
        pass

    class Write2dMesh(PyCommand):
        """
        Command Write2dMesh.

        Parameters
        ----------
        FileName : str
        SkipExport : bool

        Returns
        -------
        bool
        """
        pass

    class WriteSkinMesh(PyCommand):
        """
        Command WriteSkinMesh.

        Parameters
        ----------
        FileName : str

        Returns
        -------
        bool
        """
        pass

