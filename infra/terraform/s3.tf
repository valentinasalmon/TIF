resource "aws_s3_bucket" "evidencia" {
  bucket = var.evidencia_bucket_name

  tags = {
    Name = "${var.project_name}-${var.environment}-evidencia"
  }
}

# Versionado: la evidencia fotográfica es prueba legal, necesitamos poder ver
# el historial de un archivo y no perder versiones anteriores por sobreescritura.
resource "aws_s3_bucket_versioning" "evidencia" {
  bucket = aws_s3_bucket.evidencia.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidencia" {
  bucket = aws_s3_bucket.evidencia.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# El bucket nunca debe ser público: la app accede vía SDK/URLs firmadas, no
# navegación directa. Bloqueamos las 4 formas de acceso público de S3.
resource "aws_s3_bucket_public_access_block" "evidencia" {
  bucket = aws_s3_bucket.evidencia.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
