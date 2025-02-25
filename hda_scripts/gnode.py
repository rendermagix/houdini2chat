import hou
import houdini_node_manager as hnm
import hda_manager as hdam

class GNode:
    # class variables are static and shared among all instances
    
    # there can be only one constructor in python
    def __init__(self, path):
        """
            Initialize a GNode object with the given path and populate its attributes from the corresponding Houdini node.
        """
        node = hou.node(path)
        self._path = path
        self._type = node.type().name()
        self._name = node.name()
        self._comment = node.comment()
        self._inputs = [inp.path() if inp is not None else None for inp in node.inputs()]
        self._outputs = [out.path() if out is not None else None for out in node.outputs()]
        self._position = node.position()
        self._in_loop = False  # Indicate whether this node is inside a loop
        self._reference = None
        self._loop_id = None  # Store the loop's block_end node_path, initialized empty
        self._note = None
        self._props = {}
    
    # def __init__(self, path, type="", name="", comment="", inputs=[], outputs=[], position=[0,0], reference="",
    #             in_loop=False, loop_id="", note=None):
    #     """
    #         Initialize a GNode object with the given parameters.
    #     """
    #     self._path = path
    #     self._type = type
    #     self._name = name if name else path.split("/")[-1]  # Use the last segment of the path as the name
    #     self._comment = comment
    #     self._inputs = inputs
    #     self._outputs = outputs
    #     self._position = position  # Record the position of the node
    #     self._in_loop = in_loop  # Indicate whether this node is inside a loop
    #     self._reference = reference
    #     self._loop_id = loop_id  # Store the loop's block_end node_path, initialized empty
    #     self._note = note
            
    def update(self, path=None, type=None, name=None, comment=None, inputs=None, outputs=None, position=None, reference = None,
                in_loop=None, loop_id=None, note=None):
        """
            Update the attributes of the GNode object with the given parameters.
        """
        self._path = path if path else self._path
        self._type = type if type else self._type
        self._name = name if name else self._name
        self._comment = comment if comment else self._comment
        self._inputs = inputs if inputs else self._inputs
        self._outputs = outputs if outputs else self._outputs
        self._position = position if position else self._position
        self._in_loop = in_loop if in_loop else self._in_loop
        self._reference = reference if reference else self._reference
        self._loop_id = loop_id if loop_id else self._loop_id
        self._note = note if note else self._note

    def getInputs(self):
        return self._inputs

    def getOutputs(self):
        return self._outputs
    
    def getPath(self):
        return self._path

    def getName(self):      
        return self._name
    
    def getType(self):
        return self._type

    def getPosition(self):
        return self._position
    
    def inLoop(self):
        return self._in_loop
    
    def getLoopId(self):
        return self._loop_id
    
    def getNote(self):
        return self._note

    def toDict(self):
        # convert GNode to a dict
        return {
            "name": self._name,
            "type": self._type,
            "path": self._path,
            "comment": self._comment,
            "inputs": self._inputs,
            "outputs": self._outputs,
            "position": self._position,
            "in_loop": self._in_loop,
            "loop_id": self._loop_id,
            "note": self._note,
            "props": self._props
        }

    def getNote(self):
        return self._note
    
    def inputsToString(self):
        # if graph node has more than one input, add an inputs property with node names
        inputs = [inp for inp in self.getInputs() if inp and isinstance(inp, str)]
        inputs_str = ""
        if len(inputs) > 1:
            # get names only, separated by commas
            inputs_str = ", ".join([inp.split('/')[-1] for inp in inputs])
        return inputs_str

    def getHProps(self):
        # get Houdini properties of the node
        # TODO: refactor the use of @ in nodepath, this will avoid many bugs
        nodePath = self.getPath().split('@')[0]
        props = hnm.HoudiniNodeManager.extract_node_properties(nodePath)
        self._props = props
        return props
    
    def getRenderData(self):
        dict = self.toDict()        
        dict["type"] = hdam.HDAManager().sanitize_string(dict["type"])

        dict["properties"] = self.getHProps()
        inputs_str = self.inputsToString()
        dict["inputs"] = inputs_str if inputs_str else None
        return dict

    def copy(self):
        """
        Returns a deep copy of the current GNode instance.
        """
        import copy
        return copy.deepcopy(self)