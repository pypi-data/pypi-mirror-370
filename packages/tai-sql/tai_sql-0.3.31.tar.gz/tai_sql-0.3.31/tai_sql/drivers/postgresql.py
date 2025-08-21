"""
Driver para PostgreSQL
"""
import re
from sqlalchemy import URL, Column, Table, ForeignKeyConstraint, Engine, text
from typing import Dict, Any
from .base import DatabaseDriver, drivers
from tai_sql import pm, View

class PostgreSQLDriver(DatabaseDriver):
    
    @property
    def name(self) -> str:
        return "postgresql"
    
    @property
    def default_port(self) -> int:
        return 5432
    
    @property
    def default_database(self) -> str:
        return "postgres"
    
    def create_temp_url(self, username: str, password: str, host: str, 
                       port: int, database: str = None) -> URL:
        return URL.create(
            drivername="postgresql",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database or self.default_database
        )
    
    def get_connect_args(self, timeout: int) -> Dict[str, Any]:
        connect_args = {
            "connect_timeout": timeout,
            "options": f"-c statement_timeout={timeout * 1000}"
        }
        
        return connect_args
    
    def database_exists_query(self) -> str:
        return "SELECT 1 FROM pg_database WHERE datname = :db_name"
    
    def schema_exists_query(self) -> str:
        return "SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema_name"
    
    def create_database_statement(self, database_name: str) -> str:
        return f'CREATE DATABASE "{database_name}"'
    
    def create_schema_statement(self, schema_name: str) -> str:
        return f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
    
    def get_ddl_prefix(self, schema_name: str) -> str:
        return f'"{schema_name}".' if schema_name != 'public' else ''
    
    def supports_schemas(self) -> bool:
        return True
    
    @property
    def type_mapping(self) -> Dict[str, str]:
        """Mapeo de tipos de datos de PostgreSQL a SQLAlchemy"""
        return {
            'DATETIME': ['DATETIME', 'TIMESTAMP', 'TIMESTAMP WITH TIME ZONE', 'TIMESTAMP WITHOUT TIME ZONE'],
            'TIME': ['TIME', 'TIME WITH TIME ZONE', 'TIME WITHOUT TIME ZONE'],
            'INTEGER': ['INTEGER', 'INT4'],
            'VARCHAR': ['VARCHAR', 'TEXT', 'CHARACTER VARYING'],
            'BIGINT': ['BIGINT', 'BIGSERIAL', 'INT8'],
            'FLOAT': ['FLOAT', 'DOUBLE PRECISION', 'REAL', 'FLOAT8'],
            'BOOLEAN': ['BOOLEAN', 'BOOL'],
            'TEXT': ['TEXT', 'VARCHAR'],
            'BYTES': ['BYTEA', 'BLOB'],
        }
    
    def get_views_statement(self, schema_name: str = 'public') -> str:
        return f"""
            SELECT 
                table_name as view_name,
                view_definition
            FROM information_schema.views 
            WHERE table_schema = COALESCE('{schema_name}', 'public')
        """
    
    def normalize_query(self, query) -> str:
        """Normalización específica para PostgreSQL"""
        # PostgreSQL tiende a añadir paréntesis extra en FROM clauses
        query = re.sub(r'from\s*\(\s*([^)]+(?:join[^)]*)*)\s*\)', r'from \1', query)
        
        # PostgreSQL reformatea condiciones ON con paréntesis dobles
        query = re.sub(r'on\s*\(\s*\(\s*([^)]+)\s*\)\s*\)', r'on \1', query)
        
        return query
    
    def drop_view_statement(self, view_name, schema_name: str = 'public', view_definition = None) -> str:
        """Genera la sentencia para eliminar una vista"""
        # Detectar si es vista materializada
        is_materialized = 'materialized' in view_definition.lower()
        view_type = "MATERIALIZED VIEW" if is_materialized else "VIEW"
        prefix = self.get_ddl_prefix(schema_name)
        return f"DROP {view_type} IF EXISTS {prefix}{view_name}"
    
    def get_column_definition(self, column: Column) -> str:
        """Genera la definición de columna para PostgreSQL"""
        # Obtener el tipo compilado para PostgreSQL
        column_type = str(column.type.compile(dialect=self._get_dialect()))

        if column_type in ('INTEGER', 'BIGINT') and column.autoincrement and column.primary_key:
            if column_type == 'INTEGER':
                column_type = 'SERIAL'
            elif column_type == 'BIGINT':
                column_type = 'BIGSERIAL'
        
        # Construir definición base
        definition_parts = [self.reserved_word_mapper(column.name), column_type]
        
        # Añadir NOT NULL
        if not column.nullable:
            definition_parts.append("NOT NULL")
        
        # Manejar DEFAULT
        if column.server_default is not None:
            definition_parts.append(f"DEFAULT {self.get_default_value(column.server_default)}")
        
        # Añadir UNIQUE para columnas únicas individuales
        if column.unique:
            definition_parts.append("UNIQUE")
        
        return " ".join(definition_parts)
    
    def alter_column_statements(self, table_name: str, column: Column) -> list[str]:
        """Genera sentencias ALTER COLUMN específicas para PostgreSQL"""
        statements = []
        table_name = self.reserved_word_mapper(table_name)
        column_name = self.reserved_word_mapper(column.name)
        
        # Cambiar tipo de datos
        column_type = str(column.type.compile(dialect=self._get_dialect()))
        using = self._get_using_clause(column_name, column_type)
        
        alter_type_stmt = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {column_type}"
        if using:
            alter_type_stmt += f" USING {using}"
        statements.append(alter_type_stmt)
        
        # Manejar NULL/NOT NULL
        if column.nullable:
            statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP NOT NULL")
        else:
            statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL")
        
        # Manejar DEFAULT
        if column.server_default is not None:
            default_value = self.get_default_value(column.server_default)
            statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET DEFAULT {default_value}")
        else:
            statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP DEFAULT")
        
        # Manejar UNIQUE
        if column.unique:
            constraint_name = f'unique_{table_name}_{column_name}'
            statements.append(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({column_name})")

        return statements
    
    def _get_using_clause(self, column_name: str, target_type: str) -> str:
        """Genera la cláusula USING apropiada para conversión de tipos en PostgreSQL"""
        target_type_lower = target_type.lower()
        
        # Mapeo de conversiones comunes
        if 'integer' in target_type_lower or 'serial' in target_type_lower:
            return f"{column_name}::integer"
        elif 'varchar' in target_type_lower or 'text' in target_type_lower:
            return f"{column_name}::text"
        elif 'boolean' in target_type_lower:
            return f"CASE WHEN {column_name} IN ('true', '1', 'yes', 't', 'y') THEN true ELSE false END"
        elif 'timestamp' in target_type_lower:
            return f"{column_name}::timestamp"
        else:
            clean_type = target_type_lower.split('(')[0]
            return f"{column_name}::{clean_type}"
    
    def get_default_value(self, default) -> str:
        """Procesa el valor DEFAULT para PostgreSQL"""
        if hasattr(default, 'arg'):
            value = default.arg
            if isinstance(value, str):
                if value.lower() in ['now', 'current_timestamp']:
                    return 'NOW()'
                return f"'{value}'"
            elif isinstance(value, bool):
                return 'TRUE' if value else 'FALSE'
            elif isinstance(value, (int, float)):
                return str(value)
            elif value is None:
                return 'NULL'
        
        # Fallback
        str_value = str(default)
        if 'now' in str_value.lower() or 'current_timestamp' in str_value.lower():
            return 'NOW()'
        return f"'{str_value}'"
    
    def reserved_word_mapper(self, identifier: str) -> str:
        """Escapa identificadores para PostgreSQL"""
        if identifier.lower() in self.reserved_words:
            return f'"{identifier}"'
        return identifier
    
    @property
    def reserved_words(self) -> set[str]:
        """Palabras reservadas de PostgreSQL"""
        return {
            'user', 'order', 'group', 'table', 'index', 'view', 'database',
            'schema', 'column', 'row', 'select', 'insert', 'update', 'delete',
            'create', 'drop', 'alter', 'grant', 'revoke', 'commit', 'rollback',
            'transaction', 'begin', 'end', 'function', 'procedure', 'trigger',
            'constraint', 'primary', 'foreign', 'unique', 'check', 'default',
            'null', 'not', 'and', 'or', 'in', 'exists', 'between', 'like',
            'is', 'as', 'on', 'from', 'where', 'having', 'limit', 'offset'
        }
    
    def create_table_statement(self, table: Table) -> str:
        """Genera CREATE TABLE para PostgreSQL"""
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
        pk_columns = [col.name for col in table.columns if col.primary_key]
        if pk_columns:
            pk_def = f"    PRIMARY KEY ({', '.join(pk_columns)})"
            constraint_definitions.append(pk_def)
        
        # Unique constraints
        for constraint in table.constraints:
            if hasattr(constraint, 'columns') and len(constraint.columns) > 1:
                if constraint.__class__.__name__ == 'UniqueConstraint':
                    col_names = [col.name for col in constraint.columns]
                    unique_def = f"    UNIQUE ({', '.join(col_names)})"
                    constraint_definitions.append(unique_def)
        
        # Combinar definiciones
        all_definitions = column_definitions + constraint_definitions
        lines.append(',\n'.join(all_definitions))
        lines.append(")")
        
        return '\n'.join(lines)
    
    def drop_table_statement(self, table_name: str, schema_name: str = None) -> str:
        """Genera DROP TABLE para PostgreSQL"""
        escaped_table = self.reserved_word_mapper(table_name)
        
        if schema_name and schema_name != 'public':
            schema_prefix = f'"{schema_name}".'
        else:
            schema_prefix = ''
        
        return f"DROP TABLE IF EXISTS {schema_prefix}{escaped_table} CASCADE"
    
    def foreign_key_statement(self, table: Table, fk: ForeignKeyConstraint) -> str:
        """Genera Foreign Key para PostgreSQL"""
        try:
            table_name = self.reserved_word_mapper(table.name)
            schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
            
            # Obtener columnas locales
            local_columns_names = [self.reserved_word_mapper(col.name) for col in fk.columns]
            
            # Obtener tabla y columnas de referencia
            target_table_name = self.reserved_word_mapper(fk.referred_table.name)
            target_columns_names = [self.reserved_word_mapper(element.column.name) for element in fk.elements]
            
            # Generar nombre del constraint
            constraint_name = f"fk_{table.name}_{fk.referred_table.name}"
            if len(constraint_name) > 63:  # PostgreSQL limit
                import hashlib
                hash_suffix = hashlib.md5(constraint_name.encode()).hexdigest()[:8]
                constraint_name = f"fk_{table.name}_{hash_suffix}"
            
            # Construir statement
            local_columns_str = ", ".join(local_columns_names)
            target_columns_str = ", ".join(target_columns_names)
            
            statement = (
                f"ALTER TABLE {schema_prefix}{table_name} "
                f"ADD CONSTRAINT {constraint_name} "
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
        """PostgreSQL soporta vistas materializadas"""
        return True
    
    def create_view_statement(self, view: View) -> str:
        """Genera CREATE VIEW para PostgreSQL"""
        view_name = self.reserved_word_mapper(view.__tablename__)
        view_type = "MATERIALIZED VIEW" if view.materialized else "VIEW"
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        print(view_name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return f"CREATE {view_type} {schema_prefix}{view_name} AS\n{query}"
    
    def alter_view_statement(self, view: View) -> str:
        """Genera ALTER VIEW para PostgreSQL"""
        if getattr(view, 'materialized', False):
            return self.recreate_materialized_view_statement(view)
        
        view_name = self.reserved_word_mapper(view._name)
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return f"CREATE OR REPLACE VIEW {schema_prefix}{view_name} AS\n{query}"
    
    def recreate_materialized_view_statement(self, view: View) -> list[str]:
        """Genera DROP + CREATE para vistas materializadas en PostgreSQL"""
        view_name = self.reserved_word_mapper(view._name)
        schema_prefix = self.get_ddl_prefix(pm.db.schema_name)
        
        query = view.query.strip()
        if query.endswith(';'):
            query = query[:-1]
        
        return [
            f"DROP MATERIALIZED VIEW IF EXISTS {schema_prefix}{view_name}",
            f"CREATE MATERIALIZED VIEW {schema_prefix}{view_name} AS\n{query}"
        ]
    
    def _get_dialect(self):
        """Helper para obtener el dialecto PostgreSQL"""
        return pm.db.engine.dialect


# Auto-registrar el driver
drivers.register(PostgreSQLDriver())