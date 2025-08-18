"""
Implementation of `zut.db` for the MariaDB database backend.
"""
from __future__ import annotations

from typing import Any
from zut.db import DbObj
from zut.db.mysql import MysqlDb

class MariaDb(MysqlDb):
    scheme = 'mariadb'

    def _get_table_foreign_key_descriptions(self, table: DbObj) -> list[dict[str,Any]]:
        # (optimization compared to mysql version)
        sql = f"""
        SELECT
            fk.CONSTRAINT_NAME AS constraint_name
            ,cu.COLUMN_NAME AS column_name
            ,null AS related_schema
            ,r_uk.TABLE_NAME AS related_table
            ,r_cu.COLUMN_NAME AS related_column_name
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE cu ON cu.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA AND cu.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c ON c.COLUMN_NAME = cu.COLUMN_NAME AND c.TABLE_NAME = fk.TABLE_NAME AND c.TABLE_SCHEMA = fk.TABLE_SCHEMA AND c.TABLE_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON rc.TABLE_NAME = fk.TABLE_NAME AND rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME AND cu.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA AND cu.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS r_uk ON r_uk.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE') AND r_uk.TABLE_NAME = rc.REFERENCED_TABLE_NAME AND r_uk.CONSTRAINT_NAME = rc.UNIQUE_CONSTRAINT_NAME AND r_uk.CONSTRAINT_SCHEMA = rc.UNIQUE_CONSTRAINT_SCHEMA AND r_uk.CONSTRAINT_CATALOG = rc.UNIQUE_CONSTRAINT_CATALOG
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE r_cu ON r_cu.TABLE_NAME = r_uk.TABLE_NAME AND r_cu.CONSTRAINT_NAME = r_uk.CONSTRAINT_NAME AND r_cu.CONSTRAINT_SCHEMA = r_uk.CONSTRAINT_SCHEMA AND r_cu.CONSTRAINT_CATALOG = r_uk.CONSTRAINT_CATALOG AND r_cu.ORDINAL_POSITION = cu.ORDINAL_POSITION
        WHERE fk.CONSTRAINT_TYPE = 'FOREIGN KEY' AND fk.TABLE_SCHEMA = DATABASE() AND fk.TABLE_NAME = {self._pos_placeholder}
        ORDER BY c.ORDINAL_POSITION
        """
        return self.get_dicts(sql, [table.name])
