# 🚀 TAI-SQL Framework

**TAI-SQL** es un framework declarativo para Python que simplifica el trabajo con bases de datos relacionales usando SQLAlchemy. Permite definir esquemas de forma intuitiva y generar automáticamente modelos, CRUDs y diagramas ER.

## 📦 Instalación

### Usando Poetry (Recomendado)
```bash
poetry add tai-sql
```

### Usando pip
```bash
pip install tai-sql
```

### Dependencias del sistema
Para generar diagramas ER, necesitas instalar Graphviz:

```bash
# Ubuntu/Debian
sudo apt install graphviz

# macOS
brew install graphviz

# Windows
# Descargar desde: https://graphviz.org/download/
```

## 🗂️ Schema

Un **schema** es un archivo Python que define la estructura completa de tu base de datos. Es el punto central donde configuras la conexión, defines tus modelos y especificas qué recursos se generarán automáticamente.

### 📁 Estructura típica de un schema

```python
# schemas/mi_proyecto.py
from __future__ import annotations
from tai_sql import *
from tai_sql.generators import *

# 1️⃣ Configurar conexión a la base de datos
datasource(provider=env('DATABASE_URL'))

# 2️⃣ Configurar generadores
generate(
    ModelsGenerator(output_dir='mi_proyecto'),
    CRUDGenerator(output_dir='mi_proyecto'),
    ERDiagramGenerator(output_dir='mi_proyecto/diagrams')
)

# 3️⃣ Definir modelos (Tablas y Vistas)
class Usuario(Table):
    '''Tabla que almacena información de los usuarios del sistema'''
    __tablename__ = "usuario"
    
    id: int = column(primary_key=True, autoincrement=True)
    nombre: str
    pwd: str = column(encrypt=True)
    email: str = column(unique=True)
    
    posts: List[Post]  # Relación implícita

class Post(Table):
    '''Tabla que almacena los posts de los usuarios'''
    __tablename__ = "post"
    
    id: int = column(primary_key=True, autoincrement=True)
    titulo: str = 'Post title'
    contenido: str
    timestamp: datetime = column(default=datetime.now)
    usuario_id: int
    
    # Relación explícita
    usuario: Usuario = relation(
        fields=['usuario_id'],
        references=['id'], 
        backref='posts'
    )

class UserStats(View):
    '''Vista que muestra estadísticas de los usuarios'''
    __tablename__ = "user_stats"
    __query__ = query('user_stats.sql')

    usuario_id: int
    nombre_usuario: str
    post_count: int
```

### 🎯 Concepto clave

El schema actúa como el **"blueprint"** de tu aplicación:
- **Define** la estructura de base de datos (tablas, vistas, tipos, etc...)
- **Configura** la conexión y parámetros
- **Especifica** qué código se generará automáticamente
- **Centraliza** toda la configuración en un solo lugar

Una vez definido, el CLI de TAI-SQL usa este schema para:
- Sincronizar la base de datos (`tai-sql push`)
- Generar modelos SQLAlchemy, CRUDs y diagramas (`tai-sql generate`)

## 🏗️ Elementos del Schema

El esquema es el corazón de TAI-SQL. Define la estructura de tu base de datos y los recursos que se generarán automáticamente.

### 📊 `datasource()` - Configuración de la Base de Datos

La función `datasource()` configura la conexión a tu base de datos:

```python
from tai_sql import datasource, env, connection_string, params

# ✅ Opción 1: Variables de entorno (Recomendado para producción)
datasource(
    provider=env('DATABASE_URL')  # postgres://user:pass@host:port/dbname
)

# ✅ Opción 2: String de conexión directo (Para desarrollo/testing)
datasource(
    provider=connection_string('postgresql://user:password@localhost/mydb')
)

# ✅ Opción 3: Parámetros individuales (Para desarrollo/testing)
datasource(
    provider=params(
        drivername='postgresql',
        username='user',
        password='password',
        host='localhost',
        port=5432,
        database='mydb'
    )
)
```

**Opciones avanzadas:**
```python
datasource(
    provider=env('DATABASE_URL'),
    secret_key_name='SECRET_KEY',  # Variable de entorno para encriptación
    pool_size=20,           # Tamaño del pool de conexiones
    max_overflow=30,        # Conexiones adicionales permitidas
    pool_timeout=30,        # Timeout para obtener conexión
    pool_recycle=3600,      # Reciclar conexiones cada hora
    echo=True              # Mostrar consultas SQL en desarrollo
)
```

### 🔧 `generate()` - Configuración de Generadores

La función `generate()` define qué recursos se generarán automáticamente:

```python
from tai_sql import generate
from tai_sql.generators import ModelsGenerator, CRUDGenerator, ERDiagramGenerator

generate(
    # Generar modelos SQLAlchemy
    ModelsGenerator(
        output_dir='database/database'
    ),
    # Generar CRUDs sincronos
    CRUDGenerator(
        output_dir='database/database',
        mode='sync'  # 'sync', 'async', o 'both'
    ),
    # Generar diagramas ER
    ERDiagramGenerator(
        output_dir='database/diagrams'
    )
)
```

### 📋 `Table` - Definición de Tablas

Las tablas son la base de tu modelo de datos:

```python
from __future__ import annotations
from tai_sql import Table, column, relation
from typing import List, Optional
from datetime import date

class Usuario(Table):
    '''Tabla que almacena información de los usuarios'''
    __tablename__ = "usuario"
    
    # Columnas básicas
    id: int = column(primary_key=True, autoincrement=True)
    name: str
    email: str = column(unique=True)
    fecha_alta: date
    
    # Relaciones
    posts: List[Post] # Implícita

class Post(Table):
    '''Tabla que almacena la información de los posts de los usuarios'''
    __tablename__ = "post"
    
    id: int = column(primary_key=True, autoincrement=True)
    title: str = 'Post title'
    content: str
    author_id: int
    published: Optional[bool]
    
    # Relación explícita
    author: Usuario = relation(
        fields=['author_id'], 
        references=['id'], 
        backref='posts'
    )
```

#### 📝 Documentación de Tablas

TAI-SQL permite documentar las tablas de dos formas equivalentes para proporcionar contexto y descripción de cada modelo:

```python
# Opción 1: Usando docstring de la clase
class Usuario(Table):
    '''Tabla que almacena información de los usuarios del sistema'''
    __tablename__ = "usuario"
    
    id: int = column(primary_key=True, autoincrement=True)
    name: str
    email: str

# Opción 2: Usando el metaparámetro __description__
class Post(Table):
    __tablename__ = "post"
    __description__ = "Tabla que almacena los posts de los usuarios"
    
    id: int = column(primary_key=True, autoincrement=True)
    title: str
    content: str
```

**Prioridad**
- El uso del metaparámetro __description__ tiene preferencia sobre el docstring de la clase.
De esta forma si concurren ambos en una tabla, __description__ tendrá prioridad.

**Usos de la documentación:**
- 📊 **Diagramas ER**: Aparece en los diagramas generados por `ERDiagramGenerator`

Ambas formas son equivalentes y permiten que los generadores accedan a la descripción de la tabla para crear documentación automática, comentarios en los modelos generados y descripciones en los diagramas ER.

#### 🛠️ Función `column()` - Configuración de Columnas

La función `column()` permite configurar las propiedades específicas de las columnas:

```python
def column(
    primary_key=False,      # Si es clave primaria
    unique=False,           # Si debe ser único
    default=None,           # Valor por defecto
    server_now=False,       # Para usar NOW() del servidor
    index=False,            # Si debe tener índice
    autoincrement=False,    # Si es autoincremental
    encrypt=False           # Si queremos que se encripte
):
```

**Ejemplos de uso:**

```python
class Producto(Table):
    __tablename__ = "producto"
    
    # Clave primaria autoincremental
    id: int = column(primary_key=True, autoincrement=True)
    
    # Campo único
    sku: str = column(unique=True)
    
    # Campo con valor por defecto
    estado: str = "activo"
    
    # Equivalente a
    estado: str = column(default="activo")
    
    # Campo con índice para búsquedas rápidas
    categoria: str = column(index=True)
    
    # Campo opcional (nullable automático por tipo Optional)
    descripcion: Optional[str]
    
    # Campo obligatorio (nullable=False automático)
    nombre: str

    # Campo encriptado (necesita una SECRET_KEY)
    password: str = column(encrypt=True)
```

**Parámetros detallados:**

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `primary_key` | `bool` | Define si la columna es clave primaria | `column(primary_key=True)` |
| `unique` | `bool` | Garantiza valores únicos en la columna | `column(unique=True)` |
| `default` | `Any` | Valor por defecto para nuevos registros | `column(default="activo")` |
| `server_now` | `bool` | Usa la función NOW() del servidor de BD | `column(server_now=True)` |
| `index` | `bool` | Crea un índice en la columna para búsquedas rápidas | `column(index=True)` |
| `autoincrement` | `bool` | Incrementa automáticamente el valor (solo integers) | `column(autoincrement=True)` |
| `encrypt` | `bool` | Encripta automáticamente el contenido de la columna | `column(encrypt=True)` |

#### 🔗 Función `relation()` - Definición de Relaciones

La función `relation()` define relaciones explícitas entre tablas:

```python
def relation(
    fields: List[str],          # Campos en la tabla actual (foreign keys)
    references: List[str],      # Campos referenciados en la tabla destino
    backref: str,              # Nombre de la relación inversa
    onDelete='cascade',        # Comportamiento al eliminar
    onUpdate='cascade'         # Comportamiento al actualizar
):
```

**Conceptos importantes:**

1. **Relaciones Explícitas vs Implícitas:**
   - **Explícita:** Se define usando `relation()` en la tabla que CONTIENE la foreign key
   - **Implícita:** Se declara solo con el tipo en la tabla que NO contiene la foreign key

2. **Dónde usar `relation()`:**
   - SOLO en la tabla que tiene la columna foreign key
   - La tabla "origen" muestra la relación como `List[...]` (implícita)

**Ejemplo completo:**

```python
class Usuario(Table):
    __tablename__ = "usuario"
    
    id: int = column(primary_key=True, autoincrement=True)
    nombre: str
    email: str = column(unique=True)
    
    # Relación IMPLÍCITA - Usuario NO tiene foreign key hacia Post
    # Se muestra automáticamente como List por la relación inversa
    posts: List[Post]  # ← No necesita relation()

class Post(Table):
    __tablename__ = "post"
    
    id: int = column(primary_key=True, autoincrement=True)
    titulo: str
    contenido: str
    autor_id: int  # ← Esta ES la foreign key
    
    # Relación EXPLÍCITA - Post SÍ tiene foreign key hacia Usuario
    autor: Usuario = relation(
        fields=['autor_id'],     # Campo FK en esta tabla
        references=['id'],       # Campo PK en tabla destino
        backref='posts'         # Nombre de relación inversa en Usuario
    )
```

**Parámetros de `relation()`:**

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `fields` | Lista de columnas FK en la tabla actual | `['autor_id']` |
| `references` | Lista de columnas PK en la tabla destino | `['id']` |
| `backref` | Nombre de la relación inversa | `'posts'` |
| `onDelete` | Acción al eliminar: `'cascade'`, `'restrict'`, `'set null'` | `'cascade'` |
| `onUpdate` | Acción al actualizar: `'cascade'`, `'restrict'`, `'set null'` | `'cascade'` |

**Regla fundamental:**
- ✅ Usa `relation()` SOLO en la tabla que tiene la foreign key
- ✅ La tabla "origen" automáticamente muestra `List[...]` por la relación inversa
- ❌ NO uses `relation()` en ambos lados de la relación

#### 🔐 Encriptación de Columnas

TAI-SQL soporta encriptación automática de columnas para proteger datos sensibles:

```python
from tai_sql import Table, column, datasource

# Configurar datasource con clave de encriptación
datasource(
    provider=env('DATABASE_URL'),
    secret_key_name='SECRET_KEY'  # Variable de entorno con la clave secreta
)

class Usuario(Table):
    __tablename__ = "usuarios"
    
    id: int = column(primary_key=True, autoincrement=True)
    email: str = column(unique=True)
    nombre: str
    
    # Columnas encriptadas - Los datos se encriptan automáticamente
    password: str = column(encrypt=True)
    telefono: Optional[str] = column(encrypt=True)
    datos_bancarios: Optional[str] = column(encrypt=True)

```

**Configuración requerida:**

1. **Variable de entorno**: Define una clave secreta segura
   ```bash
   export SECRET_KEY="tu_clave_secreta_de_al_menos_32_caracteres"
   ```

2. **Configuración en datasource**: Especifica el nombre de la variable
   ```python
   datasource(
       provider=env('DATABASE_URL'),
       secret_key_name='SECRET_KEY'  # Por defecto es 'SECRET_KEY'
   )
   ```

**Características de la encriptación:**

- ✅ **Automática**: Los datos se encriptan al escribir y desencriptan al leer
- ✅ **Transparente**: El código funciona igual que columnas normales
- ✅ **Segura**: Usa `cryptography.fernet` con claves de 256 bits
- ✅ **Validación**: Verifica la existencia de la clave secreta antes de generar

**Ejemplo de uso:**

```python
# El ModelGenerator crea propiedades híbridas automáticamente
user = Usuario(
    email="juan@example.com",
    nombre="Juan",
    password="mi_password_secreto",  # Se encripta automáticamente
    telefono="123-456-7890"          # Se encripta automáticamente
)

# Al leer, se desencripta automáticamente
print(user.password)  # "mi_password_secreto" (desencriptado)
print(user.telefono)  # "123-456-7890" (desencriptado)

# En la BD se almacena encriptado
print(user._password)  # "gAAAAABh..." (encriptado)
```

**Validaciones de seguridad:**

- ❗ **Clave requerida**: Si hay columnas con `encrypt=True`, la clave secreta debe existir
- ❗ **Longitud mínima**: La clave debe tener al menos 32 caracteres
- ❗ **Solo strings**: Solo columnas de tipo string pueden encriptarse


### 👁️ `View` - Definición de Vistas

Las vistas permiten crear consultas complejas reutilizables:

```python
from tai_sql import View, query

class UserStats(View):
    '''Estadísticas de usuarios y sus posts'''
    __tablename__ = "user_stats"
    __query__ = query('user_stats.sql')  # Archivo SQL en .../views/
    
    # Definir las columnas que retorna la vista
    user_id: int
    user_name: str
    post_count: int
    last_post_date: datetime
```

**Archivo SQL correspondiente** (`.../views/user_stats.sql`):
```sql
SELECT
    u.id AS user_id,
    u.name AS user_name,
    COUNT(p.id) AS post_count,
    MAX(p.created_at) AS last_post_date
FROM usuarios u
LEFT JOIN posts p ON u.id = p.author_id
WHERE u.active = true
GROUP BY u.id, u.name
```

### 🔢 `Enum` - Definición de Enumeraciones

Los enums permiten definir listas de valores predefinidos para ciertas columnas, garantizando integridad de datos:

```python
from tai_sql import Table, column
from enum import Enum

# Definir enum como clase Python estándar
class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"

class Post(Table):
    '''Tabla de posts con tipo de contenido controlado'''
    __tablename__ = "post"
    
    id: int = column(primary_key=True, autoincrement=True)
    title: str
    content: str
    content_type: ContentType  # ← Usar enum como tipo de columna
    timestamp: datetime = column(server_now=True)
```

**Características de los Enums:**

- ✅ **Auto-registro**: Los enums se registran automáticamente al definirlos
- ✅ **Validación automática**: Solo acepta valores definidos en el enum
- ✅ **Integración CRUD**: El CRUD generado expone los valores disponibles
- ✅ **Soporte en DTOs**: Los Pydantic DTOs incluyen validación de enum
- ✅ **Type hints**: Autocompletado completo en tu IDE

**Ejemplo con múltiples enums:**

```python
class Status(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Table):
    __tablename__ = "tasks"
    
    id: int = column(primary_key=True, autoincrement=True)
    title: str
    status: Status = Status.DRAFT          # ← Con valor por defecto
    priority: Priority
    created_at: datetime = column(server_now=True)
```

**Ventajas de usar Enums:**

- 🛡️ **Integridad de datos**: Previene valores inválidos en la BD
- 📝 **Documentación clara**: Los valores posibles están definidos en el código
- 🔄 **Refactoring seguro**: Cambios de enum se propagan automáticamente
- 🚀 **Performance**: Validación rápida sin consultas a BD
- 🎯 **Type safety**: Detección de errores en tiempo de desarrollo

## 🎯 Generadores Incluidos

### 📝 ModelsGenerator

Genera modelos SQLAlchemy estándar desde tus definiciones de `Table` y `View`.

```python
ModelsGenerator(
    output_dir='...'  # Directorio donde se generarán los modelos
)
```

### 🔄 CRUDGenerator

Genera clases CRUD completas con operaciones Create, Read, Update, Delete optimizadas.

```python
CRUDGenerator(
    output_dir='...',
    models_import_path='...',
    mode='sync'  # 'sync', 'async', o 'both'
)
```

**Estructura generada:**
```
.../<schema_name>/crud/
├── syn/                    # Si mode='sync' o 'both'
│   ├── __init__.py         # API unificada (public_api)
│   ├── session_manager.py  # Gestor de sesiones síncronas
│   ├── daos.py             # Data Access Objects por tabla
│   ├── dtos.py             # Data Transfer Objects (Pydantic)
│   └── utils.py            # Utilidades y decoradores
└── asyn/                   # Si mode='async' o 'both'
    ├── __init__.py         # API unificada (public_api)
    ├── session_manager.py  # Gestor de sesiones asíncronas
    ├── daos.py             # Data Access Objects por tabla
    ├── dtos.py             # Data Transfer Objects (Pydantic)
    └── utils.py            # Utilidades y decoradores
```

**Arquitectura del CRUD generado:**

El sistema genera una arquitectura por capas completa:

1. **📋 DTOs (Data Transfer Objects)**: Objetos Pydantic para validación y serialización
2. **🗃️ DAOs (Data Access Objects)**: Clases especializadas por tabla con métodos CRUD
3. **🔗 API Unificada**: Objeto `public_api` que centraliza el acceso a todos los DAOs
4. **⚙️ Gestión de sesiones**: SessionManager para manejo automático de transacciones

**Ejemplo de uso del CRUD generado:**

```python
from database.public.crud.syn import public_api

# ===== 🔍 OPERACIONES DE LECTURA =====

# Buscar un usuario por ID
user = public_api.usuario.find(id=1)
# Retorna: UsuarioRead | None

# Buscar múltiples usuarios con filtros
users = public_api.usuario.find_many(
    limit=10, 
    offset=0,
    name="Juan",
    email="juan@example.com"
)
# Retorna: List[UsuarioRead]

# Buscar con relaciones incluidas
user = public_api.usuario.find(
    id=1, 
    includes=['posts', 'posts.comments']  # ← Carga optimizada
)
# user.posts estará poblado automáticamente

# Contar registros con filtros
total_users = public_api.usuario.count(name="Juan")
# Retorna: int

# Verificar existencia
exists = public_api.usuario.exists(email="juan@example.com")
# Retorna: bool

# ===== 🆕 OPERACIONES DE CREACIÓN =====

# Crear usuario usando DTO
from database.public.crud.syn import UsuarioCreate

user_data = UsuarioCreate(
    name="Ana García",
    pwd="password123",
    email="ana@example.com"
)
user = public_api.usuario.create(user_data)
# Retorna: UsuarioRead

# Crear múltiples usuarios
users_data = [
    UsuarioCreate(name="Pedro", pwd="pass1", email="pedro@example.com"),
    UsuarioCreate(name="María", pwd="pass2", email="maria@example.com"),
]
count = public_api.usuario.create_many(users_data)
# Retorna: int (número de registros creados)

# ===== 🔄 OPERACIONES DE ACTUALIZACIÓN =====

# Actualizar usuario específico
from database.public.crud.syn import UsuarioUpdateValues

updated_count = public_api.usuario.update(
    id=1,  # Filtro por ID
    updated_values=UsuarioUpdateValues(
        name="Juan Carlos",
        email="juancarlos@example.com"
    )
)
# Retorna: int (número de registros actualizados)

# Actualización masiva con filtros
from database.public.crud.syn import UsuarioUpdate, UsuarioFilter

result = public_api.usuario.update_many(
    payload=UsuarioUpdate(
        filter=UsuarioFilter(name="Juan"),
        values=UsuarioUpdateValues(name="Juan Actualizado")
    )
)
# Retorna: int

# Upsert (crear o actualizar)
user = public_api.usuario.upsert(
    usuario=UsuarioCreate(
        name="Carlos",
        pwd="password",
        email="carlos@example.com"
    ),
    match_fields=['email']  # Campo para verificar existencia
)
# Retorna: UsuarioRead

# ===== 🗑️ OPERACIONES DE ELIMINACIÓN =====

# Eliminar por ID
deleted_count = public_api.usuario.delete(id=1)
# Retorna: int

# Eliminación masiva con filtros
filters_list = [
    {"name": "Usuario1"},
    {"email": "obsoleto@example.com"}
]
deleted_count = public_api.usuario.delete_many(filters_list)
# Retorna: int

# ===== 📊 INTEGRACIÓN CON PANDAS =====

# Exportar a DataFrame
users_df = public_api.usuario.as_dataframe(
    limit=1000,
    name="Juan"  # ← Con filtros opcionales
)
# Retorna: pandas.DataFrame con optimización automática de tipos

# Importar desde DataFrame
import pandas as pd

new_users_df = pd.DataFrame({
    'name': ['Luis', 'Carmen', 'Roberto'],
    'pwd': ['pass1', 'pass2', 'pass3'],
    'email': ['luis@test.com', 'carmen@test.com', 'roberto@test.com']
})

inserted_count = public_api.usuario.from_dataframe(
    df=new_users_df,
    validate_types=True,           # Validar tipos automáticamente
    ignore_extra_columns=True,     # Ignorar columnas no definidas
    fill_missing_nullable=True     # Llenar campos opcionales con None
)
# Retorna: int (registros insertados)

# ===== 🔢 TRABAJAR CON ENUMS =====

# Obtener valores disponibles del enum
content_types = public_api.content_type.find_many()
# Retorna: ['text', 'image', 'video']

# Usar en creación con validación
post = public_api.post.create(PostCreate(
    title="Mi post",
    content="Contenido",
    content_type="text"  # ← Validado automáticamente
))

# ===== 🏗️ GESTIÓN DE SESIONES TRANSACCIONALES =====

# Operaciones transaccionales (múltiples operaciones en una transacción)
with public_api.session_manager.get_session() as session:
    # Crear usuario
    user = public_api.usuario.create(
        UsuarioCreate(name="Transaccional", pwd="test", email="trans@test.com"),
        session=session
    )
    
    # Crear post asociado
    post = public_api.post.create(
        PostCreate(title="Post", content="Contenido", author_id=user.id),
        session=session
    )
    
    # Si cualquier operación falla, toda la transacción se revierte
```

**🎯 Características avanzadas del CRUD:**

1. **✅ Type Safety completo**: Todos los métodos tienen type hints precisos
2. **🔄 Carga optimizada de relaciones**: Soporte para `includes` con `joinedload`/`selectinload`
3. **📊 Integración nativa con Pandas**: Exportación/importación optimizada
4. **🛡️ Validación automática**: DTOs Pydantic validan datos antes de BD
5. **⚡ Gestión de sesiones**: Automática o manual según necesidad
6. **🔍 Logging integrado**: Todas las operaciones quedan registradas
7. **🎭 Manejo de errores**: Decorador `@error_handler` con rollback automático

**📋 DTOs Generados por tabla:**

Para cada tabla se generan los siguientes DTOs Pydantic:

```python
# Lectura (datos que vienen de la BD)
UsuarioRead: BaseModel  # Con relaciones opcionales

# Creación (datos para nuevos registros)  
UsuarioCreate: BaseModel  # Sin campos autogenerados

# Filtros (para operaciones de búsqueda)
UsuarioFilter: BaseModel  # Todos los campos opcionales

# Actualización de valores
UsuarioUpdateValues: BaseModel  # Campos a modificar

# Actualización completa (filtros + valores)
UsuarioUpdate: BaseModel  # Combina filter + values

# Validador de DataFrame
UsuarioDataFrameValidator  # Para operaciones con Pandas
```

**🏗️ DAOs Generados por tabla:**

Cada tabla genera una clase DAO especializada:

```python
class UsuarioSyncDAO:
    """DAO con documentación completa de todos los métodos"""
    
    def __init__(self, session_manager: SyncSessionManager)
    
    # Métodos de lectura
    def find(self, id: int, includes: Optional[List[str]] = None, session: Optional[Session] = None) -> Optional[UsuarioRead]
    def find_many(self, limit: Optional[int] = None, offset: Optional[int] = None, **filters, session: Optional[Session] = None) -> List[UsuarioRead]
    
    # Métodos de escritura  
    def create(self, usuario: UsuarioCreate, session: Optional[Session] = None) -> UsuarioRead
    def create_many(self, records: List[UsuarioCreate], session: Optional[Session] = None) -> int
    def update(self, id: int, updated_values: UsuarioUpdateValues, session: Optional[Session] = None) -> int
    def update_many(self, payload: UsuarioUpdate, session: Optional[Session] = None) -> int
    def upsert(self, usuario: UsuarioCreate, match_fields: List[str], session: Optional[Session] = None) -> UsuarioRead
    def upsert_many(self, records: List[UsuarioCreate], match_fields: List[str], session: Optional[Session] = None) -> int
    def delete(self, id: int, session: Optional[Session] = None) -> int
    def delete_many(self, filters_list: List[Dict[str, Any]], session: Optional[Session] = None) -> int
    
    # Métodos de utilidad
    def count(self, **filters, session: Optional[Session] = None) -> int
    def exists(self, **filters, session: Optional[Session] = None) -> bool
    
    # Integración Pandas
    def as_dataframe(self, **filters) -> DataFrame
    def from_dataframe(self, df: DataFrame, validate_types: bool = False, ignore_extra_columns: bool = False, fill_missing_nullable: bool = True) -> int
```

**👁️ DAOs para Vistas (Solo lectura):**

Las vistas generan DAOs con operaciones de solo lectura:

```python
# Acceso a vista UserStats
stats = public_api.user_stats.find_many(
    limit=10,
    user_id=1,                    # Filtros específicos de la vista
    min_post_count=5,
    max_post_count=100
)
# Retorna: List[UserStatsRead]

# Exportar vista a DataFrame
stats_df = public_api.user_stats.as_dataframe(
    min_post_count=10  # Con filtros opcionales
)
# Retorna: pandas.DataFrame optimizado

# Las vistas NO tienen métodos de escritura (create, update, delete)
# Solo: find_many, count, exists, as_dataframe
```

**🔗 Acceso unificado con `public_api`:**

El objeto `public_api` es un singleton que centraliza el acceso:

```python
from database.public.crud.syn import public_api

# ✅ Acceso a tablas (CRUD completo)
public_api.usuario      # UsuarioSyncDAO - Operaciones completas
public_api.post         # PostSyncDAO - Operaciones completas  
public_api.comment      # CommentSyncDAO - Operaciones completas

# 👁️ Acceso a vistas (Solo lectura)
public_api.user_stats   # UserStatsSyncDAO - Solo lectura

# 🔢 Acceso a enums (Solo valores)
public_api.content_type # EnumModel - Lista de valores

# ⚙️ Gestor de sesiones compartido
public_api.session_manager  # SyncSessionManager para transacciones
```

### 📊 ERDiagramGenerator

Genera diagramas Entity-Relationship profesionales usando Graphviz.

```python
ERDiagramGenerator(
    output_dir='docs/diagrams',
    format='png',           # 'png', 'svg', 'pdf', 'dot'
    include_views=True,     # Incluir vistas en el diagrama
    include_columns=True,   # Mostrar detalles de columnas
    include_relationships=True,  # Mostrar relaciones
    dpi=300                # Resolución para formatos bitmap
)
```

**Características del diagrama:**
- 🔑 **Primary Keys**: Marcadas con icono de llave
- 🔗 **Foreign Keys**: Marcadas con icono de enlace
- ⭐ **Unique**: Columnas únicas marcadas
- ❗ **Not Null**: Columnas obligatorias marcadas
- ⬆️ **Auto Increment**: Columnas auto-incrementales marcadas
- 👁️ **Views**: Diferenciadas visualmente de las tablas

## 🖥️ Comandos CLI

### `tai-sql init` - Inicializar Proyecto

Crea un nuevo proyecto TAI-SQL con la estructura completa:

```bash
# Crear proyecto básico
tai-sql init

# Crear proyecto con nombre personalizado
tai-sql init --name mi-proyecto --schema-name mi-esquema

# Estructura generada:
mi-proyecto/
├── pyproject.toml
├── README.md
├── mi_proyecto/             # CRUD/Models Folder
├── schemas/
│   └── mi_esquema.py        # Schema principal
├── views/
│   └── mi_esquema/
│       └── user_stats.sql   # Vista de ejemplo
└── diagrams/                
    └── mi_esquema.png       # ERD Diagram
```
**Opciones:**
- `--name, -n`: Nombre del proyecto (default: `database`)
- `--schema, -s`: Nombre del primer schema (default: `public`)

### `tai-sql new-schema` - Crear Nuevo Schema

Agrega un nuevo schema a un proyecto existente:

```bash
# Crear nuevo schema en proyecto existente
tai-sql new-schema productos

# Con proyecto personalizado
tai-sql new-schema --project mi-empresa productos
```

**Características:**
- ✅ Detecta automáticamente el proyecto TAI-SQL actual
- ✅ Crea archivo de schema con plantilla completa
- ✅ Crea directorio de vistas correspondiente
- ✅ Actualiza configuración del proyecto si es necesario

### `tai-sql set-default-schema` - Establecer Schema por Defecto

Configura qué schema se usará por defecto en los comandos:

```bash
# Establecer schema por defecto
tai-sql set-default-schema productos

# Si el schema no existe, muestra opciones disponibles:
# ❌ El schema 'nonexistent' no existe en el proyecto
# 
# 📄 Schemas disponibles:
#    ✅ public (actual por defecto)
#       productos  
#       ventas
```

### `tai-sql info` - Información del Proyecto

Muestra información completa del proyecto actual:

```bash
tai-sql info
```

**Información mostrada:**
```bash
📁 Información del proyecto:
   Nombre: mi-proyecto
   Directorio: /path/to/mi-proyecto
   Schema por defecto: productos

📄 Schemas disponibles:
   • public
   • productos (✅ default, 📌 current)
   • ventas
     └─ Estado: Cargado

🔧 Comandos disponibles:
   tai-sql generate              # Usa schema por defecto
   tai-sql push                  # Usa schema por defecto
   tai-sql set-default-schema <nombre>  # Cambiar default

### `tai-sql generate` - Generar Recursos

Ejecuta todos los generadores configurados en el schema:

```bash
# Generar usando schema por defecto
tai-sql generate

# Generar usando schema específico
tai-sql generate --schema database/schemas/productos.py
```

**Proceso de generación:**
1. ✅ Carga y valida el schema
2. 🔍 Descubre modelos (tablas y vistas)
3. 🏗️ Ejecuta generadores configurados
4. 📊 Muestra resumen de archivos generados


### `tai-sql generate` - Generar Recursos

Ejecuta todos los generadores configurados en el schema:

```bash
# Generar usando schema por defecto
tai-sql generate

# Generar usando schema específico
tai-sql generate --schema productos

# Generar para todos los schemas del proyecto
tai-sql generate --all
```

**Opciones:**
- `--schema, -s`: Schema específico a procesar
- `--all`: Procesar todos los schemas del proyecto

**Proceso de generación:**
1. ✅ Carga y valida el schema
2. 🔍 Descubre modelos (tablas y vistas)
3. 🏗️ Ejecuta generadores configurados
4. 📊 Muestra resumen de archivos generados


### `tai-sql push` - Sincronizar con Base de Datos

Aplica los cambios del schema a la base de datos:

```bash
# Push básico
tai-sql push

# Con opciones avanzadas
tai-sql push --schema public --createdb --force --verbose

# Dry run (mostrar cambios sin aplicar)
tai-sql push --dry-run
```

**Opciones disponibles:**
- `--createdb, -c`: Crear base de datos si no existe
- `--force, -f`: Aplicar cambios sin confirmación
- `--dry-run, -d`: Mostrar DDL sin ejecutar
- `--verbose, -v`: Mostrar información detallada

**Proceso de push:**
1. 🔍 Analiza diferencias entre schema y BD
2. 📋 Genera sentencias DDL necesarias
3. ⚠️ Muestra advertencias de operaciones peligrosas
4. ✅ Aplica cambios tras confirmación
5. 🚀 Ejecuta generadores automáticamente

**Ejemplo de salida:**
```bash
🚀 Push schema: database/schemas/main.py

📋 Resumen de cambios:
   🆕 2 tabla(s) nueva(s): usuarios, posts
   ➕ 3 columna(s) a añadir en 1 tabla(s)
   🆕 1 vista(s) nueva(s): user_stats

¿Deseas ejecutar estas sentencias en la base de datos? [y/N]: y

✅ Esquema sincronizado exitosamente
🚀 Ejecutando generadores...
   ✅ ModelsGenerator completado
   ✅ CRUDGenerator completado  
   ✅ ERDiagramGenerator completado
```


### `tai-sql ping` - Verificar Conectividad

Verifica la conectividad con el servidor de base de datos:

```bash
# Verificación básica (ping al host)
tai-sql ping

# Verificación con schema específico
tai-sql ping --schema productos

# Verificación completa (incluye ping ICMP, TCP y BD)
tai-sql ping --full

# Verificar también existencia de la base de datos
tai-sql ping --check-db

# Modo silencioso (solo resultado final)
tai-sql ping --quiet
```

**Opciones:**
- `--schema, -s`: Schema específico para conectividad
- `--timeout, -t`: Timeout en segundos (default: 5)
- `--check-db, -d`: Verificar si la base de datos específica existe
- `--full, -f`: Verificación completa (ICMP + TCP + BD)
- `--quiet, -q`: Modo silencioso, solo resultado final

**Tipos de verificación:**

1. **Básica** (default): Solo ping al host
2. **Full** (`--full`): Ping ICMP + conectividad TCP + conexión BD
3. **Con BD** (`--check-db`): Incluye verificación de existencia de BD

**Ejemplo de salida:**
```bash
🔧 Información de conexión:
   Motor: postgresql
   Host: localhost
   Puerto: 5432
   Base de datos: mi_proyecto
   Usuario: postgres

🏓 Verificación BASIC

✅ Host accesible

🗄️  Verificando existencia de la base de datos...

✅ La base de datos existe

🎉 Verificación de conectividad completada exitosamente
```

### Gestión Automática de Schemas

**Resolución automática del schema:**
- Si no especificas `--schema`, los comandos usan automáticamente el schema por defecto
- Si no hay schema por defecto configurado, el comando te guía para establecer uno
- Todos los comandos muestran qué schema están usando

**Mensajes de ayuda inteligentes:**
```bash
# Si no hay schema por defecto:
❌ No existe ningún esquema por defecto
   Puedes definir uno con: tai-sql set-default-schema <nombre>
   O usar la opción: --schema <nombre_esquema>

# Si especificas un schema que no existe:
❌ El schema 'inexistente' no existe en el proyecto

📄 Schemas disponibles:
   ✅ public
      productos
      ventas
```

### Workflow Típico

```bash
# 1. Crear nuevo proyecto
tai-sql init --name mi-empresa --schema productos

# 2. Entrar al proyecto
cd mi-empresa

# 3. Configurar base de datos
export DATABASE_URL="postgresql://user:pass@localhost/mi_empresa"

# 4. Editar el schema
# Editar schemas/productos.py

# 5. Sincronizar con BD (crear BD si no existe)
tai-sql push --createdb

# 6. Verificar conectividad
tai-sql ping --full

# 7. Crear schema adicional
tai-sql new-schema ventas

# 8. Cambiar schema por defecto
tai-sql set-default-schema ventas

# 9. Ver información del proyecto
tai-sql info

# 10. Generar recursos para todos los schemas
tai-sql generate --all
```

### Gestión de Proyectos Multi-Schema

TAI-SQL soporta múltiples schemas en un mismo proyecto:

```bash
# Crear schemas adicionales
tai-sql new-schema productos
tai-sql new-schema ventas  
tai-sql new-schema usuarios

# Trabajar con schemas específicos
tai-sql push --schema productos
tai-sql generate --schema ventas

# O procesar todos a la vez
tai-sql generate --all

# Cambiar entre schemas por defecto
tai-sql set-default-schema productos
tai-sql push  # Usa 'productos' automáticamente

tai-sql set-default-schema ventas  
tai-sql generate  # Usa 'ventas' automáticamente
```

**Ventajas del multi-schema:**
- ✅ **Modularidad**: Separar lógicamente diferentes dominios
- ✅ **Escalabilidad**: Cada schema puede tener su propia configuración
- ✅ **Flexibilidad**: Procesar schemas individualmente o en conjunto
- ✅ **Organización**: Mejor estructura para proyectos complejos


## 🛠️ Crear tu Propio Generador

Puedes crear generadores personalizados heredando de `BaseGenerator`:

```python
from tai_sql.generators.base import BaseGenerator
from tai_sql import db
import os

class APIDocsGenerator(BaseGenerator):
    """Generador de documentación API desde los modelos"""
    
    def __init__(self, output_dir=None, format='markdown'):
        super().__init__(output_dir or 'docs/api')
        self.format = format
    
    def generate(self) -> str:
        """Genera la documentación API"""
        
        docs_content = self._create_header()
        
        # Procesar cada modelo
        for model in self.models:
            if hasattr(model, '__tablename__'):  # Es una tabla
                docs_content += self._generate_table_docs(model)
            else:  # Es una vista
                docs_content += self._generate_view_docs(model)
        
        # Guardar archivo
        output_path = os.path.join(self.config.output_dir, f'api.{self.format}')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(docs_content)
        
        return output_path
    
    def _create_header(self) -> str:
        """Crea el header de la documentación"""
        return f"""# API Documentation
                    
            Database: {db.provider.database}
            Schema: {db.schema_name}
            Generated: {datetime.now().isoformat()}

            ## Models

        """
    
    def _generate_table_docs(self, model) -> str:
        """Genera documentación para una tabla"""
        docs = f"### {model.__name__} (Table)\n\n"
        docs += f"**Table name:** `{model.__tablename__}`\n\n"
        
        if hasattr(model, '__description__'):
            docs += f"**Description:** {model.__description__}\n\n"
        
        docs += "**Columns:**\n\n"
        docs += "| Column | Type | Constraints |\n"
        docs += "|--------|------|-------------|\n"
        
        for name, column in model.columns.items():
            constraints = []
            if column.primary_key:
                constraints.append("PRIMARY KEY")
            if not column.nullable:
                constraints.append("NOT NULL")
            if column.unique:
                constraints.append("UNIQUE")
            if column.autoincrement:
                constraints.append("AUTO INCREMENT")
                
            docs += f"| {name} | {column.type} | {', '.join(constraints)} |\n"
        
        docs += "\n"
        return docs
    
    def _generate_view_docs(self, model) -> str:
        """Genera documentación para una vista"""
        docs = f"### {model.__name__} (View)\n\n"
        docs += f"**View name:** `{model.__tablename__}`\n\n"
        
        if hasattr(model, '__description__'):
            docs += f"**Description:** {model.__description__}\n\n"
        
        # Agregar información de la vista...
        return docs

# Uso del generador personalizado

generate(
    ...,
    APIDocsGenerator(output_dir='docs/api', format='markdown')
)
```

**Métodos requeridos:**
- `generate()`: Método principal que debe retornar la ruta del archivo generado

**Métodos/propiedades útiles heredados:**
- `self.models`: Propiedad que contiene todos los modelos (tablas y vistas)
- `self.config.output_dir`: Directorio de salida configurado
- `self.register_model(model)`: Registra un modelo manualmente
- `self.clear_models()`: Limpia la lista de modelos


Este framework te permite construir aplicaciones robustas con una definición declarativa simple, generación automática de código y herramientas CLI potentes para el desarrollo ágil.