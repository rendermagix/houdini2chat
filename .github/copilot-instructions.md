we are building a Houdini HDA that extracts Node network of the currently open hip file.
that HDA includes a python script that processes the network and extract its data in a text format that is easy to use later by LLM Tools.
the HDA includes a number of parameters that are referenced by the script (hint: they are in the parent node)

Important Notes:-
- Please only send me necessary code updates, don't just dump whole class or whole function if you are changing small parts.
- you always mix up between the HDA node and the python node inside it. make sure to understand if the request about updating the HDA node or the python node.
- when working on the main.py (visualization app), this is not running on Houdini, so you cannot make references to Houdini nodes/parameters directly here.