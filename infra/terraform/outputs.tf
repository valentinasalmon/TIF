output "rds_endpoint" {
  description = "Endpoint de conexión a la base de datos (host:puerto)."
  value       = aws_db_instance.principal.endpoint
}

output "rds_database_name" {
  description = "Nombre de la base de datos."
  value       = aws_db_instance.principal.db_name
}

output "rds_database_url" {
  description = "DATABASE_URL lista para pegar en tu .env (sin la contraseña, por seguridad)."
  value       = "postgresql://${var.db_username}:<DB_PASSWORD>@${aws_db_instance.principal.endpoint}/${aws_db_instance.principal.db_name}"
}

output "evidencia_bucket_name" {
  description = "Nombre del bucket S3 de evidencia fotográfica."
  value       = aws_s3_bucket.evidencia.bucket
}

output "evidencia_bucket_arn" {
  description = "ARN del bucket S3 de evidencia fotográfica."
  value       = aws_s3_bucket.evidencia.arn
}

output "vpc_id" {
  description = "ID de la VPC creada."
  value       = aws_vpc.principal.id
}
