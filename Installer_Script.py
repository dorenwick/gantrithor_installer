import subprocess
import shutil
import os

# Paths
spec_file_path = "C:\\Users\\doren\\PycharmProjects\\GANTRITHOR_FINAL_2024\\Main.spec"
dist_source_path = "C:\\Users\\doren\\PycharmProjects\\GANTRITHOR_FINAL_2024\\dist"
dist_destination_path = "C:\\Users\\doren\\OneDrive\\Desktop\\GantrithorInstaller"
nsis_script_path = "C:\\Users\\doren\\OneDrive\\Desktop\\GantrithorInstaller\\script_installer_prep_nsis.py"

# Run PyInstaller with the spec file
subprocess.run(["pyinstaller", spec_file_path], check=True)

# Copy the dist directory to the desired location
shutil.copytree(dist_source_path, dist_destination_path, dirs_exist_ok=True)

# Run the NSIS preparation script
subprocess.run(["python", nsis_script_path], check=True)
