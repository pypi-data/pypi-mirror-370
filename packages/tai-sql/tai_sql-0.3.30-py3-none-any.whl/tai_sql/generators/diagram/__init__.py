import os
import subprocess
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from enum import Enum

from tai_sql.generators.base import BaseGenerator
from tai_sql import pm


class DiagramTheme(Enum):
    """Temas disponibles para el diagrama ER"""
    CLASSIC = "classic"
    MODERN = "modern" # NOT IMPLEMENTED
    DARK = "dark" # NOT IMPLEMENTED
    MINIMAL = "minimal" # NOT IMPLEMENTED
    CORPORATE = "corporate" # NOT IMPLEMENTED

class ColumnEmoji(Enum):
    """Emojis para representar tipos de columnas"""
    PRIMARY_KEY = '🔑'
    FOREIGN_KEY = '🔗'
    UNIQUE = '⭐'
    NOT_NULL = '❗'
    AUTOINCREMENT = '⬆️'
    ENCRYPT = '🔒'


class RelationshipType(Enum):
    """Tipos de relaciones entre entidades"""
    ONE_TO_ONE = 'one-to-one'
    ONE_TO_MANY = 'one-to-many'
    MANY_TO_ONE = 'many-to-one'
    MANY_TO_MANY = 'many-to-many'


@dataclass
class ERColumn:
    """Representa una columna en el diagrama ER"""
    name: str
    type: str
    nullable: bool
    primary_key: bool
    foreign_key: bool
    autoincrement: bool
    unique: bool
    encrypt: bool
    description: str


@dataclass
class ERRelationship:
    """Representa una relación entre entidades"""
    from_table: str
    to_table: str
    relationship_type: RelationshipType
    local_name: str
    target_name: str


@dataclass
class EREntity:
    """Representa una entidad en el diagrama ER"""
    name: str
    table_name: str
    columns: List[ERColumn]
    is_view: bool = False
    description: Optional[str] = None


class ERDiagramGenerator(BaseGenerator):
    """
    Generador de diagramas ER usando Graphviz.
    
    Crea diagramas Entity-Relationship profesionales y visualmente atractivos
    desde los modelos SQLAlchemy definidos en el schema.
    
    Características:
    - Múltiples temas visuales
    - Detección automática de relaciones
    - Soporte para tablas y vistas
    - Múltiples formatos de salida
    - Personalización avanzada de estilos
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        format: str = 'png',
        theme: Literal['classic'] = DiagramTheme.CLASSIC.value,
        include_views: bool = True,
        include_columns: bool = True,
        include_relationships: bool = True,
        group_by_schema: bool = False,
        dpi: int = 300
    ) -> None:
        """
        Inicializa el generador de diagramas ER.
        
        Args:
            output_dir: Directorio de salida (default: docs/diagrams)
            filename: Nombre del archivo sin extensión
            format: Formato de salida (png, svg, pdf, dot)
            theme: Tema visual del diagrama
            include_views: Si incluir vistas en el diagrama
            include_columns: Si mostrar detalles de columnas
            include_relationships: Si mostrar relaciones entre entidades
            group_by_schema: Si agrupar entidades por schema
            dpi: Resolución del diagrama (solo para formatos bitmap)
        """
        super().__init__(output_dir or 'database/diagrams')
        self.format = format.lower()
        self.theme = theme
        self.include_views = include_views
        self.include_columns = include_columns
        self.include_relationships = include_relationships
        self.group_by_schema = group_by_schema
        self.dpi = dpi

        # Estado interno
        self._entities: List[EREntity] = []
        self._relationships: List[ERRelationship] = []

        # Valida que el formato sea soportado
        supported_formats = ['png', 'svg', 'pdf', 'dot', 'eps', 'ps']
        if self.format not in supported_formats:
            raise ValueError(
                f"Formato '{self.format}' no soportado. "
                f"Formatos disponibles: {', '.join(supported_formats)}"
            )
        
        #### Verificar dependencias

        # Verificar que Graphviz esté instalado en el sistema
        try:
            import graphviz
        except ImportError:
            raise ImportError(
                "graphviz no está instalado. Para usar ERDiagramGenerator:\n"
                "pip install graphviz\n"
                "o si usas poetry:\n"
                "poetry add graphviz\n\n"
                "También instala Graphviz en tu sistema:\n"
                "Ubuntu/Debian: sudo apt install graphviz\n"
                "macOS: brew install graphviz\n"
                "Windows: https://graphviz.org/download/"
            )
        
        # Verificar que la fuente esté disponible
        result = subprocess.run(['fc-list'], capture_output=True, text=True, check=True)
        if 'Noto Color Emoji' not in result.stdout:
            raise RuntimeError(
                "La fuente 'Noto Color Emoji' no está instalada.\n"
                "Para mejor compatibilidad con emojis, instala:\n"
                "Ubuntu/Debian: sudo apt install fonts-noto-color-emoji\n"
                "macOS: La fuente ya debería estar disponible"
            )
        try:
            import graphviz
            test_graph = graphviz.Digraph()
            test_graph.pipe('svg')
        except Exception:
            raise RuntimeError(
                "Graphviz no está instalado en el sistema.\n"
                "Descarga e instala desde: https://graphviz.org/download/\n"
                "Ubuntu/Debian: sudo apt install graphviz\n"
                "macOS: brew install graphviz"
            )

    @property
    def themes(self) -> Dict[DiagramTheme, Dict]:
        """Carga la configuración de temas"""
        return {
            DiagramTheme.CLASSIC.value: {
                'layout': {
                    'direction': 'BT',
                    'size': '16,10'
                },
                'fonts': {
                    'default': 'Arial',
                    'size': 10,
                    'header_size': 12
                },
                'colors': {
                    'background': '#FAFAFA',
                    'table': '#FFFFFF',
                    'table_header': '#2E3B4E',
                    'view': '#F8F9FA',
                    'view_header': "#2E4E6E",
                    'primary_key': '#FFF3CD',
                    'foreign_key': '#D1ECF1',
                    'column': '#FFFFFF',
                    'column_alt': '#F8F9FA',
                    'description': '#E9ECEF',
                    'border': '#6C757D',
                    'relationship': '#495057'
                }
            }
        }
    
    def generate(self) -> str:
        """
        Genera el diagrama ER.
        
        Returns:
            str: Ruta del archivo generado
        """
        
        # Analizar modelos y crear entidades
        self.load_entities()
        
        # Detectar relaciones
        if self.include_relationships:
            self.load_relationships()
        
        # Crear diagrama Graphviz
        dot = self.create_diagram()
        
        # Renderizar
        output_path = os.path.join(self.config.output_dir, pm.db.schema_name)
        dot.render(output_path, format=self.format, cleanup=True)
        
        final_path = f"{output_path}.{self.format}"
        
        return final_path
    
    def load_entities(self):
        """Analiza los modelos y crea entidades ER"""
        self._entities = []
        
        for model in self.models:
            try:
                
                # Saltar vistas si no están incluidas
                if model.is_view and not self.include_views:
                    continue
        
                # Crear columnas
                columns = []
                
                for name, column in model.columns.items():
                    er_column = ERColumn(
                        name=name,
                        type=column.type,
                        nullable=column.nullable,
                        primary_key=column.args.primary_key,
                        foreign_key=column.is_foreign_key,
                        autoincrement=column.args.autoincrement,
                        unique=column.args.unique,
                        encrypt=column.encrypt,
                        description=column.description
                    )
                    columns.append(er_column)
                
                entity = EREntity(
                    name=model.tablename,
                    table_name=model.tablename,
                    columns=columns,
                    is_view=model.is_view,
                    description=model._description
                )

                self._entities.append(entity)
                
            except Exception as e:
                raise Exception(f"⚠️  Error procesando modelo {getattr(model, '__name__', str(model))}: {e}")
    
    def load_relationships(self):
        """Detecta relaciones entre entidades"""
        self._relationships = []
        
        for model in self.models:

            if model.is_view:
                continue
            
            for relation in model.relations.values():

                if not relation.implicit:
                    continue

                relationship = ERRelationship(
                    from_table=relation.local.tablename,
                    to_table=relation.target.tablename,
                    relationship_type=relation.direction,
                    local_name=relation.name,
                    target_name=relation.backref
                )
                    
                self._relationships.append(relationship)
    
    def create_diagram(self):
        """Crea el diagrama Graphviz"""
        import graphviz
        
        # Crear diagrama base
        dot = graphviz.Digraph(
            name=f'{pm.db.provider.database}@{pm.db.schema_name}',
            comment='Entity Relationship Diagram'
        )

        # Configuración global
        dot.attr(
            rankdir=self.themes[self.theme]['layout']['direction'],
            size=self.themes[self.theme]['layout']['size'],
            dpi=str(self.dpi),
            bgcolor=self.themes[self.theme]['colors']['background'],
            fontname=self.themes[self.theme]['fonts']['default'],
            fontsize=str(self.themes[self.theme]['fonts']['size']),
            splines='ortho',         # Lo ideal son líneas ortogonales (ortho)
            overlap='false',         # Evitar solapamiento
            sep='+20',              # Separación mayor entre nodos
            esep='+10',             # Separación mayor entre edges
            nodesep='1.0',          # Separación horizontal entre nodos
            ranksep='1.5',          # Separación vertical entre ranks
            concentrate='false',     # No concentrar edges
            newrank='true'          # Mejor algoritmo de ranking
        )

        # Configuración de nodos por defecto
        dot.attr('node',
                shape='plaintext',
                fontname=self.themes[self.theme]['fonts']['default'],
                fontsize=str(self.themes[self.theme]['fonts']['size']))
        
        # Configuración de edges por defecto
        dot.attr('edge',
                fontname=self.themes[self.theme]['fonts']['default'],
                fontsize=str(self.themes[self.theme]['fonts']['size'] - 1),
                color=self.themes[self.theme]['colors']['relationship'])
        
        for entity in self._entities:
            # Crear tabla HTML para la entidad
            html_table = self._create_entity_html_table(entity)
            
            # Configurar color según el tipo
            if entity.is_view:
                fillcolor = self.themes[self.theme]['colors']['view']
                style = 'filled,rounded'
            else:
                fillcolor = self.themes[self.theme]['colors']['table']
                style = 'filled'
            
            # Agregar nodo al diagrama
            dot.node(
                entity.table_name,
                label=f'<{html_table}>',
                shape='plaintext',
                style=style,
                fillcolor=fillcolor,
                color=self.themes[self.theme]['colors']['border']
            )
        
        # Agregar relaciones si están habilitadas
        if self.include_relationships:
            for rel in self._relationships:
                # Configurar estilo según el tipo de relación
                down_label = f'🔽 {rel.local_name}'
                up_label = f'🔼 {rel.target_name}'
                if rel.relationship_type == RelationshipType.ONE_TO_ONE.value:
                    arrowhead = 'dot'
                    arrowtail = 'dot'
                elif rel.relationship_type == RelationshipType.ONE_TO_MANY.value:
                    arrowhead = 'dot'
                    arrowtail = 'crow'
                elif rel.relationship_type == RelationshipType.MANY_TO_ONE.value:
                    arrowhead = 'crow'
                    arrowtail = 'dot'
                else:  # MANY_TO_MANY
                    arrowhead = 'crow'
                    arrowtail = 'crow'
                
                # Crear nodo invisible intermedio
                # Esto es para evitar que Graphviz dibuje una línea directa entre las tablas
                # y permitir un mejor control del layout
                # El nodo invisible se usa como un "waypoint" para la relación
                waypoint_name = f"waypoint_{rel.from_table}_{rel.to_table}"
                dot.node(
                    waypoint_name,
                    label='',
                    shape='point',
                    style='invis',
                    width='0',
                    height='0',
                    pos=f'{rel.from_table}+0.1,0'
                )
                
                # Crear dos edges: desde origen a waypoint y desde waypoint a destino
                # Agregar edge
                dot.edge(
                    waypoint_name,
                    rel.from_table,
                    label=down_label,
                    arrowhead=arrowhead,
                    arrowsize='1',
                    headclip='true',
                    tailclip='true',
                    dir='forward',
                    fontsize=str(self.themes[self.theme]['fonts']['size']),
                    color=self.themes[self.theme]['colors']['relationship'],
                    penwidth='1.5',
                )
                 # Agregar edge
                dot.edge(
                    rel.to_table,
                    waypoint_name,
                    label=up_label,
                    arrowtail=arrowtail,
                    arrowsize='1.5',
                    headclip='true',
                    tailclip='true',
                    dir='back',
                    fontsize=str(self.themes[self.theme]['fonts']['size']),
                    color=self.themes[self.theme]['colors']['relationship'],
                    penwidth='1.5',
                )
        
        theme_config = self.themes[self.theme]
        legend_html = self._create_legend_html_table()
        
        # Agregar nodo de leyenda
        dot.node(
            'legend',
            label=f'<{legend_html}>',
            shape='plaintext',
            style='filled',
            fillcolor=theme_config['colors']['background'],
            color=theme_config['colors']['border']
        )
        
        # ✅ Crear un rank para posicionar la leyenda
        # Esto asegura que aparezca en la parte inferior
        with dot.subgraph() as s:
            s.attr(rank='max')
            s.node('legend')
        
        return dot

    
    def _create_entity_html_table(self, entity: EREntity) -> str:
        """Crea la tabla HTML para representar una entidad"""
        
        theme_config = self.themes[self.theme]

        if entity.is_view:
            header_color = theme_config['colors']['view_header']
            icon = '👁️'
            span = 3
        else:
            header_color = theme_config['colors']['table_header']
            icon = '📋'
            span = 4

        html = '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">'

        # Agregar fila de encabezado con nombre de entidad
        html += (
            '<TR>'
            f'<TD COLSPAN="{span}" BGCOLOR="{header_color}" BORDER="1">'
            f'<FONT POINT-SIZE="{theme_config["fonts"]["header_size"]}" COLOR="white">'
            f'{icon} {entity.name}'
            '</FONT>'
            '</TD>'
            '</TR>'
        )
        
        # Agregar descripción si existe
        if entity.description:
            # Dividir la descripción en líneas de máximo 50 caracteres
            description_lines = []
            words = entity.description.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= 70:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        description_lines.append(current_line)
                    current_line = word
            
            if current_line:
                description_lines.append(current_line)
            
            html += (
                f'<TR>'
                f'<TD COLSPAN="{span}" BGCOLOR="{theme_config["colors"]["description"]}" ALIGN="LEFT" BORDER="1">'
                f'<FONT POINT-SIZE="{theme_config["fonts"]["size"] - 1}" COLOR="black">'
            )
            
            # Generar HTML para cada línea
            for line in description_lines:
                html += f'{line}<BR ALIGN="LEFT"/>'
            
            html += (
                f'</FONT>'
                f'</TD>'
                f'</TR>'
            )
        
        # Agregar columnas si están habilitadas
        if self.include_columns and entity.columns:
            for column in entity.columns:
                html += self._create_column_html_row(column, theme_config, entity.is_view)

        elif not self.include_columns:
            # Mostrar solo el número de columnas
            html += (
                f'<TR>'
                f'<TD COLSPAN="{span}" BGCOLOR="{theme_config["colors"]["column_alt"]}" HEIGHT="20" BORDER="1">'
                f'<FONT POINT-SIZE="{theme_config["fonts"]["size"] - 1}">'
                f'{len(entity.columns)} columnas'
                f'</FONT>'
                f'</TD>'
                f'</TR>'
            )
        
        # Cerrar tabla al final
        html += '</TABLE>'
        
        return html
    
    def _create_column_html_row(self, column: ERColumn, theme_config: Dict, is_view: bool) -> str:
        """Crea una fila HTML para una columna"""
        
        # Determinar color de fondo
        if column.primary_key:
            bg_color = theme_config['colors']['primary_key']
        elif column.foreign_key:
            bg_color = theme_config['colors']['foreign_key']
        else:
            bg_color = theme_config['colors']['column']
        
        # Indicadores de columna
        icons = []
        if column.primary_key:
            icons.append(ColumnEmoji.PRIMARY_KEY.value)
        if column.foreign_key:
            icons.append(ColumnEmoji.FOREIGN_KEY.value)
        if column.unique:
            icons.append(ColumnEmoji.UNIQUE.value)
        if not column.nullable:
            icons.append(ColumnEmoji.NOT_NULL.value)
        if column.autoincrement:
            icons.append(ColumnEmoji.AUTOINCREMENT.value)
        if column.encrypt:
            icons.append(ColumnEmoji.ENCRYPT.value)
        
        icon_str = ''.join(icons)

        span = 'COLSPAN="2"' if is_view else 'COLSPAN="1"'

        # Column name
        row = (
            f'<TR>'
            f'<TD {span} BGCOLOR="{bg_color}" ALIGN="LEFT" BORDER="1" SIDES="LTB">'
            f'<FONT POINT-SIZE="{theme_config["fonts"]["size"]}">'
            f'{column.name}'
            f'</FONT>'
            f'</TD>'
        )

        if not is_view:
            # Column properties
            row += (
                f'<TD BGCOLOR="{bg_color}" ALIGN="RIGHT" BORDER="1" SIDES="TB">'
                f'<FONT POINT-SIZE="{theme_config["fonts"]["size"] - 1}">'
                f'{icon_str or " "}'
                f'</FONT>'
                f'</TD>'
            )
        
        # Column type
        row += (
            f'<TD BGCOLOR="{bg_color}" ALIGN="LEFT" BORDER="1">'
            f'<FONT POINT-SIZE="{theme_config["fonts"]["size"] - 1}">'
            f'{column.type.upper()}'
            f'</FONT>'
            f'</TD>'
            f'{"</TR>" if is_view else ""}'
        )

        if not is_view:
            # Dividir la descripción en líneas de máximo 50 caracteres
            description_lines = []
            words = column.description.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= 50:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        description_lines.append(current_line)
                    current_line = word
            
            if current_line:
                description_lines.append(current_line)
            
            # Generar HTML para cada línea
            description = ''
            for line in description_lines:
                description += f'{line}<BR ALIGN="LEFT"/>'

            row += (
                f'<TD BGCOLOR="{bg_color}" ALIGN="LEFT" BORDER="1">'
                f'<FONT POINT-SIZE="{theme_config["fonts"]["size"] - 1}">'
                f'{description or "---"}'
                f'</FONT>'
                f'</TD>'
                f'</TR>'
            )

        return row

    def _create_legend_html_table(self) -> str:
        """Crea una leyenda compacta horizontal"""
        
        legend_items = [
            (ColumnEmoji.PRIMARY_KEY.value, 'Primary key'),
            (ColumnEmoji.FOREIGN_KEY.value, 'Foreign key'),
            (ColumnEmoji.UNIQUE.value, 'Unique'),
            (ColumnEmoji.NOT_NULL.value, 'Not null'),
            (ColumnEmoji.AUTOINCREMENT.value, 'Autoincrement'),
            (ColumnEmoji.ENCRYPT.value, 'Encrypted'),
        ]
        
        html = '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2">'
        
        for emoji, description in legend_items:
            html += (
                '<TR>'
                '<TD ALIGN="LEFT">'
                f'{emoji}'
                '</TD>'
                '<TD ALIGN="LEFT">'
                f'{description}'
                '</TD>'
                '</TR>'
            )
        
        html += '</TABLE>'
        
        return html