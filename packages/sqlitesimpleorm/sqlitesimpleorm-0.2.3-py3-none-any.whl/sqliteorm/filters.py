from .enums.filters import LOOKUPS

class Q:
    def __init__(self, **kwargs):
        self.children = []
        for expr, value in kwargs.items():
            if "__" in expr:
                field, lookup = expr.split("__", 1)
            else:
                field, lookup = expr, "exact"

            op = LOOKUPS.get(lookup)
            if not op:
                raise ValueError(f"Unknown lookup: {lookup}")

            if lookup == "contains":
                value = f"%{value}%"
            elif lookup == "startswith":
                value = f"{value}%"
            elif lookup == "endswith":
                value = f"%{value}"
            elif lookup == "icontains":
                value = f"%{value.lower()}%"
                sql = f"LOWER({field}) {op} ?"
                self.children.append((sql, [value]))
                continue

            sql = f"{field} {op} ?"
            self.children.append((sql, [value]))

        self.connector = "AND"

    def __or__(self, other):
        q = Q()
        q.children = [(f"({a[0]} OR {b[0]})", a[1] + b[1])
                      for a in self.children for b in other.children]
        return q

    def __and__(self, other):
        q = Q()
        q.children = [(f"({a[0]} AND {b[0]})", a[1] + b[1])
                      for a in self.children for b in other.children]
        return q
