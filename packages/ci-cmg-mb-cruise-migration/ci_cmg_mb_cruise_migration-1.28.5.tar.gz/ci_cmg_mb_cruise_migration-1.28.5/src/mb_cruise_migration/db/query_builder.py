class QueryBuilder(object):
    def __init__(self, schema):
        self.schema = schema + "."

    def select_query_size(self, query: str):
        return f"SELECT COUNT(*) FROM {query}"

    def select_all(self, table: str):
        return f"SELECT * FROM {self.schema}{table}"

    def select_all_where_fields_match(self, table: str, search_fields: dict):
        field_names = list(dict.keys(search_fields))
        search_values = list(dict.values(search_fields))

        query = f"SELECT * FROM {self.schema}{table} WHERE " + self.build_field_query_string(field_names)

        return query, search_values

    def select_some(self, table: str, wanted_fields: list):
        wanted_fields = ", ".join(wanted_fields)

        return f"SELECT {wanted_fields} FROM {self.schema}{table}"

    def select_some_constrained_by_field_values(self, table: str, wanted_fields: list, search_fields):
        field_names = list(dict.keys(search_fields))
        search_values = list(dict.values(search_fields))

        wanted_fields = ", ".join(wanted_fields)
        query = f"SELECT {wanted_fields} FROM {self.schema}{table} WHERE " + self.build_field_query_string(field_names)

        return query, search_values

    def select_survey_shape(self, table, ngdc_id, shape_field):
        query = f"SELECT SDO_UTIL.TO_WKTGEOMETRY({shape_field}) as {shape_field} FROM {self.schema}{table} WHERE NGDC_ID=:NGDC_ID"
        search_values = {'NGDC_ID': ngdc_id}

        return query, search_values

    def select_file_shape(self, table, data_file):
        query = f"SELECT SDO_UTIL.TO_WKTGEOMETRY(SHAPE) as SHAPE FROM {self.schema}{table} WHERE DATA_FILE=:DATA_FILE"
        search_values = {'DATA_FILE': data_file}
        return query, search_values

    @staticmethod
    def select_subset(view: str, skip: int, limit: int):
        return f"SELECT * FROM ({view}) ORDER BY NGDC_ID OFFSET {skip} ROWS FETCH NEXT {limit} ROWS ONLY"

    def insert(self, table: str, fields: dict):
        field_names = list(fields.keys())
        values = list(fields.values())

        bind_variables = self.build_bind_variables_string(field_names)
        field_names = self.build_fields_string(field_names)

        query = f"INSERT INTO {self.schema}{table} ({field_names}) VALUES ({bind_variables})"

        return query, values

    def insert_statement(self, table: str, fields: list):

        bind_variables = self.build_bind_variables_string(fields)
        field_names = self.build_fields_string(fields)

        return f"INSERT INTO {self.schema}{table} ({field_names}) VALUES ({bind_variables})"

    def delete_all_rows(self, table: str):
        return f"DELETE FROM {self.schema}{table}"

    @staticmethod
    def build_fields_string(keys: list):
        return ", ".join(keys)

    @staticmethod
    def build_bind_variables_string(keys):
        return ":" + ", :".join(keys)

    @staticmethod
    def build_field_query_string(field_names: list):
        fields = ""
        for i, arg in enumerate(field_names):
            fields += f"{arg}=:{arg}"  # :{arg} is the bind variable
            if i < len(field_names) - 1:
                fields += f" and "
        return fields
