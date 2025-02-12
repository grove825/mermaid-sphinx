"""Tests for `mermaid_sphinx`package."""

import pytest


@pytest.fixture
def build_all(app):
    """Build all files in the Sphinx app."""
    app.builder.build_all()


@pytest.fixture
def index(app, build_all):  # noqa: ARG001
    """Return the content of the index.html file."""
    return (app.outdir / "index.html").read_text().replace("<script >", "<script>")


@pytest.mark.sphinx("html", testroot="file")
def test_html_raw__file_input__correctly_parsed(index):
    assert "mermaid.run()" in index
    assert (
        '<script type="module" src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs"></script>' in index
    )
    assert (
        '<script type="module">'
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs";'
        "mermaid.initialize({startOnLoad:false});</script>" in index
    )
    assert (
        """<pre class="mermaid">
           sequenceDiagram
      Alice-&gt;John: Hello John, how are you?
      John--&gt;&gt;Alice: Great!
      Alice-)John: See you later!

    </pre>"""
        in index
    )


@pytest.mark.sphinx("html", testroot="file")
def test_html__file_input__link_not_available(index):
    assert "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" not in index


@pytest.mark.sphinx("html", testroot="file_not_found")
def test_html_raw__file_not_available__warning(index, warning):
    assert "mermaid.run()" not in index
    assert "File: '" in warning.getvalue()
    assert "' does not exist" in warning.getvalue()


@pytest.mark.sphinx("html", testroot="file_icon_fa")
def test_html__file_icon_font_awesome__link_available(index):
    assert "mermaid.run()" in index
    assert "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" in index


@pytest.mark.sphinx("html", testroot="file_icon_mdi")
def test_html__file_icon_material_design__link_available(index):
    assert "mermaid.run()" in index
    assert "https://cdn.materialdesignicons.com/6.5.95/css/materialdesignicons.min.css" in index


@pytest.mark.sphinx("html", testroot="file_icon_unknown")
def test_html__file_icon_unknown__link_not_available(index):
    assert "mermaid.run()" in index
    assert "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" not in index


@pytest.mark.sphinx("html", testroot="file_empty")
def test_html_raw__file_empty__warning(index, warning):
    assert "mermaid.run()" not in index
    assert 'ERROR: Error in "mermaid" directive:\n' in warning.getvalue()
    assert "1 argument(s) required, 0 supplied.\n" in warning.getvalue()
