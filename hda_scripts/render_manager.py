import hou
import jinja2
import os
import hda_manager as hda
import re

class RenderManager:
    def __init__(self):
        self.hda_settings = hda.HDAManager()

    @staticmethod
    def ensure_unique_filename(txtFilename):
        """
        Appends a numeric counter suffix to txtFilename until a unique filename is found.
        
        Parameters:
            txtFilename (str): The original filename.
            
        Returns:
            str: A unique filename.
        """
        if os.path.exists(txtFilename):
            base, ext = os.path.splitext(txtFilename)
            counter = 1
            newFilename = f"{base}_{counter}{ext}"
            while os.path.exists(newFilename):
                counter += 1
                newFilename = f"{base}_{counter}{ext}"
            return newFilename
        return txtFilename
    
    @staticmethod    
    def has_macro(template, node):
        """
        Checks if a macro exists in the template for the given node type.
        
        The macro name is built by converting the node type to lowercase and
        replacing "::" with "_" (e.g.: "kinefx::skeleton" becomes "kinefx_skeleton").
        """
        macro_name = node["type"].lower().replace("::", "_")
        return hasattr(template.module, macro_name)    

    def get_embedded_templates(self):
        """
        Retrieves all embedded templates as a dictionary mapping template names to their contents.
        For this example, we're using a predefined list of template names.
        In your HDA, you may store the list of embedded templates in a parameter.
        """
        templates = {}
        embedded_template_names = [
            "branches_unit.py.j2",
            "loop_branches.py.j2"
        ]
        for tmpl_name in embedded_template_names:
            tmpl_string = hou.readFile(f"opdef:.?{tmpl_name}")
            templates[tmpl_name] = tmpl_string
        return templates

    def load_template(self, template_name):
        """
        Loads a Jinja2 template given the template name.
        
        Parameters:
            template_name (str): The name of the template file (e.g., "network_unit.py.j2")
        
        Returns:
            jinja2.Template: The loaded Jinja2 template.
        """
        # template_path = os.path.join(os.path.dirname(__file__), "templates")
        # env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        # print(f"Loading template: {template_name} from {template_path}")
        # return env.get_template(template_name)
        # get file content for the main template from Houdini
        main_template_string = hou.readFile(f"opdef:.?{template_name}")
        # Retrieve all embedded templates from the HDA parameters or fixed list
        embedded_templates = self.get_embedded_templates()
        # Ensure the main template is also present
        embedded_templates[template_name] = main_template_string
        # Create a Jinja2 environment with a DictLoader to resolve includes
        env = jinja2.Environment(loader=jinja2.DictLoader(embedded_templates))
        template = env.get_template(template_name)
        return template        

    def render_node_with_macro(self, template, node):
        """
        Renders a node using the macro in the template matching the node type,
        falling back on the default macro if no matching macro exists.
        
        The macro name is built by converting the node type to lowercase and
        replacing "::" with "_" (e.g.: "kinefx::skeleton" becomes "kinefx_skeleton").
        """
        
        # Build macro name based on node type.
        macro_name = node["type"].lower().replace("::", "_")
        # Access the module with rendered macros.
        tmpl_module = template.module

        if hasattr(tmpl_module, macro_name):
            render_macro = getattr(tmpl_module, macro_name)
        else:
            render_macro = getattr(tmpl_module, "default")
        return render_macro(node)
    
    def render_nodes(self, nodes):
        template = self.load_template("nodes_unit.py.j2")  # use your load_template function
        rendered_nodes = []
        for node in nodes:
            # TODO: if node has no changed properties, but we have a template for it, we will miss it here
            changed = any(prop["changed"] for prop in node["properties"].values())
            has_inputs = node["inputs"] is not None
            has_special_macro = RenderManager.has_macro(template, node)
            if changed or has_inputs or has_special_macro:
                rendered_nodes.append(self.render_node_with_macro(template, node))
        return "\n".join(rendered_nodes)

    def buildFilename(self, metadata):
        # Choose file format string based on render type
        format_str = self.hda_settings.defaultFileFormat
        if metadata["render.type"] == "nodePath":
            format_str = self.hda_settings.nodeFilenameFormat
        elif metadata["render.type"] == "networkBox":
            format_str = self.hda_settings.netboxFilenameFormat
    
        def sanitize_string(filename):
            # Replace any character that's not a letter, digit, underscore, hyphen, or dot with an underscore.
            return re.sub(r'[^A-Za-z0-9_.-]+', '_', filename)
    
        # Function to replace tokens in square brackets
        def replace_token(match):
            token = match.group(1)
            if token in metadata:
                return str(metadata[token])
            else:
                self.hda_settings.consoleLog(
                    f"=========== RenderManager.buildFilename Warning: Token '{token}' not found in metadata. Replacing with _NONE_.",
                    hda.TYPES.WARNING)
                self.hda_settings.consoleLog(f"=========== RenderManager.buildFilename Metadata: {metadata}'", hda.TYPES.INFO)
                return "_NONE_"
    
        # Replace any [token] with its value from metadata or _NONE_ if not found.
        filename = re.sub(r"\[([^\]]+)\]", replace_token, format_str)
        filename = sanitize_string(filename)
        txtFilename = os.path.join(self.hda_settings.projectLocation, filename)
    
        txtFilename = RenderManager.ensure_unique_filename(txtFilename)
    
        return txtFilename

    def save_rendered_output(self, rendered_text, nodeName, metadata):
        """
        Saves the rendered text to a file located at the project location defined by
        the HDA parent node.
        """
        txtFilename = self.buildFilename(metadata)        
        with open(txtFilename, 'w') as f:
            self.hda_settings.consoleLog(f"=========== RenderManager.save_rendered_output Saving Unit {nodeName} to {txtFilename}", hda.TYPES.INFO)
            f.write(rendered_text)
            
    def save_all_nodes(self, rendered_text, metadata):       
       txtFilename = os.path.join(self.hda_settings.projectLocation, self.hda_settings.defaultFileFormat)
       txtFilename = RenderManager.ensure_unique_filename(txtFilename)
       with open(txtFilename, 'w') as f:
           self.hda_settings.consoleLog(f"=========== RenderManager.save_all_nodes Saving all nodes to {txtFilename}", hda.TYPES.INFO)
           f.write(rendered_text)