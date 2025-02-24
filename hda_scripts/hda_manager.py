import hou
import os
import keyword
import re

# Define a list of constants to be used as types for console logging
class TYPES:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    DEEP = "DEEP"

class HDAManager:
    def __init__(self):
        # hdaNode = hou.pwd().parent()
        hdaNode = hou.pwd()
        self.hdaNode = hdaNode        
        
        # Network Box Settings
        self.groupByNetworkBoxL1 = hdaNode.evalParm("group_by_network_box_l1")
        self.includeNodesOutsideNetworkBox = hdaNode.evalParm("include_nodes_outside_boxes") 

        # Sticky Note Settings
        self.linkStickyNotesToBoxes = hdaNode.evalParm("link_sticky_notes_to_boxes")
        self.linkLeftStickyNotes = hdaNode.evalParm("link_left_sticky_notes")
        self.linkRightStickyNotes = hdaNode.evalParm("link_right_sticky_notes")
        self.linkTopStickyNotes = hdaNode.evalParm("link_top_sticky_notes")
        self.stickyNotesDistanceThreshold = hdaNode.evalParm("sticky_notes_distance")
        
        # File Settings
        self.projectLocation = hdaNode.evalParm("project_location")
        self.initFolder()

        self.breakByNodePath = hdaNode.evalParm("break_by_node_path")
        self.breakByNetworkBox = hdaNode.evalParm("break_by_network_box")

        self.defaultFileFormat = hdaNode.evalParm("default_filename_format")
        self.nodeFilenameFormat = hdaNode.evalParm("node_filename_format")
        self.netboxFilenameFormat = hdaNode.evalParm("netbox_filename_format")
        
        # General Filters
        self.filterNetworkBoxes = hdaNode.evalParm("filter_network_boxes")
        self.networkBoxFilter = hdaNode.evalParm("network_box_filter")        
        self.ignoreStickyNotes = hdaNode.evalParm("ignore_notes")
        
        # Node List
        self.nodePathsCount = hdaNode.evalParm("nodes_to_extract")
        self.nodePaths = []
        self.nodeErrors = []
        self.getNodePaths()

        # Text Settings
        self.header = hdaNode.evalParm("header_text")
        self.footer = hdaNode.evalParm("footer_text")
        
        self.actionSelected = hdaNode.evalParm("action_selected")

        # Advanced Settings
        self.exportThisNode = hdaNode.evalParm("export_this_node")
        self.noBMI = hdaNode.evalParm("no_bmi")
        
        # Debug Settings
        self.exportDebugFiles = hdaNode.evalParm("export_debug_files")
        self.printDebugMessages = hdaNode.evalParm("print_debug_messages")

    @staticmethod
    def sanitize_string(text):
        """
        Replaces any character that's not a letter, digit, or underscore with an underscore.
        If the resulting string is a Python keyword, appends an extra underscore.
        
        Parameters:
            text (str): The input string.
            
        Returns:
            str: The sanitized string.
        """
        sanitized = re.sub(r'[^A-Za-z0-9_]+', '_', text)
        if sanitized in keyword.kwlist:
            sanitized += '_'
        return sanitized

    def initFolder(self):
        # Create the project location folder if it does not exist
        if not os.path.exists(self.projectLocation):
            os.makedirs(self.projectLocation)

    def getNodePaths(self):
        self.nodePaths = []
        self.nodeErrors = []
        # if no multiparm, then just get the parent path
        if self.nodePathsCount == 0:
            parent = self.hdaNode.parent()
            self.nodePaths.append(parent.path())
            return
        # if multiparm, then get the paths from the multiparm
        for i in range(1, self.nodePathsCount + 1): # start from 1, coz multiparm is 1 based
            node_path = self.hdaNode.evalParm("node_path_" + str(i))
            if not node_path.startswith("/obj/"):
                errorMsg = f"Error: Only paths starting with '/obj/' are supported. Found: {node_path}"
                self.nodeErrors.append(errorMsg)
            else:
                self.nodePaths.append(node_path)

    def cleanFolder(self):
        # check if the project location has .py files
        fileList = []
        for file in os.listdir(self.projectLocation):
            if file.endswith(".py"):
                fileList.append(file)
        self.consoleLog(f"======= HDAManager.cleanFolder Found {len(fileList)} .py files in the project location.", TYPES.INFO)    
        # remove all .py files from the project location
        for file in os.listdir(self.projectLocation):
            if file.endswith(".py"):
                os.remove(os.path.join(self.projectLocation, file))
        
    def setParm(self, parmName, value):
        # TODO: need a better way to use actual variable names and map them to parmnames
        self.hdaNode.parm(parmName).set(value)

    def consoleLog(self, message, type=TYPES.INFO):
        if type == TYPES.ERROR or type == TYPES.INFO or type == TYPES.WARNING:
            print(message)
            # hou.ui.displayMessage(message, title="Error", severity=hou.severityType.Error)
        elif type == TYPES.DEBUG and self.printDebugMessages:
            print(message)

    def consoleLogInfo(self, message):
        self.consoleLog(message, TYPES.INFO)

    def consoleLogError(self, message):
        self.consoleLog(message, TYPES.ERROR)        
    
    def consoleLogWarning(self, message):
        self.consoleLog(message, TYPES.WARNING)

    def consoleLogDebug(self, message):
        self.consoleLog(message, TYPES.DEBUG)
    
    def consoleLogDeep(self, message):
        self.consoleLog(message, TYPES.DEEP)