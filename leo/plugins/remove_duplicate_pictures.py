#@+leo-ver=5-thin
#@+node:ekr.20220126054240.1: * @file ../plugins/remove_duplicate_pictures.py
#@+<< docstring (remove_duplicate_pictures.py) >>
#@+node:ekr.20220126054240.2: ** << docstring (remove_duplicate_pictures.py) >>
"""
Remove duplicate 

This plugin will display all files in a directory tree that have image
extensions. By default the recognized extensions are '.jpeg', '.jpg', and
'.png'. Other types of image files can be displayed as long as the they are
types known by the Qt PixMap class, including '.gif' and '.bmp'. See, for
example:

https://doc.qt.io/qt-5/qpixmap.html#reading-and-writing-image-files

This plugin should be called from a script (or @command or @button node) as follows:

    from leo.plugins.picture_viewer import Slides
    Slides().run(c)  # See below for defaults.

*Note*: do not enable this plugin. It will be loaded by the calling script.

**Key bindings**

Plain keys control the display of slides:

      space: show the next slide.
  backspace: show the previous slide.
     escape: end the slideshow
          =: zoom in
          -: zoom out
arrows keys: pan the slide
          d: prompt to move the slide to the trash
          h: show the help message
          m: move the file.
          r: restart: choose another folder

**Defaults**

The following keyword arguments may be supplied to the run method:

    background_color = "black",  # Default background color.
    delay = 100,  # Delay between slides, in seconds.
    extensions = ['.jpeg', '.jpg', '.png'],  # List of file extensions.
    full_screen = True,  # True: start in full-screen mode.
    height = 900,  # Window height (pixels) when not in full screen mode.
    path = None,  # If none, display a dialog.
    reset_zoom = True,  # True, reset zoom factor when changing slides.
    sort_kind = 'random',  # 'date', 'name', 'none', 'random', or 'size'
    width = 1500,  # Window width (pixels) when not un full screen mode.

"""
#@-<< docstring (remove_duplicate_pictures.py) >>
#@+<< imports (remove_duplicate_pictures.py) >>
#@+node:ekr.20220126054240.3: ** << imports (remove_duplicate_pictures.py) >>
import argparse
from collections import defaultdict
import os
import pathlib
import sys
import time
# Third party
try:
    from PIL import Image
except Exception:
    print('remove_duplicate_pictures: PIL required')
    print('pip install pillow')
    Image = None
try:
    import imagehash
except Exception:
    imagehash = None
    print('remove_duplicate_pictures: imagehash required')
    print('pip install imagehash')
try:
    import numpy as np
except Exception:
    np = None
    print('remove_duplicate_pictures: numpy required')
    print('pip install numpy')
try:
    from send2trash import send2trash
except Exception:
    send2trash = None  # Optional
# Leo
import leo.core.leoGlobals as g
from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets
#@-<< imports (remove_duplicate_pictures.py) >>

# Globals to retain references to objects.
gApp = None
gWidget = None

#@+others
#@+node:ekr.20220126054240.4: ** init (remove_duplicate_pictures.py)
def init():
    """Return True if the plugin has loaded successfully."""
    return Image and imagehash and np and g.app.gui.guiName().lower().startswith('qt')
#@+node:ekr.20220126054240.5: ** get_args & checkers
def get_args():

    # Automatically implements the --help option.
    description = "usage: python -m remove_duplicate_pictures [options]"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)

    # Add args.
    add = parser.add_argument
    add('--background', dest='background', metavar='COLOR', 
        help='Background color')
    add('--extensions', dest='extensions', nargs='*', metavar='TYPES',
        help='List of image file extensions.')
        # Default: .jpeg,.jpg,.png  (no spaces allowed)
    add('--full-screen', dest='fullscreen', action='store_true',
        help='Start in full-screen mode')
    add('--height', dest='height', metavar='PIXELS',
        help='Height of window')
    add('--path', dest='path', metavar='DIRECTORY',
        help='Path to root directory')
    add('--width', dest='width', metavar='PIXELS',
        help='Width of window')

    # Parse the options, and remove them from sys.argv.
    args = parser.parse_args()

    # Check and return the args.
    return {
         'background_color': args.background or "black",
         'extensions': get_extensions(args.extensions),
         'full_screen': args.fullscreen,
         'height': get_pixels('height', args.height),
         'path': get_path(args.path),
         'width': get_pixels('width', args.width)
    }
#@+node:ekr.20220126054240.7: *3* get_extensions
def get_extensions(aList):
    
    # Ensure extensions start with '.'
    return [
        z if z.startswith('.') else f".{z}"
            for z in aList or []
    ]
#@+node:ekr.20220126054240.8: *3* get_path
def get_path(path):
    
    if path and not os.path.exists(path):
        print(f"--path: not found: {path!r}")
        path = None
    return path
#@+node:ekr.20220126054240.9: *3* get_pixels
def get_pixels(kind, pixels):
    
    if pixels is None:
        return None
    try:
        return int(pixels)
    except ValueError:
        print(f"Bad --{kind} value: {pixels!r}")
        return None
#@+node:ekr.20220126054240.12: ** main
def main():
    global gApp
    gApp = QtWidgets.QApplication(sys.argv)
    args = get_args()
    ok = RemoveDuplicates().run(c = None, **args)
    if ok:
        if isQt5:
            sys.exit(gApp.exec_())
        else:
            sys.exit(gApp.exec())
#@+node:ekr.20220126054240.13: ** class RemoveDuplicates
class RemoveDuplicates:
    
    filename_dict = {}  # Keys are filenames, values are hashes.
    hash_size = 8
    hash_dict = defaultdict(list)  # Keys are hashes, values are lists of filenames.
    max_open_windows = 20
    window = None
    window_height = 900
    window_width = 1500
            
    #@+others
    #@+node:ekr.20220126063935.1: *3* Dups.compute_dicts
    def compute_dicts(self, filenames):
        for i, filename in enumerate(filenames):
            try:
                h = imagehash.average_hash(Image.open(filename), self.hash_size)
                self.filename_dict [filename] = h.hash
                self.hash_dict [str(h)].append(filename)
            except Exception:
                print('Bad img:', filename)
                # g.es_exception()
                filenames.remove(filename)
    #@+node:ekr.20220126064207.1: *3* Dups.create_frame
    def create_frame(self, filename, filenames, window):

        QLabel = QtWidgets.QLabel
        # Create the frame.
        frame = QtWidgets.QFrame(parent=window)
        # Create the vertical layout.
        layout = QtWidgets.QVBoxLayout()
        frame.setLayout(layout)
        # Create the labels..
        creation_time = time.ctime(os.path.getctime(filename))
        layout.addWidget(QLabel(text=filename, parent=frame))
        size = os.path.getsize(filename) / 1000
        layout.addWidget(QLabel(text=f"size: {size} KB date: {creation_time}"))
        # Create the delete button.
        delete_button = QtWidgets.QPushButton(text='Delete', parent=frame)
        layout.addWidget(delete_button)
        # Set the button actions.
        def delete_action(arg):
            self.delete_file(filename)
            filenames.remove(filename)
            if len(filenames) < 2:
                window.close()
        delete_button.clicked.connect(delete_action)
        # Create the picture area.
        picture = QtWidgets.QLabel('picture', parent=frame)
        layout.addWidget(picture)
        # Display the picture.
        pixmap = QtGui.QPixmap(filename)
        try:
            TransformationMode = QtCore.Qt if isQt5 else QtCore.Qt.TransformationMode
            image = pixmap.scaledToHeight(self.window_height, TransformationMode.SmoothTransformation)
            picture.setPixmap(image)
            picture.adjustSize()
            return frame
        except Exception:
            g.trace('Bad image')
            g.es_exception()
            return None
    #@+node:ekr.20220126062304.1: *3* Dups.create_window
    def create_window(self, filenames):
        # Create the widget.
        self.window = window = QtWidgets.QWidget()
        window.setWindowTitle(f"{len(filenames)} duplicates of {filenames[0]}")
        window.setMinimumHeight(self.window_height)
        # Move the window.
        window.move(50, 50)
        # Set the layout.
        layout = QtWidgets.QHBoxLayout()
        window.setLayout(layout)
        # Create the subframes.
        for filename in filenames:
            frame = self.create_frame(filename, filenames[:], window)
            if frame:
                layout.addWidget(frame)
        # Show the window.
        window.show()
    #@+node:ekr.20220126064335.1: *3* Dups.delete_file
    send_to_trash_warning_given = False

    def delete_file(self, filename):
        """Issue a prompt and delete the file if the user agrees."""
        if not send2trash:
            if not self.send_to_trash_warning_given:
                self.send_to_trash_warning_given = True
                print("Deleting files requires send2trash")
                print("pip install Send2Trash")
                return
        if os.path.exists(filename):
            send2trash(filename)
            print('Deleted', filename)
        else:
            print('Not found', filename)
    #@+node:ekr.20220126064032.1: *3* Dups.find_duplicates
    def find_duplicates(self):
        """Find duplicates."""
        duplicates = []
        for h in self.hash_dict:
            aList = self.hash_dict.get(h)
            if len(aList) > 1:
                duplicates.append(aList)
        return duplicates
        
    #@+node:ekr.20220126060911.1: *3* Dups.get_files
    def get_files(self, path):
        """Return all files in path, including all subdirectories."""
        return [
            str(z) for z in pathlib.Path(path).rglob('*')
                if z.is_file()
                and os.path.splitext(str(z))[1].lower() in self.extensions
        ]
    #@+node:ekr.20220126060646.1: *3* Dups.run
    def run(self,
        c,  # Required. The commander for this slideshow.
        background_color = None,  # Default background color.
        extensions = None,  # List of file extensions.
        full_screen = False,  # True: start in full-screen mode.
        hash_size = 8,  # Size of compressed image.
        height = None,  # Window height (default 1500 pixels) when not in full screen mode.
        path = None,  # Root directory.
        max_open_windows = None,  # Maximum number of open windows.
        starting_directory = None,  # Starting directory for file dialogs.
        width = None,  # Window width (default 1500 pixels) when not in full screen mode.
    ):
        """
        Create the widgets and run the slideshow.
        Return True if any pictures were found.
        """
        # Init ivars.
        self.c = c
        self.background_color = background_color or "black"
        self.extensions = extensions or ['.jpeg', '.jpg', '.png']
        self.full_screen = False
        self.hash_size = hash_size or 8
        self.starting_directory = starting_directory or os.getcwd()
        self.window_height = height or 900
        self.window_width = width or 1500
        # Get the directory.
        if not path:
            dialog = QtWidgets.QFileDialog(directory=self.starting_directory)
            path = dialog.getExistingDirectory()
        if not path:
            print("No path given")
            return False
        # Get the files.
        filenames = self.get_files(path)
        if not filenames:
            print(f"No slides found in {path!r}")
            return False
        print(f"{len(filenames)} file{g.plural(len(filenames))} in {path}")
        print(f"\nPreprocessing with hash size {self.hash_size}. This may take awhile...")
        # Compute the hash dicts.
        t1 = time.process_time()
        self.compute_dicts(filenames)
        # Find the duplicates.
        t2 = time.process_time()
        duplicates = self.find_duplicates()
        t3 = time.process_time()
        g.es_print(f"{len(duplicates):4} duplicate sets")
        print(
            f"preprocess: {t2-t1:8.2} sec.\n"
            f"duplicates: {t3-t2:8.2} sec.\n"
            f"     total: {t3-t1:8.2} sec.")
        # Show the duplicates
        if max_open_windows:
            for aList in duplicates[:max_open_windows]:
                self.create_window(aList)
        else:
            for aList in duplicates[:]:
                self.create_window(aList)
        return True
    #@-others
#@-others

if __name__ == '__main__':
    main()
#@-leo
