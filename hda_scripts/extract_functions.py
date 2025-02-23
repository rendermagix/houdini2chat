import hou
import json
import re
import hda_manager as hdaSettings
import keyword

class ExtractFunctions:
    # Static exclusion list for parameter types (only the type string, e.g. "parmTemplateType.type")
    EXCLUDED_PARAM_TYPES = ["FolderSet", "Button", "Folder", "Separator", "Label", "Data" ]    

    # Mapping list for parameter types
    PARAM_TYPE_MAPPING = {
        "Int": "int",
        "Float": "float",
        "String": "str",
        "Toggle": "bool",
        "Menu": "enum",
        # Add more mappings as needed
    }    
    
    def __init__(self):
        self.hdaSettings = hdaSettings.HDAManager()
        pass

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

    def extract_all_node_types(self):
        # Loop through all available categories from Houdini
        for category in hou.nodeTypeCategories().keys():
            self.extractNodeTypes(category)

    def extractNodeTypes(self, category="Sop"):
        node_category = hou.nodeTypeCategories()[category]
        data = {}

        for node_type in node_category.nodeTypes().values():
            help_text = node_type.embeddedHelp()            
            node_info = {
                "name": node_type.name(),
                "description": node_type.description(),
                "help": help_text,
                "parameters": []
            }
            for parm_template in node_type.parmTemplates():
                # Determine parameter type
                param_type = (str(parm_template.type()) if hasattr(parm_template, "type") and callable(parm_template.type)
                              else "Unknown")
                param_type = param_type.split('.')[-1]  # Strip the first part of the type value
                # Skip parameters whose types are in the exclusion list
                if param_type in ExtractFunctions.EXCLUDED_PARAM_TYPES:
                    continue
                
                # Map parameter type if it exists in the mapping list
                param_type = ExtractFunctions.PARAM_TYPE_MAPPING.get(param_type, param_type)                
                                
                parm_info = {
                    "name": parm_template.name(),
                    "label": parm_template.label(),
                    "default_value": parm_template.defaultValue() if hasattr(parm_template, "defaultValue") and callable(parm_template.defaultValue) else "No default",
                    "help": parm_template.help() if hasattr(parm_template, "help") and callable(parm_template.help) else "No help available",
                    "type": param_type,
                    "numComponents": parm_template.numComponents() if hasattr(parm_template, "numComponents") and callable(parm_template.numComponents) else "Unknown",
                    "namingScheme": str(parm_template.namingScheme()) if hasattr(parm_template, "namingScheme") and callable(parm_template.namingScheme) else "Unknown",
                    "isHidden": parm_template.isHidden() if hasattr(parm_template, "isHidden") and callable(parm_template.isHidden) else False,
                }
                node_info["parameters"].append(parm_info)
            data[node_type.name()] = node_info

        file_name = f"{category.lower()}_nodes_info.json"
        with open(self.hdaSettings.projectLocation + f"/extraction/{file_name}", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return data
            
    def export_node_types_as_functions(self, data, filepath):
        """
        Exports the node types data as Python function definitions.
        Each function uses the node type's name as the function name.
        
        Args:
            data (dict): Dictionary of node types from extractNodeTypes.
            filepath (str): Destination file path for the generated code.
        """
        with open(filepath, "w", encoding="utf-8") as outfile:
            for node_name, node_info in data.items():
                sanitized_node_name = ExtractFunctions.sanitize_string(node_name)
                outfile.write(f"# Node: {node_name} - {node_info['description']}\n")
                outfile.write(f"def {sanitized_node_name}(\n")
                
                # Write parameters
                param_set = set()
                for parm in node_info["parameters"]:
                    param_label = ExtractFunctions.sanitize_string(parm["label"])
                    if not param_label.strip():
                        param_label = ExtractFunctions.sanitize_string(parm["name"])
                    # If the parameter label starts with a digit, prepend an underscore
                    if param_label and param_label[0].isdigit():
                        param_label = "_" + param_label
                    if param_label in param_set:
                        continue
                    param_set.add(param_label)
                    
                    try:
                        num_components = int(parm.get("numComponents", 1))
                    except (ValueError, TypeError):
                        num_components = 1
                    type_display = parm["type"] if num_components == 1 else f"{parm['type']}[{num_components}]"
                    
                    default_value = parm["default_value"]
                    if default_value != "No default":
                        if isinstance(default_value, (list, tuple)) and len(default_value) == 1:
                            default_value = default_value[0]
                        if isinstance(default_value, str):
                            default_repr = json.dumps(default_value)
                        elif isinstance(default_value, (list, tuple)):
                            default_repr = str(list(default_value))
                        else:
                            default_repr = str(default_value)
                        line = f"    {param_label} = {default_repr},"
                    else:
                        line = f"    {param_label},"
                    
                    outfile.write(f"{line}  # ({param_label}, {type_display})\n")
                
                outfile.write("):\n")
                outfile.write("    ...\n\n")