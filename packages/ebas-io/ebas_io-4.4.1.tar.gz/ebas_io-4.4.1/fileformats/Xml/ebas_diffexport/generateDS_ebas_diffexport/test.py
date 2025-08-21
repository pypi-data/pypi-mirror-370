#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import sys
from . import ebas_diffexport
import datetime
import pytz

state = datetime.datetime.utcnow()
state = pytz.utc.localize(state)
diff = ebas_diffexport.diffExportType(
    dbState=state,
    diffState=datetime.datetime(2016, 1, 1, tzinfo=pytz.timezone('UTC')))

start = datetime.datetime(2015, 1, 1, tzinfo=pytz.timezone('UTC'))
end = datetime.datetime(2015, 2, 1, tzinfo=pytz.timezone('UTC'))
deleted = ebas_diffexport.dataIntervalType(datasetKey=1, startTime=start, endTime=end)
diff.add_deleted(deleted)

start = datetime.datetime(2015, 3, 1, tzinfo=pytz.timezone('UTC'))
end = datetime.datetime(2015, 4, 1, tzinfo=pytz.timezone('UTC'))
deleted = ebas_diffexport.dataIntervalType(datasetKey=2, startTime=start, endTime=end)
diff.add_deleted(deleted)

start = datetime.datetime(2015, 1, 1, tzinfo=pytz.timezone('UTC'))
end = datetime.datetime(2016, 1, 1, tzinfo=pytz.timezone('UTC'))
added = ebas_diffexport.dataIntervalType(datasetKey=1, startTime=start, endTime=end)
diff.add_added(added)

start = datetime.datetime(2015, 1, 1, tzinfo=pytz.timezone('UTC'))
end = datetime.datetime(2016, 1, 1, tzinfo=pytz.timezone('UTC'))
added = ebas_diffexport.dataIntervalType(datasetKey=2, startTime=start, endTime=end)
diff.add_added(added)

#position=ebas.Position(gml.PointType(id='pos1', srsName='urn:ogc:def:crs:EPSG:6.6:4979', srsDimension=3, pos=gml.DirectPositionType(valueOf_='1 2 3')))
#res.add_DataSet(ebas.DataSetType(123456, 'NO0001R', 'Birkenes', 'filterpack', 'sulfate', Matrix='pm10', Unit='mg/m3', Statistics='arithmetic mean', ResolutionCode='1d', DataLevel='2', Position=position, HeightAGL=ebas.HeightAGL('m', 11), Values=(1,2,3,4,5)))
#result = ebas.Result()
#result.add_ResultSet(res)

sys.stdout.write('<?xml version="1.0" ?>\n')
diff.export(sys.stdout, 0, name_="diffExport")
