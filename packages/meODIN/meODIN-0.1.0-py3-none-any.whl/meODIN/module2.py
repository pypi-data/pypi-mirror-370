from .decorators import requires_auth
from .core import BaseSecuredLib
import clr, os, winreg, random
    
class ZOSpy(BaseSecuredLib):
    """
    Main interface class for connecting and controlling Zemax OpticStudio via ZOS-API.
    Inherits from BaseSecuredLib to support token-based authentication.
    """
    def __init__(self, token=None):
        """
        Initialize a ZOSpy instance.

        Parameters:
            token (str, optional): Authentication token for secured usage. Defaults to None.
        """
        super().__init__(token) # initialize BaseSecuredLib with token

        self.TheConnection = None
        self.TheApplication = None
        self.TheSystem = None
        self.SampleDir = None
        self.ZOSAPI = None
        self.LDE = self.LDE(self)  # Pass reference of ZOSpy to LDE
        self.MFE = self.MFE(self)  # Pass reference of ZOSpy to MFE
        self.TDE = self.TDE(self)  # Pass reference of ZOSpy to TDE
        self.Tolerancing = self.Tolerancing(self) # Pass reference of ZOSpy to Tolerancing

    @requires_auth
    def connectOS(self):
        """
        Connect to Zemax OpticStudio through ZOS-API.

        Raises:
            Exception: If OpticStudio installation is not found.
            Exception: If connection to ZOSAPI fails.
            Exception: If license is not valid for API usage.
        """
        # Determine the Zemax working directory
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
        zemaxData = winreg.QueryValueEx(aKey, "ZemaxRoot")
        NetHelper = os.path.join(os.sep, zemaxData[0], r"ZOS-API\Libraries\ZOSAPI_NetHelper.dll")
        winreg.CloseKey(aKey)

        # Add the NetHelper DLL for locating the OpticStudio install folder
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper

        pathToInstall = ""

        # List of possible installation paths
        install_paths = [
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R2.02",
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R2.01",
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R2.00",
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R1.03",
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R1.02",
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R1.01",
            r"C:/Program Files/Ansys Zemax OpticStudio 2025 R1.00",
            r"C:/Program Files/Ansys Zemax OpticStudio 2024 R1.02",
            r"C:/Program Files/Ansys Zemax OpticStudio 2024 R1.01",
            r"C:/Program Files/Ansys Zemax OpticStudio 2024 R1.00",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R2.02",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R2.01",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R2.00",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R1.03",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R1.02",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R1.01",
            r"C:/Program Files/Ansys Zemax OpticStudio 2023 R1.00"]

        # Connect to OpticStudio with the first path
        success = False
        for path in install_paths:
            success = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)
            if success:
                pathToInstall = path
                break

        if success:
            zemaxDir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
            print("Found OpticStudio at:   %s" % zemaxDir)
        else:
            raise Exception("Cannot find OpticStudio")

        # Load the ZOS-API assemblies
        clr.AddReference(os.path.join(os.sep, zemaxDir, r"ZOSAPI.dll"))
        clr.AddReference(os.path.join(os.sep, zemaxDir, r"ZOSAPI_Interfaces.dll"))
        import ZOSAPI
        self.ZOSAPI = ZOSAPI

        self.TheConnection = ZOSAPI.ZOSAPI_Connection()
        if self.TheConnection is None:
            raise Exception("Unable to initialize NET connection to ZOSAPI")

        self.TheApplication = self.TheConnection.ConnectAsExtension(0)
        if self.TheApplication is None:
            raise Exception("Unable to acquire ZOSAPI application")

        if not self.TheApplication.IsValidLicenseForAPI:
            raise Exception("License is not valid for ZOSAPI use. Make sure you have enabled 'Programming > Interactive Extension' from the OpticStudio GUI.")

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise Exception("Unable to acquire Primary system")

    def disconnectOS(self):
        """
        Disconnect from OpticStudio and close the application.
        """
        self.TheApplication.CloseApplication()

    def openFile(self, path):
        """
        Open an existing OpticStudio file.

        Parameters:
            path (str): Full path to the .ZMX or .ZOS file.
        """
        self.TheSystem.LoadFile(path, False)

    def saveFile(self):
        """
        Save the currently loaded system in OpticStudio.
        """
        self.TheSystem.Save()

    def saveAsFile(self, pathWithName):
        """
        Save the current system under a new file name.

        Parameters:
            pathWithName (str): Full path including filename for saving.
        """
        self.TheSystem.SaveAs(pathWithName)

#    def addSurfaceAfter(self, surface):
#
#    def addSurfaceBefore(self, surface):
#
#    def deleteSurface(self, surface):

    def localOptimalization(self, cores=2):
        """
        Run local optimization in OpticStudio.

        Parameters:
            cores (int): Number of CPU cores to use. Default is 2.
        """
        LocalOpt = self.TheSystem.Tools.OpenLocalOptimization()
        LocalOpt.Algorithm = self.ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares
        LocalOpt.Cycles = self.ZOSAPI.Tools.Optimization.OptimizationCycles.Fixed_5_Cycles
        LocalOpt.NumberOfCores = cores
        LocalOpt.RunAndWaitForCompletion()
        LocalOpt.Close()

    class LDE:
        """
        Wrapper for the Lens Data Editor (LDE) in OpticStudio.
        Provides methods to manipulate optical surfaces and parameters.
        """
        def __init__(self, outer_instance):
            """
            Initialize LDE wrapper.

            Parameters:
                outer_instance (ZOSpy): Reference to the parent ZOSpy instance.
            """
            self.outerLDE = outer_instance  # Store reference to ZOSpy

        def getSurfaceByComment(self, comment):
            """
            Find a surface index by its comment field.

            Parameters:
                comment (str): Comment string to search for.

            Returns:
                int or None: Surface index if a match is found, otherwise None.
            """
            for surface in range(self.outerLDE.TheSystem.LDE.NumberOfSurfaces):
                if self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).Comment == comment:
                    return surface


        def removeSurfaces(self, first_surface, last_surface):
            """
            Remove a range of surfaces from the Lens Data Editor (LDE).

            Parameters:
                first_surface (int): Index of the first surface to remove.
                last_surface (int): Index of the last surface to remove.
            """
            self.outerLDE.TheSystem.LDE.RemoveSurfacesAt(first_surface, (last_surface - first_surface) + 1)

        def setUiUpdate(self, bool):
            """
            Enable or disable live updates in the OpticStudio user interface.

            Parameters:
                enable (bool): If True, updates will be shown in the UI.
                               If False, updates will be suppressed.
            """
            self.outerLDE.TheApplication.ShowChangesInUI = bool# False or True

        def ignoreSurface(self, surface, bool):
            """
            Mark a surface as ignored or active.

            Parameters:
                surface_index (int): Index of the surface to modify.
                ignore (bool): True to ignore the surface, False to include it.
            """
            surface = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface)
            surface.TypeData.IgnoreSurface = bool

        def setSurfaceType(self, surfaces, type):
            """
            Change the type of one or more surfaces in the Lens Data Editor (LDE).

            Parameters:
                surfaces (list[int]): List of surface indices to update.
                surface_type (str): Type of surface to assign. Supported values:
                                    - "Standard"
                                    - "Even Asphere"
                                    - "Coordinate Break"
                                    - "Zernike Fringe Sag"

            Raises:
                ValueError: If an unsupported surface type is requested.
            """
            match type:
                case "Standard":
                    get_surface_type = self.outerLDE.ZOSAPI.Editors.LDE.SurfaceType.Standard
                    for surface in surfaces:
                        get_surface_type_setting = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetSurfaceTypeSettings(get_surface_type)
                        self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).ChangeType(get_surface_type_setting)
                case "Even Asphere":
                    get_surface_type = self.outerLDE.ZOSAPI.Editors.LDE.SurfaceType.EvenAspheric
                    for surface in surfaces:
                        get_surface_type_setting = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetSurfaceTypeSettings(get_surface_type)
                        self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).ChangeType(get_surface_type_setting)
                case "Coordinate Break":
                    get_surface_type = self.outerLDE.ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak
                    for surface in surfaces:
                        get_surface_type_setting = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetSurfaceTypeSettings(get_surface_type)
                        self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).ChangeType(get_surface_type_setting)
                case "Zernike Fringe Sag":
                    get_surface_type = self.outerLDE.ZOSAPI.Editors.LDE.SurfaceType.ZernikeFringeSag

                    for surface in surfaces:
                        get_surface_type_setting = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetSurfaceTypeSettings(get_surface_type)
                        self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).ChangeType(get_surface_type_setting)
                        self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetCellAt(24).Value = "37"

                        solve = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetCellAt(25).CreateSolveType(self.outerLDE.ZOSAPI.Editors.SolveType.SurfacePickup)
                        solve._S_SurfacePickup.Surface = surface
                        solve._S_SurfacePickup.Column = self.outerLDE.TheSystem.LDE.SurfaceColumn.SemiDiameter
                        self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetCellAt(25).SetSolveData(solve)
                case _:
                    raise ValueError(f"Unknown surface type: {type}")


        def setParameter(self, surface, parameter, value):
            """
            Set a parameter of a surface in the Lens Data Editor (LDE).

            Parameters:
                surface (int | str): Surface index or comment string.
                parameter (str): Name of the parameter to set. Supported keys include:
                                 "Comment", "Radius", "Thickness", "Material", "Coating",
                                 "Semi-Diameter", "Conic", "TCE", "Decenter X", "Decenter Y",
                                 "Tilt About X", "Tilt About Y", "Tilt About Z",
                                 and "Zernike 1" ... "Zernike 56".
                value (str | float | int): New value for the parameter.
                                           Use "Variable" to mark the parameter as a variable
                                           (only supported for some parameters).

            Raises:
                ValueError: If the parameter is not recognized.
            """
            parameter_map = {
                "Comment": (1, False),
                "Radius": (2, True),
                "Thickness": (3, True),
                "Material": (4, False),
                "Coating": (5, False),
                "Semi-Diameter": (6, False),
                "Conic": (9, True),
                "TCE": (10, True),
                "Decenter X": (12, True),
                "Decenter Y": (13, True),
                "Tilt About X": (14, True),
                "Tilt About Y": (15, True),
                "Tilt About Z": (16, True),
                "Zernike 1": (26, True),
                "Zernike 2": (27, True),
                "Zernike 3": (28, True),
                "Zernike 4": (29, True),
                "Zernike 5": (30, True),
                "Zernike 6": (31, True),
                "Zernike 7": (32, True),
                "Zernike 8": (33, True),
                "Zernike 9": (34, True),
                "Zernike 10": (35, True),
                "Zernike 11": (36, True),
                "Zernike 12": (37, True),
                "Zernike 13": (38, True),
                "Zernike 14": (39, True),
                "Zernike 15": (40, True),
                "Zernike 16": (41, True),
                "Zernike 17": (42, True),
                "Zernike 18": (43, True),
                "Zernike 19": (44, True),
                "Zernike 20": (45, True),
                "Zernike 21": (46, True),
                "Zernike 22": (47, True),
                "Zernike 23": (48, True),
                "Zernike 24": (49, True),
                "Zernike 25": (50, True),
                "Zernike 26": (51, True),
                "Zernike 27": (52, True),
                "Zernike 28": (53, True),
                "Zernike 29": (54, True),
                "Zernike 30": (55, True),
                "Zernike 31": (56, True),
                "Zernike 32": (57, True),
                "Zernike 33": (58, True),
                "Zernike 34": (59, True),
                "Zernike 35": (60, True),
                "Zernike 36": (61, True),
                "Zernike 37": (62, True),
                "Zernike 38": (63, True),
                "Zernike 39": (64, True),
                "Zernike 40": (65, True),
                "Zernike 41": (66, True),
                "Zernike 42": (67, True),
                "Zernike 43": (68, True),
                "Zernike 44": (69, True),
                "Zernike 45": (70, True),
                "Zernike 46": (71, True),
                "Zernike 47": (72, True),
                "Zernike 48": (73, True),
                "Zernike 49": (74, True),
                "Zernike 50": (75, True),
                "Zernike 51": (76, True),
                "Zernike 52": (77, True),
                "Zernike 53": (78, True),
                "Zernike 54": (79, True),
                "Zernike 55": (80, True),
                "Zernike 56": (81, True)
            }



            if isinstance(surface, str):
                surface = self.getSurfaceByComment(surface)
                
            if parameter in parameter_map:
                cell_index, supports_variable = parameter_map[parameter]
                cell = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetCellAt(cell_index)

                if supports_variable and value == "Variable":
                    cell.MakeSolveVariable()
                else:
                    if isinstance(value, str):
                        cell.Value = value
                    else:
                        cell.DoubleValue = value

        def getParameter(self, surface, parameter):
            """
            Get a parameter value of a surface in the Lens Data Editor (LDE).

            Parameters:
                surface (int | str): Surface index or comment string.
                parameter (str): Name of the parameter to read. Supported keys include:
                                 "Comment", "Radius", "Thickness", "Material", "Coating",
                                 "Semi-Diameter", "Conic", "TCE", "Decenter X", "Decenter Y",
                                 "Tilt About X", "Tilt About Y", "Tilt About Z",
                                 and "Zernike 1" ... "Zernike 56".

            Returns:
                float | str: Parameter value.
                             Returns float for numeric parameters,
                             str for text-based parameters.

            Raises:
                ValueError: If the parameter is not recognized.
            """
            parameter_map = {
                "Comment": (1, False),
                "Radius": (2, True),
                "Thickness": (3, True),
                "Material": (4, False),
                "Coating": (5, False),
                "Semi-Diameter": (6, True),
                "Conic": (9, True),
                "TCE": (10, True),
                "Decenter X": (12, True),
                "Decenter Y": (13, True),
                "Tilt About X": (14, True),
                "Tilt About Y": (15, True),
                "Tilt About Z": (16, True),
                "Zernike 1": (26, True),
                "Zernike 2": (27, True),
                "Zernike 3": (28, True),
                "Zernike 4": (29, True),
                "Zernike 5": (30, True),
                "Zernike 6": (31, True),
                "Zernike 7": (32, True),
                "Zernike 8": (33, True),
                "Zernike 9": (34, True),
                "Zernike 10": (35, True),
                "Zernike 11": (36, True),
                "Zernike 12": (37, True),
                "Zernike 13": (38, True),
                "Zernike 14": (39, True),
                "Zernike 15": (40, True),
                "Zernike 16": (41, True),
                "Zernike 17": (42, True),
                "Zernike 18": (43, True),
                "Zernike 19": (44, True),
                "Zernike 20": (45, True),
                "Zernike 21": (46, True),
                "Zernike 22": (47, True),
                "Zernike 23": (48, True),
                "Zernike 24": (49, True),
                "Zernike 25": (50, True),
                "Zernike 26": (51, True),
                "Zernike 27": (52, True),
                "Zernike 28": (53, True),
                "Zernike 29": (54, True),
                "Zernike 30": (55, True),
                "Zernike 31": (56, True),
                "Zernike 32": (57, True),
                "Zernike 33": (58, True),
                "Zernike 34": (59, True),
                "Zernike 35": (60, True),
                "Zernike 36": (61, True),
                "Zernike 37": (62, True),
                "Zernike 38": (63, True),
                "Zernike 39": (64, True),
                "Zernike 40": (65, True),
                "Zernike 41": (66, True),
                "Zernike 42": (67, True),
                "Zernike 43": (68, True),
                "Zernike 44": (69, True),
                "Zernike 45": (70, True),
                "Zernike 46": (71, True),
                "Zernike 47": (72, True),
                "Zernike 48": (73, True),
                "Zernike 49": (74, True),
                "Zernike 50": (75, True),
                "Zernike 51": (76, True),
                "Zernike 52": (77, True),
                "Zernike 53": (78, True),
                "Zernike 54": (79, True),
                "Zernike 55": (80, True),
                "Zernike 56": (81, True)
            }

            

            if isinstance(surface, str):
                surface = self.getSurfaceByComment(surface)

            if parameter in parameter_map:
                cell_index, isFloat = parameter_map[parameter]
                cell = self.outerLDE.TheSystem.LDE.GetSurfaceAt(surface).GetCellAt(cell_index)

                if isFloat:
                    return cell.DoubleValue
                else:
                    return cell.Value
            else:
                raise ValueError(f"Parameter '{parameter}' not found in parameter map.")
            
        def removeAllVariable(self):
            """
            Remove all variables from the current system.

            This clears all variables defined in the system (e.g. in the LDE, MCE, etc.).
            After this call, no parameters will remain as variables.

            Notes:
                - This action cannot be undone through the API.
                - Use with caution, as it resets the optimization setup.
            """
            self.outerLDE.TheSystem.Tools.RemoveAllVariables()

        def setCoordinateBreakToElement(self, surface_1, surface_2, color="Default Color"):
            """
            Groups a range of surfaces into an element using a coordinate break.

            Equivalent to using 'Tilt/Decenter Elements' in Zemax OpticStudio.

            Parameters:
                surface_1 (int or str): Index or comment of the first surface in the group.
                surface_2 (int or str): Index or comment of the last surface in the group.
                color (str): Display color for the element in the LDE. 
                             Must be one of the keys in `color_mapping`. Default is "Default Color".

            Raises:
                ValueError: If an invalid color name is provided.
            """
            # Mapping of string inputs to ZemaxColor attributes
            color_mapping = {
                "Default Color": self.outerLDE.ZOSAPI.Common.ZemaxColor.Default,
                "Color 1": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color1,
                "Color 2": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color2,
                "Color 3": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color3,
                "Color 4": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color4,
                "Color 5": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color5,
                "Color 6": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color6,
                "Color 7": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color7,
                "Color 8": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color8,
                "Color 9": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color9,
                "Color 10": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color10,
                "Color 11": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color11,
                "Color 12": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color12,
                "Color 13": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color13,
                "Color 14": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color14,
                "Color 15": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color15,
                "Color 16": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color16,
                "Color 17": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color17,
                "Color 18": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color18,
                "Color 19": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color19,
                "Color 20": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color20,
                "Color 21": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color21,
                "Color 22": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color22,
                "Color 23": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color23,
                "Color 24": self.outerLDE.ZOSAPI.Common.ZemaxColor.Color24,
            }

            # Get the corresponding ZemaxColor attribute
            zemax_color = color_mapping.get(color)
            if zemax_color is None:
                raise ValueError(f"Invalid color: {color}. Valid options are: {list(color_mapping.keys())}")

            if isinstance(surface_1, str):
                surface_1 = self.getSurfaceByComment(surface_1)

            if isinstance(surface_2, str):
                surface_2 = self.getSurfaceByComment(surface_2)

            change = self.outerLDE.TheSystem.LDE.GetTool_TiltDecenterElements()
            change.FirstSurface = surface_1
            change.LastSurface = surface_2
            change.CoordinateBreakColor = zemax_color
            self.outerLDE.TheSystem.LDE.RunTool_TiltDecenterElements(change)

        def tolerancePreparation(self, surfaces):
            """
            Prepares a set of surfaces for tolerance analysis:
            - Ensures surfaces are processed in pairs.
            - Converts them to 'Zernike Fringe Sag'.
            - Groups each pair with a coordinate break.

            Parameters:
                surfaces (list[int|str]): List of surface indices or comments.
                color (str): Display color for the element grouping. Defaults to "Default Color".
                strict (bool): If True, enforces even number of surfaces (raises error).
                               If False, last unpaired surface is ignored.

            Raises:
                ValueError: If number of surfaces is odd and `strict=True`.
            """
            # Ensure the number of surfaces is even
            if len(surfaces) % 2 != 0:
                raise ValueError("The number of surfaces must be even.")

            # Set the surface type to "Zernike Fringe Sag" for each surface
            self.setSurfaceType(surfaces, "Zernike Fringe Sag")

            # Pair the surfaces from the end to the beginning and set coordinate breaks
            for i in range(len(surfaces) - 1, 0, -2):
                surface_1 = surfaces[i - 1]
                surface_2 = surfaces[i]
                self.setCoordinateBreakToElement(surface_1, surface_2)

    class MFE:
        """
        Wrapper for the Merit Function Editor (MFE) in OpticStudio.
        Provides methods to control Merit Function Editor.
        """
        def __init__(self, outer_instance):
            """
            Initialize MFE wrapper.

            Parameters:
                outer_instance (ZOSpy): Reference to the parent ZOSpy instance.
            """
            self.outerMFE = outer_instance  # Store reference to ZOSpy

        def loadMeritFunction(self, path):
            """
            Load a merit function from a file into the system.

            Parameters:
                path (str): File path to the merit function (.zmx or .mfe) to load.
            """
            self.outerMFE.TheSystem.MFE.LoadMeritFunction(path)

        def calculateMeritFunction(self):
            """
            Trigger the calculation of the currently loaded merit function.
            """
            self.outerMFE.TheSystem.MFE.CalculateMeritFunction()

        def getValue(self, line):
            """
            Retrieve the value of the merit function from a specific row.

            Parameters:
                line (int): The row number in the merit function (1-based index).

            Returns:
                float: The merit function value at the specified row.
            """
            return self.outerMFE.TheSystem.MFE.GetRowAt(line - 1).GetCellAt(12).DoubleValue

    class TDE:
        def __init__(self, outer_instance):
            self.outerTDE = outer_instance  # Store reference to ZOSpy

        def loadTDE(self, fileName):
            self.outerTDE.TheSystem.TDE.LoadToleranceFile (fileName)
            
        def clearTDE(self):
            self.outerTDE.TheSystem.TDE.DeleteAllRows()

        def addTWAV(self, wavelength):
            typ = self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TWAV
            self.outerTDE.TheSystem.TDE.GetOperandAt(1).ChangeType(typ)
            self.outerTDE.TheSystem.TDE.GetRowAt(0).GetCellAt(6).DoubleValue = wavelength
            self.outerTDE.TheSystem.TDE.GetRowAt(0).GetCellAt(8).Value = "Test wavelength"

        def addComment(self, comment):
            self.outerTDE.TheSystem.TDE.AddOperand().Comment = comment

        def addSTAT(self, distribution):
            match distribution:
                case "Normal":
                    Int1 = 0
                case "Uniform":
                    Int1 = 1
                case "Parabolic":
                    Int1 = 2
            typ = self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.STAT
            self.outerTDE.TheSystem.TDE.AddOperand().ChangeType(typ)
            self.outerTDE.TheSystem.TDE.GetRowAt(self.outerTDE.TheSystem.TDE.NumberOfOperands - 1).GetCellAt(2).IntegerValue = Int1
            self.outerTDE.TheSystem.TDE.GetRowAt(self.outerTDE.TheSystem.TDE.NumberOfOperands - 1).GetCellAt(8).Value = distribution

        # Operands depending on surfaces
        def add_tolerance_operand(self, surfaces, value, operand_type):

            for surface in surfaces:
                operand = self.outerTDE.TheSystem.TDE.AddOperand()
                operand.ChangeType(operand_type)
                row = self.outerTDE.TheSystem.TDE.GetRowAt(self.outerTDE.TheSystem.TDE.NumberOfOperands - 1)
                row.GetCellAt(2).IntegerValue = surface
                row.GetCellAt(6).DoubleValue = -value
                row.GetCellAt(7).DoubleValue = value

        # Operands depending on pair surfaces
        def add_tolerance_operand_2(self, surfaces, value, operand_type):

            for surface in surfaces:
                operand = self.outerTDE.TheSystem.TDE.AddOperand()
                operand.ChangeType(operand_type)
                row = self.outerTDE.TheSystem.TDE.GetRowAt(self.outerTDE.TheSystem.TDE.NumberOfOperands - 1)
                row.GetCellAt(2).IntegerValue = surface
                row.GetCellAt(3).IntegerValue = surface
                row.GetCellAt(6).DoubleValue = -value
                row.GetCellAt(7).DoubleValue = value

        def addTFRN(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TFRN)

        def addTIRR(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TIRR)

        def addTIND(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TIND)

        def addTTHI(self, surfaces, value):
            self.add_tolerance_operand_2(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TTHI)

        def addTUDX(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TUDX)

        def addTUDY(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TUDY)

        def addTUTX(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TUTX)

        def addTUTY(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TUTY)

        def addTUTZ(self, surfaces, value):
            self.add_tolerance_operand(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TUTZ)

        def addTETX(self, surfaces, value):
            self.add_tolerance_operand_2(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TETX)

        def addTETY(self, surfaces, value):
            self.add_tolerance_operand_2(surfaces, value, self.outerTDE.ZOSAPI.Editors.TDE.ToleranceOperandType.TETY)



        # Procedures
        def addTolClass(self, surfaces, OpticalTolerance, MechanicalTolerance):
            match OpticalTolerance:
                case "Commercial":
                    CenterThickness = 0.150 # mm
                    Radius = 5 # fringe
                    Irregularity = 1 # fringe, doplniť = ZER, ISO A,B,C
                    Wedge = 0.05 # degree, treba domyslieť závislosť na priemere čočky
                    RefractionIndex = 0.001 # -
                    #casova_narocnost = 1 #Koliášová kalkulácia + technologie Dalibor Zlámal

                case "Precision":
                    CenterThickness = 0.050 # mm
                    Radius = 3 # fringe
                    Irregularity = 0.25 # fringe
                    Wedge = 0.025 # degree, treba domyslieť závislosť na priemere čočky
                    RefractionIndex = 0.0005 # -
                    #casova_narocnost = 1.4


                case "High Precision":
                    CenterThickness = 0.010 # mm
                    Radius = 1 # fringe
                    Irregularity = 0.05 # fringe
                    Wedge = 0.01 # degree, treba domyslieť závislosť na priemere čočky
                    RefractionIndex = 0.0005 # -

            match MechanicalTolerance:
                case "Sypačka1":
                    AirgapsThickness = 0.025 # mm vyňať vzduchové medzery z Mechanical Tolerance(Mali by byť samostane)!!
                    Decenter = 0.01 # mm
                    ElementTilt = 0.02 # degree

                case "Sypačka2":
                    AirgapsThickness = 0.025 # mm
                    Decenter = 0.01 # mm
                    ElementTilt = 0.02 # degree

                case "Sypačk3":
                    AirgapsThickness = 0.025 # mm
                    Decenter = 0.01 # mm
                    ElementTilt = 0.02 # degree

                case "PresnéVlepovanie":
                    AirgapsThickness = 0.025 # mm
                    Decenter = 0.01 # mm
                    ElementTilt = 0.02 # degree

                case "CentrickéStáčanie":
                    AirgapsThickness = 0.025 # mm
                    Decenter = 0.01 # mm
                    ElementTilt = 0.02 # degree

            # OPTICAL
            self.addComment("TOLERANCES FOR SURFACES: " + str(surfaces))
            self.addComment("OPTICAL TOLERANCES")
            self.addComment("Center Glass Thickness [mm]")
            self.addSTAT("Uniform")
            self.addTTHI(surfaces[::2], CenterThickness)

            self.addComment("Radius [fringe]")
            self.addSTAT("Uniform")
            self.addTFRN(surfaces, Radius)

            self.addComment("Irregularity [fringe]")
            self.addSTAT("Uniform")
            self.addTIRR(surfaces, Irregularity)

            self.addComment("Wedge [degree]")
            self.addSTAT("Uniform")
            self.addTETX(surfaces, Wedge)
            self.addTETY(surfaces, Wedge)

            self.addComment("Refraction Index [-]")
            self.addSTAT("Uniform")
            self.addTIND(surfaces, RefractionIndex)

            # MECHANICAL
            self.addComment("")
            self.addComment("MECHANICAL TOLERANCES")
            self.addComment("Airgaps Thickness [mm]")
            self.addSTAT("Uniform")
            self.addTTHI([x + 3 for x in surfaces[::2]], AirgapsThickness)

            self.addComment("Element Decenter [mm]")
            self.addSTAT("Uniform")
            self.addTUDX([x - 1 for x in surfaces[::2]], Decenter)
            self.addTUDY([x - 1 for x in surfaces[::2]], Decenter)

            self.addComment("Element Tilt [degree]")
            self.addSTAT("Uniform")
            self.addTUTX([x - 1 for x in surfaces[::2]], ElementTilt)
            self.addTUTY([x - 1 for x in surfaces[::2]], ElementTilt)

    class Tolerancing:
        """
        A utility class for performing Monte Carlo tolerancing analyses using ZOS-API.
        Provides methods to run Monte Carlo simulations, retrieve results, and extract
        specific data columns from the analysis.
        """

        def __init__(self, outer_instance):
            """
            Initialize the Tolerancing helper with a reference to the outer ZOS-API instance.

            Parameters:
                outer_instance: The ZOS-API instance containing the optical system.
            """
            self.outerTolerancing = outer_instance  # Store reference to ZOSpy
            self.tol = None
        
        def getMonteCarlo(self):
            """
            Perform a single Monte Carlo run and load the generated result file.

            Generates a temporary Monte Carlo result file, loads it into the optical system,
            and deletes the file afterward to keep the workspace clean.
            """
            tol = None
            tol = self.outerTolerancing.TheSystem.Tools.OpenTolerancing()
            # Select index of # of Cores
            tol.SetupCore = 0
            # Unmarked: Open Tolerance Data Viewer on Completion
            tol.OpenDataViewer = False
            # Select Sensitivity mode
            tol.SetupMode =  self.outerTolerancing.ZOSAPI.Tools.Tolerancing.SetupModes.SkipSensitivity
            # Select Criterion and related settings
            tol.Criterion = self.outerTolerancing.ZOSAPI.Tools.Tolerancing.Criterions.MeritFunction
            tol.CriterionComps = None
            # Select number of MC runs and files to save
            tol.NumberOfRuns = 1
            tol.NumberToSave = 1

            # Generate a random number between 0 and 999999
            number = random.randint(0, 999999)
            # Format the number as a 6-digit string, padding with zeros if necessary
            six_digit_string = f"{number:06}"

            tol.FilePrefix = six_digit_string
            # Run the Tolerancing analysis
            tol.RunAndWaitForCompletion()
            tol.Close()
            tol = None

            # Construct the file path
            file_path = fr"H:\Projects\A10 CORRECTOR\{six_digit_string}MC_T0001.zmx"

            # Open generated MC
            self.outerTolerancing.TheSystem.LoadFile(file_path, False)

            # Check if the file exists
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)

        def runMonteCarlos(self, cores, ScriptIndex, NumberOfRuns, NumberToSave):
            """
            Run a Monte Carlo tolerancing analysis with user-defined settings.

            Parameters:
                cores (int): Number of CPU cores to use for the analysis.
                ScriptIndex (int): Index of the user-defined tolerancing script to apply.
                NumberOfRuns (int): Total number of Monte Carlo runs to execute.
                NumberToSave (int): Number of output files to save from the analysis.
            """
            tol = self.outerTolerancing.TheSystem.Tools.OpenTolerancing()
            # Select index of # of Cores
            tol.SetupCore = cores - 1
            # Select Sensitivity mode
            tol.SetupMode =  self.outerTolerancing.ZOSAPI.Tools.Tolerancing.SetupModes.SkipSensitivity
            # Select Criterion and related settings
            tol.Criterion = self.outerTolerancing.ZOSAPI.Tools.Tolerancing.Criterions.UserScript
            tol.CriterionScript =  ScriptIndex - 1
            # Select number of MC runs and files to save
            tol.NumberOfRuns = NumberOfRuns
            tol.NumberToSave = NumberToSave
            # Run the Tolerancing analysis
            tol.RunAndWaitForCompletion()
            tol.Close()
            tol = None

        def getData(self, column):
            """
            Retrieve a specific column of Monte Carlo result data.

            Parameters:
                column (int): Zero-based index of the column to extract.

            Returns:
                list[float]: Values from the specified column across all rows.
            """
            # Open the Tolerance Data Viewer tool
            viewer = self.outerTolerancing.TheSystem.Tools.OpenToleranceDataViewer()

            # Run the Tolerance Data Viewer and wait for it to complete
            viewer.RunAndWaitForCompletion()

            # Get the number of rows in the Monte Carlo data
            numberOfRows = viewer.MonteCarloData.Values.Rows

            # Initialize an empty list to store row data
            rowData = []

            # Iterate through each row in the Monte Carlo data
            for row in range(numberOfRows):
                # Append the value at the specified column for the current row to the rowData list
                rowData.append(viewer.MonteCarloData.Values.GetValueAt(row, column))

            # Return the collected column data
            return rowData

