import click
from pathlib import Path
from tai_sql import pm

def create_workflow_file() -> bool:
    """
    Crea el workflow de GitHub Actions para TAI-SQL deploy basado en Pull Requests
    
    Returns:
        True si se creó exitosamente
    """
    try:
        # Crear directorio .github/workflows si no existe
        workflows_dir = Path('.github') / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Contenido del workflow basado en PR (con contexto corregido)
        workflow_content = f'''name: TAI-SQL Database Deploy

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
    paths:
      - '**/dbdeployments.md'  # Solo se dispara si cambia deployments.md en cualquier carpeta
  pull_request_review:
    types: [submitted]

env:
  PYTHON_VERSION: '3.11'

jobs:
  detect-deployment:
    name: 🔍 Detectar deployment request
    runs-on: ubuntu-latest
    if: startsWith(github.head_ref, 'database-deploy/')
    
    outputs:
      is-deployment: ${{{{ steps.parse.outputs.is-deployment }}}}
      entorno: ${{{{ steps.parse.outputs.entorno }}}}
      schema: ${{{{ steps.parse.outputs.schema }}}}
      
    steps:
      - name: 📋 Parsear información de deployment
        id: parse
        run: |
          BRANCH_NAME="${{{{ github.head_ref }}}}"
          echo "Branch: $BRANCH_NAME"
          
          if [[ $BRANCH_NAME =~ ^database-deploy/([^-]+)-([^-]+)-[0-9]{{8}}-[0-9]{{6}}$ ]]; then
            ENTORNO="${{BASH_REMATCH[1]}}"
            SCHEMA="${{BASH_REMATCH[2]}}"
            
            echo "is-deployment=true" >> $GITHUB_OUTPUT
            echo "entorno=$ENTORNO" >> $GITHUB_OUTPUT
            echo "schema=$SCHEMA" >> $GITHUB_OUTPUT
            
            echo "✅ Deployment detectado: $ENTORNO/$SCHEMA"
          else
            echo "is-deployment=false" >> $GITHUB_OUTPUT
            echo "❌ No es un deployment request válido"
          fi

  validate:
    name: 🔍 Validar cambios (${{{{ needs.detect-deployment.outputs.entorno }}}}/${{{{ needs.detect-deployment.outputs.schema }}}})
    runs-on: ubuntu-latest
    needs: detect-deployment
    if: needs.detect-deployment.outputs.is-deployment == 'true'
    environment: ${{{{ needs.detect-deployment.outputs.entorno }}}}
    
    outputs:
      has-changes: ${{{{ steps.dry-run.outputs.has-changes }}}}
      has-destructive: ${{{{ steps.dry-run.outputs.has-destructive }}}}
      validation-status: ${{{{ steps.dry-run.outputs.validation-status }}}}
      
    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v4
        with:
          ref: ${{{{ github.head_ref }}}}
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}
          cache: 'pip'
      
      - name: 📦 Install TAI-SQL
        run: |
          python -m pip install --upgrade pip
          pip install tai-sql
      
      - name: 🔍 Validar cambios
        id: dry-run
        env:
          {pm.db.provider.var_name}: ${{{{ secrets.{pm.db.provider.var_name} }}}}
        run: |
          echo "🚀 Validando deployment: ${{{{ needs.detect-deployment.outputs.entorno }}}}/${{{{ needs.detect-deployment.outputs.schema }}}}"
          
          OUTPUT_FILE="/tmp/tai-sql-output.log"
          EXIT_CODE=0
          
          tai-sql push --schema "${{{{ needs.detect-deployment.outputs.schema }}}}" --dry-run --verbose 2>&1 | tee "$OUTPUT_FILE" || EXIT_CODE=$?
          
          if [ $EXIT_CODE -eq 0 ]; then
            echo "validation-status=success" >> $GITHUB_OUTPUT
            
            if grep -q "No se detectaron cambios" "$OUTPUT_FILE"; then
              echo "has-changes=false" >> $GITHUB_OUTPUT
              echo "has-destructive=false" >> $GITHUB_OUTPUT
              echo "ℹ️ No se detectaron cambios"
            else
              echo "has-changes=true" >> $GITHUB_OUTPUT
              
              if grep -q "⚠️\\|DESTRUCTIVO\\|DROP" "$OUTPUT_FILE"; then
                echo "has-destructive=true" >> $GITHUB_OUTPUT
                echo "🚨 Cambios destructivos detectados"
              else
                echo "has-destructive=false" >> $GITHUB_OUTPUT
                echo "✅ Cambios seguros detectados"
              fi
            fi
          else
            echo "validation-status=failed" >> $GITHUB_OUTPUT
            echo "❌ Error en validación"
            exit $EXIT_CODE
          fi
          
          # Guardar salida para el comentario
          echo "VALIDATION_OUTPUT<<EOF" >> $GITHUB_ENV
          cat "$OUTPUT_FILE" >> $GITHUB_ENV
          echo "EOF" >> $GITHUB_ENV
      
      - name: 📊 Comentar resultado de validación
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{{{ needs.detect-deployment.outputs.entorno }}}}';
            const schema = '${{{{ needs.detect-deployment.outputs.schema }}}}';
            const hasChanges = '${{{{ steps.dry-run.outputs.has-changes }}}}' === 'true';
            const hasDestructive = '${{{{ steps.dry-run.outputs.has-destructive }}}}' === 'true';
            const validationStatus = '${{{{ steps.dry-run.outputs.validation-status }}}}';
            const validationOutput = process.env.VALIDATION_OUTPUT || 'No disponible';
            
            // Obtener número de PR de forma segura
            const pullNumber = context.payload.pull_request?.number || context.issue?.number;
            
            if (!pullNumber) {{
              console.log('❌ No se pudo obtener el número de PR para comentar');
              return;
            }}
            
            let statusEmoji = validationStatus === 'success' ? '✅' : '❌';
            let statusText = validationStatus === 'success' ? 'Validación exitosa' : 'Validación falló';
            
            const body = `## ${{statusEmoji}} ${{statusText}} - Base de Datos de ${{entorno.toUpperCase()}}
            
            **Entorno:** \\`${{entorno}}\\` 🎯 **Validado contra BD real del entorno**  
            **Schema:** \\`${{schema}}\\`  
            **Cambios detectados:** ${{hasChanges ? '✅ Sí' : 'ℹ️ No'}}  
            **Cambios destructivos:** ${{hasDestructive ? '🚨 Sí' : '✅ No'}}
            
            ### 🎯 Esta validación se ejecutó contra:
            - **Base de datos real** del entorno \\`${{entorno}}\\`
            - **NO** contra una base de datos local
            - Usando las credenciales configuradas para el entorno
            
            ### 📋 Detalles de la validación:
            <details>
            <summary>Ver cambios completos detectados en ${{entorno}}</summary>
            
            \\`\\`\\`sql
            ${{validationOutput.slice(0, 3000)}}${{validationOutput.length > 3000 ? '\\n...(truncado)' : ''}}
            \\`\\`\\`
            </details>
            
            ### 🎯 Próximos pasos:
            ${{validationStatus === 'success' ? 
              (entorno === 'development' && !hasDestructive ? 
                '🟢 **Development con cambios seguros** - Listo para merge automático' :
                hasDestructive ?
                  `🚨 **Cambios DESTRUCTIVOS en ${{entorno}}** - Requiere revisión cuidadosa de los reviewers` :
                  `🟡 **${{entorno}}** - Requiere aprobación de reviewers`) :
              '🔴 **Validación falló** - Corrige los errores antes de continuar'
            }}
            
            ${{hasDestructive ? 
              `### ⚠️ ATENCIÓN: CAMBIOS DESTRUCTIVOS
              
              Los cambios detectados incluyen operaciones que **pueden causar pérdida de datos** en \\`${{entorno}}\\`.
              
              **Revisa cuidadosamente:**
              - Operaciones DROP
              - Modificaciones de columnas
              - Eliminación de restricciones
              - Cambios de tipos de datos
              ` : ''
            }}
            
            ---
            *Validación automática de TAI-SQL contra BD de ${{entorno}}*`;
            
            await github.rest.issues.createComment({{
              issue_number: pullNumber,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            }});

  check-approval:
    name: 🎯 Verificar aprobación
    runs-on: ubuntu-latest
    needs: [detect-deployment, validate]
    if: needs.validate.outputs.validation-status == 'success' && needs.validate.outputs.has-changes == 'true'
    
    outputs:
      can-deploy: ${{{{ steps.approval.outputs.can-deploy }}}}
      
    steps:
      - name: 🔍 Verificar estado de aprobación
        id: approval
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{{{ needs.detect-deployment.outputs.entorno }}}}';
            const hasDestructive = '${{{{ needs.validate.outputs.has-destructive }}}}' === 'true';
            
            // Obtener número de PR de forma segura
            const pullNumber = context.payload.pull_request?.number || context.issue?.number;
            
            if (!pullNumber) {{
              console.log('❌ No se pudo obtener el número de PR');
              core.setOutput('can-deploy', 'false');
              return;
            }}
            
            console.log(`🔍 Verificando aprobaciones para PR #${{pullNumber}}`);
            
            // Para development sin cambios destructivos, auto-aprobar
            if (entorno === 'development' && !hasDestructive) {{
              console.log('✅ Auto-aprobando deployment seguro en development');
              core.setOutput('can-deploy', 'true');
              return;
            }}
            
            // Para otros casos, verificar reviews
            const {{ data: reviews }} = await github.rest.pulls.listReviews({{
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: pullNumber
            }});
            
            const approvals = reviews.filter(review => review.state === 'APPROVED').length;
            const rejections = reviews.filter(review => review.state === 'CHANGES_REQUESTED').length;
            
            console.log(`Reviews: ${{approvals}} aprobaciones, ${{rejections}} rechazos`);
            
            if (rejections > 0) {{
              console.log('❌ Deployment bloqueado por reviews que requieren cambios');
              core.setOutput('can-deploy', 'false');
              return;
            }}
            
            // Requisitos por entorno
            const requirements = {{
              development: 1,
              preproduction: 1,
              production: hasDestructive ? 2 : 1
            }};
            
            const required = requirements[entorno] || 1;
            
            if (approvals >= required) {{
              console.log(`✅ Suficientes aprobaciones (${{approvals}}/${{required}})`);
              core.setOutput('can-deploy', 'true');
            }} else {{
              console.log(`⏳ Esperando más aprobaciones (${{approvals}}/${{required}})`);
              core.setOutput('can-deploy', 'false');
            }}

  deploy:
    name: 🚀 Deploy cambios
    runs-on: ubuntu-latest
    needs: [detect-deployment, validate, check-approval]
    if: github.event.action == 'closed' && github.event.pull_request.merged == true && needs.check-approval.outputs.can-deploy == 'true'
    environment: ${{{{ needs.detect-deployment.outputs.entorno }}}}
    
    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v4
        with:
          ref: ${{{{ github.event.pull_request.merge_commit_sha }}}}
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}
          cache: 'pip'
      
      - name: 📦 Install TAI-SQL
        run: |
          python -m pip install --upgrade pip
          pip install tai-sql
      
      - name: 🚀 Ejecutar deployment
        env:
          {pm.db.provider.var_name}: ${{{{ secrets.{pm.db.provider.var_name} }}}}
        run: |
          echo "🚀 Ejecutando deployment: ${{{{ needs.detect-deployment.outputs.entorno }}}}/${{{{ needs.detect-deployment.outputs.schema }}}}"
          tai-sql push --schema "${{{{ needs.detect-deployment.outputs.schema }}}}" --force --verbose
      
      - name: 📊 Reporte de deployment exitoso
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{{{ needs.detect-deployment.outputs.entorno }}}}';
            const schema = '${{{{ needs.detect-deployment.outputs.schema }}}}';
            
            // Obtener número de PR de forma segura
            const pullNumber = context.payload.pull_request?.number;
            
            if (!pullNumber) {{
              console.log('❌ No se pudo obtener el número de PR para el reporte');
              return;
            }}
            
            const body = `## 🎉 Deployment Completado Exitosamente
            
            **Entorno:** \\`${{entorno}}\\`  
            **Schema:** \\`${{schema}}\\`  
            **Merge commit:** \\`${{{{ github.event.pull_request.merge_commit_sha }}}}\\`
            
            El schema ha sido actualizado exitosamente en la base de datos.
            
            ### 📋 Próximos pasos:
            - Verificar que la aplicación funciona correctamente
            - Monitorear logs en busca de errores
            - Ejecutar tests de integración si están disponibles
            
            ---
            *Deployment automático completado*`;
            
            await github.rest.issues.createComment({{
              issue_number: pullNumber,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            }});

  cleanup:
    name: 🧹 Limpiar rama
    runs-on: ubuntu-latest
    needs: [detect-deployment, deploy]
    if: always() && github.event.action == 'closed' && github.event.pull_request.merged == true
    
    steps:
      - name: 🗑️ Borrar rama de deployment
        uses: actions/github-script@v7
        with:
          script: |
            const branchName = '${{{{ github.head_ref }}}}';
            
            try {{
              await github.rest.git.deleteRef({{
                owner: context.repo.owner,
                repo: context.repo.repo,
                ref: `heads/${{branchName}}`
              }});
              console.log(`✅ Rama ${{branchName}} borrada exitosamente`);
            }} catch (error) {{
              console.log(`⚠️ No se pudo borrar la rama: ${{error.message}}`);
            }}

  no-changes:
    name: ℹ️ Sin cambios detectados
    runs-on: ubuntu-latest
    needs: [detect-deployment, validate]
    if: needs.detect-deployment.outputs.is-deployment == 'true' && needs.validate.outputs.has-changes == 'false'
    
    steps:
      - name: 📊 Reporte sin cambios
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{{{ needs.detect-deployment.outputs.entorno }}}}';
            const schema = '${{{{ needs.detect-deployment.outputs.schema }}}}';
            
            // Obtener número de PR de forma segura
            const pullNumber = context.payload.pull_request?.number || context.issue?.number;
            
            if (!pullNumber) {{
              console.log('❌ No se pudo obtener el número de PR para el reporte');
              return;
            }}
            
            const body = `## ℹ️ TAI-SQL Validation - Sin Cambios
            
            **Entorno:** \\`${{entorno}}\\`  
            **Schema:** \\`${{schema}}\\`  
            **Status:** ✅ Schema sincronizado
            
            El esquema está completamente sincronizado con la base de datos.
            No se detectaron diferencias entre el código y la base de datos actual.
            
            Puedes hacer merge de este PR sin riesgo, aunque no se ejecutará ningún deployment.
            
            ---
            *Validación completada por TAI-SQL*`;
            
            await github.rest.issues.createComment({{
              issue_number: pullNumber,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            }});
'''
        
        # Escribir el archivo
        workflow_file = workflows_dir / 'database-deploy.yml'
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        
        click.echo(f"✅ Workflow creado: {workflow_file}")
        return True
        
    except Exception as e:
        click.echo(f"❌ Error al crear workflow: {e}")
        return False