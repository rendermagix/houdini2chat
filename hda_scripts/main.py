# External Libraries
import datetime

# Internal Libraries
import houdini_node_manager as hnm
import node_graph as ng
import render_manager as rm
import hda_manager as hdam
import extract_functions as xf

hda = None

# ========================================
# ========= RENDERING OUTPUT =============
# ========================================
   
def renderNetworkUnit(graph):
    props = {
        "networkName": graph.name
    }
    branchRenderData = graph.getBranchRenderData()
    nodeRenderData = graph.getNodesRenderData()        
    renderMan = rm.RenderManager() 
    rendered_nodes_text = renderMan.render_nodes(nodeRenderData)
    # Load the network unit template.
    template = renderMan.load_template("network_unit.py.j2")    
    # Render the full unit, now passing rendered_nodes as a variable.
    rendered_text = template.render(props=props, branches=branchRenderData, rendered_nodes=rendered_nodes_text)
    return rendered_text

def renderLoopUnit(graph):
    # get node data
    nodesRenderData = graph.getNodesRenderData() # get all nodes data
    loopRenderData = graph.getLoopRenderData() # get loop data    
    branchRenderData = graph.getBranchRenderData()
                    
    renderMan = rm.RenderManager()
    rendered_nodes_text = renderMan.render_nodes(nodesRenderData)
    template = renderMan.load_template("loop_unit.py.j2")
    rendered_text = template.render(props=loopRenderData, branches=branchRenderData, 
                                    rendered_nodes=rendered_nodes_text)                
    return rendered_text

def renderNodePathNetwork(nodeName, metadata, graphList, single=False, saveToFile=True):
    rendered_text = ""    
    template_data = {
        "nodeName": nodeName,
        "header": hda.header,
        "footer": hda.footer,
        "single": single
    }
    hda.consoleLog(f"========= renderNodePathNetwork for: -> {nodeName}, single= {single}", hdam.TYPES.DEBUG)
    # loop on graphList and render each graph
    for graph in graphList:                
        # graph.save_network("debug", pretty=True)
        if graph.is_loop_graph: # render loop graph
            rendered_text += renderLoopUnit(graph)
        else:  # render normal graph
            rendered_text += renderNetworkUnit(graph)            
            
    # Load the network unit template.
    renderMan = rm.RenderManager() # pun intended!
    template = renderMan.load_template("network_full.py.j2")
    network_text = template.render(props=template_data, graphs=rendered_text )
    if saveToFile:
        # Save the rendered output using our helper.    
        renderMan.save_rendered_output(network_text, nodeName, metadata)
    return network_text

def renderNodePathNetworkCombined(nodeName, nodeData, metadata, saveToFile=True):
    template_data = {
        "nodeName": nodeName,
        "header": hda.header,
        "footer": hda.footer,
        "single": True
    }
    
    hda.consoleLog(f"======= renderNodePathNetworkCombined for: -> {nodeName}", hdam.TYPES.DEBUG)
            
    # Load the network Full template.
    renderMan = rm.RenderManager() # pun intended!
    template = renderMan.load_template("network_full.py.j2")
    network_text = template.render(props=template_data, graphs=nodeData )
    if saveToFile:
        renderMan.save_rendered_output(network_text, nodeName, metadata)
    return network_text
            
# ========================================
# ========= BUILDING NETWORK =============
# ========================================

def getMetadata(nodePath, netbox, type="nodePath"):
    metadata = {}
    if type == "nodePath":
        metadata["render.type"] = "nodePath"
    elif type == "networkBox":
        metadata["render.type"] = "networkBox"
    else:
        metadata["render.type"] = "default"

    if nodePath:   
        # TODO: do we really need to get that info from Houdini?
        nodeInfo = hnm.HoudiniNodeManager.extract_node_info(nodePath)
        metadata["node.name"] = nodeInfo["name"]
        metadata["node.path"] = nodePath
    if netbox:
        metadata["netbox.name"] = netbox.name()
        metadata["netbox.title"] = netbox.comment()
    return metadata

def BuildNodePathNetworkNoBoxes(nodePath):
    networkText = None # A list of Rendered Networks
    # create a graphlist ignoring network boxes
    hda.consoleLogDebug(f"======= BuildNodePathNetworkNoBoxes.plain.network: {nodePath} ")
    # Build Main Graph
    nodeList = hnm.HoudiniNodeManager.get_node_children(nodePath)
    # Filter by Network Boxes
    if hda.filterNetworkBoxes and hda.networkBoxFilter:
        nodeList = hnm.HoudiniNodeManager.filter_by_network_boxes(nodePath, hda.networkBoxFilter, nodeList)
    if not len(nodeList):
        hda.consoleLogDebug(f"======= BuildNodePathNetworkNoBoxes.ZERO nodes in: {nodePath} ")
        return None
    hda.consoleLogDebug(f"======= BuildNodePathNetworkNoBoxes.Compose Graph for: -> {nodePath} ")
    graph = ng.NodeGraph(nodePath, nodePath, nodeList)
    graphList = graph.graphList
    saveToFile = hda.breakByNodePath # Create a file per node path
    single = True if saveToFile else False
    metadata = getMetadata(nodePath, None, "nodePath")
    networkText = renderNodePathNetwork(nodePath, metadata, graphList, single, saveToFile)
    return networkText

def BuildNodePathNetworkWithBoxes(nodePath, rootNetworkBoxes):
    nodeNetworks = [] # A list of Rendered Networks
    # for each network box
    for netbox in rootNetworkBoxes:
        # set name and filename
        gName = netbox.comment()
        gFileName = netbox.name() + "_" + netbox.comment()
        # get network box children
        nodeList = hnm.HoudiniNodeManager.get_network_box_children(netbox)
        # Filter by Network Boxes
        if hda.filterNetworkBoxes and hda.networkBoxFilter:
            nodeList = hnm.HoudiniNodeManager.filter_by_network_boxes(nodePath, hda.networkBoxFilter, nodeList)
        # skip empty network boxes
        if not len(nodeList):
            hda.consoleLogDebug(f"======= BuildNodePathNetworkWithBoxes.NetBoxLoop - ZERO nodes in: {gFileName}")
            continue
        hda.consoleLogDebug(f"======= BuildNodePathNetworkWithBoxes.NetBoxLoop processing {gFileName}")
        graph = ng.NodeGraph(nodePath, nodePath, nodeList)
        graphList = graph.graphList
        metadata = getMetadata(nodePath, netbox, "networkBox")
        saveToFile = hda.breakByNetworkBox # Create a file per network box
        single = True if saveToFile else False # single will let the template save headers and footers
        networkText = renderNodePathNetwork(nodePath, metadata, graphList, single, saveToFile)
        nodeNetworks.append(networkText)
    # Get Nodes outside network boxes
    if hda.includeNodesOutsideNetworkBox:
        # if there are nodes outside the network boxes, process them
        nodeList = hnm.HoudiniNodeManager.get_nodes_not_in_network_boxes(nodePath)
        # Filter by Network Boxes
        if hda.filterNetworkBoxes and hda.networkBoxFilter:
            nodeList = hnm.HoudiniNodeManager.filter_by_network_boxes(nodePath, hda.networkBoxFilter, nodeList)
        # skip if no nodes outside netboxes
        if not len(nodeList):
            hda.consoleLog(f"======= BuildNodePathNetworkWithBoxes.OutsideNetwork ZERO nodes (after Netbox Filter) in: {nodePath}", hdam.TYPES.DEBUG)
        else:
            # Duplicate code from below - refactor
            hda.consoleLog(f"======= BuildNodePathNetworkWithBoxes.OutsideNetwork Compose Graph for: -> {nodePath}", hdam.TYPES.DEBUG)
            graph = ng.NodeGraph(nodePath, nodePath, nodeList)
            graphList = graph.graphList
            metadata = getMetadata(nodePath, None, "nodePath")
            # these are never saved alone anyway
            single = False
            networkText = renderNodePathNetwork(nodePath, metadata, graphList, single, False)
            nodeNetworks.append(networkText)
    # Save Network Boxes and Free Nodes in one File if breakByNodePath
    if nodeNetworks:
        # break by path and not break by network - # TODO: this setting is really confusing! 
        if hda.breakByNodePath and not hda.breakByNetworkBox:
            nodeNetworksText = "".join(nodeNetworks)
            hda.consoleLog(f"======= BuildNodePathNetworkWithBoxes.NetBox Combined for: -> {nodePath}", hdam.TYPES.DEBUG)
            metadata = getMetadata(nodePath, None, "nodePath")
            renderNodePathNetworkCombined(nodePath, nodeNetworksText, metadata, True)
    return nodeNetworks

def buildNodePathNetwork(nodePath):
    nodeNetworks = [] # A list of GraphList Networks
    # Get Root Network Boxes if needed
    rootNetworkBoxes = []
    hda.consoleLogDebug("======= buildNodePathNetwork")    
    if hda.groupByNetworkBoxL1:
        rootNetworkBoxes = hnm.HoudiniNodeManager.get_root_network_boxes(nodePath)
    
    # if root network boxes are found and needed
    if hda.groupByNetworkBoxL1 and rootNetworkBoxes:
        nodeNetworks = BuildNodePathNetworkWithBoxes(nodePath, rootNetworkBoxes)
    else: # No Network Boxes Exist, or, groupByNetworkBoxL1 is False
        networkText = BuildNodePathNetworkNoBoxes(nodePath)
        nodeNetworks.append(networkText)
    # Return nodeNetworks
    return nodeNetworks
                    
def extractFromNodes():
    hda.consoleLog("===== extractFromNodes", hdam.TYPES.DEBUG)
    if hda.nodeErrors:
        for error in hda.nodeErrors:
            hda.consoleLogError(error)
        return
    nodeList = hda.nodePaths
    nodesText = []
    if nodeList:
        hda.cleanFolder() # deleting all files in the project location
        for node_path in nodeList:
            hda.consoleLog(f"===== extractFromNodes.processing: {node_path}", hdam.TYPES.DEBUG)
            networkTextList = buildNodePathNetwork(node_path)            
            nodesText.append("\n".join(networkTextList))
        # if not file per node path, save all nodes in one file
        if not hda.breakByNodePath:
            hda.consoleLog(f"===== extractFromNodes.saving all nodes", hdam.TYPES.DEBUG)
            metadata = getMetadata("", None, "default")
            allNodesText = "\n".join(nodesText)
            renderNodePathNetworkCombined(node_path, allNodesText, metadata, True)
            
    else:
        hda.consoleLogWarning("No valid nodes to extract.")
     
def main():
    """
    Main function that extracts information from the nodes specified in the HDA.
    """
    global hda
    hda = hdam.HDAManager() # necessary to refresh settings

    # keeping if/else instead of match/case, to stay compatible with 3.7 (Houdini 19)
    if hda.actionSelected != 0:
        startTime = datetime.datetime.now()
        hda.consoleLogInfo("=== Houdini2Chat -> Starting @ "  + startTime.strftime("%I:%M:%S %p"))
    if hda.actionSelected == 1:
        hda.consoleLogInfo("=== Houdini2Chat.Export")
        extractFromNodes()
        hda.setParm("action_selected", 0)
    elif hda.actionSelected == 2:
        hda.consoleLogInfo("=== main.Extract Selected")
        data = xf.ExtractFunctions().extractNodeTypes("Sop")
        xf.ExtractFunctions().export_node_types_as_functions(data, hda.projectLocation + "/extraction/node_types_functions.py")
        hda.setParm("action_selected", 0)
    elif hda.actionSelected == 3:
        hda.consoleLogInfo("=== main.Extract Selected")
        xf.ExtractFunctions().extract_all_node_types()
        hda.setParm("action_selected", 0)
    if hda.actionSelected != 0:
        endTime = datetime.datetime.now()
        hda.consoleLogInfo("=== Houdini2Chat Ending @ " + endTime.strftime("%I:%M:%S %p") +
                     " | Duration: " + str((endTime - startTime).total_seconds() * 1000) + "ms")
    return
