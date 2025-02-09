import hou
import os

class FbxImporter:
    """
    A class to handle importing multiple FBX files into a Houdini network.
    This version creates a separate File node for each FBX file and transforms them.
    """

    def __init__(self):
        """
        Initializes the FbxImporter class.
        """
        self.fbx_files = []  # List of FBX files selected.
        self.geo_node_name = "fbx_imports"
        self.output_node_name = "output1"
        self.translate_x = 20  # Translation amount in Houdini units
        
       

    def get_fbx_files_from_ui(self):
        """
        Prompts the user to select multiple FBX files using a Houdini file dialog.
        """
        self.fbx_files = hou.ui.selectFile(
            title="Select FBX Files to Import",
            pattern="*.fbx",
            multiple_select=True,  # Allow multiple selection
            file_type=hou.fileType.Any,
        )

        if not self.fbx_files:
            hou.ui.displayMessage("FBX file selection cancelled.")
            return False  # Indicate cancellation

        self.fbx_files = self.fbx_files.split(";")
        # Remove any leading or trailing spaces from each file path in the list
        self.fbx_files = [file_path.strip() for file_path in self.fbx_files]
        return True

    def create_fbx_import_network(self):
        """
        Creates a Houdini network that imports multiple FBX files, creating a File node
        for each FBX file, transforms them and then merges them.
        """

        if not self.fbx_files:
            hou.ui.displayMessage("FBX files not selected. Please select files first.")
            return

        # Create a Geometry node to contain the FBX imports
        geo_node = hou.node("/obj").createNode("geo", self.geo_node_name)
        geo_node.moveToGoodPosition()

        # Create the output node
        output_node = geo_node.createNode("output", self.output_node_name)
        output_node.moveToGoodPosition()
        output_node.setDisplayFlag(True)
        output_node.setRenderFlag(True)

        if not self.fbx_files:
            hou.ui.displayMessage(f"No FBX files selected.")
            geo_node.destroy()
            return

        # Create a list to store the output of each file node
        file_nodes = []

        # Create a File node for each FBX file
        for i, fbx_file_path in enumerate(self.fbx_files):
            fbx_import_node = geo_node.createNode("file", f"fbx_import_{i}")
            fbx_import_node.parm("file").set(fbx_file_path)
            fbx_import_node.moveToGoodPosition()

            # Create a Transform node for the imported geometry
            transform_node = geo_node.createNode("xform", f"transform_{i}")
            transform_node.setInput(0, fbx_import_node)  # Connect transform to file node
            transform_node.moveToGoodPosition()
            transform_node.parm("tx").set(self.translate_x * i)  # Set X translation for each file (cumulative offset)

            file_nodes.append(transform_node)  # Store the TRANSFORM node, not the file node.
            
            
            """ Group Goes here-=------------------"""

        # Merge all the File nodes together
        if file_nodes:
            if len(file_nodes) > 1: # Only create a merge if more than one input is available
                merge_node = geo_node.createNode("merge", "fbx_merge")
                for i, node in enumerate(file_nodes):
                    merge_node.setInput(i, node)
                merge_node.moveToGoodPosition()
                output_node.setInput(0, merge_node)
            else:
                output_node.setInput(0, file_nodes[0]) #Just set the output to the file node if it is the only one
        else:
            hou.ui.displayMessage("No valid FBX files selected.")
            geo_node.destroy()  # Remove the geo node

        # Automatically arrange the network for better readability
        geo_node.layoutChildren()
        print(f"FBX import network created successfully in: {geo_node.path()}")


# --- Example Usage (in the Houdini Python Shell) ---
# Create an instance of the importer
importer = FbxImporter()

# Get the FBX files from the UI
if importer.get_fbx_files_from_ui():
    # Create the import network
    importer.create_fbx_import_network()

# Optionally, change the Geo node and output node names
# importer.geo_node_name = "my_fbx_assets"
# importer.output_node_name = "final_output"