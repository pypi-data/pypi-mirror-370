import argparse
import gettext
import os
import threading
import time

# import pkg_resources
from importlib.metadata import version  # , PackageNotFoundError
from packaging.requirements import Requirement
from packaging.version import parse as parse_version

from collections import defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler

# from tempfile import TemporaryDirectory
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from graphviz import Source

from .generate import generate, generate_pdf

import hashlib

# __version__ = "3.0.1" #pkg_resources.require("prezentprogramo")[0].version
__version__ = parse_version(version(Requirement("prezentprogramo").name))


class YoGraphvizDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        "alt": str,
        "height": int,
        "width": int,
        "scale": float,
        "align": str,
        "class": str,
    }

    count = 0

    def run(self):
        graphviz_code = "\n".join(self.content)
        options = self.options

        try:
            # Get the path of the input .rst file
            rst_file_path = os.path.abspath(self.state.document.current_source)
            rst_directory = os.path.dirname(rst_file_path)
            rst_filename = os.path.splitext(os.path.basename(rst_file_path))[0]

            # Create a 'img' directory inside the same directory as the input .rst file
            graphs_directory = os.path.join(rst_directory, rst_filename, "img")
            os.makedirs(graphs_directory, exist_ok=True)

            # Generate the graph image using Graphviz and save it to the 'img' directory
            dot = Source(graphviz_code)
            dot.format = "png"  # Output format

            # Increment the count for each instance
            self.__class__.count += 1

            graph_filename = "yoo_graphviz_"
            graph_filename += hashlib.md5(graphviz_code.encode("utf-8")).hexdigest()

            graph_path = os.path.join(graphs_directory, graph_filename)

            if not os.path.exists(graph_path):
                dot.render(filename=graph_path, cleanup=True, format="png", quiet=True)
            relative_image_path = os.path.relpath(graph_path, rst_directory)

            if not relative_image_path.endswith(".png"):
                relative_image_path = f"{relative_image_path}.png"
            image_node = nodes.image(uri=relative_image_path, format="png")

            # Apply options to the image node
            if "alt" in options:
                image_node["alt"] = options["alt"]
            if "class" in options:
                image_node["classes"] += options["class"].split()
            if "width" in options:
                image_node["width"] = options["width"]
            if "height" in options:
                image_node["height"] = options["height"]
            if "scale" in options:
                image_node["scale"] = options["scale"]
            if "align" in options:
                image_node["align"] = options["align"]
            return [image_node]

        except Exception as e:
            error_node = nodes.error()
            error_node += nodes.Text(f"Error generating Graphviz image: {str(e)}")
            return [error_node]


directives.register_directive("yographviz", YoGraphvizDirective)

'''
# https://github.com/liuyug/python-docutils-graphviz/blob/master/docutils_graphviz.py
# https://graphviz.readthedocs.io/en/stable/manual.html
# https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Digraph.pipe
# https://pypi.org/project/beautifulsoup4/
# https://www.crummy.com/software/BeautifulSoup/
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://stackabuse.com/parsing-xml-with-beautifulsoup-in-python/
# https://www.tutorialspoint.com/beautiful_soup/beautiful_soup_souping_the_page.htm
# https://developer.mozilla.org/en-US/docs/Web/SVG
# https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Adding_vector_graphics_to_the_Web

# pip3 install beautifulsoup4

import graphviz
from bs4 import BeautifulSoup

gfc="""
  digraph {
    rankdir = "LR";
    node [shape=circle];
    END [shape=doublecircle, label="2"];
    B [shape=plaintext];
    0 -> 1 [label="+"];
    1 -> END [label="E"];
    0 -> END [label="λ"];
  }
"""

dot = graphviz.Source(gfc)
fullDocTypeSvg = dot.pipe(encoding='utf-8', format='svg', quiet=True)
#soup = BeautifulSoup(fullDocTypeSvg, 'html.parser')
#soup = BeautifulSoup(fullDocTypeSvg, 'html5lib')
soup = BeautifulSoup(fullDocTypeSvg, 'xml')
soupJustSvg = soup.find('svg')

# https://developer.mozilla.org/en-US/docs/Web/SVG

if soupJustSvg:
  if 'class' in options:
      soupJustSvg.attrs['classes'] += options['class'].split()
  if 'width' in options:
      soupJustSvg.attrs['width'] = options['width']
  if 'height' in options:
      soupJustSvg.attrs['height'] = options['height']
  if 'scale' in options:
      soupJustSvg.attrs['scale'] = options['scale']
  if 'align' in options:
      soupJustSvg.attrs['align'] = options['align']
  img = Str(soupJustSvg)
else:
  img = 'It is not SVG'

return [nodes.raw('', img, format='html')]
'''


class HovercraftEventHandler(FileSystemEventHandler):
    def __init__(self, filelist):
        self.filelist = filelist
        self.quit = False
        super().__init__()

    def on_modified(self, event):
        self._update(event.src_path)

    def on_created(self, event):
        self._update(event.src_path)

    def on_moved(self, event):
        self._update(event.dest_path)

    def _update(self, src_path):
        if self.quit:
            return
        if src_path in self.filelist:
            print("File %s modified, update presentation" % src_path)
            self.quit = True


def generate_and_observe(args, event):
    while event.isSet():
        # Generate the presentation
        monitor_list = generate(args)
        print("Presentation generated.")

        # Make a list of involved directories
        directories = defaultdict(list)
        for file in monitor_list:
            directory, filename = os.path.split(file)
            directories[directory].append(filename)

        observer = Observer()
        handler = HovercraftEventHandler(monitor_list)
        for directory, files in directories.items():
            observer.schedule(handler, directory, recursive=False)

        observer.start()
        while event.wait(1):
            time.sleep(0.05)
            if handler.quit:
                break

        observer.stop()
        observer.join()


def yoo_run_browser(bind: str, port: int):
    time.sleep(0.1)
    import webbrowser

    webbrowser.open_new("http://" + bind + ":" + str(port))


def main(args=None):
    parser = create_arg_parser()
    args = parser.parse_args(args=args)

    if args.pdf_output_path:  # Check if the -pdf switch is provided
        generate_pdf(args)
    else:
        serve_presentation(args)


def create_arg_parser():
    # That the argparse default strings are lowercase is ugly.

    def my_gettext(s):
        return s.capitalize()

    gettext.gettext = my_gettext

    parser = argparse.ArgumentParser(
        description="Create impress.js presentations with reStructuredText",
        add_help=False,
    )
    parser.add_argument(
        "presentation",
        metavar="<presentation>",
        help="The path to the reStructuredText presentation file.",
    )
    parser.add_argument(
        "targetdir",
        metavar="<targetdir>",
        nargs="?",
        help=(
            "The directory where the presentation is saved. Will be created "
            "if it does not exist. If you do not specify a targetdir "
            "prezentprogramo will instead start a webserver and serve the "
            "presentation from that server."
        ),
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help.")
    parser.add_argument(
        "-t",
        "--template",
        help=(
            "Specify a template. Must be a .cfg file, or a directory with a "
            "template.cfg file. If not given it will use a default template."
        ),
    )
    parser.add_argument(
        "-c",
        "--css",
        help=(
            "An additional css file for the presentation to use. "
            "See also the ``:css:`` settings of the presentation."
        ),
    )
    parser.add_argument(
        "-j",
        "--js",
        help=(
            "An additional javascript file for the presentation to use. Added as a js-body script."
            "See also the ``:js-body:`` settings of the presentation."
        ),
    )
    parser.add_argument(
        "-a",
        "--auto-console",
        action="store_true",
        help=(
            "Open the presenter console automatically. This is useful when "
            "you are rehearsing and making sure the presenter notes are "
            "correct. You can also set this by having ``:auto-console: "
            "true`` first in the presentation."
        ),
    )
    parser.add_argument(
        "-s",
        "--skip-help",
        action="store_true",
        help=("Do not show the initial help popup."),
    )
    parser.add_argument(
        "-n",
        "--skip-notes",
        action="store_true",
        help=("Do not include presenter notes in the output."),
    )
    parser.add_argument(
        "-p",
        "--port",
        default="0.0.0.0:8000",
        help=(
            "The address and port that the server uses. "
            "Ex 8080 or 127.0.0.1:9000. Defaults to 0.0.0.0:8000."
        ),
    )
    parser.add_argument(
        "--mathjax",
        default=os.environ.get(
            "HOVERCRAFT_MATHJAX" "js/MathJax/es5/tex-mml-chtml.js",
            # "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML",
        ),
        help=(
            "The URL to the mathjax library."
            " (It will only be used if you have rST ``math::`` in your document)"
        ),
    )
    parser.add_argument(
        "-N",
        "--slide-numbers",
        action="store_true",
        help=("Show slide numbers during the presentation."),
    )
    parser.add_argument(
        "-d",
        "--default-movement",
        help=(
            "The default value of moving to the right in pixel during presentation execution."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        # help=('Display version and exit.'),
        version="prezentprogramo %s" % __version__,
    )
    parser.add_argument(
        "-pdf",
        "--pdf",
        help="Path to the output PDF file",
        action="store",
        dest="pdf_output_path",
    )  # -pdf switch

    return parser


def serve_presentation(args):

    # Check whether the file or folder as input exists.
    if not os.path.exists(os.path.abspath(args.presentation)):
        print(f"File or folder '{args.presentation}' does not exists.")
        exit(-1)

    # XXX Bit of a hack, clean this up, I check for this twice, also in the template.
    if args.template and args.template not in ("simple", "default"):
        args.template = os.path.abspath(args.template)

    if args.targetdir:
        # Generate the presentation
        generate(args)
    else:
        # Server mode. Start a server that serves a temporary directory.
        args.presentation = os.path.abspath(args.presentation)
        dir_name = os.path.dirname(args.presentation)
        file_name = os.path.basename(args.presentation)
        targetdir_name = os.path.splitext(file_name)[0]
        targetdir = os.path.join(dir_name, targetdir_name)
        args.targetdir = targetdir

        # Create the directory if it doesn't exist
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)

        # Set up watchdog to regenerate presentation if saved.
        event = threading.Event()
        event.set()
        thread = threading.Thread(target=generate_and_observe, args=(args, event))

        try:
            # Serve presentation
            if ":" in args.port:
                bind, port = args.port.split(":")
            else:
                bind, port = "0.0.0.0", args.port
            port = int(port)

            # First create the server. This checks that we can connect to
            # the port we want to.
            os.chdir(targetdir)
            server = HTTPServer((bind, port), SimpleHTTPRequestHandler)
            print("Serving HTTP on", bind, "port", port, "...")

            th1 = threading.Thread(
                target=yoo_run_browser,
                args=(
                    bind,
                    port,
                ),
            )

            try:
                # Now generate the presentation
                th1.start()

                thread.start()

                try:
                    # All is good, start the server
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("\nKeyboard interrupt received, exiting.")
                finally:
                    # Server exited
                    server.server_close()

            finally:
                # Stop the generation thread
                event.clear()
                # Wait for it to end
                thread.join()
                th1.join()

        except PermissionError:
            print("Can't bind to port %s:%s: No permission" % (bind, port))
        except OSError as e:
            if e.errno == 98:
                print("Can't bind to port %s:%s: port already in use" % (bind, port))
            else:
                raise
