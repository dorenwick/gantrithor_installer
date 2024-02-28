import os
import shutil

class GantrithorInstallerPrep:
    """
    GantrithorInstallerPrep Class Description:

    The GantrithorInstallerPrep class is designed to prepare the Gantrithor installation files for packaging using NSIS (Nullsoft Scriptable Install System).
    It automates the process of setting up the required directory structure and moving necessary files to their respective locations.

    Attributes:
    - base_path (str): The base path where the GantrithorInstaller folder is located.
    - dist_path (str): The path to the 'dist/Main' directory containing the installation files.
    - gantrithor_path (str): The path to the 'Gantrithor' directory where files will be copied or moved.
    - excluded_path (str): The path to the 'excluded' directory within the 'Gantrithor' directory.
    - internal_path (str): The path to the '_internal' directory within the 'Gantrithor' directory.
    - dll_paths (list): A list of relative paths to the DLL files to be moved.

    Steps:
    Step 1: Create the 'Gantrithor' directory if it doesn't exist.
    Step 2: Copy 'Main.exe' and '_internal' directory from 'dist/Main' to 'Gantrithor'.
    Step 3: Move DLL files from '_internal' to 'excluded/ToMain'.
    Step 4: Move the 'torch' folder from '_internal' to 'excluded'.
    Step 5: Print a message with the path to 'exe_coded.nsi' for NSIS packaging.

    Usage:
    1. Instantiate the GantrithorInstallerPrep class.
    2. Call the setup() method to execute the setup process.

    Example:
    installer_prep = GantrithorInstallerPrep()
    installer_prep.setup()

    Note: Ensure that the paths are correctly set for your system.
    """
    def __init__(self):
        self.base_path = "C:\\Users\\doren\\OneDrive\\Desktop\\GantrithorInstaller"
        self.dist_path = os.path.join(self.base_path, "dist", "Main")
        self.gantrithor_path = os.path.join(self.base_path, "Gantrithor")
        self.excluded_path = os.path.join(self.gantrithor_path, "excluded")
        self.to_main_path = os.path.join(self.excluded_path, "ToMain")
        self.internal_path = os.path.join(self.gantrithor_path, "_internal")
        self.data_template_path = os.path.join(self.base_path, "data_template")
        self.dll_paths = [
            "cublasLt64_11.dll",
            "cusolver64_11.dll",
            "cufft64_10.dll",
            "cusparse64_11.dll",
        ]

    def setup(self):
        self.create_gantrithor_directory()
        self.create_excluded_directories()
        self.copy_main_files()
        self.move_dll_files()
        self.move_torch_folder()
        self.copy_data_template()
        self.print_nsis_message()

    def create_gantrithor_directory(self):
        if not os.path.exists(self.gantrithor_path):
            os.makedirs(self.gantrithor_path)

    def create_excluded_directories(self):
        if not os.path.exists(self.excluded_path):
            os.makedirs(self.excluded_path)
        if not os.path.exists(self.to_main_path):
            os.makedirs(self.to_main_path)

    def copy_data_template(self):
        data_path = os.path.join(self.gantrithor_path, "data")
        shutil.copytree(self.data_template_path, data_path)

    def copy_main_files(self):
        # Copy Main.exe to the Gantrithor directory
        shutil.copy(os.path.join(self.dist_path, "Main.exe"), self.gantrithor_path)
        # Rename Main.exe to Gantrithor.exe
        os.rename(os.path.join(self.gantrithor_path, "Main.exe"), os.path.join(self.gantrithor_path, "Gantrithor.exe"))
        # Copy the _internal directory
        shutil.copytree(os.path.join(self.dist_path, "_internal"), self.internal_path)

    def move_dll_files(self):
        for dll in self.dll_paths:
            src_path = os.path.join(self.internal_path, dll)
            dest_path = os.path.join(self.excluded_path, "ToMain", dll)
            shutil.move(src_path, dest_path)

    def move_torch_folder(self):
        src_path = os.path.join(self.internal_path, "torch")
        dest_path = os.path.join(self.excluded_path, "torch")
        shutil.move(src_path, dest_path)

    def print_nsis_message(self):
        print("Please now use the exe_coded file and load it into the NSIS software. Here it is: " + os.path.join(self.base_path, "exe_coded.nsi"))

# Usage
installer_prep = GantrithorInstallerPrep()
installer_prep.setup()
