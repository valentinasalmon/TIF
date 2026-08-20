terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Estado local por ahora (proyecto individual, sin equipo).
  # Cuando haya más de una persona aplicando cambios, migrar a un backend
  # remoto (S3 + DynamoDB para locking) para evitar pisar el estado.
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Proyecto      = var.project_name
      Entorno       = var.environment
      GestionadoPor = "terraform"
    }
  }
}
