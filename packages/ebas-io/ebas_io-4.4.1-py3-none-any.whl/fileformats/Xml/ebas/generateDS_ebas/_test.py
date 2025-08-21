#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import sys
from . import ebas
from . import gml
import datetime
res = ebas.ResultSetType()
res.set_TimeDimension(ebas.TimeDimensionType(
   [datetime.datetime(2011,1,1), datetime.datetime(2011, 1, 2), datetime.datetime(2011,1,3), datetime.datetime(2011, 1, 4)],
   [datetime.datetime(2011,1,2), datetime.datetime(2011, 1, 3), datetime.datetime(2011,1,4), datetime.datetime(2011, 1, 5)]))


position=ebas.Position(gml.PointType(id='pos1', srsName='urn:ogc:def:crs:EPSG:6.6:4979', srsDimension=3, pos=gml.DirectPositionType(valueOf_='1 2 3')))
res.add_DataSet(ebas.DataSetType(123456, 'NO0001R', 'Birkenes', 'filterpack', 'sulfate', Matrix='pm10', Unit='mg/m3', Statistics='arithmetic mean', ResolutionCode='1d', DataLevel='2', Position=position, HeightAGL=ebas.HeightAGL('m', 11), Values=(1,2,3,4,5)))
result = ebas.Result()
result.add_ResultSet(res)

sys.stdout.write('<?xml version="1.0" ?>\n')
result.export(sys.stdout, 0, namespacedef_='xmlns:ebas="http://ebas.nilu.no/EBAS" xmlns:gml="http://www.opengis.net/gml/3.2"')
