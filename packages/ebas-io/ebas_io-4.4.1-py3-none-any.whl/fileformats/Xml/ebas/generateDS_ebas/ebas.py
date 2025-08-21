from .generated.ebas_generated import *
from .generated.ebas_generated import GeneratedsSuper, showIndent, __all__

# "hook" gml Point into the ebas scheme
def _PosExportChildren(self, outfile, level, namespace_='ebas:', name_='PositionType', fromsubclass_=False, pretty_print=True):
    if pretty_print:
        eol_ = '\n'
    else:
        eol_ = ''
    if self.Point is not None:
        # pe:
        # < showIndent(outfile, level, pretty_print)
        # < outfile.write('<%sPoint>%s</%sPoint>%s' % (namespace_, self.gds_format_string(quote_xml(self.Point).encode(ExternalEncoding), input_name='Point'), namespace_, eol_))
        self.Point.export(outfile, level, namespace_='gml:', name_='Point', pretty_print=pretty_print)
Position.exportChildren = _PosExportChildren


# Add "Z" to datetime format
GeneratedsSuper.orig_gds_format_datetime = GeneratedsSuper.gds_format_datetime
def _gds_format_datetime(self, input_data, input_name=''):
    return self.orig_gds_format_datetime(input_data, input_name) + 'Z'
GeneratedsSuper.gds_format_datetime = _gds_format_datetime

# make Start and End Times lists of datetime
# This could partly also be done by changing GeneratedsSuper, but this way all
# changes are coded in this file.
def _gds_format_datetime_list(self, input_data, input_name=''):
    res = []
    for dat in input_data:
        res.append(self.gds_format_datetime(dat, input_name))
    return ' '.join(res)
GeneratedsSuper.gds_format_datetime_list = _gds_format_datetime_list
def _TdtExportChildren(self, outfile, level, namespace_='ebas:', name_='TimeDimensionType', fromsubclass_=False, pretty_print=True):
    if pretty_print:
        eol_ = '\n'
    else:
        eol_ = ''
    if self.StartTimes is not None:
        showIndent(outfile, level, pretty_print)
        outfile.write('<%sStartTimes>%s</%sStartTimes>%s' % (namespace_, self.gds_format_datetime_list(self.StartTimes, input_name='StartTimes'), namespace_, eol_))
    if self.EndTimes is not None:
        showIndent(outfile, level, pretty_print)
        outfile.write('<%sEndTimes>%s</%sEndTimes>%s' % (namespace_, self.gds_format_datetime_list(self.EndTimes, input_name='EndTimes'), namespace_, eol_))
TimeDimensionType.exportChildren = _TdtExportChildren

# correct version of format_float and gds_format_float_list
# This could also be done by changing GeneratedsSuper, but this way all changes
# are coded in this file.
def _gds_format_float(self, input_data, input_name=''):
    if input_data is None:
        return 'NaN'
    return str(input_data)
def _gds_format_float_list(self, input_data, input_name=''):
    res = []
    for val in input_data:
        res.append(self.gds_format_float(val, input_name))
    return ' '.join(res)
GeneratedsSuper.gds_format_float = _gds_format_float
GeneratedsSuper.gds_format_float_list = _gds_format_float_list
