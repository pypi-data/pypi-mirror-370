from os import path
from sqlite3 import Connection
from .models.fileds import BaseColumn, ForeignColumn
import logging


class SQLiteORM():
    tables = []

    def __init__(self, db_name):
        self.db_name = db_name
        if not path.exists(db_name):
            logging.info("Creating database")
            self.execute('SELECT 1')

    def check_table(self, table_name):
        return table_name in [
            table[0] for table in self.execute(
                'SELECT name FROM sqlite_master WHERE type="table"').fetchall()]

    def create_table(self, table_name, fields=['id INTEGER PRIMARY KEY AUTOINCREMENT']):
        self.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)})')

    def check_column(self, table_name, column_name):
        return column_name in [
            column[1] for column in self.execute(f'PRAGMA table_info({table_name})').fetchall()]

    def execute(self, query, values=()):
        logging.debug(query)
        with Connection(self.db_name) as connection:
            return connection.cursor().execute(query, values)

    def add_table(self, table):
        self.tables.append(table)
        if not self.check_table(table.table_name):
            columns = {
                name: column 
                for name, column in vars(type(table)).items()
                if isinstance(column, BaseColumn)
            }

            fields = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
            references = []
            
            for column in columns:
                ldict = {}
                exec(f"params = " + "table." + column + ".params()", locals(), ldict)
                
                fields.append(f'{column} {columns[column].type} {ldict.get('params', '')}')

                if isinstance(columns[column], ForeignColumn):
                    exec(f"reference = " + "table." + column + ".constraint()", locals(), ldict)
                    references.append(ldict.get('reference', ''))

            fields.extend(references)

            self.create_table(table.table_name, fields)

        else:
            self.migrate()

    def migrate(self):
        for table in self.tables:
            columns = {
                name: column 
                for name, column in vars(type(table)).items()
                if isinstance(column, BaseColumn)
            }
            for column in columns:
                exec("table." + column + ".create_column(table)")