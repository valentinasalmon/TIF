# Infraestructura AWS (Terraform)

Provisiona la infraestructura mínima definida para el proyecto: base de datos (RDS PostgreSQL) y
almacenamiento de evidencia fotográfica (S3), dentro de una VPC propia. **No incluye cómputo
todavía** (ni servidor para el backend Flask ni hosting del frontend React) — hoy corrés la app
localmente contra esta base de datos y este bucket. Eso se suma en una iteración futura.

Esto se aplica **desde tu máquina**, no desde Claude Code — para no compartir tus credenciales de
AWS con esta sesión.

## 1. Prerrequisitos

- Cuenta de AWS (ya la tenés).
- [Terraform CLI](https://developer.hashicorp.com/terraform/install) instalado (`terraform -version`, cualquier 1.7.x en adelante).
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) instalado (`aws --version`).

## 2. Crear un usuario IAM para Terraform (no uses tu usuario root)

1. Entrá a la consola de AWS → **IAM** → **Users** → **Create user**.
2. Nombre: `terraform-tif`. No le des acceso a la consola (solo "programmatic access" vía claves).
3. Permisos: para este alcance (VPC + RDS + S3) alcanza con adjuntar estas políticas administradas
   de AWS:
   - `AmazonRDSFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonVPCFullAccess`

   (Son más permisivas de lo estrictamente necesario, pero para un proyecto individual es un
   balance razonable entre seguridad y no perder tiempo armando una política custom. **Nunca**
   uses `AdministratorAccess` para esto.)
4. Creá el usuario y generá un **Access key** (tipo "Command Line Interface (CLI)"). Guardá el
   `Access Key ID` y el `Secret Access Key` — el secret no se puede volver a ver después.

## 3. Configurar las credenciales en tu máquina

```bash
aws configure
```

Te va a pedir el Access Key ID, el Secret Access Key, la región por defecto (`us-east-1` si no
tenés preferencia) y el formato de salida (`json`). Esto guarda las credenciales en
`~/.aws/credentials` — **nunca las pegues en un archivo del repo ni en un mensaje de chat.**

Verificá que funcionó:

```bash
aws sts get-caller-identity
```

Debería devolverte el ARN del usuario `terraform-tif` que creaste.

## 4. Configurar las variables de este módulo

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
```

Editá `terraform.tfvars` y completá:

- `allowed_ip`: tu IP pública en formato CIDR. Conseguila con `curl ifconfig.me` y agregale `/32`
  al final (ej. `"200.55.130.10/32"`). Es la única IP que va a poder conectarse a la base de
  datos — si tu IP cambia (router doméstico, otra red), vas a tener que actualizar esta variable y
  volver a aplicar.
- `db_password`: una contraseña fuerte para el usuario administrador de la base de datos.
- `evidencia_bucket_name`: los nombres de bucket S3 son únicos en **toda** AWS (no solo tu cuenta),
  así que el nombre por defecto probablemente ya esté tomado por otra persona. Elegí algo único,
  por ejemplo con tu usuario: `tif-evidencia-valentinasalmon`.

`terraform.tfvars` está en `.gitignore` — nunca se commitea (tiene tu password).

## 5. Inicializar, revisar y aplicar

```bash
terraform init      # descarga el provider de AWS
terraform plan       # te muestra qué va a crear, sin crear nada todavía — revisalo
terraform apply       # te pide confirmación (escribí "yes") y crea los recursos
```

`terraform apply` tarda unos 5-10 minutos, principalmente por la creación de la instancia RDS.

Al terminar, `terraform output` te muestra el endpoint de la base de datos y el nombre del bucket.
Para armar tu `DATABASE_URL` completa, tomá el output `rds_database_url` y reemplazá
`<DB_PASSWORD>` por la password que pusiste en `terraform.tfvars`.

## 6. Costos — importante

- `db.t4g.micro` con 20GB de almacenamiento entra en la **capa gratuita de AWS durante los
  primeros 12 meses** de la cuenta. Pasado ese período (o si excedés las 750 hs/mes de la capa
  gratuita), tiene costo.
- S3 tiene un costo mínimo por almacenamiento y requests, prácticamente insignificante para el
  volumen de un TIF, pero no es gratis desde el día 1 como RDS.
- **Activá alertas de facturación** en AWS (Billing → Budgets) para no llevarte una sorpresa.

## 7. Destruir la infraestructura

Cuando no la estés usando (para no acumular costo), o cuando termines de probar:

```bash
terraform destroy
```

Esto borra la base de datos y el bucket (y todo su contenido versionado) de forma **irreversible**.
Si tenés datos que te importan, hacé un backup/export antes.

## 8. Decisiones de diseño (por qué está armado así)

- **RDS `publicly_accessible = true` restringido por security group a tu IP**: como todavía no hay
  ningún servidor corriendo dentro de la VPC (el backend lo corrés local), la base de datos
  necesita ser alcanzable desde tu máquina. El acceso real sigue acotado por el security group,
  nunca abierto a `0.0.0.0/0`. Cuando se agregue cómputo dentro de la VPC (ECS/EC2 para el
  backend), esto debería cambiar a `publicly_accessible = false` con acceso solo desde el security
  group de la aplicación — ver el comentario en `security_groups.tf`.
- **Estado de Terraform local** (no remoto): es un proyecto individual, no hay riesgo de que dos
  personas apliquen cambios en simultáneo. Si en algún momento colaboran varias personas, conviene
  migrar a un backend remoto (S3 + DynamoDB para locking).
- **Versionado + bloqueo de acceso público en S3**: la evidencia fotográfica es prueba legal —
  necesitás poder ver el historial de un archivo (versionado) y estar segura de que nadie accede
  al bucket sin pasar por la aplicación (bloqueo de acceso público).
