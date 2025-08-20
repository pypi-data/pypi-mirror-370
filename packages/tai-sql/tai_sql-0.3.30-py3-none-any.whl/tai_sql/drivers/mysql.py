"""
Driver para MySQL/MariaDB
"""
import re
from sqlalchemy import URL, Column, ForeignKeyConstraint, Table
from typing import Dict, Any, List
from .base import DatabaseDriver, drivers
from tai_sql import pm, View

class MySQLDriver(DatabaseDriver):
    
    @property
    def name(self) -> str:
        return "mysql"
    
    @property
    def default_port(self) -> int:
        return 3306
    
    @property
    def default_database(self) -> str:
        return "mysql"
    
    def create_temp_url(self, username: str, password: str, host: str, 
                       port: int, database: str = None) -> URL:
        return URL.create(
            drivername="mysql",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database  # MySQL puede conectar sin especificar BD
        )
    
    def get_connect_args(self, timeout: int) -> Dict[str, Any]:
        return {
            "connect_timeout": timeout
        }
    
    def database_exists_query(self) -> str:
        return "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"
    
    def schema_exists_query(self) -> str:
        # En MySQL, database = schema
        return self.database_exists_query()
    
    def create_database_statement(self, database_name: str) -> str:
        return f"CREATE DATABASE IF NOT EXISTS `{database_name}`"
    
    def create_schema_statement(self, schema_name: str) -> str:
        # En MySQL, crear schema es igual que crear database
        return self.create_database_statement(schema_name)
    
    def get_ddl_prefix(self, schema_name: str) -> str:
        return f"`{schema_name}`." if schema_name else ''
    
    def supports_schemas(self) -> bool:
        return False  # MySQL usa databases en lugar de schemas
    
    @property
    def type_mapping(self) -> Dict[str, List[str]]:
        """Mapeo de tipos de datos de MySQL a SQLAlchemy"""
        return {
            'DATETIME': ['DATETIME', 'TIMESTAMP'],
            'TIME': ['TIME'],
            'INTEGER': ['INTEGER', 'INT'],
            'VARCHAR': ['VARCHAR', 'TEXT'],
            'BIGINT': ['BIGINT'],
            'FLOAT': ['FLOAT', 'DOUBLE'],
            'BOOLEAN': ['BOOLEAN', 'TINYINT(1)'],
            'TEXT': ['TEXT', 'LONGTEXT', 'MEDIUMTEXT'],
            'BYTES': ['BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'VARBINARY'],
        }
    
    def get_views_statement(self, schema_name: str = None) -> str:
        return """
            SELECT 
                TABLE_NAME as view_name,
                VIEW_DEFINITION as view_definition
            FROM information_schema.VIEWS
            WHERE TABLE_SCHEMA = DATABASE()
        """
    
    def normalize_query(self, query) -> str:
        """Normalización específica para MySQL"""
        # MySQL maneja backticks en nombres
        query = re.sub(r'`([^`]+)`', r'\1', query)
        return query
    
    def drop_view_statement(self, view_name, schema_name = None, view_definition = None) -> str:
        return f"DROP VIEW IF EXISTS `{view_name}`"
    
    def get_column_definition(self, column: Column) -> str:
        """Genera la definición de columna para MySQL"""
        column_type = str(column.type.compile(dialect=self._get_dialect()))

        if column_type in ('INTEGER', 'BIGINT') and column.autoincrement and column.primary_key:
            column_type = 'INT AUTO_INCREMENT'
        
        definition_parts = [self.reserved_word_mapper(column.name), column_type]
        
        if not column.nullable:
            definition_parts.append("NOT NULL")
        
        if column.server_default is not None:
            definition_parts.append(f"DEFAULT {self.get_default_value(column.server_default)}")
        
        if column.unique:
            definition_parts.append("UNIQUE")
        
        return " ".join(definition_parts)
    
    def alter_column_statements(self, table_name: str, column: Column) -> list[str]:
        """MySQL usa MODIFY COLUMN con la definición completa"""
        table_name = self.reserved_word_mapper(table_name)
        column_def = self.get_column_definition(column)
        
        return [f"ALTER TABLE {table_name} MODIFY COLUMN {column_def}"]
    
    def get_default_value(self, default) -> str:
        """Procesa el valor DEFAULT para MySQL"""
        if hasattr(default, 'arg'):
            value = default.arg
            if isinstance(value, str):
                if value.lower() in ['now', 'current_timestamp']:
                    return 'NOW()'
                return f"'{value}'"
            elif isinstance(value, bool):
                return '1' if value else '0'  # MySQL usa 1/0 para booleanos
            elif isinstance(value, (int, float)):
                return str(value)
            elif value is None:
                return 'NULL'
        
        str_value = str(default)
        if 'now' in str_value.lower():
            return 'NOW()'
        return f"'{str_value}'"
    
    def reserved_word_mapper(self, identifier: str) -> str:
        """Escapa identificadores para MySQL"""
        if identifier.lower() in self.reserved_words:
            return f"`{identifier}`"
        return identifier
    
    @property
    def reserved_words(self) -> set[str]:
        """Palabras reservadas de MySQL"""
        return {
            'user', 'order', 'group', 'table', 'index', 'view', 'database',
            'schema', 'column', 'row', 'select', 'insert', 'update', 'delete',
            'create', 'drop', 'alter', 'grant', 'revoke', 'commit', 'rollback',
            'transaction', 'begin', 'end', 'function', 'procedure', 'trigger',
            'constraint', 'primary', 'foreign', 'unique', 'check', 'default',
            'null', 'not', 'and', 'or', 'in', 'exists', 'between', 'like'
        }
    
    def create_table_statement(self, table: Table) -> str:
        """Genera CREATE TABLE para MySQL"""
        table_name = self.reserved_word_mapper(table.name)
        lines = [f"CREATE TABLE `{table_name}` ("]
        
        column_definitions = []
        for column in table.columns:
            column_def = self.get_column_definition(column)
            column_definitions.append(f"    {column_def}")
        
        constraint_definitions = []
        pk_columns = [col.name for col in table.columns if col.primary_key]
        if pk_columns:
            pk_def = f"    PRIMARY KEY ({', '.join([f'`{col}`' for col in pk_columns])})"
            constraint_definitions.append(pk_def)
        
        all_definitions = column_definitions + constraint_definitions
        lines.append(',\n'.join(all_definitions))
        lines.append(")")
        
        return '\n'.join(lines)

    def drop_table_statement(self, table_name: str, schema_name: str = None) -> str:
        """Genera DROP TABLE para MySQL"""
        escaped_table = self.reserved_word_mapper(table_name)
        
        if schema_name:
            # En MySQL, schema es equivalente a database
            return f"DROP TABLE IF EXISTS `{schema_name}`.`{escaped_table}`"
        else:
            return f"DROP TABLE IF EXISTS `{escaped_table}`"
    
    def foreign_key_statement(self, table: Table, fk: ForeignKeyConstraint) -> str:
        """Genera Foreign Key para MySQL"""
        try:
            table_name = self.reserved_word_mapper(table.name)
            
            local_columns_names = [f"`{col.name}`" for col in fk.columns]
            target_table_name = f"`{fk.referred_table.name}`"
            target_columns_names = [f"`{element.column.name}`" for element in fk.elements]
            
            constraint_name = f"fk_{table.name}_{fk.referred_table.name}"
            if len(constraint_name) > 64:  # MySQL limit
                import hashlib
                hash_suffix = hashlib.md5(constraint_name.encode()).hexdigest()[:8]
                constraint_name = f"fk_{hash_suffix}"
            
            local_columns_str = ", ".join(local_columns_names)
            target_columns_str = ", ".join(target_columns_names)
            
            statement = (
                f"ALTER TABLE `{table_name}` "
                f"ADD CONSTRAINT `{constraint_name}` "
                f"FOREIGN KEY ({local_columns_str}) "
                f"REFERENCES {target_table_name} ({target_columns_str})"
            )
            
            if hasattr(fk, 'ondelete') and fk.ondelete:
                statement += f" ON DELETE {fk.ondelete}"
            
            if hasattr(fk, 'onupdate') and fk.onupdate:
                statement += f" ON UPDATE {fk.onupdate}"
            
            return statement
            
        except Exception as e:
            raise Exception(f"   ⚠️  Error generando Foreign Key para {table.name}: {e}")
    
    def supports_materialized_views(self) -> bool:
        """MySQL no soporta vistas materializadas nativamente"""
        return False
    
    def create_view_statement(self, view: View) -> str:
        """Genera CREATE VIEW para MySQL"""
        view_name = self.reserved_word_mapper(view.__tablename__)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return f"CREATE VIEW `{view_name}` AS\n{query}"
    
    def alter_view_statement(self, view: View) -> str:
        """Genera ALTER VIEW para MySQL"""
        view_name = self.reserved_word_mapper(view._name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return f"CREATE OR REPLACE VIEW `{view_name}` AS\n{query}"
    
    def recreate_materialized_view_statement(self, view: View) -> list[str]:
        """MySQL no soporta vistas materializadas"""
        raise NotImplementedError("MySQL no soporta vistas materializadas")
    
    def _get_dialect(self):
        """Helper para obtener el dialecto MySQL"""
        return pm.db.engine.dialect

# Auto-registrar el driver
drivers.register(MySQLDriver())