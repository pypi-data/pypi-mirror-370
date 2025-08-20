from __future__ import annotations
import re
import click
from typing import List, Dict
from sqlalchemy import MetaData, Column, text
from sqlalchemy.schema import Table, UniqueConstraint

from tai_sql import pm, View


class DriftManager:
    """
    Clase para almacenar los cambios detectados en el esquema (tablas y vistas)
    """

    def __init__(self) -> None:
        """
        Inicializa el gestor de drift
        """
        self.target = f'{pm.db.provider.database}{"@" + pm.db.schema_name if pm.db.driver.supports_schemas() else ""}'
        self.local_metadata = MetaData(schema=pm.db.schema_name)
        self.target_metadata = MetaData(schema=pm.db.schema_name)
        
        # Tablas
        self.tables_to_create: dict[str, Table] = {}
        self.existing_tables: dict[str, Table] = {}
        self.tables_to_drop: dict[str, Table] = {}
        self.columns_to_add: dict[str, list[Column]] = {}
        self.columns_to_drop: dict[str, list[Column]] = {}
        self.columns_to_modify: dict[str, list[Column]] = {}
        
        # Vistas
        self.views_to_create: dict[str, View] = {}
        self.target_views: dict[str, View] = {}
        self.modified_views: dict[str, View] = {}
        self.views_to_drop: dict[str, str] = {}

        self.debug_mode: bool = True

    def run(self) -> None:
        """
        Detecta cambios entre el esquema definido y el esquema actual
        """
        
        click.echo(f"🔎 Detectando cambios en: {self.target}")
        click.echo()

        self.load_and_reflect()
        self.table_changes()
        self.view_changes()
    
    def load_and_reflect(self) -> None:
        """
        Carga el esquema actual de la base de datos y esquema local
        """
        click.echo(f"🔄 Cargando esquema actual de la base de datos: {self.target}")

        # Reflejar metadata existente
        try:
            if pm.db.driver.supports_schemas():
                self.target_metadata.reflect(bind=pm.db.engine, schema=pm.db.schema_name)
            else:
                self.target_metadata.reflect(bind=pm.db.engine)
        except Exception as e:
            click.echo(f"❌ Error al reflejar local_metadata existente: {e}", err=True)
            return
        
        # Cargar metadata del esquema local
        for table in pm.db.tables:
            table.to_sqlalchemy_table(self.local_metadata)

    def table_changes(self) -> None:
        """Detecta cambios en tablas usando el driver específico"""
        
        target_tables = set(self.target_metadata.tables.keys())
        local_tables = set(self.local_metadata.tables.keys())
        
        # Tablas nuevas
        new_table_names = local_tables - target_tables
        for table_name in new_table_names:
            new_table = self.local_metadata.tables[table_name]
            self.tables_to_create[table_name] = new_table
            click.echo(f"   🆕 Nueva tabla detectada: {table_name}")
        
        # Tablas a eliminar
        tables_to_drop_names = target_tables - local_tables
        for table_name in tables_to_drop_names:
            table_to_drop = self.target_metadata.tables[table_name]
            self.tables_to_drop[table_name] = table_to_drop
            click.echo(f"   🗑️  Tabla a eliminar: {table_name}")
        
        # Tablas existentes - analizar cambios en columnas
        existing_table_names = local_tables & target_tables
        for table_name in existing_table_names:
            target_table = self.target_metadata.tables[table_name]
            self.existing_tables[table_name] = target_table
            local_table = self.local_metadata.tables[table_name]

            self._analyze_column_changes(table_name, target_table, local_table)

    def _analyze_column_changes(self, table_name: str, target_table: Table, local_table: Table) -> None:
        """
        Analiza cambios en columnas usando comparación específica del driver
        """

        # Obtener restricciones
        constraint_columns = []
        for constraint in target_table.constraints:
            if isinstance(constraint, UniqueConstraint):
                constraint_columns = [col.name for col in constraint.columns]
        

        target_columns = {col.name: col for col in target_table.columns}
        local_columns = {col.name: col for col in local_table.columns}
        
        # Columnas a añadir
        columns_to_add = set(local_columns.keys()) - set(target_columns.keys())
        if columns_to_add:
            self.columns_to_add[table_name] = [
                local_columns[col_name] for col_name in columns_to_add
            ]
            click.echo(f"      ➕ {len(columns_to_add)} columna(s) a añadir en {table_name}")
        
        # Columnas a eliminar
        columns_to_drop = set(target_columns.keys()) - set(local_columns.keys())
        if columns_to_drop:
            self.columns_to_drop[table_name] = [
                target_columns[col_name] for col_name in columns_to_drop
            ]
            click.echo(f"      ⚠️  {len(columns_to_drop)} columna(s) a eliminar en {table_name}")
        
        # Columnas a modificar
        for col_name in set(target_columns.keys()) & set(local_columns.keys()):
            target_col = target_columns[col_name]
            local_col = local_columns[col_name]

            # Usar comparación específica del driver
            if self._column_needs_modification(target_col, local_col, constraint_columns):
                if table_name not in self.columns_to_modify:
                    self.columns_to_modify[table_name] = []
                self.columns_to_modify[table_name].append(local_col)

    def _column_needs_modification(self, target_col: Column, local_col: Column, 
                                 constraint_columns: list[str]) -> bool:
        """
        Determina si una columna necesita modificación usando reglas específicas del driver
        """
        # Usar mapeo de tipos específico del driver
        type_mappings = pm.db.driver.type_mapping
        
        current_type = str(target_col.type).upper()
        new_type = str(local_col.type).upper()

        # Verificar si los tipos son equivalentes según el driver
        type_changed = not self._types_are_equivalent(current_type, new_type, type_mappings)

        # Comparar otras propiedades
        nullable_changed = target_col.nullable != local_col.nullable
        pk_changed = target_col.primary_key != local_col.primary_key
        autoincrement_changed = target_col.autoincrement != local_col.autoincrement

        # Manejar unique constraints
        if target_col.name in constraint_columns:
            target_col.unique = True
        unique_changed = target_col.unique != local_col.unique
        
        return any([type_changed, nullable_changed, pk_changed, autoincrement_changed, unique_changed])

    def _types_are_equivalent(self, type1: str, type2: str, mappings: Dict[str, List[str]]) -> bool:
        """
        Verifica si dos tipos son equivalentes según el mapeo del driver
        """
        if type1 == type2:
            return True
        
        # Buscar en los mapeos si ambos tipos pertenecen al mismo grupo
        for _, equivalent_types in mappings.items():
            if type1 in equivalent_types and type2 in equivalent_types:
                return True
        
        return False

    def view_changes(self) -> None:
        """Detecta cambios en vistas usando consultas específicas del driver"""
        
        # Obtener vistas del registro
        local_views = {view.tablename: view for view in pm.db.views}
        
        # Obtener vistas existentes usando método específico del driver
        target_views = self._get_existing_views()
        
        # Vistas nuevas
        new_view_names = set(local_views.keys()) - set(target_views.keys())
        for view_name in new_view_names:
            self.views_to_create[view_name] = local_views[view_name]
            click.echo(f"   🆕 Nueva vista detectada: {view_name}")
        
        # # Vistas existentes - verificar si han cambiado
        # existing_view_names = set(local_views.keys()) & set(target_views.keys())
        # for view_name in existing_view_names:
        #     schema_view = local_views[view_name]
        #     existing_view_query = target_views[view_name]
            
        #     # Usar comparación semántica específica del driver
        #     if not self._semantic_query_comparison_with_driver(schema_view.query, existing_view_query):
        #         self.modified_views[view_name] = schema_view
        #         click.echo(f"   🔄 Vista modificada detectada: {view_name}")
        
        # Vistas a eliminar
        views_to_drop = set(target_views.keys()) - set(local_views.keys())
        for view_name in views_to_drop:
            # Usar generación de DROP específica del driver
            drop_stmt = pm.db.driver.drop_view_statement(
                view_name=view_name,
                schema_name=pm.db.schema_name,
                view_definition=target_views[view_name]
            )
            self.views_to_drop[view_name] = drop_stmt
            click.echo(f"   🗑️  Vista a eliminar: {view_name}")

    def _get_existing_views(self) -> dict[str, str]:
        """
        Obtiene las vistas existentes usando consultas específicas del driver
        """
        views = {}
        
        try:
            with pm.db.engine.connect() as conn:
                # Usar consulta específica del driver
                query = pm.db.driver.get_views_statement(pm.db.schema_name)
                if not query:
                    return views
                
                result = conn.execute(text(query))
                
                for row in result:
                    views[row.view_name] = row.view_definition
                    
        except Exception as e:
            click.echo(f"   ⚠️  Error obteniendo vistas existentes: {e}")
        
        return views

    def _semantic_query_comparison_with_driver(self, query1: str, query2: str) -> bool:
        """
        Comparación semántica de consultas usando reglas específicas del driver
        """
        # Normalización específica del driver
        norm1 = self._normalize_query_with_driver(query1)
        norm2 = self._normalize_query_with_driver(query2)
        
        if norm1 == norm2:
            return True
        
        # Debug si está habilitado
        if self.debug_mode:
            click.echo(f"      🔍 Análisis detallado:")
            click.echo(f"         Query 1: '{norm1}'")
            click.echo(f"         Query 2: '{norm2}'")
            
            differences = self._find_query_differences(norm1, norm2)
            if differences:
                click.echo(f"         Diferencias: {differences}")
        
        return False

    def _normalize_query_with_driver(self, query: str) -> str:
        """
        Normaliza consulta usando reglas específicas del driver
        """
        if not query:
            return ""
        
        # Normalización básica
        normalized = self._basic_normalize_query(query)
        
        # Usar normalización específica del driver
        normalized = pm.db.driver.normalize_query(normalized)
        
        return normalized

    def _basic_normalize_query(self, query: str) -> str:
        """Normalización básica de consultas SQL"""
        # Remover comentarios
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Convertir a minúsculas
        query = query.lower()
        
        # Normalizar espacios
        query = re.sub(r'\s+', ' ', query)
        
        # Normalizar operadores
        query = re.sub(r'\s*([,;=<>!+\-*/])\s*', r'\1', query)
        
        return query.strip().rstrip(';')

    def _find_query_differences(self, query1: str, query2: str) -> list[str]:
        """
        Encuentra las diferencias específicas entre dos consultas
        """
        differences = []
        
        if len(query1) != len(query2):
            differences.append(f"Longitud diferente ({len(query1)} vs {len(query2)})")
        
        for i, (c1, c2) in enumerate(zip(query1, query2)):
            if c1 != c2:
                start = max(0, i - 10)
                end = min(len(query1), i + 10)
                context1 = query1[start:end]
                context2 = query2[start:end]
                differences.append(f"Pos {i}: '{context1}' vs '{context2}'")
                break
        
        return differences

    def show(self):
        """Muestra un resumen de los cambios detectados"""
        click.echo(f"📋 Resumen de cambios para: {self.target}")
        
        # Tablas
        if self.tables_to_create:
            click.echo(f"   🆕 {len(self.tables_to_create)} tabla(s) nueva(s): {', '.join(self.tables_to_create)}")
        
        if self.tables_to_drop:  # ✅ NUEVO: Mostrar tablas a eliminar
            click.echo(f"   🗑️  {len(self.tables_to_drop)} tabla(s) a eliminar: {', '.join(self.tables_to_drop)}")
        
        if self.columns_to_add:
            total_columns = sum(len(cols) for cols in self.columns_to_add.values())
            click.echo(f"   ➕ {total_columns} columna(s) a añadir en {len(self.columns_to_add)} tabla(s)")
        
        if self.columns_to_drop:
            total_columns = sum(len(cols) for cols in self.columns_to_drop.values())
            click.echo(f"   ⚠️  {total_columns} columna(s) a eliminar en {len(self.columns_to_drop)} tabla(s)")
        
        if self.columns_to_modify:
            total_columns = sum(len(cols) for cols in self.columns_to_modify.values())
            click.echo(f"   ✏️  {total_columns} columna(s) a modificar en {len(self.columns_to_modify)} tabla(s)")
        
        # Vistas
        if self.views_to_create:
            click.echo(f"   🆕 {len(self.views_to_create)} vista(s) nueva(s): {', '.join(self.views_to_create)}")
        
        if self.modified_views:
            click.echo(f"   🔄 {len(self.modified_views)} vista(s) modificada(s): {', '.join(self.modified_views)}")
        
        if self.views_to_drop:
            click.echo(f"   🗑️  {len(self.views_to_drop)} vista(s) a eliminar: {', '.join(self.views_to_drop)}")

        # Verificar si no hay cambios
        has_changes = any([
            self.tables_to_create, self.tables_to_drop, self.columns_to_add, self.columns_to_drop,
            self.columns_to_modify, self.views_to_create, self.modified_views, self.views_to_drop
        ])
        
        if not has_changes:
            click.echo("   ✅ No se detectaron cambios")
        
        click.echo()

    def has_destructive_changes(self) -> bool:
        """
        Verifica si hay cambios destructivos (eliminar tablas/columnas/vistas)
        
        Returns:
            bool: True si hay cambios que podrían causar pérdida de datos
        """
        return bool(
            self.tables_to_drop or 
            self.columns_to_drop or 
            self.views_to_drop
        )

    def get_destructive_changes_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de cambios destructivos
        
        Returns:
            dict: Resumen de cambios destructivos
        """
        return {
            'tables_to_drop': len(self.tables_to_drop),
            'columns_to_drop': sum(len(cols) for cols in self.columns_to_drop.values()),
            'views_to_drop': len(self.views_to_drop)
        }

    def show_destructive_warning(self) -> None:
        """
        Muestra advertencia sobre cambios destructivos
        """
        if not self.has_destructive_changes():
            return
        
        click.echo("⚠️  ¡ADVERTENCIA! Los siguientes cambios pueden causar pérdida de datos:")
        
        if self.tables_to_drop:
            click.echo(f"   🗑️  Tablas a eliminar ({len(self.tables_to_drop)}):")
            for table_name in self.tables_to_drop:
                click.echo(f"      • {table_name}")
        
        if self.columns_to_drop:
            click.echo(f"   🗑️  Columnas a eliminar:")
            for table_name, columns in self.columns_to_drop.items():
                click.echo(f"      • {table_name}: {[col.name for col in columns]}")
        
        if self.views_to_drop:
            click.echo(f"   🗑️  Vistas a eliminar ({len(self.views_to_drop)}):")
            for view_name in self.views_to_drop:
                click.echo(f"      • {view_name}")
        
        click.echo()

    def get_creation_order(self) -> List[str]:
        """
        Obtiene el orden correcto para crear tablas considerando dependencias
        
        Returns:
            list: Lista de nombres de tabla en orden de creación
        """
        # Por ahora, orden simple. Se puede mejorar con análisis de FK
        return list(self.tables_to_create.keys())

    def get_drop_order(self) -> List[str]:
        """
        Obtiene el orden correcto para eliminar tablas considerando dependencias
        
        Returns:
            list: Lista de nombres de tabla en orden de eliminación (inverso a creación)
        """
        # Por ahora, orden inverso simple. Se puede mejorar con análisis de FK
        return list(reversed(self.tables_to_drop.keys()))

