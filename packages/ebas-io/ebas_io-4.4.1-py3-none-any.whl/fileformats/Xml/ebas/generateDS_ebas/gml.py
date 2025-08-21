from .generated.gml_generated import *
from .generated.gml_generated import quote_attrib, ExternalEncoding, showIndent, __all__

# correct version of export
# This could also be done by changing GeneratedsSuper, but this way all changes
# are coded in this file.
def _export(self, outfile, level, namespace_='gml:', name_='DirectPositionType', namespacedef_='xmlns:gml="http://www.opengis.net/gml/3.2"', pretty_print=True):
    if pretty_print:
        eol_ = '\n'
    else:
        eol_ = ''
    if self.original_tagname_ is not None:
        name_ = self.original_tagname_
    showIndent(outfile, level, pretty_print)
    outfile.write('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
    already_processed = set()
    self.exportAttributes(outfile, level, already_processed, namespace_, name_='DirectPositionType')
    if self.hasContent_():
        outfile.write('>')
        res = []
        for val in self.valueOf_:
            res.append(str(val).encode(ExternalEncoding))
        outfile.write(' '.join(res))
        self.exportChildren(outfile, level + 1, namespace_='gml:', name_='DirectPositionType', pretty_print=pretty_print)
        outfile.write('</%s%s>%s' % (namespace_, name_, eol_))
    else:
        outfile.write('/>%s' % (eol_, ))
DirectPositionType.export=_export


# make attribute gml:id being printed with namespace
def _exportAttributes(self, outfile, level, already_processed, namespace_='gml:', name_='AbstractGMLType'):
    if self.id is not None and 'id' not in already_processed:
        already_processed.add('id')
        #outfile.write(' id=%s' % (self.gds_format_string(quote_attrib(self.id).encode(ExternalEncoding), input_name='id'), ))
        outfile.write(' %sid=%s' % (namespace_, self.gds_format_string(quote_attrib(self.id).encode(ExternalEncoding), input_name='id'), ))
    if self.extensiontype_ is not None and 'xsi:type' not in already_processed:
        already_processed.add('xsi:type')
        outfile.write(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        outfile.write(' xsi:type="%s"' % self.extensiontype_)

AbstractGMLType.exportAttributes = _exportAttributes
