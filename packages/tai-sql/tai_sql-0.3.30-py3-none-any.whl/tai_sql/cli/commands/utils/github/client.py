"""
Utilidades para interactuar con la API de GitHub
"""
import subprocess
from typing import Optional, Dict, Any, List, Set
import click
import requests
from datetime import datetime
from nacl import encoding, public
from base64 import b64encode
from .auth import GitHubAuth
from .models import RepositoryInfo

from tai_sql import pm

class GitHubClient:
    """Cliente para interactuar con la API de GitHub"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or GitHubAuth.get_token()
        if not self.token:
            raise ValueError("No se pudo obtener token de GitHub")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }

        self.base_url = 'https://api.github.com'
        
    def get_repo_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del repositorio actual
        
        Returns:
            Información del repositorio o None si no se encuentra
        """
        try:
            # Obtener remote origin
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                click.echo("❌ No se encontró remote 'origin' en git")
                return None
            
            remote_url = result.stdout.strip()
            
            # Parsear URL para obtener owner/repo
            repo_info = self._parse_git_url(remote_url)
            if not repo_info:
                return None
            
            # Verificar que el repositorio existe en GitHub
            response = requests.get(
                f"{self.base_url}/repos/{repo_info.owner}/{repo_info.repo}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                click.echo(f"❌ Repositorio no encontrado en GitHub: {repo_info['owner']['login']}/{repo_info['name']}")
                return None
                
        except subprocess.TimeoutExpired:
            click.echo("❌ Timeout al obtener información de git")
            return None
        except Exception as e:
            click.echo(f"❌ Error al obtener información del repositorio: {e}")
            return None
    
    def _parse_git_url(self, url: str) -> Optional[RepositoryInfo]:
        """Parsea una URL de git para obtener información del repositorio"""
        try:
            # SSH format: git@github.com:owner/repo.git
            if url.startswith('git@github.com:'):
                path = url[15:]  # Remove 'git@github.com:'
                if path.endswith('.git'):
                    path = path[:-4]
                owner, repo = path.split('/')
                return RepositoryInfo(owner=owner, repo=repo)
            
            # HTTPS format: https://github.com/owner/repo.git
            elif 'github.com' in url:
                parts = url.rstrip('/').split('/')
                if len(parts) >= 2:
                    repo = parts[-1]
                    owner = parts[-2]
                    if repo.endswith('.git'):
                        repo = repo[:-4]
                    return RepositoryInfo(owner=owner, repo=repo)
            
            return None
            
        except:
            return None
    
    def create_environment(self, owner: str, repo: str, environment: str) -> bool:
        """
        Crea un entorno en GitHub si no existe
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            environment: Nombre del entorno
            
        Returns:
            True si se creó o ya existía
        """
        try:
            # Verificar si el entorno ya existe
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                click.echo(f"   ℹ️  Entorno '{environment}' ya existe")
                return True
            elif response.status_code == 404:
                # Crear el entorno
                data = {}
                response = requests.put(
                    f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}",
                    headers=self.headers,
                    json=data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    click.echo(f"   ✅ Entorno '{environment}' creado")
                    return True
                else:
                    click.echo(f"   ❌ Error al crear entorno '{environment}': {response.status_code}")
                    return False
            else:
                click.echo(f"   ❌ Error al verificar entorno '{environment}': {response.status_code}")
                return False
                
        except Exception as e:
            click.echo(f"   ❌ Error al gestionar entorno '{environment}': {e}")
            return False
    
    def get_environment_variable(self, owner: str, repo: str, environment: str, variable_name: str) -> Optional[str]:
        """
        Obtiene una variable de entorno
        
        Returns:
            Valor de la variable o None si no existe
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/variables/{variable_name}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('value')
            else:
                return None
                
        except Exception:
            return None
    
    def set_environment_variable(self, owner: str, repo: str, environment: str, 
                               variable_name: str, value: str) -> bool:
        """
        Establece una variable de entorno
        
        Returns:
            True si se estableció correctamente
        """
        try:
            data = {'name': variable_name, 'value': value}
            
            response = requests.post(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/variables",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            return False
    
    def list_environment_variables(self, owner: str, repo: str, environment: str) -> List[Dict[str, Any]]:
        """
        Lista todas las variables de un entorno
        
        Returns:
            Lista de variables del entorno
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/variables",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('variables', [])
            else:
                return []
                
        except Exception:
            return []

    def get_environment_secret(self, owner: str, repo: str, environment: str, secret_name: str) -> bool:
        """
        Verifica si un secret de entorno existe
        
        Returns:
            True si el secret existe, False si no existe
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}",
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
                
        except Exception as e:
            click.echo(e)
            return False
    
    def set_environment_secret(self, owner: str, repo: str, environment: str, 
                                secret_name: str, value: str) -> bool:
        """
        Establece un secret de entorno
        
        Returns:
            True si se estableció correctamente
        """
        try:
            # Para secrets necesitamos encriptar el valor
            # Primero obtenemos la clave pública del repositorio
            pub_key_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets/public-key",
                headers=self.headers,
                timeout=10
            )
            
            if pub_key_response.status_code != 200:
                return False
                
            pub_key_data = pub_key_response.json()
            
            # Encriptar el valor usando la clave pública
            public_key = public.PublicKey(pub_key_data['key'], encoding.Base64Encoder())
            sealed_box = public.SealedBox(public_key)
            encrypted = sealed_box.encrypt(value.encode('utf-8'))
            encrypted_value = b64encode(encrypted).decode("utf-8")
            
            data = {
                'encrypted_value': encrypted_value,
                'key_id': pub_key_data['key_id']
            }
            
            response = requests.put(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            return response.status_code in [200, 201, 204]
            
        except Exception as e:
            click.echo(e)
            return False
    
    def list_environment_secrets(self, owner: str, repo: str, environment: str) -> List[Dict[str, Any]]:
        """
        Lista todos los secrets de un entorno
        
        Returns:
            Lista de secrets del entorno (solo nombres, no valores)
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('secrets', [])
            else:
                return []
                
        except Exception:
            return []

    def check_user_permissions(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Verifica los permisos del usuario en el repositorio
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            
        Returns:
            Diccionario con información de permisos y recomendaciones
        """
        try:
            # Obtener información del usuario actual
            user_info = self.get_current_user()
            if not user_info:
                return {
                    'has_sufficient_permissions': False,
                    'error': 'No se pudo obtener información del usuario',
                    'recommendations': ['Verificar que el token sea válido']
                }
            
            username = user_info['login']
            
            # Verificar permisos en el repositorio
            repo_permissions = self.get_repository_permissions(owner, repo, username)
            
            # Verificar scopes del token
            token_scopes = self.get_token_scopes()
            
            # Analizar permisos
            analysis = self._analyze_permissions(repo, repo_permissions, token_scopes, owner, username)
            
            return analysis
            
        except Exception as e:
            return {
                'has_sufficient_permissions': False,
                'error': f'Error verificando permisos: {str(e)}',
                'recommendations': ['Verificar conectividad con GitHub', 'Validar token de acceso']
            }
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del usuario actual
        
        Returns:
            Información del usuario o None si hay error
        """
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None
    
    def get_repository_permissions(self, owner: str, repo: str, username: str) -> Dict[str, Any]:
        """
        Obtiene los permisos específicos del usuario en el repositorio
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            username: Usuario a verificar
            
        Returns:
            Diccionario con información de permisos
        """
        try:
            # Verificar si el usuario es colaborador
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/collaborators/{username}/permission",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Si no es colaborador directo, verificar si es el owner
            if username.lower() == owner.lower():
                return {
                    'permission': 'admin',
                    'user': {'login': username},
                    'role_name': 'owner'
                }
            
            # Verificar si tiene acceso via organization
            org_permission = self._check_organization_permission(owner, repo, username)
            if org_permission:
                return org_permission
            
            return {
                'permission': 'none',
                'user': {'login': username},
                'role_name': 'none'
            }
            
        except Exception:
            return {
                'permission': 'unknown',
                'user': {'login': username},
                'role_name': 'unknown'
            }
    
    def get_token_scopes(self) -> Set[str]:
        """
        Obtiene los scopes del token actual
        
        Returns:
            Set con los scopes del token
        """
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Los scopes vienen en el header X-OAuth-Scopes
                scopes_header = response.headers.get('X-OAuth-Scopes', '')
                if scopes_header:
                    return set(scope.strip() for scope in scopes_header.split(','))
            
            return set()
            
        except Exception:
            return set()
    
    def _check_organization_permission(self, owner: str, repo: str, username: str) -> Optional[Dict[str, Any]]:
        """
        Verifica permisos via organización
        
        Args:
            owner: Propietario del repositorio (organización)
            repo: Nombre del repositorio
            username: Usuario a verificar
            
        Returns:
            Información de permisos o None
        """
        try:
            # Verificar si el owner es una organización
            response = requests.get(
                f"{self.base_url}/orgs/{owner}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None  # No es una organización
            
            # Verificar membresía en la organización
            response = requests.get(
                f"{self.base_url}/orgs/{owner}/members/{username}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Es miembro, verificar permisos en el repositorio
                response = requests.get(
                    f"{self.base_url}/repos/{owner}/{repo}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    repo_data = response.json()
                    permissions = repo_data.get('permissions', {})
                    
                    if permissions.get('admin'):
                        role = 'admin'
                    elif permissions.get('maintain'):
                        role = 'maintain'
                    elif permissions.get('push'):
                        role = 'write'
                    elif permissions.get('pull'):
                        role = 'read'
                    else:
                        role = 'none'
                    
                    return {
                        'permission': role,
                        'user': {'login': username},
                        'role_name': f'organization_{role}'
                    }
            
            return None
            
        except Exception:
            return None
    
    def _analyze_permissions(self, repo: str, repo_permissions: Dict[str, Any], token_scopes: Set[str], 
                           owner: str, username: str) -> Dict[str, Any]:
        """
        Analiza los permisos y genera recomendaciones
        
        Args:
            repo_permissions: Permisos en el repositorio
            token_scopes: Scopes del token
            owner: Propietario del repositorio
            username: Usuario actual
            
        Returns:
            Análisis completo de permisos
        """
        permission_level = repo_permissions.get('permission', 'none')
        role_name = repo_permissions.get('role_name', 'unknown')
        
        # Scopes requeridos para deploy-config
        required_scopes = {'repo', 'admin:repo_hook'}
        
        # Permisos mínimos requeridos en el repositorio
        required_repo_permissions = {'admin', 'maintain'}
        
        # Análisis de scopes
        missing_scopes = required_scopes - token_scopes
        has_sufficient_scopes = len(missing_scopes) == 0
        
        # Análisis de permisos en repositorio
        has_sufficient_repo_permissions = permission_level in required_repo_permissions
        
        # Determinar si tiene permisos suficientes
        has_sufficient_permissions = has_sufficient_scopes and has_sufficient_repo_permissions
        
        # Generar recomendaciones
        recommendations = []
        warnings = []
        
        if not has_sufficient_scopes:
            recommendations.append(f"Regenerar token con scopes: {', '.join(sorted(required_scopes))}")
            warnings.append(f"Scopes faltantes: {', '.join(sorted(missing_scopes))}")
        
        if not has_sufficient_repo_permissions:
            if permission_level == 'none':
                recommendations.append(f"Solicitar acceso al repositorio {owner}/{repo}")
                warnings.append("Sin acceso al repositorio")
            elif permission_level in ['read', 'triage']:
                recommendations.append("Solicitar permisos de 'Maintain' o 'Admin' en el repositorio")
                warnings.append(f"Permisos insuficientes: {permission_level} (se requiere admin/maintain)")
            elif permission_level == 'write':
                recommendations.append("Solicitar permisos de 'Maintain' o 'Admin' para gestionar environments")
                warnings.append("Permisos de 'Write' insuficientes para gestionar environments")
        
        # Información adicional
        info = []
        if username.lower() == owner.lower():
            info.append("Eres el propietario del repositorio")
        elif 'organization' in role_name:
            info.append("Acceso via organización")
        
        return {
            'has_sufficient_permissions': has_sufficient_permissions,
            'user': {
                'login': username,
                'is_owner': username.lower() == owner.lower()
            },
            'repository': {
                'permission': permission_level,
                'role_name': role_name,
                'required_permissions': list(required_repo_permissions)
            },
            'token': {
                'scopes': sorted(list(token_scopes)),
                'required_scopes': sorted(list(required_scopes)),
                'missing_scopes': sorted(list(missing_scopes))
            },
            'warnings': warnings,
            'recommendations': recommendations,
            'info': info
        }
    
    def display_permissions_report(self, owner: str, repo: str) -> bool:
        """
        Muestra un reporte completo de permisos
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            
        Returns:
            True si tiene permisos suficientes, False si no
        """
        click.echo("🔍 Verificando permisos de GitHub...")
        
        analysis = self.check_user_permissions(owner, repo)
        
        if analysis.get('error'):
            click.echo(f"❌ {analysis['error']}")
            for rec in analysis.get('recommendations', []):
                click.echo(f"   💡 {rec}")
            return False
        
        user = analysis['user']
        repo_info = analysis['repository']
        token_info = analysis['token']
        
        click.echo(f"👤 Usuario: {user['login']}")
        
        # Mostrar información adicional
        for info in analysis.get('info', []):
            click.echo(f"   ℹ️  {info}")
        
        # Mostrar permisos del repositorio
        click.echo(f"📂 Repositorio: {owner}/{repo}")
        click.echo(f"   🔑 Permisos: {repo_info['permission']}")
        click.echo(f"   👥 Rol: {repo_info['role_name']}")
        
        # Mostrar scopes del token
        click.echo(f"🎫 Token scopes:")
        for scope in token_info['scopes']:
            click.echo(f"   ✅ {scope}")
        
        # Mostrar warnings
        if analysis.get('warnings'):
            click.echo("⚠️  Advertencias:")
            for warning in analysis['warnings']:
                click.echo(f"   🚨 {warning}")
        
        # Mostrar recomendaciones
        if analysis.get('recommendations'):
            click.echo("💡 Recomendaciones:")
            for rec in analysis['recommendations']:
                click.echo(f"   📝 {rec}")
        
        # Resultado final
        if analysis['has_sufficient_permissions']:
            click.echo("✅ Permisos suficientes")
            return True
        else:
            click.echo("❌ Permisos insuficientes")
            click.echo()
            click.echo("🔧 Para resolver:")
            click.echo("   1. Regenerar token con scopes requeridos")
            click.echo("   2. Solicitar permisos de Admin/Maintain en el repositorio")
            click.echo("   3. Verificar que el repositorio existe y es accesible")
            return False

    def check_git_repository_status(self) -> dict:
        """
        Verifica el estado del repositorio Git local (sin validar schema)
        
        Returns:
            Diccionario con información del estado del repositorio
        """
        try:
            status_result = {
                'is_git_repo': False,
                'has_uncommitted_changes': False,
                'current_branch': None,
                'current_sha': None,
                'remote_url': None,
                'error': None
            }
            
            # Verificar que es un repositorio Git
            try:
                subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, check=True)
                status_result['is_git_repo'] = True
            except subprocess.CalledProcessError:
                status_result['error'] = 'No es un repositorio Git'
                return status_result
            
            # Obtener rama actual
            try:
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                       capture_output=True, text=True, check=True)
                status_result['current_branch'] = result.stdout.strip()
            except:
                status_result['error'] = 'No se pudo obtener la rama actual'
                return status_result
            
            # Obtener SHA actual
            try:
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                       capture_output=True, text=True, check=True)
                status_result['current_sha'] = result.stdout.strip()
            except:
                status_result['error'] = 'No se pudo obtener el SHA del commit'
                return status_result
            
            # Verificar cambios sin confirmar
            try:
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                       capture_output=True, text=True, check=True)
                status_result['has_uncommitted_changes'] = bool(result.stdout.strip())
            except:
                # No es crítico si no podemos verificar esto
                pass
            
            # Obtener URL del remote
            try:
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                       capture_output=True, text=True, check=True)
                status_result['remote_url'] = result.stdout.strip()
            except:
                status_result['error'] = 'No se encontró remote origin'
                return status_result
            
            return status_result
            
        except Exception as e:
            return {
                'is_git_repo': False,
                'has_uncommitted_changes': False,
                'current_branch': None,
                'current_sha': None,
                'remote_url': None,
                'error': str(e)
            }
        
    def get_current_commit_sha(self) -> Optional[str]:
        """
        Obtiene el SHA del commit actual
        
        Returns:
            SHA del commit o None si hay error
        """
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                   capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None
    
    def get_current_branch(self) -> Optional[str]:
        """
        Obtiene la rama actual
        
        Returns:
            Nombre de la rama o None si hay error
        """
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                   capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None
    
    def create_branch_reference(self, owner: str, repo: str, branch_name: str, sha: str) -> bool:
        """
        Crea una nueva rama en GitHub
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            branch_name: Nombre de la nueva rama
            sha: SHA del commit base
            
        Returns:
            True si se creó exitosamente
        """
        try:
            data = {
                'ref': f'refs/heads/{branch_name}',
                'sha': sha
            }

            response = requests.post(
                f"{self.base_url}/repos/{owner}/{repo}/git/refs",
                headers=self.headers,
                timeout=10,
                json=data
            )
            
            if response.status_code == 201:
                click.echo(f"✅ Rama '{branch_name}' creada exitosamente")
                return True
            elif response.status_code == 422:
                click.echo(f"⚠️ La rama '{branch_name}' ya existe")
                return True
            elif response.status_code == 404:
                click.echo(f"❌ Create branch: repositorio {owner}/{repo} no encontrado")
                return False
            else:
                click.echo(f"❌ Error creando rama: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            click.echo(f"❌ Error creando rama: {e}")
            return False
    
    def create_pull_request(self, owner: str, repo: str, title: str, body: str, 
                           head: str, base: str = 'main') -> Optional[dict]:
        """
        Crea un Pull Request
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            title: Título del PR
            body: Descripción del PR
            head: Rama origen
            base: Rama destino
            
        Returns:
            Información del PR creado o None si hay error
        """
        try:
            data = {
                'title': title,
                'body': body,
                'head': head,
                'base': base,
                'draft': False
            }

            response = requests.post(
                f"{self.base_url}/repos/{owner}/{repo}/pulls",
                headers=self.headers,
                timeout=10,
                json=data
            )

            if response.status_code in [200, 201]:
                return response.json()
        
            elif response.status_code == 404:
                click.echo(f"❌ Create PR: Repositorio {owner}/{repo} no encontrado")
                return None
            
        except Exception as e:
            click.echo(f"❌ Error creando PR: {e}")
            return None
    
    def add_labels_to_issue(self, owner: str, repo: str, issue_number: int, labels: list) -> bool:
        """
        Añade labels a un issue/PR
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            issue_number: Número del issue/PR
            labels: Lista de labels
            
        Returns:
            True si se añadieron exitosamente
        """
        try:
            data = {'labels': labels}

            response = requests.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels",
                headers=self.headers,
                timeout=10,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
        
            elif response.status_code == 404:
                click.echo(f"❌ Add labels: Repositorio {owner}/{repo} no encontrado")
                return None
            
        except Exception as e:
            click.echo(f"❌ Error añadiendo labels: {e}")
            return False
    
    def enable_auto_merge(self, owner: str, repo: str, pr_number: int, merge_method: str = 'squash') -> bool:
        """
        Habilita auto-merge en un PR
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            pr_number: Número del PR
            merge_method: Método de merge (squash, merge, rebase)
            
        Returns:
            True si se habilitó exitosamente
        """
        try:
            data = {'merge_method': merge_method}
        
            response = requests.put(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/merge",
                headers=self.headers,
                timeout=10,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
        
            elif response.status_code == 404:
                click.echo(f"❌ Add labels: Repositorio {owner}/{repo} no encontrado")
                return None
            
        except Exception as e:
            # Auto-merge puede fallar si no está habilitado en el repo
            click.echo(f"⚠️  No se pudo habilitar auto-merge: {e}")
            return False
    
    def validate_local_schema_changes(self, schema: str) -> dict:
        """
        Valida cambios locales del schema usando tai-sql
        
        Args:
            schema: Nombre del schema
            
        Returns:
            Diccionario con información de la validación
        """
        try:
            # Ejecutar tai-sql push en modo dry-run para validar
            result = subprocess.run([
                'tai-sql', 'push', 
                '--schema', schema, 
                '--dry-run', 
                '--verbose'
            ], capture_output=True, text=True, timeout=60)
            
            validation_result = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'has_changes': False,
                'has_destructive': False
            }
            
            if result.returncode == 0:
                output = result.stdout
                
                # Verificar si hay cambios
                if not any(phrase in output for phrase in ["No se detectaron cambios", "Sin cambios detectados"]):
                    validation_result['has_changes'] = True
                
                # Verificar cambios destructivos
                if any(keyword in output for keyword in ["DROP", "DESTRUCTIVO", "⚠️"]):
                    validation_result['has_destructive'] = True
                    
            return validation_result
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Timeout en validación',
                'has_changes': False,
                'has_destructive': False
            }
        except FileNotFoundError:
            return {
                'success': False,
                'output': '',
                'error': 'tai-sql no encontrado',
                'has_changes': False,
                'has_destructive': False
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'has_changes': False,
                'has_destructive': False
            }
    
    def create_deployment_commit(self, branch_name: str, pr_body: str, entorno: str, schema: str) -> bool:
        """
        Crea un commit en la rama de deployment actualizando dbdeployments.md
        
        Args:
            branch_name: Nombre de la rama de deployment
            pr_body: Contenido del PR para añadir al archivo
            entorno: Entorno del deployment
            schema: Schema del deployment
            
        Returns:
            True si el commit se creó exitosamente
        """
        try:
            
            # Hacer checkout a la nueva rama
            result = subprocess.run(['git', 'checkout', '-b', branch_name], 
                                   capture_output=True, text=True)
            
            if result.returncode != 0:
                click.echo(f"❌ Error haciendo checkout a {branch_name}: {result.stderr}")
                return False
            
            click.echo(f"✅ Checkout exitoso a rama {branch_name}")
            
            # Crear o actualizar dbdeployments.md
            deployments_file = pm.find_project_root() / 'dbdeployments.md'
            
            # Leer contenido existente si el archivo existe
            existing_content = ""
            if deployments_file.exists():
                try:
                    with open(deployments_file, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                except Exception as e:
                    click.echo(f"⚠️  Error leyendo dbdeployments.md existente: {e}")
                    existing_content = ""
            
            # Generar timestamp para el deployment
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Preparar nueva entrada de deployment
            deployment_entry = f"""
---

## 🚀 Deployment Request - {timestamp}

**Entorno:** `{entorno}`  
**Schema:** `{schema}`

{pr_body}

---
"""
            
            # Combinar contenido: nueva entrada al principio
            if existing_content.strip():
                new_content = f"# TAI-SQL Deployments Log\n{deployment_entry}\n{existing_content}"
            else:
                new_content = f"# TAI-SQL Deployments Log\n{deployment_entry}"
            
            # Escribir el archivo actualizado
            try:
                with open(deployments_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                click.echo(f"✅ Archivo dbdeployments.md actualizado")
            except Exception as e:
                click.echo(f"❌ Error escribiendo dbdeployments.md: {e}")
                return False
            
            # Añadir el archivo al staging area
            result = subprocess.run(['git', 'add', deployments_file], 
                                   capture_output=True, text=True)
            
            if result.returncode != 0:
                click.echo(f"❌ Error añadiendo dbdeployments.md: {result.stderr}")
                return False
            
            # Crear commit
            commit_message = f"TAI-SQL deployment request {entorno}/{schema}\n\nAutomated deployment request created by tai-sql deploy command."
            
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                   capture_output=True, text=True)
            
            if result.returncode != 0:
                click.echo(f"❌ Error creando commit: {result.stderr}")
                return False
            
            click.echo(f"✅ Commit creado: {commit_message.split()[0]} {commit_message.split()[1]} {commit_message.split()[2]}")
            
            # Push de la rama al remoto
            result = subprocess.run(['git', 'push', 'origin', branch_name], 
                                   capture_output=True, text=True)
            
            if result.returncode != 0:
                click.echo(f"❌ Error haciendo push: {result.stderr}")
                return False
            
            click.echo(f"✅ Push exitoso a origin/{branch_name}")
            
            # Volver a la rama original
            result = subprocess.run(['git', 'checkout', '-'], 
                                   capture_output=True, text=True)
            
            if result.returncode != 0:
                click.echo(f"⚠️  Error volviendo a la rama original: {result.stderr}")
                # No es crítico, continuamos
            
            return True
            
        except Exception as e:
            click.echo(f"❌ Error en create_deployment_commit: {e}")
            
            # Intentar volver a la rama original en caso de error
            try:
                subprocess.run(['git', 'checkout', '-'], capture_output=True)
            except:
                pass
                
            return False

    def create_deployment_pr(self, entorno: str, schema: str, git_status: dict, message: Optional[str] = None, 
                           auto_merge: bool = False) -> Optional[str]:
        """
        Crea un PR completo para deployment
        
        Args:
            entorno: Nombre del entorno
            schema: Nombre del schema
            git_status: Estado del repositorio Git
            message: Mensaje personalizado
            auto_merge: Habilitar auto-merge
            
        Returns:
            URL del PR creado o None si hay error
        """
        try:
            # Obtener información del repositorio
            repo_info = self.get_repo_info()
            if not repo_info:
                click.echo("❌ No se pudo obtener información del repositorio remoto")
                return None
            
            owner = repo_info['owner']['login']
            repo = repo_info['name']
            current_sha = git_status['current_sha']
            current_branch = git_status['current_branch']
            
            # Generar nombre de rama única
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            branch_name = f"database-deploy/{entorno}-{schema}-{timestamp}"
            
            # Obtener información del usuario
            user_info = self.get_current_user()
            actor = user_info['login'] if user_info else 'unknown'
            
            # Crear contenido del PR (sin preview de cambios local)
            pr_title = f"🚀 TAI-SQL Deploy: {entorno}/{schema}"
            
            pr_body = f"""## 🚀 TAI-SQL Deployment Request

**Entorno:** `{entorno}`  
**Schema:** `{schema}`  
**Solicitado por:** @{actor}  
**Rama:** `{branch_name}` → `main`

### 📋 Información del Deploy:
- **Timestamp:** {datetime.now().isoformat()}
- **Commit:** `{current_sha[:8]}`
- **Auto-merge:** {'✅ Habilitado' if auto_merge else '❌ Deshabilitado'}

### 💬 Mensaje:
{message or '_Sin mensaje personalizado_'}

### 🔍 Validación de Cambios:
La validación de cambios se realizará automáticamente en GitHub Actions contra la base de datos del entorno `{entorno}`.

### 🤖 Proceso Automático:
1. 🔍 **Validación**: El workflow validará los cambios contra la BD de `{entorno}`
2. 📊 **Reporte**: Se generará un comentario con los cambios detectados
3. 👥 **Revisión**: Los reviewers aprobarán/rechazarán según el entorno
4. 🚀 **Deploy**: Al hacer merge, se ejecutará el deployment automáticamente
5. 🧹 **Cleanup**: La rama se borrará automáticamente

### ⚠️ Instrucciones por Entorno:
- **Development**: 
  - Cambios seguros: Merge automático tras validación
  - Cambios destructivos: Requiere aprobación manual
- **Preproduction**: Requiere 1 reviewer
- **Production**: Requiere 2+ reviewers y revisión cuidadosa

### 📋 Próximos pasos:
1. ⏳ Esperar validación automática (aparecerá como comentario)
2. 👀 Revisar los cambios detectados
3. 👥 Obtener aprobaciones según el entorno
4. 🔀 Hacer merge para ejecutar deployment

---
*Creado automáticamente por `tai-sql deploy {entorno} {schema}`*
"""
            
            click.echo(f"🌿 Creando rama y commit para: {branch_name}")
            
            # Crear commit en la nueva rama con dbdeployments.md actualizado
            if not self.create_deployment_commit(branch_name, pr_body, entorno, schema):
                click.echo("❌ Error creando commit de deployment")
                return None
            
            # Ahora crear el PR (ya no necesitamos crear la rama manualmente)
            click.echo(f"📄 Creando Pull Request...")
            pr_data = self.create_pull_request(owner, repo, pr_title, pr_body, branch_name)

            print(pr_data)
            
            if not pr_data:
                click.echo("❌ Error creando Pull Request")
                
                # Limpiar: borrar rama local y remota en caso de error
                try:
                    subprocess.run(['git', 'push', 'origin', '--delete', branch_name], 
                                  capture_output=True)
                    subprocess.run(['git', 'branch', '-D', branch_name], 
                                  capture_output=True)
                except:
                    pass
                    
                return None
            
            pr_number = pr_data['number']
            pr_url = pr_data['html_url']
            
            # Añadir labels
            labels = [
                'tai-sql',
                'database-deploy',
                entorno,
                'auto-merge' if auto_merge else 'manual-merge'
            ]
            
            self.add_labels_to_issue(owner, repo, pr_number, labels)
            
            # Habilitar auto-merge si se solicita (solo para development)
            if auto_merge and entorno == 'development':
                self.enable_auto_merge(owner, repo, pr_number)
            
            return pr_url
            
        except Exception as e:
            import logging
            logging.exception(e)
            click.echo(f"❌ Error creando deployment PR: {e}")
            return None