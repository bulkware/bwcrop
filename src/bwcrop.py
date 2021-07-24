#!/usr/bin/env python3

""" An application to automatically crop image files. """

# Python imports
import os  # Miscellaneous operating system interfaces
import re  # Regular expression operations
import sys  # System-specific parameters and functions

# GTK imports
import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk  # GIMP Drawing Kit
from gi.repository import GdkPixbuf  #  Image loading and manipulation
from gi.repository import Gio  # VFS API
#from gi.repository import GLib  # Low-level core library
from gi.repository import Gtk  # GIMP ToolKit
#from gi.repository import Pango  # Text layout engine

# 3rd party imports
from PIL import Image # Image object from "The friendly PIL fork"

# Declare variables
application_version = "0.4.0"
file_filters = (
    ("Joint Photographic Expert Group Image", "image/jpeg"),
    ("Portable Network Graphics", "image/png"),
    ("Scalable Vector Graphics", "image/svg+xml"),
    ("Tag Image File Format", "image/tiff")
)
gsettings_key = "org.bulkware.bwcrop"
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
#css_path = os.path.join(script_dir, "default.css")
icon_path = os.path.join(script_dir, "icon_128x128.png")

# Main window
class bwcrop(Gtk.Window):

    def __init__(self):

        # Declare application variables
        self.drawing_mode = False
        self.settings = Gio.Settings.new(gsettings_key)

        # Set window defaults
        Gtk.Window.__init__(self, title="bwcrop")
        screen = self.get_screen()
        self.set_icon_from_file(icon_path)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(800, 600)
        self.set_size_request(800, 600)
        self.set_border_width(5)

        # Menu
        open_selection = Gtk.ModelButton(label="Open")
        open_selection.connect("clicked", self.open_file)
        open_selection.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.MENU))

        about_selection = Gtk.ModelButton(label="About")
        about_selection.connect("clicked", self.about_application)
        about_selection.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ABOUT, Gtk.IconSize.MENU))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=10, spacing=10)
        vbox.pack_start(open_selection, 1, 0, 0)
        vbox.pack_start(about_selection, 1, 0, 0)
        vbox.show_all()

        popover = Gtk.Popover()
        popover.add(vbox)
        popover.set_position(Gtk.PositionType.BOTTOM)

        menu_button = Gtk.MenuButton(popover=popover)
        menu_icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU)
        menu_button.add(menu_icon)

        headerbar = Gtk.HeaderBar()
        headerbar.props.show_close_button = True
        headerbar.props.title = "bwcrop"
        headerbar.pack_start(menu_button)
        self.set_titlebar(headerbar)

        # Statusbar
        self.statusbar = Gtk.Statusbar()

        # Overlay with image
        self.pixbuf = GdkPixbuf.Pixbuf()
        self.image = Gtk.Image()
        self.image.set_valign(Gtk.Align.START)
        self.image.set_halign(Gtk.Align.START)
        overlay = Gtk.Overlay()
        overlay.add(self.image)

        # Overlay with drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        overlay.add_overlay(self.drawing_area)

        # Create a scroller for overlays
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(overlay)

        # Settings
        zoom_store = Gtk.ListStore(str)
        zoom_store.append(["100%"])
        zoom_store.append(["75%"])
        zoom_store.append(["50%"])
        zoom_store.append(["25%"])
        zoom_store.append(["12.5%"])

        self.cbx_zoom = Gtk.ComboBox.new_with_model_and_entry(zoom_store)
        self.cbx_zoom.get_child().set_text("100%")
        self.cbx_zoom.set_entry_text_column(0)

        self.cbx_zoom.connect("changed", self.on_zoom_changed)

        # Horizontal box to hold scroller
        hbox = Gtk.Box(orientation="horizontal", spacing=5)
        hbox.pack_start(Gtk.Separator(), 0, 0, 0)
        hbox.pack_start(scroller, 1, 1, 0)
        hbox.pack_start(Gtk.Separator(), 0, 0, 0)

        # Horizontal box to hold statusbar and settings
        hbox2 = Gtk.Box(orientation="horizontal", spacing=5)
        hbox2.pack_start(self.statusbar, 1, 1, 0)
        hbox2.pack_start(self.cbx_zoom, 0, 0, 0)

        # Vertical box to hold everything
        vbox = Gtk.Box(orientation="vertical", spacing=5)
        vbox.pack_start(hbox, 1, 1, 0)
        vbox.pack_start(hbox2, 0, 0, 0)

        # Add the box to the window
        self.add(vbox)

        # Try to load image
        self.load_image(self.settings.get_string("imgpath"))

    # Zoom level changed
    def on_zoom_changed(self, widget):

        # Retrieve zom selection
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:
            model = widget.get_model()
            zoom_percent = model[tree_iter][0]
        else:
            zoom_percent = widget.get_child().get_text()

        # Validate zoom percent
        if not re.fullmatch(r"^[1-9]([\d]+?)(\.[\d]+)?%$", zoom_percent):
            return True

        # Convert percent to float for multiplying
        zoom_float = abs(float(zoom_percent.strip("%"))) / 100

        # Scale image
        self.pixbuf = self.pixbuf.scale_simple(
            self.imgwidth * zoom_float,
            self.imgheight * zoom_float,
            GdkPixbuf.InterpType.BILINEAR
        )

        # Set scaled image to widget
        self.image.set_from_pixbuf(self.pixbuf)
        self.statusbar.push(0, f"Zoom: {zoom_percent}")

    # Open file
    def open_file(self, widget):

        # Declare variables
        imgpath = None

        # Initialize file open dialog
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )

        # Define file open dialog buttons
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        # Set file open dialog filters
        for item in file_filters:
            file_filter = Gtk.FileFilter()
            file_filter.set_name(item[0])
            file_filter.add_mime_type(item[1])
            dialog.add_filter(file_filter)

        # Show dialog and retrieve possible selection(s)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            imgpath = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

        # Check file selection
        if imgpath:
           self.load_image(imgpath)

    # Load new image into widget
    def load_image(self, imgpath):

        # Check if image file is defined (setting might be empty)
        if not imgpath:
            return False

        # Check if image file exists first
        if not os.path.exists(imgpath):
            self.statusbar.push(0, f"File does not exist: {imgpath}")
            return False

        # Create image pixbuf and retrieve image size
        self.imgwidth = self.pixbuf.get_file_info(imgpath).width
        self.imgheight = self.pixbuf.get_file_info(imgpath).height
        self.pixbuf = self.pixbuf.new_from_file_at_scale(
            filename=imgpath,
            width=-1,
            height=-1,
            preserve_aspect_ratio=True
        )

        # Clear and set a new image to widget
        self.image.clear()
        self.image.set_from_pixbuf(self.pixbuf)

        # Store image path into settings
        self.settings.set_string("imgpath", imgpath)

        # Inform user
        self.statusbar.push(0, f"Image loaded: {imgpath}")

        # Reset zoom level
        self.cbx_zoom.get_child().set_text("100%")

        self.drawing_mode = False

        return True

    # Draw on image
    def on_draw(self, widget, ctx):

        # This is to prevent drawing after initial one
        if self.drawing_mode:
            return False

        imgpath = self.settings.get_string("imgpath")

        if not imgpath:
            return False
        elif not os.path.exists(imgpath):
            return False

        self.drawing_mode = True

        print(ctx)

        # Open and create a pixel map from image
        image = Image.open(imgpath)
        pixels = image.load()
        y_pos = image.size[1] // 2
        for x_pos in range(0, image.size[0] // 6):
            colours = pixels[x_pos, y_pos]
            luminance = int(
                (0.2126 * colours[0]) +
                (0.7152 * colours[1]) +
                (0.0722 * colours[2])
            )
            print(f"{x_pos}x{y_pos}: {luminance}")

        ctx.rectangle(0, 0, 100, 100)
        ctx.set_source_rgb(1, 0, 0)
        ctx.fill()
        #drawing_area.queue_draw()
        self.drawing_area.queue_draw_area(0, 0, 100, 100)

    # About application
    def about_application(self, widget):
        about = Gtk.AboutDialog(transient_for=self)
        about.set_program_name("bwcrop")
        about.set_version(application_version)
        about.set_copyright("Copyright (c) 2021+ Antti-Pekka Meronen.")
        about.set_comments("An application to automatically crop image files.")
        about.set_website("https://github.com/bulkware/bwcrop")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(icon_path))
        about.run()
        about.destroy()
        return True

    # Quit application
    def quit_application(self, widget):
        Gtk.main_quit()
        return True


# Only run as a standalone application
if __name__ == "__main__":
    win = bwcrop()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
