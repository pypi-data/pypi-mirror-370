"""
Driver para SQL Server - Implementación completa
"""
import re
import click
from sqlalchemy import URL, Column, Table, ForeignKeyConstraint
from typing import Dict, Any, List
from .base import DatabaseDriver, drivers
from tai_sql import pm, View

class SQLServerDriver(DatabaseDriver):
    
    @property
    def name(self) -> str:
        return "mssql"
    
    @property
    def default_port(self) -> int:
        return 1433
    
    @property
    def default_database(self) -> str:
        return "master"
    
    def create_temp_url(self, username: str, password: str, host: str, 
                       port: int, database: str = None) -> URL:
        return URL.create(
            drivername="mssql+pyodbc",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database or self.default_database,
            query={"driver": "ODBC Driver 17 for SQL Server"}
        )
    
    def get_connect_args(self, timeout: int) -> Dict[str, Any]:
        return {
            "timeout": timeout
        }
    
    def database_exists_query(self) -> str:
        return "SELECT 1 FROM sys.databases WHERE name = :db_name"
    
    def schema_exists_query(self) -> str:
        return "SELECT 1 FROM sys.schemas WHERE name = :schema_name"
    
    def create_database_statement(self, database_name: str) -> str:
        return f"CREATE DATABASE [{database_name}]"
    
    def create_schema_statement(self, schema_name: str) -> str:
        return f"CREATE SCHEMA [{schema_name}]"
    
    def get_ddl_prefix(self, schema_name: str) -> str:
        return f"[{schema_name}]." if schema_name and schema_name != 'dbo' else ''
    
    def supports_schemas(self) -> bool:
        return True
    
    @property
    def type_mapping(self) -> Dict[str, List[str]]:
        """Mapeo de tipos de datos de SQL Server a SQLAlchemy"""
        return {
            'DATETIME': ['DATETIME', 'DATETIME2', 'SMALLDATETIME'],
            'TIME': ['TIME'],
            'INTEGER': ['INTEGER', 'INT'],
            'VARCHAR': ['VARCHAR', 'NVARCHAR', 'CHAR', 'NCHAR'],
            'BIGINT': ['BIGINT'],
            'FLOAT': ['FLOAT', 'REAL'],
            'BOOLEAN': ['BIT'],
            'TEXT': ['TEXT', 'NTEXT', 'VARCHAR(MAX)', 'NVARCHAR(MAX)'],
            'DECIMAL': ['DECIMAL', 'NUMERIC', 'MONEY', 'SMALLMONEY'],
            'UNIQUEIDENTIFIER': ['UNIQUEIDENTIFIER'],
            'BYTES': ['VARBINARY', 'IMAGE', 'BLOB'],
        }
    
    def get_views_statement(self, schema_name: str = 'dbo') -> str:
        schema_condition = f"'{schema_name}'" if schema_name else "'dbo'"
        return f"""
            SELECT 
                TABLE_NAME as view_name,
                VIEW_DEFINITION as view_definition
            FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = {schema_condition}
        """
    
    def normalize_query(self, query: str) -> str:
        """Normalización específica para SQL Server"""
        # SQL Server maneja corchetes en nombres
        query = re.sub(r'\[([^\]]+)\]', r'\1', query)
        
        # SQL Server puede tener diferencias en TOP vs LIMIT
        query = re.sub(r'\bTOP\s+(\d+)\b', r'LIMIT \1', query, flags=re.IGNORECASE)
        
        return query
    
    def drop_view_statement(self, view_name: str, schema_name: str = 'dbo', view_definition: str = None) -> str:
        """Genera DROP VIEW para SQL Server"""
        escaped_view = f"[{view_name}]"
        
        if schema_name and schema_name != 'dbo':
            schema_prefix = f"[{schema_name}]."
        else:
            schema_prefix = ''
        
        return f"DROP VIEW IF EXISTS {schema_prefix}{escaped_view}"
    
    def drop_table_statement(self, table_name: str, schema_name: str = None) -> str:
        """Genera DROP TABLE para SQL Server"""
        escaped_table = f"[{table_name}]"
        
        if schema_name and schema_name != 'dbo':
            schema_prefix = f"[{schema_name}]."
        else:
            schema_prefix = ''
        
        return f"DROP TABLE IF EXISTS {schema_prefix}{escaped_table}"
    
    def get_column_definition(self, column: Column) -> str:
        """Genera la definición de columna para SQL Server"""
        column_type = str(column.type.compile(dialect=self._get_dialect()))

        # SQL Server maneja IDENTITY para autoincrement
        if column_type in ('INTEGER', 'BIGINT') and column.autoincrement and column.primary_key:
            if column_type == 'INTEGER':
                column_type = 'INT IDENTITY(1,1)'
            elif column_type == 'BIGINT':
                column_type = 'BIGINT IDENTITY(1,1)'
        
        definition_parts = [self.reserved_word_mapper(column.name), column_type]
        
        if not column.nullable:
            definition_parts.append("NOT NULL")
        
        if column.server_default is not None:
            definition_parts.append(f"DEFAULT {self.get_default_value(column.server_default)}")
        
        if column.unique:
            definition_parts.append("UNIQUE")
        
        return " ".join(definition_parts)
    
    def alter_column_statements(self, table_name: str, column: Column) -> list[str]:
        """Genera sentencias ALTER COLUMN específicas para SQL Server"""
        statements = []
        table_name = self.reserved_word_mapper(table_name)
        column_name = self.reserved_word_mapper(column.name)
        
        # SQL Server requiere ALTER COLUMN para cambios de tipo
        column_def = self.get_column_definition(column)
        statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {column_def}")
        
        # Manejar constraints UNIQUE por separado si es necesario
        if column.unique:
            constraint_name = f'UQ_{table_name}_{column_name}'
            statements.append(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({column_name})")
        
        return statements
    
    def get_default_value(self, default) -> str:
        """Procesa el valor DEFAULT para SQL Server"""
        if hasattr(default, 'arg'):
            value = default.arg
            if isinstance(value, str):
                if value.lower() in ['getdate', 'getdate()', 'current_timestamp']:
                    return 'GETDATE()'
                return f"'{value}'"
            elif isinstance(value, bool):
                return '1' if value else '0'  # SQL Server usa 1/0 para BIT
            elif isinstance(value, (int, float)):
                return str(value)
            elif value is None:
                return 'NULL'
        
        str_value = str(default)
        if 'getdate' in str_value.lower() or 'current_timestamp' in str_value.lower():
            return 'GETDATE()'
        return f"'{str_value}'"
    
    def reserved_word_mapper(self, identifier: str) -> str:
        """Escapa identificadores para SQL Server"""
        if identifier.lower() in self.reserved_words:
            return f"[{identifier}]"
        return f"[{identifier}]"  # SQL Server siempre usa corchetes por seguridad
    
    @property
    def reserved_words(self) -> set[str]:
        """Palabras reservadas de SQL Server"""
        return {
            'user', 'order', 'group', 'table', 'index', 'view', 'database',
            'schema', 'column', 'row', 'select', 'insert', 'update', 'delete',
            'create', 'drop', 'alter', 'grant', 'revoke', 'commit', 'rollback',
            'transaction', 'begin', 'end', 'function', 'procedure', 'trigger',
            'constraint', 'primary', 'foreign', 'unique', 'check', 'default',
            'null', 'not', 'and', 'or', 'in', 'exists', 'between', 'like',
            'top', 'distinct', 'having', 'over', 'partition', 'case', 'when',
            'then', 'else', 'cast', 'convert', 'identity', 'rowid', 'key',
            'backup', 'restore', 'dump', 'load', 'bulk', 'openrowset',
            'contains', 'freetext', 'containstable', 'freetexttable'
        }
    
    def create_table_statement(self, table: Table) -> str:
        """Genera CREATE TABLE para SQL Server"""
        table_name = self.reserved_word_mapper(table.name)
        
        # Añadir prefijo de schema si existe
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        full_table_name = f"{schema_prefix}{table_name}"
        
        lines = [f"CREATE TABLE {full_table_name} ("]
        
        # Procesar columnas
        column_definitions = []
        for column in table.columns:
            column_def = self.get_column_definition(column)
            column_definitions.append(f"    {column_def}")
        
        # Procesar constraints
        constraint_definitions = []
        
        # Primary Key
        pk_columns = [self.reserved_word_mapper(col.name) for col in table.columns if col.primary_key]
        if pk_columns:
            pk_def = f"    PRIMARY KEY ({', '.join(pk_columns)})"
            constraint_definitions.append(pk_def)
        
        # Unique constraints
        for constraint in table.constraints:
            if hasattr(constraint, 'columns') and len(constraint.columns) > 1:
                if constraint.__class__.__name__ == 'UniqueConstraint':
                    col_names = [self.reserved_word_mapper(col.name) for col in constraint.columns]
                    unique_def = f"    UNIQUE ({', '.join(col_names)})"
                    constraint_definitions.append(unique_def)
        
        # Combinar definiciones
        all_definitions = column_definitions + constraint_definitions
        lines.append(',\n'.join(all_definitions))
        lines.append(")")
        
        return '\n'.join(lines)
    
    def foreign_key_statement(self, table: Table, fk: ForeignKeyConstraint) -> str:
        """Genera Foreign Key para SQL Server"""
        try:
            table_name = self.reserved_word_mapper(table.name)
            schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
            
            # Obtener columnas locales
            local_columns_names = [self.reserved_word_mapper(col.name) for col in fk.columns]
            
            # Obtener tabla y columnas de referencia
            target_table_name = self.reserved_word_mapper(fk.referred_table.name)
            target_columns_names = [self.reserved_word_mapper(element.column.name) for element in fk.elements]
            
            # Generar nombre del constraint
            constraint_name = f"FK_{table.name}_{fk.referred_table.name}"
            if len(constraint_name) > 128:  # SQL Server limit
                import hashlib
                hash_suffix = hashlib.md5(constraint_name.encode()).hexdigest()[:8]
                constraint_name = f"FK_{table.name}_{hash_suffix}"
            
            # Construir statement
            local_columns_str = ", ".join(local_columns_names)
            target_columns_str = ", ".join(target_columns_names)
            
            statement = (
                f"ALTER TABLE {schema_prefix}{table_name} "
                f"ADD CONSTRAINT [{constraint_name}] "
                f"FOREIGN KEY ({local_columns_str}) "
                f"REFERENCES {schema_prefix}{target_table_name} ({target_columns_str})"
            )
            
            # Añadir ON DELETE y ON UPDATE si están definidos
            if hasattr(fk, 'ondelete') and fk.ondelete:
                statement += f" ON DELETE {fk.ondelete}"
            
            if hasattr(fk, 'onupdate') and fk.onupdate:
                statement += f" ON UPDATE {fk.onupdate}"
            
            return statement
            
        except Exception as e:
            raise Exception(f"   ⚠️  Error generando Foreign Key para {table.name}: {e}")
    
    def supports_materialized_views(self) -> bool:
        """SQL Server soporta vistas indexadas (equivalente a materializadas)"""
        return True
    
    def create_view_statement(self, view: View) -> str:
        """Genera CREATE VIEW para SQL Server"""
        view_name = self.reserved_word_mapper(view.__tablename__)
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        # SQL Server no tiene MATERIALIZED VIEW nativo, pero se puede simular con vistas indexadas
        if getattr(view, 'materialized', False):
            click.echo(f"   ⚠️  SQL Server no soporta MATERIALIZED VIEW nativo. Creando vista regular.")
        
        return f"CREATE VIEW {schema_prefix}{view_name} AS\n{query}"
    
    def alter_view_statement(self, view: View) -> str:
        """Genera ALTER VIEW para SQL Server"""
        view_name = self.reserved_word_mapper(view._name)
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return f"ALTER VIEW {schema_prefix}{view_name} AS\n{query}"
    
    def recreate_materialized_view_statement(self, view: View) -> list[str]:
        """SQL Server no tiene vistas materializadas nativas, usar DROP + CREATE"""
        view_name = self.reserved_word_mapper(view._name)
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return [
            f"DROP VIEW IF EXISTS {schema_prefix}{view_name}",
            f"CREATE VIEW {schema_prefix}{view_name} AS\n{query}"
        ]
    
    def _get_dialect(self):
        """Helper para obtener el dialecto SQL Server"""
        from tai_sql import pm
        return pm.db.engine.dialect

# Auto-registrar el driver
drivers.register(SQLServerDriver())