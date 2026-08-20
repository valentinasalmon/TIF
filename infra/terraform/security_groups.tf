# Sin cómputo dentro de la VPC todavía (ver decisión en infra/terraform/README.md):
# la base de datos queda accesible solo desde tu IP pública, nunca 0.0.0.0/0.
# Cuando se agregue un backend corriendo dentro de la VPC (ECS/EC2), este
# security group debe reemplazarse por uno que solo permita tráfico desde el
# security group de la aplicación, y la instancia debería dejar de ser
# publicly_accessible.
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Acceso a PostgreSQL solo desde la IP autorizada"
  vpc_id      = aws_vpc.principal.id

  ingress {
    description = "PostgreSQL desde IP autorizada"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip]
  }

  egress {
    description = "Salida sin restricciones"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}
