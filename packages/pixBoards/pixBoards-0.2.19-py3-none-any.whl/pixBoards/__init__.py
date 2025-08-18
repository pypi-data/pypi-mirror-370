import os
import subprocess


# def get_git_version():
#     try:
#         commit_hash = (
#             subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
#             .decode()
#             .strip()
#         )
#         return commit_hash
#     except Exception:
#         return "untracked"


# __version__ = get_git_version()
__version__ = "0.2.19" 

templates_folder_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)

with open(os.path.join(templates_folder_path, "configTemplate.yml"), "r") as f:
    configTemplate = f.read()
