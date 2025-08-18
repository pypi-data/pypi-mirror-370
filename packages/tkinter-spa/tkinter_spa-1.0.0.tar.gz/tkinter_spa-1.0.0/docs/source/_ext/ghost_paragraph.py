"""
    This extension adds a directive that generates an empty <p> in the HTML DOM.
    Using standard reStructuredText label and :ref: role, it generates a link to
    relevant parts of the documentation without the need of section title or any
    visible elements.

    For example, this extension was motivated by creating an anchor right
    above a video without any title related.
"""

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class GhostParagraphDirective(SphinxDirective):

    required_arguments = 0

    def run(self):
        paragraph_node = nodes.paragraph()

        return [paragraph_node]

def setup(app: Sphinx):

    app.add_directive('ghost_paragraph', GhostParagraphDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
