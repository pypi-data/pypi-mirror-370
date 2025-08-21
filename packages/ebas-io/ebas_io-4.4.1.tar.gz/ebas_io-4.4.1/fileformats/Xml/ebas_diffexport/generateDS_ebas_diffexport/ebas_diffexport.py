from .generated.ebas_diffexport_generated import *
from .generated.ebas_diffexport_generated import quote_attrib, __all__

# force datetime in attribute export (dbState and diffState)
def exportAttributes(self, outfile, level, already_processed,
                     namespace_='diffexport:', name_='diffExportType'):
    if self.dbState is not None and 'dbState' not in already_processed:
        already_processed.add('dbState')
        outfile.write(' dbState=%s' % (quote_attrib(self.gds_format_datetime(
            self.dbState, input_name='dbState')), ))
    if self.diffState is not None and 'diffState' not in already_processed:
        already_processed.add('diffState')
        outfile.write(' diffState=%s' % (quote_attrib(self.gds_format_datetime(
            self.diffState, input_name='dbState')), ))
diffExportType.exportAttributes = exportAttributes

# avoid namespacedef_ in child element's export calls
def exportChildren(self, outfile, level, namespace_='diffexport:',
                   name_='diffExportType', fromsubclass_=False,
                   pretty_print=True):
    for deleted_ in self.deleted:
        deleted_.export(outfile, level, namespace_, name_='deleted',
                        pretty_print=pretty_print, namespacedef_='')
    for added_ in self.added:
        added_.export(outfile, level, namespace_, name_='added',
                      pretty_print=pretty_print, namespacedef_='')
diffExportType.exportChildren = exportChildren



# force datetime in attribute export (startTime and endTime)
def dit_exportAttributes(self, outfile, level, already_processed,
                         namespace_='diffexport:', name_='dataIntervalType'):
    if self.datasetKey is not None and 'datasetKey' not in already_processed:
        already_processed.add('datasetKey')
        outfile.write(' datasetKey="%s"' % self.gds_format_integer(
            self.datasetKey, input_name='datasetKey'))
    if self.startTime is not None and 'startTime' not in already_processed:
        already_processed.add('startTime')
        outfile.write(' startTime=%s' % (quote_attrib(self.gds_format_datetime(
            self.startTime, input_name="startTime")),))
    if self.endTime is not None and 'endTime' not in already_processed:
        already_processed.add('endTime')
        outfile.write(' endTime=%s' % (quote_attrib(self.gds_format_datetime(
            self.endTime, input_name="endTime")),))
dataIntervalType.exportAttributes = dit_exportAttributes

