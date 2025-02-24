import hou
import json
import hda_manager as hda
import gnode as gn
import math
import os
import copy
import houdini_node_manager as hnm

class NodeGraph:
    # class variables are static and shared among all instances
    
    def __init__(self, name, parent_path, nodeList=[], is_loop_graph=False):        
        self.name = name
        self.parent_path = parent_path
        self.gNodes = {} # it is a dictionary, to allow fast access to nodes by path
        self.edges = []
        self.branches = []
        self.graphLoops = []
        self.noLoopNodes = []
        self.loop_id = None
        self.loop_end = None
        self.begin_nodes = []
        self.graphList = []
        self.begin_end_nodes = []
        self.hdaSettings = hda.HDAManager()
        # self.hdaSettings.consoleLogDebug(f"NodeGraph: {parent_path},  {nodeList} {is_loop_graph}")
        self.is_loop_graph = is_loop_graph
        if nodeList:
            self.compose(nodeList)

# ==================================
# ========= Building Graph ELEMENTS
# ==================================
 
    def get_node(self, node_path):
        """
        Returns the node from the graph corresponding to the given node path.
        If the node does not exist in the graph, returns None.
        """
        return self.gNodes.get(node_path)
    
    def add_edge(self, from_node_path, to_node_path):
        # check if the edge already exists
        if (from_node_path, to_node_path) in self.edges:
            return False
        else:
            self.edges.append((from_node_path, to_node_path))
        return True

    def delete_edge(self, from_node_path, to_node_path):
        """
        Deletes the edge from from_node_path to to_node_path if it exists.
        """
        self.edges = [edge for edge in self.edges if not (edge[0] == from_node_path and edge[1] == to_node_path)]

    def build_graph_from_node_list(self, nodeList):
        """
        Builds a graph from a list of node objects.
        """
        # TODO: this is not taking in consideration that input nodes may be coming from nodes outside this sub network.
        # TODO: we loop on inputs only, that means, we dont take in consideration output links that go to nodes outside this sub network.
        for nodePath in nodeList:
            gNode = gn.GNode(nodePath)
            self.gNodes[nodePath] = gNode
            for gNode_input_path in gNode.getInputs():
                self.add_edge(gNode_input_path, nodePath)
        return self

    def set_node_above(self, moving_node_path, reference_node_path):
        """
        Sets the position of the moving node to be right above the reference node.
        The new position is computed by adding the offset to the y coordinate of the reference node's position.
        
        Parameters:
            moving_node_path (str): The node path of the node to reposition.
            reference_node_path (str): The node path of the reference node.
        """

        ref_node = self.gNodes[reference_node_path]
        moving_node = self.gNodes[moving_node_path]
        
        offset = 0.4 # Default offset
        ref_pos = ref_node.getPosition()
        new_x = ref_pos[0]
        new_y = ref_pos[1] + offset  # Increase y to place above; adjust if your coordinate system is different.        
        moving_node.update(position=[new_x, new_y])
        
    def get_distance(self, node, note):
        hdaSettings = hda.HDAManager()
        distance = None
        # note position is the bottom left corner
        pos_note = [
            note["position"][0] + note["size"][0] / 2,
            note["position"][1] + note["size"][1] / 2
        ]
        pos_node = node.getPosition()
        distance = math.sqrt((pos_note[0] - pos_node[0])**2 + (pos_note[1] - pos_node[1])**2)
        # hdaSettings.consoleLog(f"note: {note['text']}, node: {node['name']}, distance: {distance}", type=hda.TYPES.DEBUG)
        # hdaSettings.consoleLog(f"pos_note: {note['position']}, pos_size: {note['size']}", type=hda.TYPES.DEBUG)
        # hdaSettings.consoleLog(f"pos_node: {pos_node}", type=hda.TYPES.DEBUG)
        # hdaSettings.consoleLog(f"pos_note: {pos_note}", type=hda.TYPES.DEBUG)
        # hdaSettings.consoleLog(f"distance: {distance}", type=hda.TYPES.DEBUG)
        # if note is above the node, ignore it        
        # hdaSettings.consoleLog(f"note_bottom: {note_bottom}", type=hda.TYPES.DEBUG)
        if pos_node[1] < note["position"][1]:
            hdaSettings.consoleLog(f"note is above the node", type=hda.TYPES.DEBUG)
            return None        
        # if node is further from distance threshold, return
        if distance > hdaSettings.stickyNotesDistanceThreshold:
            hdaSettings.consoleLog(f"distance is greater than threshold", type=hda.TYPES.DEBUG)
            return None
        return distance

    def assign_sticky_notes(self, sticky_notes):
        # loop on sticky notes
        for note in sticky_notes:
            # find distance to each node
            for node in self.gNodes.values():
                distance = self.get_distance(node, note)
                if distance is not None:
                    if note["distance"] is None or distance < note["distance"]:
                        note["distance"] = distance
                        note["closest_node"] = node.getPath()
            # assign closest node to each note
            if note["closest_node"] is not None:
                updateGNode = self.gNodes.get(note["closest_node"])
                updateGNode.update(note=note["text"])                

    def get_root_nodes(self, return_names=False):
        """
        Returns the root nodes in the graph.
        A root node is defined as a node whose path never appears as a target in any edge.
        
        Parameters:
            return_names (bool): If True, returns the names of the root nodes.
                                 If False (default), returns the paths of the root nodes.
        """
        # Collect all targets from edges
        targets = {edge[1] for edge in self.edges}
        # Root nodes are those not in the targets set.
        root_nodes = [node_path for node_path in self.gNodes if node_path not in targets]
        
        if return_names:
            return [self.gNodes[node_path].getName() for node_path in root_nodes]
        else:
            return root_nodes
        
    def traverse_direct_from_edges(self, start_node_path):
        """
            Traverse direct will traverse from a node downstream using edges as long as there is exactly one edge.
            It records the node names (not paths) in the same order they are traversed.
        """
        traversed = []
        miNode = None
        current_path = start_node_path
        # print("traversing from:", current_path)
        while current_path in self.gNodes:
            current_node = self.gNodes[current_path]
            traversed.append(current_node.getPath())
            # if node has multiple inputs, break the loop
            if len(current_node.getInputs()) > 1:
                # but if its a re-entry root node, then continue
                if len(traversed) > 1:
                    self.hdaSettings.consoleLogDebug(f"NodeGraph.traverse_direct_from_edges: Multiple Inputs {current_node.getPath()}")
                    miNode = current_node.getPath()
                    break
            # Get all edges starting from the current node
            valid_edges = [edge for edge in self.edges if edge[0] == current_path]
            if len(valid_edges) == 1: # TODO scenario with 2 edges going to same node (jointdeform)
                current_path = valid_edges[0][1]
            else:
                break            
        return traversed, miNode

    # UPDATED, may need further updates
    def add_reference_node(self, node_path):
        """
            TODO: REVIEW THIS LOGIC
            create a reference copy of a node.
            The reference node will have the same type as the original, but empty inputs/outputs, WHY??
            and will include an attribute "reference" storing the original node's path.
            The reference node's key is derived from the original node path using an "@" sign
            followed by an incremented index to ensure uniqueness.
        """
        i = 1
        # Get a unique ID for the reference node
        while True:
            ref_key = f"{node_path}@{i}"
            if ref_key not in self.gNodes:
                break
            if i>10:
                print(f"ERROR: too many references!! { ref_key}")
                break
            i += 1
        original = self.gNodes[node_path]
        refGNode = original.copy() # GNode(original)
        refGNode.update(
            path=ref_key,
            name=f"{original.getName()}@{i}",
            # inputs=[], outputs=[],
            reference=node_path
            )
        self.gNodes[ref_key] = refGNode
        return self.gNodes[ref_key]

# =============================
# ========= Graph DECOMPOSITION
# =============================

    def break_nodes_with_multiple_outputs(self):
        """
            New functionality: For any node with more than one valid output, create a separate reference
            node for each output (using the existing add_reference_node function),
            disconnect the edge from the original node to that output using delete_edge(),
            and add an edge from the reference node to that output using add_edge().
        """
        for node_path, gNode in list(self.gNodes.items()):
            valid_outputs = [o for o in gNode.getOutputs() if o]
            if len(valid_outputs) > 1:
                for out_path in valid_outputs:
                    # Create a reference node for the original node.
                    ref_node = self.add_reference_node(node_path)
                    # Delete the edge from the original node to this output using the existing function.
                    self.delete_edge(node_path, out_path)
                    # Retrieve the destination node and add a new edge from the reference node to the output.
                    to_node = self.get_node(out_path)
                    if to_node:
                        self.add_edge(ref_node.getPath(), to_node.getPath())
                        self.set_node_above(ref_node.getPath(), out_path)
                # Optionally remove the moved outputs from the original node's output list.
                # node_data["outputs"] = [o for o in node_data["outputs"] if o not in valid_outputs]
        # Save Graph
        self.save_network("bmo", pretty=True)

    def break_nodes_with_multiple_inputs(self):
        """
            iterate over all nodes, 
            if any node has multiple edges coming in (multiple inputs?)
                break these edges            
        """
        for node_path, gNode in list(self.gNodes.items()):
            valid_inputs = [i for i in gNode.getInputs() if i]
            if len(valid_inputs) > 1:
                # find all edges where this node is the destination, and delete them
                for edge in list(self.edges):
                    if edge[1] == node_path:
                        self.edges.remove(edge)
        # Save Graph
        self.save_network("bmi", pretty=True)

    def break_graph_in_branches(self):
        """
        Breaks the graph into branches. A branch is defined as a list of node paths obtained by direct traversal
        starting from a root node (i.e. a node whose path never appears as a target in any edge).
        
        Returns:
            A list of branches; where each branch is a list of node paths.
        """
        self.branches = []
        # Get root nodes (using paths, not names)
        root_nodes = self.get_root_nodes(return_names=False)
        for node_path in root_nodes:
            branch, miNode = self.traverse_direct_from_edges(node_path)
            if miNode and miNode not in root_nodes:
                root_nodes.append(miNode)
                self.hdaSettings.consoleLogDebug(f"NodeGraph.break_graph_in_branches: minode added {miNode}")
            # if the branch has more than one node, add it to the list of branches
            if len(branch) > 1:
                self.branches.append(branch)
            if len(self.branches) > 1000: # TODO do better cyclic graph detection
                self.hdaSettings.consoleLogWarning(f"***** NodeGraph.break_graph_in_branches: Possible Cyclic Graph, 1000 branches?")
                break
        return self.branches

    def compose(self, nodeList):
        self.hdaSettings.consoleLogDebug(f"NodeGraph.compose: {self.parent_path}")
        self.build_graph_from_node_list(nodeList)
        nodePath = self.parent_path
        self.findGraphLoops()
        self.get_begin_end_nodes()
        # Build graph for each group
        graphList = []
        for i, graphLoop in enumerate(self.graphLoops):
            self.hdaSettings.consoleLogDebug(f"NodeGraph.compose loop: {self.parent_path} {i}")
            g = NodeGraph(nodePath, nodePath)
            g.buildLoopGraphFromNodes(self, graphLoop, i)
            g.break_nodes_with_multiple_outputs()
            if not self.hdaSettings.noBMI:
                g.break_nodes_with_multiple_inputs()
            g.break_graph_in_branches()
            graphList.append(g)

        # Build Graph for No Loops Network
        self.hdaSettings.consoleLogDebug(f"NodeGraph.compose NoLoopNet: {self.parent_path}")
        g = NodeGraph(nodePath, nodePath)
        g.buildGraphFromNodes(self, self.noLoopNodes, self.begin_end_nodes)
        g.break_nodes_with_multiple_outputs()
        if not self.hdaSettings.noBMI:
            g.break_nodes_with_multiple_inputs()
        g.break_graph_in_branches()
        graphList.append(g)

        # Extract Sticky Notes
        noteList = hnm.HoudiniNodeManager.extract_sticky_notes(self.parent_path)
        # loop on graphs and assign notes to nodes
        for g in graphList:
            noteListCopy = noteList.copy()
            g.assign_sticky_notes(noteListCopy)
        self.graphList = graphList
        return graphList

    def save_network(self, file_type, pretty=False, forceSave=False):
        """
        Saves the node network to a file in JSON format.
        Later, this file can be loaded by NetworkX.
        """

        def to_dict():
            # Create a shallow copy of __dict__ excluding non-data attributes.
            data = {k: v for k, v in self.__dict__.items() if k != "hdaSettings"}
            # Dynamically convert nodes value using their own toDict method.
            if "gNodes" in data:
                data["gNodes"] = { key: node.toDict() for key, node in data["gNodes"].items() }
            return data
                
        if self.hdaSettings.exportDebugFiles or forceSave:
            nodeName = self.parent_path
            nodeName = hda.HDAManager().sanitize_string(nodeName)
            loop = f"-loop-{self.loop_id}" if self.loop_id is not None else ""
            jsonFilename = os.path.join(self.hdaSettings.projectLocation, nodeName + "-" + file_type + "-" + loop + ".json")        

            data = to_dict()
            with open(jsonFilename, 'w') as f:
                if pretty:
                    json.dump(data, f, indent=4, default=serialize_value)
                else:
                    json.dump(data, f, default=serialize_value)
                self.hdaSettings.consoleLog(f"=========== NodeGraph.save_network Saved to {jsonFilename}", type=hda.TYPES.DEBUG)

# =============================
# ========= HANDLE GRAPH LOOPS
# =============================

    def get_end_loops(self):
        # get a list of all nodes with type="block_end"
        end_nodes = [gNode.getPath() for gNode in self.gNodes.values() if gNode.getType() == "block_end"]
        return end_nodes

    def get_begin_nodes(self, end_node):
        # get all nodes with type block_begin
        begin_nodes = [gNode.getPath() for gNode in self.gNodes.values() if gNode.getType() == "block_begin"]
        # filter them by blockpath param = ../end_node
        matched_nodes = []
        # print("end_node:", end_node)
        for begin_node in begin_nodes:
            # TODO: should we get the block path from outside hou?
            block_path = hou.node(begin_node).parm("blockpath").eval()
            # print("block_path:", block_path)
            if block_path == "../"+end_node.split("/")[-1]:
                matched_nodes.append(begin_node)
        return matched_nodes
    
    def get_begin_end_nodes(self):
        self.begin_end_nodes = []
        # if node type is block_begin or block_end, add it to the list
        for gNode in self.gNodes.values():
            if gNode.getType() in ["block_begin", "block_end"]:
                self.begin_end_nodes.append(gNode.getPath())    
        return self.begin_end_nodes

    def getLoopNodes(self, begin_nodes, end_node):
        loopNodes = []
        # For each node in the graph, traverse upstream through its inputs.
        for node_path in self.gNodes:
            visited = set()
            stack = [node_path]
            is_loop_node = False
            while stack:
                current_path = stack.pop()
                if current_path in visited:
                    continue
                visited.add(current_path)
                # If we've reached one of the begin nodes, mark this as a loop node.
                if current_path in begin_nodes:
                    is_loop_node = True
                    break
                # Stop if the end_node is encountered
                if current_path == end_node:
                    is_loop_node = False
                    break
                # Add all valid input nodes to the stack.
                # self.hdaSettings.consoleLogDebug(f"============ NodeGraph.getLoopNodes: {current_path}")
                gNode = self.gNodes[current_path]
                for inp in gNode.getInputs():
                    if inp:
                        stack.append(inp)
            if is_loop_node:
                loopNodes.append(node_path)
                gNode = self.gNodes[node_path]
                gNode.update(in_loop=True, loop_id=end_node)
        # add the end node to the loop nodes
        gNode = self.gNodes[end_node]
        gNode.update(in_loop=True, loop_id=end_node)
        loopNodes.append(end_node)
        return loopNodes

    def findGraphLoops(self):
        # find all nodes with type endLoop
        end_nodes = self.get_end_loops()
        # For each end loop, extract Loop
        self.graphLoops = []
        for end_node in end_nodes:
            # find foreach nodes
            begin_nodes = self.get_begin_nodes(end_node)
            # find all nodes that are connected upstream to foreach nodes
            loopNodes = self.getLoopNodes(begin_nodes,end_node)
            self.graphLoops.append(loopNodes)
        self.noLoopNodes = [gNode.getPath() for gNode in self.gNodes.values() if not gNode.inLoop()]

    def buildLoopGraphFromNodes(self, graph, nodes,i):
        """
        Build a graph from a list of nodes.
        This is a self contained graph, not taking in consideration edges going out or coming in the network.
        Because tese edges will be handled from outside
        """
        self.gNodes = {}
        self.edges = []
        nameListEnd = []
        nameListBegin = []
        self.is_loop_graph = True
        self.loop_id = i
        self.loop_end = ""
        for nodePath in nodes:
            # get copy of node from original graph
            gNode = graph.get_node(nodePath).copy()            
            self.gNodes[nodePath] = gNode
            if gNode.getType() == "block_end":
                nameListEnd.append(gNode.getName())
                self.loop_end = nodePath
            if gNode.getType() == "block_begin":
                nameListBegin.append(gNode.getName())
            # loop on node inputs only, if input is coming from outside the node list then ignore it
            for inp in gNode.getInputs():
                if inp in nodes:
                    self.add_edge(inp, gNode.getPath())
                    # self.edges.append((inp, gNode.getPath()))
        ### pick a loop name from being/end node names, or set it to Loop_i
        graphName = ""
        for node in nameListEnd:
            if not node.lower().startswith("foreach_end"):
                idx = node.lower().find("_end")
                if idx != -1:
                    graphName = node[:idx]
                else:
                    graphName = node
                break
        if graphName == "":
            for node in nameListBegin:
                if not node.lower().startswith("foreach_begin"):
                    idx = node.lower().find("_begin")
                    if idx != -1:
                        graphName = node[:idx]
                    else:
                        graphName = node
                    break
        if graphName == "":            
            graphName = "Loop_" + str(i+1)
        self.name = graphName
        self.begin_nodes = nameListBegin
        # Save Graph
        self.save_network("loop", pretty=True)
        return self
            
    def buildGraphFromNodes(self, graph, nodes, begin_end_nodes):
        """
        Build a graph from a list of nodes.
        """
        self.name = graph.name
        # hda.HDAManager().consoleLogDebug(f"NodeGraph.buildGraphFromNodes: {self.name} {nodes}")    
        # hda.HDAManager().consoleLogDebug(f"NodeGraph.buildGraphFromNodes: {self.name} {begin_end_nodes}")    
        all_nodes = nodes + begin_end_nodes
        hda.HDAManager().consoleLogDebug(f"NodeGraph.buildGraphFromNodes: {self.name} {len(all_nodes)}")
        for nodeName in all_nodes:
            # get copy of node from original graph
            gNode = graph.get_node(nodeName).copy()
            self.gNodes[nodeName] = gNode
            # loop on node inputs only, if input is coming from outside the node list then ignore it
            for inp in gNode.getInputs():
                if inp in all_nodes and gNode.getType() != "block_end":
                    self.add_edge(inp, gNode.getPath())
                    # self.edges.append((inp, gNode.getPath()))
            for outp in gNode.getOutputs():
                if outp in all_nodes and gNode.getType() != "block_begin":
                    self.add_edge(gNode.getPath(), outp)
                    # self.edges.append((gNode.getPath(), outp))
        # Save Graph
        self.save_network("original", pretty=True)
        return self

# =========================
# ========= RENDERING Graph 
# =========================

    def getNodesRenderData(self,isLoop):
        # loop on all nodes and get their render data
        nodesRenderData = []
        for nodePath in self.gNodes:
            # TODO: check this logic: if we have multiple nodes with reference, keep only the original one
            if "@" in nodePath:
                continue
            # this condition happens in case of loop graph only
            if nodePath == self.loop_end: # skip loop end node
                continue
            gNode = self.get_node(nodePath)
            if "houdini_2_chat" in gNode.getType():
                if not self.hdaSettings.exportThisNode:
                    continue
            if not isLoop and gNode.getType() in ["block_begin", "block_end"]:
                continue
            dict = gNode.getRenderData()
            if dict["properties"]:
                for prop in dict["properties"].values():                    
                    prop["full_value"] = self.renderParmValue(prop)
            nodesRenderData.append(dict)     
        self.save_network("nodes", pretty=True)       
        return nodesRenderData

    def renderParmValue(self, parm):        
        parmComment = ""
        comments = []
        val = parm["actual_value"]
        if parm["expression"]:
            comments.append("Expression: " + parm["expression"])
        if parm["reference"]: # TODO: check if reference is same as expression            
            comments.append("Reference to Node: " + parm["reference"])
        if parm["unexpanded"]:
            comments.append("String Formula: " + parm["unexpanded"])
        if comments:
            parmComment = ",".join(comments)
        if parmComment:
            parmComment =  f"# ({parmComment})"
        # check parm type, if it is a string, add quotes
        quotes = False
        if parm["type"] not in ["parmTemplateType.Float", "parmTemplateType.Int" ]:
            quotes = True
        if quotes:
            val = f"\"{val}\""
        return f"{val}, {parmComment}"

    def getLoopRenderData(self):
        nodePath = self.loop_end
        gNode = self.get_node(nodePath)
        props = gNode.getHProps()
        loop_data = {
            "loopName": self.name,
            "beginNodes": ", ".join(self.begin_nodes),
            "endNode": "\"" + gNode.getName().split('/')[-1].split('@')[0] + "\"," ,
            "iterationMethod": self.renderParmValue(props["itermethod"]),
            "iterationMethodVal": props["itermethod"]["value"],
            "gatherMethod": self.renderParmValue(props["method"]),
            "startValue": self.renderParmValue(props["startvalue"]),
            "incrementValue": self.renderParmValue(props["increment"]),
            "iterations": self.renderParmValue(props["iterations"]),
            "pieceElement": self.renderParmValue(props["class"]),
            # TODO: the below will not show parm value if it is disabled
            "pieceAttribute": self.renderParmValue(props["attrib"]) if props["useattrib"]["value"] == 1 else None,
            "maxIterations": self.renderParmValue(props["maxiter"]) if props["usemaxiter"]["value"] == 1 else None,
            "singlePass": self.renderParmValue(props["singlepass"]) if props["dosinglepass"]["value"] == 1 else None,
            "stopCondition": self.renderParmValue(props["stopcondition"]),
            "stopConditionVal": props["stopcondition"]["actual_value"],
        }
        return loop_data

    def getBranchRenderData(self):
        # Prepare branch data using the graph.
        branchesRenderData = []
        for branch in self.branches:
            branchNodes = []
            for branchNode in branch:
                gNode = self.get_node(branchNode)
                branchNodes.append({
                    "name": gNode.getName().split('@')[0],
                    "type": gNode.getType()
                })
            branchesRenderData.append(branchNodes)
        return branchesRenderData    
        
def serialize_value(val):
    if isinstance(val, hou.Ramp):
        try:
            interp = val.interpolation()
        except AttributeError:
            interp = None
        points = []
        try:
            num_points = val.numPoints()
            for i in range(num_points):
                pt = val.point(i)
                points.append({
                    "position": pt.position(),
                    "value": pt.value(),
                    "tangentIn": pt.tangentIn(),
                    "tangentOut": pt.tangentOut()
                })
        except AttributeError:
            points = str(val)
        return {"interpolation": interp, "points": points}
    elif isinstance(val, (hou.Vector2, hou.Vector3, hou.Vector4)):
        return list(val)
    elif isinstance(val, tuple):
        return list(val)
    elif isinstance(val, (int, float, str, bool)) or val is None:
        return val
    return str(val)