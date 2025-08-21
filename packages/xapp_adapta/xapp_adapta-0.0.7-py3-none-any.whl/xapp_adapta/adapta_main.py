#!/usr/bin/python3

# sudo apt install libgirepository-2.0-dev
from typing import Callable
import gi
import sys
import os
import importlib.metadata as metadata

gi.require_version("Gtk", "4.0")
gi.require_version("XApp", "1.0")
# so Gtk for graphics
# Gio for data files
# GLib.Error (FileDialog?)
from gi.repository import Gtk, Gio, GLib

# form gi.repository import XApp

# libAdapta uses its own module name (Adap.ApplicationWindow etc..).
# We would normally import it like this:
# from gi.repository import Adap
# Since libAdapta and libAdwaita use the same class names,
# the same code can work with both libraries, as long as we rename
# the module when importing it
try:
    gi.require_version("Adap", "1")
    from gi.repository import Adap as Adw
except ImportError or ValueError as ex:
    # To use libAdwaita, we would import this instead:
    print("Using Adwaita as Adapta not found:\n", ex)
    gi.require_version("Adw", "1")
    from gi.repository import Adw

from .adapta_test import _, MainWindow, xapp_adapta, domain

icon = domain + "." + ".".join(os.path.basename(__file__).split(".")[:-1])
# print(icon) -- ok neede white space remove


# doesn't need to be class method
def button(icon: str, callback: Callable):
    button = Gtk.Button()
    button.set_icon_name(icon)
    button.connect("clicked", callback)
    return button


class MyWindow(MainWindow):  # pyright: ignore
    # override for different behaviour
    def layout(self):
        # this appears in some window managers
        # cinnaman hover taskbar ...
        self.set_title(sys.argv[0])
        self.set_default_size(800, 600)
        self.split_view.set_min_sidebar_width(200)
        self.split_view.set_max_sidebar_width(300)
        # multipaned content by selection widget
        # set list name [] and button nav {}
        self.pages = [self.content()]
        self.buttons = {
            # yes the lest about icon (long close ad) and more oft menu burger UI
            "right": [self.burger()],  # the burger menu
            "left": [button(icon, self.about)],  # about icon
            # 1:1 pages match of subtitle injection
            "subs": [_("Sub Title")],
            # 1:1 pages match of icon names injection
            "icons": ["utilities-terminal"],
        }
        # N.B. Gtk4 error as would need Gtk3
        # self.tray = XApp.StatusIcon()
        # self.tray.set_icon_name("utilities-terminal")
        # self.tray.set_tooltip_text(sys.argv[0])
        # self.tray.connect("left-click", self.on_tray_left)

    def on_tray_left(self, icon, x, y, time, button):
        pass

    # methods to define navigation pages
    def content(self) -> Adw.NavigationPage:
        # Create the content page _() for i18n
        content_box = self.fancy()
        status_page = Adw.StatusPage()
        status_page.set_title("Python libAdapta Example")
        status_page.set_description(
            "Split navigation view, symbolic icon and a calendar widget to feature the accent color."
        )
        status_page.set_icon_name("document-open-recent-symbolic")
        calendar = Gtk.Calendar()
        content_box.append(status_page)
        content_box.append(calendar)
        # set title and bar
        return self.top(content_box, _("Content"), **{})

    def about(self, action):
        about = Gtk.AboutDialog()
        about.set_transient_for(
            self
        )  # Makes the dialog always appear in from of the parent window
        about.set_modal(
            True
        )  # Makes the parent window unresponsive while dialog is showing
        # metadata more in here to auto ...
        authors = metadata.metadata(xapp_adapta).get_all("Author-email")
        if authors is not None:
            about.set_copyright("(C) 2025 " + authors[0])
            about.set_authors(authors)
        about.set_license_type(Gtk.License.LGPL_3_0_ONLY)
        urls = metadata.metadata(xapp_adapta).get_all("Project-URL")
        splitter = "Homepage, "
        if urls is not None:
            for u in urls:
                if splitter in u:
                    # about.set_website("https://github.com/jackokring/mint-python-adapta")
                    about.set_website(u.split(splitter)[1])
        about.set_website_label(xapp_adapta)
        about.set_version(metadata.version(xapp_adapta))
        about.set_logo_icon_name(icon)
        about.set_visible(True)


class MyApp(Adw.Application):  # pyright: ignore
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self.connect("open", self.on_open)
        self.connect("command-line", self.on_command_line)
        self.set_flags(Gio.ApplicationFlags.HANDLES_OPEN)
        self.set_flags(Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.win = None

    def on_activate(self, app):
        if not self.win:
            self.win = MyWindow(application=app)
        self.win.present()

    # detects if present, but doesn't print anything?
    def on_open(self, app, files, n_files, hint):
        self.on_activate(app)
        for file in n_files:
            print("File to open: " + file.get_path() + "\n")

    def on_command_line(self, app, argv):
        self.on_activate(app)
        for file in argv.get_arguments()[1:]:
            print("File to open: " + file + "\n")
        return 0  # exit code


def main():
    app = MyApp(application_id=icon)
    sys.exit(app.run(sys.argv))
