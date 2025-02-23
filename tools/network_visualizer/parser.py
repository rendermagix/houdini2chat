"""
This module is a parser to Houdini Documentation Files
"""
mergedDocFile = r"E:\projects\mh\houdini-ai\docs\houdin_20_5 _sop_nodes_documentation.txt"

def breakIntoSections(filepath, encoding='utf-8', errors='replace'):
    """
    Reads the given file and breaks its content into sections based on
    "START - Houdini SOP Node:" and "END - Houdini SOP Node:" markers.
    
    Returns:
        sections (list): A list of dictionaries, each with keys "node" and "content".
    """
    sections = []
    current_section = None
    current_content = []
    with open(filepath, 'r', encoding=encoding, errors=errors) as f:
        for line in f:
            # Check for start of a new section
            if line.startswith("START - Houdini SOP Node:"):
                # If we were processing a previous section, store it
                if current_section is not None:
                    sections.append({
                        "node": current_section,
                        "content": "".join(current_content)
                    })
                    current_content = []
                # Extract the node identifier (assumes it's the rest of the line after the marker)
                parts = line.split("START - Houdini SOP Node:", 1)
                current_section = parts[1].strip() if len(parts) > 1 else "Unknown"
                if current_section == "Unknown":
                    print("Unknown Node:", line)
            elif line.startswith("END - Houdini SOP Node:") and current_section is not None:
                sections.append({
                    "node": current_section,
                    "content": "".join(current_content)
                })
                current_section = None
                current_content = []
            elif current_section is not None:
                current_content.append(line)
    
    # If file ends without a closing marker, store any remaining content
    if current_section is not None:
        sections.append({
            "node": current_section,
            "content": "".join(current_content)
        })
    
    return sections

def extract_metadata(sections):
    """
    """
    meta_keys = {"type", "context", "status", "internal", "index", "since", "tags", "version", "namespace"}
    
    for section in sections:
        metadata = {}
        for line in section["content"].splitlines():
            line = line.strip()
            if line.startswith("#"):
                # Remove '#' and split into key-value pair
                parts = line[1:].split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    if key in meta_keys:
                        metadata[key] = value
            else:
                # Assuming metadata is grouped at the beginning, exit once non-metadata line is encountered.
                if metadata:
                    break
        section["metadata"] = metadata
    return sections

def get_raw_parameters(section):
    """
    Extracts raw parameter lines from a section.
    Parameters are expected to be after the '@parameters' marker and end when a line starts with '@' or the text is empty.
    
    Args:
        section (dict): A section dictionary with a "content" key.
    
    Returns:
        list: A list of raw parameter lines.
    """
    raw_params = []
    start = False
    if section["node"] == "xform":
        print("Xform")
    for line in section["content"].splitlines():
        line = line.rstrip()
        if line.startswith("@parameters"):
            start = True
            continue  # Skip the marker itself.
        elif start:
            if line.startswith("@"):
                break
            raw_params.append(line)
    return raw_params

def parse_raw_parameters(raw_params):
    """
    Parses raw parameter lines into structured parameters.
    
    Each parameter is identified by a line starting without leading whitespace that contains a colon,
    and its description includes the subsequent lines until the next parameter or end of input.
    
    Args:
        raw_params (list): List of raw parameter lines.
    
    Returns:
        list: A list of dictionaries with keys 'name' and 'description'.
    """
    parsed_params = []
    current_param = None
    current_desc_lines = []
    for line in raw_params:
        # A new parameter starts when the line has no leading whitespace and contains a colon.
        if line and not line[0].isspace() and ":" in line:
            if current_param:
                parsed_params.append({
                    "name": current_param,
                    "description": "\n".join(current_desc_lines).strip()
                })
                current_desc_lines = []
            parts = line.split(":", 1)
            current_param = parts[0].strip()
            first_desc = parts[1].strip()
            if first_desc:
                current_desc_lines.append(first_desc)
        else:
            if current_param:
                current_desc_lines.append(line.strip())
    if current_param:
        parsed_params.append({
            "name": current_param,
            "description": "\n".join(current_desc_lines).strip()
        })
    return parsed_params

def extract_parameters(sections):
    """
    Updates each section with a 'parameters' key containing structured parameter information.
    
    It uses get_raw_parameters to extract the raw lines and parse_raw_parameters to build structured parameters.
    
    Args:
        sections (list): List of section dictionaries.
    
    Returns:
        list: The updated sections with parsed parameters.
    """
    empty_count = 0
    for section in sections:
        raw_params = get_raw_parameters(section)
        # if raw_params is empty, count+1
        if not raw_params:
            empty_count += 1
        section["parameters"] = parse_raw_parameters(raw_params)
    print("Empty sections:", empty_count)
    return sections

def extract_node_desc(sections):
    """
        Node Description is a line that starts with 3 double quotes and ends with them
    """    
    for section in sections:
        desc_lines = []
        for line in section["content"].splitlines():
            line = line.strip()
            if line.startswith('"""') and line.endswith('"""'):
                desc_lines.append(line[3:-3].strip())
                break
        section["node_desc"] = "\n".join(desc_lines) if desc_lines else None
    return sections

def export_sections(sections, filepath):
    print("Total sections:", len(sections))
    param_sections_count = 0  # Counter for sections with parameters

    # Use utf-8 encoding to avoid UnicodeEncodeError
    with open(filepath, "w", encoding="utf-8") as outfile:
        for section in sections:
            outfile.write(f"Section: {section['node']}\n")
            outfile.write(f"Description: {section['node_desc']}\n")
            outfile.write(f"Metadata: {section['metadata']}\n")
            outfile.write("Parameters:\n")
            if section.get("parameters"):
                if len(section["parameters"]) > 0:
                    param_sections_count += 1
                for param in section["parameters"]:
                    description = param['description'].replace('\n', ' ').replace('\r', ' ')
                    outfile.write(f"  [{param['name']}] {description}\n")
            outfile.write("\n")
        outfile.write(f"Total sections with parameters: {param_sections_count}\n")
        
def export_as_code(sections, filepath):
    """
    Exports sections as Python functions with docstrings.
    Each section is converted to a function where:
      - The function name is the section's node.
      - The function's docstring contains the node description and a formatted list of parameters.
    
    This format is designed to improve reference in VS Code.
    """
    with open(filepath, "w", encoding="utf-8") as outfile:
        for section in sections:
            # Write a function definition with a docstring
            func_name = section["node"]
            outfile.write(f"def {func_name}():\n")
            outfile.write('    """\n')
            if section["node_desc"]:
                outfile.write(f"    {section['node_desc']}\n")
            if section.get("parameters"):
                outfile.write("\n    Parameters:\n")
                for param in section["parameters"]:
                    outfile.write(f"        {param['name']}: {param['description']}\n")
            outfile.write('    """\n')
            outfile.write("    pass\n\n")

def main():
    sections = breakIntoSections(mergedDocFile)
    sections = extract_metadata(sections)  # type, context, status, internal, index, since, tags, version, namespace
    sections = extract_node_desc(sections)
    sections = extract_parameters(sections)
    export_sections(sections, "output.txt")    
    export_as_code(sections, "sop_nodes.py")

if __name__ == "__main__":
    main()