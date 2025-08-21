"""
EBAS submission templates and template checks
"""

from .ozone import EbasTemplateOzone
from .nox import EbasTemplateNOxLev0, EbasTemplateNOxLev1
from .base import NoTemplate


ALL_TEMPLATES = [
    EbasTemplateOzone,
    EbasTemplateNOxLev0,
    EbasTemplateNOxLev1,
]


def get_template(fil, ignore_templatecheck=False):
    """
    Find the matching template definition for a given file object/

    Parameters:
        fil   ebas-io file object
    Returns:
        EbasTemplateXX one of the template objects
    Raises:
        NoTemplate when no matching template could be found
        RuntimeError on any fatal condition (e.g. multiple templates match)
    """
    ret = []
    for template in ALL_TEMPLATES:
        try:
            ret.append(template(fil, ignore_templatecheck=ignore_templatecheck))
        except NoTemplate:
            pass
    if not ret:
        raise NoTemplate()
    if len(ret) > 1:
        raise RuntimeError('Multiple matches: {}'.format(', '.join(
            [x.__class__.__name__ for x in ret])))
    return ret[0]
