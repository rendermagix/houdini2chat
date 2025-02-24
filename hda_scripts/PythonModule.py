import sys
import hou
import importlib
import toolutils

hda_manager = toolutils.createModuleFromSection("hda_manager", kwargs["type"], "hda_manager")
sys.modules["hda_manager"] = hda_manager

houdini_node_manager = toolutils.createModuleFromSection("houdini_node_manager", kwargs["type"], "houdini_node_manager")
sys.modules["houdini_node_manager"] = houdini_node_manager

gnode = toolutils.createModuleFromSection("gnode", kwargs["type"], "gnode")
sys.modules["gnode"] = gnode

render_manager = toolutils.createModuleFromSection("render_manager", kwargs["type"], "render_manager")
sys.modules["render_manager"] = render_manager

node_graph = toolutils.createModuleFromSection("node_graph", kwargs["type"], "node_graph")
sys.modules["node_graph"] = node_graph

extract_functions = toolutils.createModuleFromSection("extract_functions", kwargs["type"], "extract_functions")
sys.modules["extract_functions"] = extract_functions

main = toolutils.createModuleFromSection("main", kwargs["type"], "main")
sys.modules["main"] = extract_functions

def handleActionNew(action_value):
    hda_node = hou.pwd()
    hda_node.parm("action_selected").set(action_value)    
    main.main()