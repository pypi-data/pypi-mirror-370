"""
EBAS submission templates and template checks
"""

from logging import getLogger

class NoTemplate(Exception):
    """
    Exception raised when:
     - a specific template does not match (raised in a template class)
     - or no template can be found for a file (raised in get_template)
    """
    pass


class EbasTemplateBase(object):
    """
    Base class for template objects.
    """

    TEMPLATE_NAME = None  # needs to be set in each template

    def __init__(self, fil, ignore_templatecheck=False):
        """
        Initialize object for using it for a specific ebas-io file

        Parameters:
            fil    ebas io file object
        Returns:
            None
        Raises:
            NoTemplate if the template does not match for the file.
        """
        self.file = fil
        self.ignore_templatecheck = ignore_templatecheck
        self.logger = getLogger(self.__class__.__name__)
        self.match()

    def match(self):
        """
        See if this template matches a file.
        Must be implemented in each client class
        """
        raise NotImplementedError()

    def checkfile(self):
        """
        Check the file for template complience.
        """
        # TODO: default checks?
        self.special_checks()

    def special_checks(self):
        """
        Special checks which cannot be done in the defailt checks.
        Must be implemented in each client class
        """
        raise NotImplementedError()

    def error(self, *args, **kwargs):
        """
        Wrapper for self.file.error, adds template name
        """
        if self.ignore_templatecheck:
            self.warning(*args, **kwargs)
        else:
            self.file.error(*args,
                            prefix="Template '{}': ".format(self.TEMPLATE_NAME),
                            **kwargs)

    def warning(self, *args, **kwargs):
        """
        Wrapper for self.file.warning, adds template name
        """
        self.file.warning(*args,
                          prefix="Template '{}': ".format(self.TEMPLATE_NAME),
                          **kwargs)
