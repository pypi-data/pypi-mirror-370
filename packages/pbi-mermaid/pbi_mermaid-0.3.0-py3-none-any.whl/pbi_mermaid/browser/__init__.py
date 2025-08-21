import os
import subprocess  # nosec B404
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import StrPath
from pathlib import Path

import jinja2

MERMAID_TEMPLATE = jinja2.Template((Path(__file__).parent / "template_advanced.html").read_text())


def render_html(html_path: "StrPath"):
    try:  # should work on Windows
        os.startfile(html_path)  # nosec B606
    except AttributeError:
        try:  # should work on MacOS and most linux versions
            subprocess.call(["open", html_path], shell=True)  # nosec B602, B607 - bandit hates with and without shell???
        except:  # noqa: E722
            print("Could not open URL")  # nosec


if __name__ == "__main__":
    render_html("https://stackoverflow.com")
