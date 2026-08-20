variable "aws_region" {
  description = "Región de AWS donde se provisiona la infraestructura."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nombre del proyecto, usado como prefijo de los recursos."
  type        = string
  default     = "tif"
}

variable "environment" {
  description = "Entorno (dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "Bloque CIDR de la VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDRs de las subnets públicas (una por AZ, RDS exige al menos 2 AZs)."
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "allowed_ip" {
  description = <<-EOT
    Tu IP pública en formato CIDR (ej. "200.55.130.10/32"), la única IP
    autorizada a conectarse a la base de datos mientras no haya cómputo
    dentro de la VPC. Conseguila con `curl ifconfig.me` y agregale "/32".
  EOT
  type        = string
}

variable "db_name" {
  description = "Nombre de la base de datos PostgreSQL."
  type        = string
  default     = "tif"
}

variable "db_username" {
  description = "Usuario administrador de la base de datos."
  type        = string
  default     = "tif_admin"
}

variable "db_password" {
  description = "Password del usuario administrador de la base de datos. No tiene default a propósito: se pasa por terraform.tfvars (gitignored) o variable de entorno TF_VAR_db_password."
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "Tipo de instancia de RDS. db.t4g.micro entra en la capa gratuita de AWS (12 meses)."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage_gb" {
  description = "Almacenamiento asignado a RDS en GB. 20GB entra en la capa gratuita."
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "Versión de PostgreSQL."
  type        = string
  default     = "16"
}

variable "evidencia_bucket_name" {
  description = <<-EOT
    Nombre del bucket S3 para evidencia fotográfica. Los nombres de bucket
    son globalmente únicos en AWS, así que el default probablemente esté
    ocupado: sobreescribilo en terraform.tfvars (ej. "tif-evidencia-valesalmon").
  EOT
  type        = string
  default     = "tif-evidencia-fotografica"
}
