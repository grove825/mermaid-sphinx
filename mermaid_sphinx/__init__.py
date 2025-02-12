"""A Sphinx extension to include Mermaid diagrams in the documentation."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sphinx.writers.html5
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx


class Mermaid(nodes.General, nodes.Element):
    """A node to store Mermaid code."""


def visit_mermaid_node(self: sphinx.writers.html5.HTML5Translator, node: Mermaid) -> None:
    """Visit the node."""
    encode = self.encode(node["code"])
    if "::icon" in encode:
        for line in encode.split("\n"):
            if "::icon" in line:
                icon_text = line.split("(", 1)[1].split(")", 1)[0].strip()
                if icon_text.startswith("fa"):
                    self.builder.config.mermaid_sphinx_config["font_awesome"] = True
    tag_template = f"""<pre class="mermaid">
        {encode}
    </pre>"""
    self.body.append(tag_template)


def depart_mermaid_node(_self: sphinx.writers.html5.HTML5Translator, _node: Mermaid) -> None:
    """
    Leave the node.

    This function can be empty if no specific action is needed on departure
    """


class MermaidDirective(Directive):
    """A directive to include Mermaid diagrams in the documentation."""

    has_content = True
    required_arguments = 1

    def run(self) -> Sequence[nodes.Node]:
        """
        Run the directive.

        Returns:
            Sequence[nodes.Node]: A list of nodes.
        """
        file_path = Path(self.state.document.settings.env.srcdir) / self.arguments[0]
        if file_path.exists():
            content = Path(file_path).read_text()
        else:
            return [self.state_machine.reporter.warning(f"File: '{file_path}' does not exist", line=self.lineno)]

        node = Mermaid()
        node["code"] = content
        return [node]


def install_js(
    app: Sphinx,
    _pagename: str,
    _templatename: str,
    _context: dict[str, Any],
    doctree: nodes.document | None,
) -> None:
    """
    Add the necessary JavaScript to the HTML context.

    Args:
        app: The Sphinx application object.
        _pagename: The name of the page.
        _templatename: The name of the template.
        _context: The context dictionary.
        doctree: The document tree.

    """
    if doctree and not doctree.next_node(Mermaid):
        return
    init = "mermaid.initialize({startOnLoad:false});"
    mermaid_js_url = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs"
    import_init = f'import mermaid from "{mermaid_js_url}";{init}'
    mermaid_run = f"""
    import mermaid from "{mermaid_js_url}";
    window.addEventListener("load", () => mermaid.run());
    """
    if app.config.mermaid_sphinx_config["font_awesome"]:
        app.add_css_file("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css")

    app.add_js_file(mermaid_js_url, type="module")

    app.add_js_file(None, body=import_init, type="module")
    app.add_js_file(None, body=mermaid_run, type="module")


def setup(app: Sphinx) -> dict[str, str | bool]:
    """
    Setup function for the extension.

    Args:
        app: The Sphinx application object.

    Returns:
        A dictionary containing the version of the extension, and whether it is parallel read and write safe
    """
    app.add_node(Mermaid, html=(visit_mermaid_node, depart_mermaid_node))
    app.add_directive("mermaid", MermaidDirective)
    app.add_config_value("mermaid_sphinx_config", {"font_awesome": False}, "env")

    app.connect("html-page-context", install_js)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
