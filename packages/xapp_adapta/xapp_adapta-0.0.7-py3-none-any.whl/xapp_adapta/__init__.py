# module initialization
from .adapta_test import main as test
from .adapta_main import main
import shutil, os


def copy_with(dir):
    path = os.path.dirname(__file__) + "/"
    home_local = os.path.expanduser("~/.local/share/")
    shutil.copytree(path + dir, home_local + dir, dirs_exist_ok=True)


# make_local icons and desktop files
def make_local():
    copy_with("applications")
    copy_with("icons")
    copy_with("locale")
