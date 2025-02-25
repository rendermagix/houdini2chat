from platform import node
import hou
import fnmatch
import hda_manager as hda

class HoudiniNodeManager:
    def __init__(self, parent_node):
        self.parent_node = parent_node

    @staticmethod
    def get_node_children(node_path):
        hdaSettings = hda.HDAManager()
        node = hou.node(node_path)
        nodeList = []
        for child in node.children():
            nodeList.append(child.path())
        hdaSettings.consoleLog(f"========= HoudiniNodeManager.get_node_children: Found {len(nodeList)} nodes. ", hda.TYPES.DEBUG)            
        return nodeList

    @staticmethod
    def get_nodes_not_in_network_boxes(node_path):
        hdaSettings = hda.HDAManager()
        node = hou.node(node_path)
        nodeList = []
        for child in node.children():
            if child.parentNetworkBox() is None:
                nodeList.append(child.path())
        hdaSettings.consoleLog(f"========= HoudiniNodeManager.get_nodes_not_in_network_boxes: Found {len(nodeList)} nodes. ", hda.TYPES.DEBUG)            
        return nodeList
        
    @staticmethod
    def get_root_network_boxes(node_path):
        hdaSettings = hda.HDAManager()        
        node = hou.node(node_path)
        rootNetworkBoxes = []
        for netbox in node.networkBoxes():   
            if netbox.parentNetworkBox() is None:
                rootNetworkBoxes.append(netbox)
            # hdaSettings.consoleLog(f"Nodes in Network Box: {netbox.comment()} {len(netbox.nodes())}", hda.TYPES.DEBUG)
        hdaSettings.consoleLog(f"========= HoudiniNodeManager.get_root_network_boxes: Root Network Boxes: {len(rootNetworkBoxes)}", hda.TYPES.DEBUG)
        # for netbox in rootNetworkBoxes:
        #     hda.HDAManager().consoleLog(f"Root Network Box: {netbox.comment()}", hda.TYPES.DEBUG)
        return rootNetworkBoxes

    @staticmethod
    def filter_by_network_boxes(node_path, patterns_str, nodeList):
        hdaSettings = hda.HDAManager()
        hdaSettings.consoleLog(f"========= HoudiniNodeManager.filter_by_network_boxes: Patterns: {hdaSettings.networkBoxFilter}", hda.TYPES.DEBUG)

        all_nodes = [] # all nodes in matching network boxes
        matched_nodes = [] # nodes matching nodeList
        # Split the pattern string into a list of patterns.
        patterns = patterns_str.split()
        parent = hou.node(node_path)
        if not parent:
            return None
        # Loop on all network boxes inside node_path
        for netbox in parent.networkBoxes():
            title = netbox.comment()
            # Loop on all user provided patterns
            for pattern in patterns:
                if fnmatch.fnmatch(title, pattern):
                    # when matched, capture all the node paths
                    for node in netbox.nodes():
                        all_nodes.append(node.path())      
        # hdaSettings.consoleLog(f"========= HoudiniNodeManager.filter_by_network_boxes: All Nodes: {len(all_nodes)}", hda.TYPES.DEBUG)

        # capture nodes matching nodeList
        for node in nodeList:
            if node in all_nodes:
                matched_nodes.append(node)            
        hdaSettings.consoleLog(f"========= HoudiniNodeManager.filter_by_network_boxes: Matched Nodes: {len(matched_nodes)}", hda.TYPES.DEBUG)
        return matched_nodes

    @staticmethod    
    def get_network_box_children(netbox):
        nodeList = []
        for node in netbox.nodes():
            nodeList.append(node.path())
        return nodeList
    
    @staticmethod
    def get_parm_value(parm):
        parmTemplate = parm.parmTemplate()
        parm_type = parmTemplate.type() 
        value = parm.eval()
        actual_value = value
        unexpanded = None
        reference = None
        expression = None                      
        if parm_type == hou.parmTemplateType.Menu:
            menu_labels = parm.menuLabels()
            actual_value = menu_labels[value]
        # Check if the parameter is a reference expression.
        ref_expr = parm.getReferencedParm()
        if ref_expr != parm:
            reference = ref_expr.path()
        try:
            unexp = parm.unexpandedString()
            if unexp != actual_value:
                unexpanded = unexp
        except hou.OperationFailed:
            unexpanded = None
        try:
            expr = parm.expression()
            if expr:
                expression = expr
        except hou.OperationFailed:
            expression = None                
        return value, actual_value, unexpanded, reference, expression
    
    @staticmethod
    def extract_node_properties(node_path):
        node = hou.node(node_path)
        # Check if node is valid and supports parms() method.
        if not node or not hasattr(node, "parms"):
            hda.HDAManager().consoleLogWarning(f"========= HoudiniNodeManager.extract_node_properties: {node_path} is not a valid node or does not support parms() method.")
            return {}        
        properties = {}
        for parm in node.parms():
            # skip parameter if it is a multi parameter instance (maybe keep it in some cases, TODO)
            isMultiPI = parm.isMultiParmInstance()
            if isMultiPI:
                continue            
            # check if this parm is part of a tuple
            parmTuple = parm.tuple()
            hasParmTuple = parmTuple and parm.name() != parmTuple.name()
            key = ""
            label = ""
            value = ""
            actual_value = ""
            reference = None  
            unexpanded = None      
            changed = not parm.isAtDefault()
            userCreated = parm.isSpare()
            # TO BE DELETED
            cIndex = parm.componentIndex()
            isMultiPI = parm.isMultiParmInstance()
            isMultiPP = parm.isMultiParmParent()
            multiPP = parm.parentMultiParm()
            ptype = parm.parmTemplate().type()
            pnaming = parm.parmTemplate().namingScheme()
            
            # if this is different from the parm name, then it is a tuple
            if hasParmTuple:
                # use parm tuple name
                key = parmTuple.name()
                label = parmTuple.description()
                value = parmTuple.eval()
                actual_value = value
                changed = not parmTuple.isAtDefault()
                pValue, pActual_value, pUnexpanded, pReference, pExpression = HoudiniNodeManager.get_parm_value(parm)
                # need to check if properties[key] exists, 
                # if yes, then get these values: unexpanded, reference, and update them
                prop = properties.get(key)
                if prop and prop["unexpanded"]:
                    unexpanded = f"{prop['unexpanded']}, {pUnexpanded}" if pUnexpanded else prop["unexpanded"]
                else:
                    unexpanded = pUnexpanded
                if prop and prop["reference"]:                    
                    reference = f"{prop['reference']}, {pReference}" if pReference else prop["reference"]
                else:
                    reference = pReference                    
                if prop and prop["expression"]:                    
                    expression = f"{prop['expression']}, {pExpression}" if pExpression else prop["expression"]
                else:
                    expression = pExpression                    
            else:
                # use parm name
                key = parm.name()
                label = parm.description()
                # for Menu parameters, get the actual value from the menu labels
                value, actual_value, unexpanded, reference, expression = HoudiniNodeManager.get_parm_value(parm)
                
            label = hda.HDAManager().sanitize_string(label).lower()
            # a parameter is changed if a value is not default, or has a reference or expression or stringExpr
            if reference or unexpanded or expression:
                changed = True
            # set the properties
            properties[key] = {
                "label": label,
                "value": value,
                "actual_value": actual_value,
                "changed": changed,
                "user_created": userCreated,
                "reference": reference,
                "unexpanded": unexpanded,
                "expression": expression,
                # TO BE DELETED - Debug Only
                "isTuple": hasParmTuple,
                "component_index": cIndex,
                "is_multi_parm_instance": isMultiPI,
                "is_multi_parm_parent": isMultiPP,
                "multi_parm_parent": multiPP,
                "type": ptype,
                "naming_scheme": pnaming                
            }                        
        return properties
    
    @staticmethod
    def extract_node_info(node_path):
        node = hou.node(node_path)
        if not node:
            return None
        info = {
            "name": node.name(),
            "type": node.type().name(),
            "path": node.path(),
        }
        return info

    def extract_network_boxes(self):
        network_boxes_info = []
        for netbox in self.parent_node.iterNetworkBoxes():
            network_boxes_info.append({
                "comment": netbox.comment(),
                "position": list(netbox.position()),
                "size": list(netbox.size()),
                "nodes": [node.path() for node in netbox.nodes()]
            })
        return network_boxes_info

    @staticmethod
    def extract_sticky_notes(node_path):
        parent_node = hou.node(node_path)
        noteList = []
        for note in parent_node.stickyNotes():
            noteList.append({
                "text": note.text(),
                "position": list(note.position()),
                "size": list(note.size()),
                "closest_node": None,
                "distance": None

            })
        return noteList
                            
    def zold_extract_network_box_info(self, netbox):
        return {
            "comment": netbox.comment(),
            "position": list(netbox.position()),
            "size": list(netbox.size()),
            "nodes": [node.path() for node in netbox.nodes()]
        }

    def zold_extract_sticky_note_info(self, note):
        return {
            "text": note.text(),
            "position": list(note.position()),
            "size": list(note.size())
        }                