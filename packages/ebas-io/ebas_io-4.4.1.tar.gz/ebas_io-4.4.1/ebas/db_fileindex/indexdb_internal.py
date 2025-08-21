"""
$Id: indexdb_internal.py 2266 2019-04-10 07:42:19Z pe $

DB layer for fileindex db.
The fileindex IndexDBInternal is a sqlite3 DB used internally in ebas.
"""
from textwrap import dedent
from databases.sqlite import SqliteDb


class IndexDbInternal(SqliteDb):
    """
    EBAS fileindex DB I/O class.
    """

    def __init__(self, filename, timestamp):
        """
        Initialize DB connection. Open DB, create tables.
        Parameters:
            filename   filename for the database. If prepended with '+', ignore
                       errors while creating tables.
        """
        super(IndexDbInternal, self).__init__(filename)
        self.timestamp = timestamp

    def insert_file_obj(self, ebasfile):
        """
        Main trigger method: perform all inserts reated to the data file.
        Parameters:
            ebasfile   ebas.io.file.EbasFile object
        Returns:
            None
        """
        file_dict = {
             'filename': ebasfile.metadata.filename,
             'first_start': ebasfile.sample_times[0][0],
             'first_end': ebasfile.sample_times[0][1],
             'last_start': ebasfile.sample_times[-1][0],
             'last_end': ebasfile.sample_times[-1][1],
        }
        self.insert_file(file_dict)

        var_meta = ('setkey', 'filename')
        for i in range(len(ebasfile.variables)):
            var_dict = {key: ebasfile.get_meta_for_var(i, key)
                        for key in var_meta}
            self.insert_variable(var_dict)

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
        self.create_table_update()
        self.create_table_file()
        self.create_table_variable()
        self.dbh.commit()
        self.logger.debug("tables created")

    def create_table_update(self):
        """
        Create file table.
        """
        self.dbh.execute(dedent("""\
            create table update_log
            (
               update_ts timestamp primary key)
            """))

    def create_table_file(self):
        """
        Create file table.
        """
        self.dbh.execute(dedent("""\
            create table file
            (
               filename TEXT not NULL primary key,
               first_start TEXT not NULL,
               first_end TEXT not NULL,
               last_start TEXT not NULL,
               last_end TEXT not NULL)
            """))

    def create_table_variable(self):
        """
        Create variable table.
        """
        self.dbh.execute(dedent("""\
            create table variable
            (
               setkey INTEGER not NULL,
               filename TEXT not NULL)
            """))

    def insert_update(self, update_dict):
        """
        Insert file metadata into the IndexDbInternal.
        """
        self.dbh.execute(dedent("""\
            insert into update_log values
               (:update_ts)
            """), update_dict)
        self.dbh.commit()

    def get_last_update(self):
        """
        Get the last update date from the index database.
        """
        curs = self.dbh.execute(
            "select max(update_ts) as 'update_ts [timestamp]' from update_log")
        # !!!
        # as 'update_ts [timestamp]'
        # is necessary to trigger conversion from timestamp to datetime.dateime
        return curs.fetchall()[0][0]

    def expand_reexport(self, setkeys):
        """
        Expands the set of data to be re-exported.
        Parameters:
            setkeys   set of setkeys to be re-exported (will be extended)
        Returns:
            tuple (set of filenames to be deleted,
                   set of datasets to be exported)
        """
        filenames = set()
        curs = self.dbh.cursor()
        new_setkeys = setkeys.copy()
        self.logger.info("%d setkeys for reexport: %s",
                          len(new_setkeys), new_setkeys)
        while new_setkeys:
            # select all files where the setkeys are in:
            curs = self.dbh.execute(dedent("""\
                select distinct filename
                from variable
                where setkey in ({})
                """.format(','.join('?'*len(new_setkeys)))),
                list(new_setkeys))
            new_filenames =  [x[0] for x in curs.fetchall()]
            filenames = filenames.union(new_filenames)
            self.logger.info("%d files affected: %s",
                              len(new_filenames), new_filenames)
            # ... and mark the new_setkeys as deleted
            self.dbh.execute(dedent("""\
                delete from variable
                where setkey in ({})
                """.format(','.join('?'*len(new_setkeys)))),
                tuple(new_setkeys))

            # and add the new setkeys:
            setkeys = setkeys.union(new_setkeys)

            # now select all setkeys which were in the same files
            curs = self.dbh.execute(dedent("""\
                select distinct setkey
                from variable
                where filename in ({})
                """.format(','.join('?'*len(new_filenames)))),
                tuple(new_filenames))
            new_setkeys = [x[0] for x in curs.fetchall()]
            self.logger.info("%d additional setkeys in the same files: %s",
                              len(new_setkeys), new_setkeys)
            # mark the files as deleted:
            if new_filenames:
                self.dbh.execute(dedent("""\
                    delete from file
                    where filename in ({})
                    """.format(','.join('?'*len(new_filenames)))),
                    tuple(new_filenames))
        return filenames, setkeys

    def insert_file(self, file_dict):
        """
        Insert file metadata into the IndexDbInternal.
        """
        file_dict = file_dict.copy()
        self.dbh.execute(dedent("""\
            insert into file
               (filename, first_start, first_end, last_start, last_end)
            values
               (:filename, :first_start, :first_end, :last_start, :last_end)
            """), file_dict)
        self.dbh.commit()

    def select_oldfiles(self, timestamp):
        """
        Selects all files which do not have any data after timestamp.
        Parameters:
            timestamp      timestamp for selecting old files
        Returns:
            iterator of filenames
        """
        curs = self.dbh.execute(
            "select filename from file where last_end < ?",
            (timestamp,))
        for res in curs.fetchall():
           yield res[0]

    def delete_oldfile(self, filename):
        """
        Delete old file (cascade variables) from the index db.
        Parameters:
            filename    filename of the file
        """
        self.dbh.execute(dedent("""\
            delete from variable
            where filename=?"""),
            (filename,))
        self.dbh.execute(dedent("""\
            delete from file
            where filename=?"""),
            (filename,))

    def insert_variable(self, var_dict):
        """
        Insert metadata for one variable of one file into the IndexDbInternal.
        """
        var_dict = var_dict.copy()
        self.dbh.execute(dedent("""\
            insert into variable
               (setkey, filename)
            values
               (:setkey, :filename)
            """), var_dict)
        self.dbh.commit()
