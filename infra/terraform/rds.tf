resource "aws_db_subnet_group" "principal" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.publicas[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

resource "aws_db_instance" "principal" {
  identifier     = "${var.project_name}-${var.environment}-db"
  engine         = "postgres"
  engine_version = var.db_engine_version

  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage_gb
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.principal.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  # publicly_accessible=true porque todavía no hay cómputo dentro de la VPC
  # (ver security_groups.tf y README.md) — el acceso real sigue acotado por
  # el security group a var.allowed_ip, no queda abierto a internet.
  publicly_accessible = true

  multi_az = false # capa gratuita / proyecto individual, no alta disponibilidad

  backup_retention_period = 7
  skip_final_snapshot     = true # aceptable en dev; revisar antes de un entorno real
  deletion_protection     = false

  tags = {
    Name = "${var.project_name}-${var.environment}-db"
  }
}
