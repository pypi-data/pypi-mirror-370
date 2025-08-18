from ..enums.filters import *
from ..filters import Q


class Table():
    def __init__(self, db, name: str):
        self.db = db
        self.table_name = name
        self.filters = []
        self.params = []
        self.tables = []

    def check_column(self, column_name):
        return self.db.check_column(self.table_name, column_name)

    def get_dict_list(self, cursor):
        keys = cursor.description
        values = cursor.fetchall()

        if not values:
            return []
        keys = [k[0] for k in keys]

        data = []
        while values:
            data.append(dict(zip(keys, values.pop())))
        return data

    def get_dict(self, cursor):
        keys = cursor.description
        value = cursor.fetchone()
        if not value:
            return {}

        return dict(zip([k[0] for k in keys], value))

    def get_from_clause(self):
        base = self.table_name
        if self.tables:
            return base + " " + " ".join(self.tables)
        return base

    def all(self, **kwargs):
        conditions = self.get_conditions()
        from_clause = self.get_from_clause()

        cursor = self.db.execute(f'SELECT * FROM {from_clause}' + conditions, self.params)
        return self.get_dict_list(cursor)

    def one(self, **kwargs):
        conditions = self.get_conditions()
        from_clause = self.get_from_clause()

        cursor = self.db.execute(f'SELECT * FROM {from_clause}' + conditions, self.params)
        return self.get_dict(cursor)

    def get(self, id):
        self.filters.append(("id = ?", id))
        conditions = self.get_conditions()
        self.filters.pop()

        cursor = self.db.execute(f'SELECT * FROM {self.table_name}' + conditions, self.params)
        return self.get_dict(cursor)

    def insert(self, **kwargs):
        self.db.execute(f'INSERT INTO {self.table_name} (' +
            f'{", ".join(kwargs.keys())}) ' +
            f'VALUES ({('?, ' * len(kwargs))[:-2]})',
                tuple(kwargs.values()))

    def update(self, **kwargs):
        conditions = self.get_conditions()
        from_clause = self.get_from_clause()

        updated_values = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        self.db.execute(f'UPDATE {from_clause} SET {updated_values}'
                        + conditions, list(kwargs.values()) + self.params)
        return True

    def delete(self, **kwargs):
        conditions = self.get_conditions()

        self.db.execute(f'DELETE FROM {self.table_name} ' + conditions, self.params)

    def filter(self, *args, **kwargs):
        new_table = Table(self.db, self.table_name)
        new_table.filters = self.filters[:]

        for expr, value in kwargs.items():
            if "__" in expr:
                field, lookup = expr.split("__", 1)
            else:
                field, lookup = expr, "exact"

            op = LOOKUPS.get(lookup)
            if not op:
                raise ValueError(f"Unknown lookup: {lookup}")

            if lookup == "exact":
                if isinstance(value, dict):
                    value = value.get('id', value)
                elif value is None:
                    expr_sql = f"{field} IS NULL"
                    new_table.filters.append((expr_sql,))
                    continue
            elif lookup == "contains":
                value = f"%{value}%"
            elif lookup == "startswith":
                value = f"{value}%"
            elif lookup == "endswith":
                value = f"%{value}"
            elif lookup == "icontains":
                value = f"%{value.lower()}%"
                expr_sql = f"LOWER({field}) {op} ?"
                new_table.filters.append((expr_sql, value))
                continue
            elif lookup == "null":
                expr_sql = f"{field} IS NULL"
                new_table.filters.append((expr_sql,))
                continue
            elif lookup == "notnull":
                expr_sql = f"{field} IS NOT NULL"
                new_table.filters.append((expr_sql,))
                continue

            expr_sql = f"{field} {op} ?"
            new_table.filters.append((expr_sql, value))

        for q in args:
            if not isinstance(q, Q):
                raise ValueError("filter() args must be Q objects")
            for sql, params in q.children:
                new_table.filters.append((sql, *params))

        return new_table

    def join(self, new_table, new_table_field, field, join_type="INNER"):
        if not isinstance(new_table, Table):
            raise ValueError("join() expects a Table instance")

        join_sql = f"{join_type} JOIN {new_table.table_name} ON {self.table_name}.{field} = {new_table.table_name}.{new_table_field}"
        tbl = Table(self.db, self.table_name)
        tbl.filters = self.filters[:]
        tbl.tables = self.tables[:] + [join_sql]
        return tbl

    def get_conditions(self):
        if self.filters:
            where_clauses = [f[0] for f in self.filters]
            
            self.params = []
            for filter in self.filters:
                self.params.extend(filter[1:])
            
            return " WHERE " + " AND ".join(where_clauses)
        return ""
