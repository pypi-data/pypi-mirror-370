"""
Utilidades para interactuar con la API de GitHub
"""
import json
import webbrowser
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any
import click
import requests
from urllib.parse import urlencode

class GitHubAuth:
    """Gestor de autenticación con GitHub"""
    
    TOKEN_FILE = Path.home() / '.tai_sql' / 'github_token.json'
    
    @classmethod
    def get_token(cls) -> Optional[str]:
        """
        Obtiene un token de GitHub válido
        
        Returns:
            Token de GitHub o None si no se puede obtener
        """
        # Intentar obtener de archivo almacenado
        stored_token = cls._get_stored_token()
        if stored_token and cls._validate_token(stored_token):
            return stored_token
        
        # Intentar autenticación SSH
        ssh_token = cls._try_ssh_auth()
        if ssh_token:
            return ssh_token
        
        # Autenticación por navegador
        return cls._browser_auth()
    
    @classmethod
    def _get_stored_token(cls) -> Optional[str]:
        """Lee el token almacenado del archivo"""
        if not cls.TOKEN_FILE.exists():
            return None
        
        try:
            with open(cls.TOKEN_FILE, 'r') as f:
                data = json.load(f)
                
            # Verificar si no ha expirado
            expires_at = data.get('expires_at', 0)
            if time.time() > expires_at:
                click.echo("🔄 Token almacenado ha expirado")
                return None
                
            return data.get('token')
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return None
    
    @classmethod
    def _store_token(cls, token: str, expires_in: int = 28800) -> None:
        """Almacena el token en archivo"""
        cls.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'token': token,
            'expires_at': time.time() + expires_in,
            'created_at': time.time()
        }
        
        with open(cls.TOKEN_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Establecer permisos restrictivos
        cls.TOKEN_FILE.chmod(0o600)
    
    @classmethod
    def _validate_token(cls, token: str) -> bool:
        """Valida que el token sea funcional"""
        try:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    @classmethod
    def _try_ssh_auth(cls) -> Optional[str]:
        """Intenta usar autenticación SSH con gh CLI"""
        try:
            click.echo("🔍 Intentando autenticación SSH con GitHub CLI...")
            
            # Verificar si gh está instalado
            result = subprocess.run(['gh', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                click.echo("   ℹ️  GitHub CLI (gh) no está instalado")
                return None
            
            # Verificar autenticación existente
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                click.echo("   ℹ️  No hay sesión activa en GitHub CLI")
                click.echo("   ℹ️  Si quieres hacer login a través de ssh")
                click.echo("        ejecuta 'gh auth login' para autenticarte")
                return None
            
            # Obtener token
            result = subprocess.run(['gh', 'auth', 'token'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                token = result.stdout.strip()
                if cls._validate_token(token):
                    click.echo("   ✅ Autenticación SSH exitosa")
                    cls._store_token(token)
                    return token
            
            click.echo("   ⚠️  No se pudo obtener token válido via SSH")
            return None
            
        except subprocess.TimeoutExpired:
            click.echo("   ⚠️  Timeout en autenticación SSH")
            return None
        except FileNotFoundError:
            click.echo("   ℹ️  GitHub CLI no está disponible")
            return None
        except Exception as e:
            click.echo(f"   ⚠️  Error en autenticación SSH: {e}")
            return None
    
    @classmethod
    def _browser_auth(cls) -> Optional[str]:
        """Autenticación por navegador usando GitHub Device Flow"""
        try:
            click.echo("🌐 Iniciando autenticación por navegador...")
            
            # Paso 1: Solicitar device code
            device_response = cls._request_device_code()
            if not device_response:
                return None
            
            device_code = device_response['device_code']
            user_code = device_response['user_code']
            verification_uri = device_response['verification_uri']
            interval = device_response.get('interval', 5)
            expires_in = device_response.get('expires_in', 900)
            
            # Paso 2: Mostrar código al usuario y abrir navegador
            click.echo()
            click.echo("🔑 Código de verificación:")
            click.echo(f"   {click.style(user_code, bold=True, fg='green')}")
            click.echo()
            click.echo(f"👉 Abre esta URL en tu navegador: {verification_uri}")
            click.echo("   (Se abrirá automáticamente en 3 segundos)")
            
            # Abrir navegador automáticamente
            time.sleep(3)
            try:
                webbrowser.open(verification_uri)
            except:
                pass
            
            # Paso 3: Polling para obtener el token
            click.echo()
            click.echo("⏳ Esperando autorización... (presiona Ctrl+C para cancelar)")
            
            start_time = time.time()
            while time.time() - start_time < expires_in:
                token_response = cls._poll_for_token(device_code)
                
                if token_response.get('access_token'):
                    token = token_response['access_token']
                    click.echo("✅ Autenticación exitosa!")
                    
                    # Almacenar token
                    expires_in_seconds = token_response.get('expires_in', 28800)
                    cls._store_token(token, expires_in_seconds)
                    
                    return token
                
                elif token_response.get('error') == 'authorization_pending':
                    # Continuar esperando
                    time.sleep(interval)
                    click.echo("   ⏳ Esperando autorización...")
                    
                elif token_response.get('error') == 'slow_down':
                    # Aumentar intervalo
                    interval += 5
                    time.sleep(interval)
                    
                else:
                    # Error permanente
                    error = token_response.get('error', 'unknown')
                    click.echo(f"❌ Error de autorización: {error}")
                    return None
            
            click.echo("⏰ Tiempo de autorización expirado")
            return None
            
        except click.Abort:
            click.echo("\n❌ Autenticación cancelada por el usuario")
            return None
        except Exception as e:
            click.echo(f"❌ Error en autenticación por navegador: {e}")
            return None
    
    @classmethod
    def _request_device_code(cls) -> Optional[Dict[str, Any]]:
        """Solicita un device code para GitHub OAuth"""
        try:
            # Client ID para aplicaciones públicas de GitHub - usar el client ID oficial de GitHub CLI
            client_id = "178c6fc778ccc68e1d6a"  # GitHub CLI public client ID
            
            data = {
                'client_id': client_id,
                'scope': 'repo admin:repo_hook'
            }
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                'https://github.com/login/device/code',
                data=urlencode(data),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_data = response.json()
                    click.echo(f"❌ Error al solicitar device code: {response.status_code} - {error_data}")
                except:
                    click.echo(f"❌ Error al solicitar device code: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            return {'error': str(e)}

    @classmethod
    def _poll_for_token(cls, device_code: str) -> Dict[str, Any]:
        """Hace polling para obtener el access token"""
        try:
            client_id = "178c6fc778ccc68e1d6a"  # GitHub CLI public client ID
            
            data = {
                'client_id': client_id,
                'device_code': device_code,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
            }
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                'https://github.com/login/oauth/access_token',
                data=urlencode(data),
                headers=headers,
                timeout=10
            )
            
            return response.json()
            
        except Exception as e:
            return {'error': str(e)}
