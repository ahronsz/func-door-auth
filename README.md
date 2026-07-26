# Door Auth — Lambda de autenticación

## Requisitos previos

- Python 3.12
- AWS CLI configurado
- AWS SAM CLI
- `pip install -r requirements.txt -r requirements-dev.txt`

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores.  
**Nunca** subas `.env` al repositorio.

### Configurar JWT_SECRET en Lambda (producción)

1. Generar secreto: `openssl rand -hex 32`
2. Guardar en SSM Parameter Store como SecureString:
   ```bash
   aws ssm put-parameter \
     --name /door-auth/jwt-secret \
     --value "<tu-secreto>" \
     --type SecureString \
     --region us-east-1
   ```
3. La plantilla SAM usa `{{resolve:ssm:/door-auth/jwt-secret}}` para inyectarlo en la variable de entorno de Lambda sin exponer el valor.

## Ejecución local

```bash
export $(cat .env | xargs)
sam local invoke AuthFunction --event tests/events/login.json
# O con hot-reload:
sam local start-lambda
```

## Pruebas

```bash
pytest                        # Unitarias + integración
pytest --cov-report=html      # Reporte HTML
```

## Linting y type checking

```bash
ruff check src tests
mypy src
```

## Empaquetado y despliegue

> ⚠️ argon2-cffi contiene binarios nativos. Construir en Amazon Linux o usar
> `sam build --use-container` para empaquetar correctamente.

```bash
sam build --use-container
sam deploy --guided \
  --parameter-overrides \
    AllowedOrigins="https://TU-APP.vercel.app,http://localhost:5173"
```

## Crear usuario administrativo

```bash
python scripts/create_user.py \
  --table <nombre-tabla-users> \
  --username jdoe
```

## Rollback

```bash
aws cloudformation cancel-update-stack --stack-name door-auth
# o
aws cloudformation rollback-stack --stack-name door-auth
```

## Eliminar recursos

```bash
sam delete --stack-name door-auth
# La tabla users tiene DeletionPolicy: Retain — eliminarla manualmente si es necesario:
aws dynamodb delete-table --table-name <nombre-tabla>
```