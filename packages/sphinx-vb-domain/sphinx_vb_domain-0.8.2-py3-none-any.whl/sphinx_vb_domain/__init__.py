from sphinx.application import Sphinx

from .vb_autodoc import setup as setup_autodoc
from .vb_domain import setup as setup_domain

__version__ = '0.8.1'


def setup(app: Sphinx):
    '''Set up extension
    '''
    setup_autodoc(app)
    setup_domain(app)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
