"""
$Id: indexdb.py 2792 2022-03-18 13:15:32Z pe $

DB layer for fileindex db.
The fileindex IndexDB is a sqlite3 DB used to provide a basic metadata database
which can accompany a file archive (extracted from ebas).
"""
from textwrap import dedent
from databases.sqlite import SqliteDb


class IndexDb(SqliteDb):
    """
    EBAS fileindex DB I/O class.
    """

    def __init__(self, filename):
        """
        Initialize DB connection. Open DB, create tables.
        Parameters:
            filename   filename for the database. If prepended with '+', ignore
                       errors while creating tables.
        """
        super(IndexDb, self).__init__(filename)
        self._stationcodes = None

    def insert_file_obj(self, ebasfile):
        """
        Main trigger method: perform all inserts reated to the data file.
        Parameters:
            ebasfile   ebas.io.file.EbasFile object
        Returns:
            None
        """
        station_meta = (
            'station_code', 'platform_code', 'station_name',
            'station_wdca_id', 'station_gaw_name', 'station_gaw_id',
            'station_airs_id', 'station_other_ids', 'station_state_code',
            'station_landuse', 'station_setting', 'station_gaw_type',
            'station_wmo_region', 'station_latitude', 'station_longitude',
            'station_altitude')
        station_dict = {key: ebasfile.metadata[key] for key in station_meta}
        self.insert_station(station_dict)

        var_meta = ('station_code', 'matrix', 'comp_name', 'unit', 'statistics',
                    'instr_type', #'instr_ref',
                    'method',
                    'revdate', 'period', 'resolution', 'datalevel',
                    'filename')
        for i, var in enumerate(ebasfile.variables):
            var_dict = {key: ebasfile.get_meta_for_var(i, key)
                        for key in var_meta}
            var_dict['vnum'] = i
            var_dict['instr_ref'] = ebasfile.get_meta_for_var(i, 'lab_code') + \
                '_' + ebasfile.get_meta_for_var(i, 'instr_name')
            var_dict['first_start'] = ebasfile.sample_times[0][0]
            var_dict['first_end'] = ebasfile.sample_times[0][1]
            var_dict['last_start'] = ebasfile.sample_times[-1][0]
            var_dict['last_end'] = ebasfile.sample_times[-1][1]
            var_id = self.insert_variable(var_dict)
            for cha in var.metadata.characteristics:
                cha_dict = {
                    'var_id': var_id,
                    'ct_type': cha.CT_TYPE,
                    'datatype': cha.CT_DATATYPE,
                    }
                if cha.CT_DATATYPE == 'INT':
                    cha_dict['val_int'] = cha.DC_VAL_INT
                elif cha.CT_DATATYPE == 'DBL':
                    cha_dict['val_dbl'] = cha.DC_VAL_DBL
                else:
                    cha_dict['val_chr'] = cha.DC_VAL_CHR
                self.insert_characteristic(cha_dict)

    def create_tables(self):
        """
        Create all necessary tables.
        Parameters:
            None
        Returns:
            None
        Raises:
            IndexDbExists  when the tables already exist
        """
        self.create_table_station()
        self.create_table_variable()
        self.create_table_characteristic()
        self.dbh.commit()
        self.logger.debug("tables initialized")

    def create_table_station(self):
        """
        Create station table.
        """
        curs = self.dbh.cursor()
        curs.execute(dedent("""\
            create table station
            (
               station_code TEXT not NULL primary key,
               platform_code TEXT not NULL,
               station_name TEXT,
               station_wdca_id TEXT,
               station_gaw_name TEXT,
               station_gaw_id TEXT,
               station_airs_id TEXT,
               station_other_ids TEXT,
               station_state_code TEXT,
               station_landuse TEXT,
               station_setting TEXT,
               station_gaw_type TEXT,
               station_wmo_region INTEGER,
               station_latitude REAL,
               station_longitude REAL,
               station_altitude REAL)
            """))

    def create_table_variable(self):
        """
        Create station table.
        """
        curs = self.dbh.cursor()
        curs.execute(dedent("""\
            create table variable
            (
               var_id integer not null primary key,
               station_code TEXT not NULL references station (station_code),
               matrix TEXT not NULL,
               comp_name TEXT not NULL,
               unit TEXT not NULL,
               statistics TEXT not NULL,
               instr_type TEXT not NULL,
               instr_ref TEXT not NULL,
               method TEXT not NULL,
               first_start TEXT not NULL,
               first_end TEXT not NULL,
               last_start TEXT not NULL,
               last_end TEXT not NULL,
               revdate TEXT not NULL,
               period TEXT not NULL,
               resolution TEXT not NULL,
               datalevel TEXT,
               filename TEXT not NULL,
               vnum integer not null)
            """))

    def create_table_characteristic(self):
        """
        Create station table.
        """
        curs = self.dbh.cursor()
        curs.execute(dedent("""\
            create table characteristic
            (
               var_id integer not null references variable(var_id),
               ct_type text not null,
               datatype text not null,
               val_int integer,
               val_dbl float,
               val_chr text)
            """))

    @property
    def stationcodes(self):
        """
        Property for selecting a station code list.
        Parameters:
            None
        Returns:
            Station code list from table station.
        """
        if self._stationcodes is None:
            curs = self.dbh.cursor()
            curs.execute("select station_code from station")
            self._stationcodes = [x[0] for x in curs.fetchall()]
        return self._stationcodes

    def insert_station(self, station_dict):
        """
        Insert station metadata into the IndexDb.
        """
        if station_dict['station_code'] not in self.stationcodes:
            curs = self.dbh.cursor()
            curs.execute(dedent("""\
                insert into station
                   (station_code, platform_code, station_name,
                    station_wdca_id, station_gaw_name, station_gaw_id,
                    station_airs_id, station_other_ids, station_state_code,
                    station_landuse, station_setting, station_gaw_type,
                    station_wmo_region, station_latitude, station_longitude,
                    station_altitude)
                values
                   (:station_code, :platform_code, :station_name,
                    :station_wdca_id, :station_gaw_name, :station_gaw_id,
                    :station_airs_id, :station_other_ids, :station_state_code,
                    :station_landuse, :station_setting, :station_gaw_type,
                    :station_wmo_region, :station_latitude, :station_longitude,
                    :station_altitude)
                """), station_dict)
            self.dbh.commit()
            self._stationcodes.append(station_dict['station_code'])
            self.logger.debug("insert station %s", station_dict['station_code'])

    def insert_variable(self, var_dict):
        """
        Insert metadata for one variable of one file into the IndexDb.
        """
        curs = self.dbh.cursor()
        curs.execute(dedent("""\
            insert into variable
               (vnum, station_code, matrix, comp_name, unit, statistics,
                instr_type, instr_ref, method,
                first_start, first_end, last_start, last_end,
                revdate, period, resolution, datalevel,
                filename)
            values
               (:vnum, :station_code, :matrix, :comp_name, :unit, :statistics,
                :instr_type, :instr_ref, :method,
                :first_start, :first_end, :last_start, :last_end,
                :revdate, :period, :resolution, :datalevel,
                :filename)
            """), var_dict)
        var_id = curs.lastrowid
        self.dbh.commit()
        self.logger.debug("insert variable %s. var_id=%d", var_dict, var_id)
        return var_id

    def insert_characteristic(self, cha_dict):
        """
        Insert metadata for one characteristic of one variable of one file into
        the IndexDb.
        """
        curs = self.dbh.cursor()
        curs.execute(dedent("""\
            insert into characteristic
               (var_id, ct_type, datatype, val_{0})
            values
               (:var_id, :ct_type, :datatype, :val_{0})
            """.format(cha_dict['datatype'].lower())), cha_dict)
        self.dbh.commit()
        self.logger.debug("insert characteristic for variable {}", cha_dict)
