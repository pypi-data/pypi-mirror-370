from __future__ import annotations
import click
from dataclasses import dataclass, field
from typing import List, Union, Dict, Optional, TYPE_CHECKING
from sqlalchemy import Column, text
from sqlalchemy.schema import Table, ForeignKeyConstraint

from tai_sql import pm, View

if TYPE_CHECKING:
    from tai_sql.drivers import DatabaseDriver
    from .drift import DriftManager

@dataclass
class Statement:
    """
    Clase para representar una sentencia DDL
    """
    text: str | List[str]
    table_name: str

@dataclass
class CreateStatement(Statement):
    """
    Clase para representar una sentencia CREATE TABLE
    """
    columns: List[Column] = field(default_factory=list)

@dataclass
class DropTableStatement(Statement):
    """
    Clase para representar una sentencia DROP TABLE
    """
    pass

@dataclass
class AlterColumnStatement(Statement):
    """
    Clase para representar una sentencia ALTER TABLE ADD COLUMN
    """
    column_name: str
    column: Column

    def check_unique_constraints(self) -> None:

        """
        Verifica y muestra las restricciones únicas de una tabla
        """
        # Verificar si hay datos duplicados antes de añadir constraint UNIQUE
        check_duplicates_query = f"""
        SELECT {self.column_name}, COUNT(*) as count
        FROM {self.table_name}
        GROUP BY {self.column_name}
        HAVING COUNT(*) > 1
        """

        with pm.db.engine.connect() as connection:
            result = connection.execute(text(check_duplicates_query))
        
        return result.first()

@dataclass
class ForeignKeyStatement(Statement):
    """
    Clase para representar una sentencia ALTER TABLE ADD FOREIGN KEY
    """
    fk: ForeignKeyConstraint
    local: Table
    target: Table

@dataclass
class CreateViewStatement(Statement):
    """
    Clase para representar una sentencia CREATE VIEW
    """
    view: View
    view_name: str

@dataclass
class AlterViewStatement(Statement):
    """
    Clase para representar una sentencia CREATE OR REPLACE VIEW
    """
    view: View
    view_name: str

@dataclass
class DropViewStatement(Statement):
    """
    Clase para representar una sentencia DROP VIEW
    """
    view_name: str

DDLStatements = List[
    Union[CreateStatement, DropTableStatement, AlterColumnStatement, ForeignKeyStatement,
    CreateViewStatement, AlterViewStatement, DropViewStatement]
]

class DDLManager:
    """
    Clase para gestionar las sentencias DDL generadas
    """
    def __init__(self, driver: DatabaseDriver):
        self.driver = driver
        self.statements: DDLStatements = []
    
    def add_statement(self, statement: Statement):
        """Añade una sentencia DDL a la lista"""
        self.statements.append(statement)

    def clear(self):
        """Limpia todas las sentencias DDL"""
        self.statements.clear()
    
    def generate(self, drift: DriftManager) -> list[DDLStatements]:

        self.generate_table_creations(drift.tables_to_create.values())
        self.generate_table_drops(drift.tables_to_drop.values())
        self.generate_column_modifications(
            drift.columns_to_add,
            drift.columns_to_drop,
            drift.columns_to_modify,
        )
        self.generate_view_drops(drift.views_to_drop)
        self.generate_view_creations(drift.views_to_create)
        self.generate_view_modifications(drift.modified_views)

        return self.statements
    
    def show(self) -> None:
        """Muestra las sentencias DDL que se van a ejecutar"""
        click.echo()
        click.echo("📄 DDLs:")
        click.echo("=" * 30)
        click.echo()
        
        for i, statement in enumerate(self.statements, 1):
            if isinstance(statement.text, List):
                for line in statement.text:
                    click.echo(line)
                    click.echo()
            else:
                click.echo(statement.text)
                click.echo()
        
        click.echo("=" * 30)
        click.echo()
    
    def execute(self) -> Optional[int]:
        """Ejecuta las sentencias DDL en la base de datos"""
        executed_count = 0

        if not self.statements:
            click.echo("ℹ️  No hay cambios para aplicar")
            return executed_count
            
        click.echo("⚙️  Ejecutando sentencias DDL...")
        
        try:
            
            with pm.db.engine.connect() as conn:
                # Usar transacción para todas las operaciones
                trans = conn.begin()
                
                try:

                    if pm.db.provider.drivername == 'postgresql':
                        conn.execute(text(f"SET search_path TO {pm.db.schema_name}, public"))

                    for stmt in self.statements:

                        if isinstance(stmt, CreateStatement):
                            # Ejecutar CREATE TABLE
                            conn.execute(text(stmt.text))
                            executed_count += 1
                            click.echo(f"   ⚙️  Crear tabla → {stmt.table_name}")
                            
                        elif isinstance(stmt, AlterColumnStatement):
                            # Ejecutar ALTER TABLE

                            if stmt.column.unique:
                                result = stmt.check_unique_constraints()

                                if result:
                                    click.echo("   ❌  UniqueConstraint error:")
                                    click.echo(f'   ⚠️  Columna "{stmt.column_name}" tiene valores duplicados en {stmt.table_name}, se omitirá la modificación')
                                    continue

                            if isinstance(stmt.text, List):
                                for sub_stmt in stmt.text:
                                    conn.execute(text(sub_stmt))
                            else:

                                conn.execute(text(stmt.text))

                            executed_count += 1

                            if stmt.column_name:
                                click.echo(f"   ⚙️  Añadir/modificar columna → {stmt.column_name} en {stmt.table_name}")

                        elif isinstance(stmt, ForeignKeyStatement):

                            # Ejecutar ALTER TABLE
                            conn.execute(text(stmt.text))
                            executed_count += 1

                            # Mostrar información de la ForeignKey
                            local_columns_names = [col.name for col in stmt.fk.columns]
                            target_columns_names = [element.column.name for element in stmt.fk.elements]
                            # Asegurar el mismo orden
                            local_columns_names.sort()
                            target_columns_names.sort()

                            click.echo(f'   ⚙️  Declarar ForeignKey: {stmt.local.name}[{", ".join(local_columns_names)}] → {stmt.target.name}[{", ".join(target_columns_names)}] en {stmt.local.name}')
                        
                        elif isinstance(stmt, CreateViewStatement):
                            conn.execute(text(stmt.text))
                            executed_count += 1
                            click.echo(f"   ⚙️   Crear vista → {stmt.view_name}")
                            
                        elif isinstance(stmt, AlterViewStatement):
                            conn.execute(text(stmt.text))
                            executed_count += 1
                            click.echo(f"   ⚙️   Modificar vista → {stmt.view_name}")
                            
                        elif isinstance(stmt, DropViewStatement):
                            conn.execute(text(stmt.text))
                            executed_count += 1
                            click.echo(f"   ⚙️   Eliminar vista → {stmt.view_name}")
                    
                    trans.commit()
                    click.echo()
                    click.echo(f"   🎉 {executed_count} operación(es) ejecutada(s) exitosamente")

                    return executed_count
                    
                except Exception as e:
                    trans.rollback()
                    raise e
                
                finally:
                    # Restaurar search_path por defecto
                    if pm.db.provider.drivername == 'postgresql':
                        conn.execute(text("SET search_path TO public"))
                    
        except Exception as e:
            raise Exception(f"Error al ejecutar DDL: {e}")

    def generate_table_creations(self, tables: list[Table]) -> None:
        """
        Genera sentencias DDL para crear tablas nuevas con manejo mejorado de DEFAULT
        
        Returns:
            Lista de sentencias DDL de creación
        """
        if not tables:
            return self.statements
        
        click.echo("🛠️  Generando sentencias CREATE TABLE...")
        
        for table in tables:
            
            stmt = CreateStatement(
                text=self.create_table_statement(table),
                table_name=table.name,
                columns=list(table.columns.values())
            )
            self.add_statement(stmt)
            click.echo(f"   🆕 Nueva tabla: {table.name}")
        
        click.echo()
        
        # Generar Foreign Keys como statements separados
        self.generate_foreign_key_statements(tables)
    
    def generate_table_drops(self, tables_to_drop: list[Table]) -> None:
        """
        Genera sentencias DDL para eliminar tablas
        
        Args:
            tables_to_drop: Lista de nombres de tablas a eliminar
        """
        if not tables_to_drop:
            return
            
        click.echo("🛠️  Generando sentencias DROP TABLE...")
        
        for table in tables_to_drop:
            stmt = DropTableStatement(
                text=self.drop_table_statement(table.name),
                table_name=table.name
            )
            self.add_statement(stmt)
            click.echo(f"   🗑️  Tabla a eliminar: {table.name}")
        
        click.echo()

    def generate_foreign_key_statements(self, tables: list[Table]) -> None:
        """
        Genera statements ALTER TABLE ADD CONSTRAINT para todas las Foreign Keys
        """
        if not tables:
            return
            
        click.echo("🛠️  Generando sentencias FOREIGNKEY CONTRAINT...")
        
        for table in tables:
            
            for fk in table.foreign_key_constraints:
                fk_statement = self.foreign_key_statement(table, fk)

                local = fk.parent
                target = fk.referred_table
                local_columns_names = [col.name for col in fk.columns]
                target_columns_names = [element.column.name for element in fk.elements]

                # Asegurar el mismo orden
                local_columns_names.sort()
                target_columns_names.sort()

                if fk_statement:
                    stmt = ForeignKeyStatement(
                        text=fk_statement,
                        table_name=table.name,
                        fk=fk,
                        local=local,
                        target=target,
                    )
                    self.add_statement(stmt)
                    click.echo(f'   🔗 Foreign Key: {local.name}[{", ".join(local_columns_names)}] → {target.name}[{", ".join(target_columns_names)}]')

        click.echo()
    
    def generate_view_creations(self, views: dict[str, 'View']) -> None:
        """
        Genera sentencias DDL para crear vistas nuevas
        
        Args:
            views: Diccionario de vistas nuevas
        """
        if not views:
            return
            
        click.echo("🛠️  Generando sentencias CREATE VIEW...")
        
        for view_name, view in views.items():
            stmt = CreateViewStatement(
                text=self.create_view_statement(view),
                table_name=view_name,
                view=view,
                view_name=view_name
            )
            self.add_statement(stmt)
            click.echo(f"   🆕 Nueva vista: {view_name}")
        
        click.echo()

    def generate_view_modifications(self, views: dict[str, 'View']) -> None:
        """
        Genera sentencias DDL para modificar vistas existentes
        
        Args:
            views: Diccionario de vistas modificadas
        """
        if not views:
            return
            
        click.echo("🛠️  Generando sentencias ALTER VIEW...")
        
        for view_name, view in views.items():
            # Para vistas materializadas, generar múltiples statements
            if view.materialized:
                statements = self.recreate_materialized_view_statement(view)
                for stmt_text in statements:
                    stmt = AlterViewStatement(
                        text=stmt_text,
                        table_name=view_name,
                        view=view,
                        view_name=view_name
                    )
                    self.add_statement(stmt)
            else:
                stmt = AlterViewStatement(
                    text=self.alter_view_statement(view),
                    table_name=view_name,
                    view=view,
                    view_name=view_name
                )
                self.add_statement(stmt)
            
            click.echo(f"   🔄 Vista modificada: {view_name}")
        
        click.echo()

    def generate_view_drops(self, views_to_drop: dict[str, str]) -> None:
        """
        Genera sentencias DDL para eliminar vistas
        
        Args:
            views_to_drop: Diccionario {view_name: drop_statement}
        """
        if not views_to_drop:
            return
            
        click.echo("🛠️  Generando sentencias DROP VIEW...")
        
        for view_name, drop_statement in views_to_drop.items():
            stmt = DropViewStatement(
                text=drop_statement,
                table_name=view_name,
                view_name=view_name
            )
            self.add_statement(stmt)
            click.echo(f"   🗑️  Vista a eliminar: {view_name}")
        
        click.echo()
    
    def generate_column_modifications(
            self,
            new_cols: Dict[str, list[Column]],
            delete_cols: Dict[str, list[Column]],
            modified_cols: Dict[str, list[Column]]
    ) -> list[Statement]:
        """
        Genera sentencias DDL para las migraciones incrementales
        """
        if new_cols or delete_cols or modified_cols:
            click.echo("🛠️  Generando sentencias de migración...")
        
        else:
            return
        
        # Añadir columnas nuevas
        if new_cols:
            for table_name, columns in new_cols.items():
                for column in columns:
                    # Usar el mismo método para generar definición de columna
                    column_def = self.get_column_definition(column)
                    stmt = AlterColumnStatement(
                        text=f"ALTER TABLE {column.table.name} ADD COLUMN {column_def}",
                        table_name=column.table.name,
                        column_name=column.name,
                        column=column
                    )
                    self.add_statement(stmt)
                    click.echo(f'   ➕ Añadir columna "{column.name}" a "{column.table.name}"')
        
        # Eliminar columnas
        if delete_cols:
            for table_name, columns in delete_cols.items():
                for column in columns:
                    stmt = AlterColumnStatement(
                        text=f"ALTER TABLE {column.table.name} DROP COLUMN {self.reserved_word_mapper(column.name)}",
                        table_name=column.table.name,
                        column_name=column.name,
                        column=column
                    )
                    self.add_statement(stmt)
                    click.echo(f'   ➖ Eliminar columna "{column.name}" de "{column.table.name}"')

        if modified_cols:
            for table_name, columns in modified_cols.items():
                for column in columns:
                    # Generar nueva definición de columna
                    alter_statements = self.alter_column_statements(table_name, column)

                    stmt = AlterColumnStatement(
                        text=alter_statements,
                        table_name=column.table.name,
                        column_name=column.name,
                        column=column
                    )

                    self.add_statement(stmt)
                    click.echo(f'   ✏️  Modificar columna "{column.name}" en "{column.table.name}"')
        
        click.echo()
        
        return self.statements

    def create_table_statement(self, table: Table) -> str:
        """Delega al driver específico"""
        return self.driver.create_table_statement(table)
    
    def drop_table_statement(self, table_name: str) -> str:
        """Delega al driver específico pero adaptando la interfaz"""
        # Usar el método existente del driver con parámetros apropiados
        return self.driver.drop_table_statement(
            table_name=table_name,
            schema_name=pm.db.schema_name
        )
    
    def foreign_key_statement(self, table: Table, fk: ForeignKeyConstraint) -> str:
        """Delega al driver específico"""
        return self.driver.foreign_key_statement(table, fk)
    
    def get_column_definition(self, column: Column) -> str:
        """Delega al driver específico"""
        return self.driver.get_column_definition(column)
    
    def alter_column_statements(self, table_name: str, column: Column) -> list[str]:
        """Delega al driver específico"""
        return self.driver.alter_column_statements(table_name, column)
    
    def get_default_value(self, default) -> str:
        """Delega al driver específico"""
        return self.driver.get_default_value(default)
    
    def reserved_word_mapper(self, identifier: str) -> str:
        """Delega al driver específico"""
        return self.driver.reserved_word_mapper(identifier)
    
    def create_view_statement(self, view: 'View') -> str:
        """Delega al driver específico"""
        return self.driver.create_view_statement(view)
    
    def alter_view_statement(self, view: 'View') -> str:
        """Delega al driver específico"""
        return self.driver.alter_view_statement(view)
    
    def recreate_materialized_view_statement(self, view: 'View') -> list[str]:
        """Delega al driver específico"""
        return self.driver.recreate_materialized_view_statement(view)
    
    def drop_view_statement(self, view_name: str, is_materialized: bool = False) -> str:
        """Delega al driver específico pero adaptando la interfaz"""
        # Usar el método existente del driver con parámetros apropiados
        return self.driver.drop_view_statement(
            view_name=view_name,
            schema_name=pm.db.schema_name,
            view_definition="materialized" if is_materialized else ""
        )

