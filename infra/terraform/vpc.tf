data "aws_availability_zones" "disponibles" {
  state = "available"
}

resource "aws_vpc" "principal" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-${var.environment}-vpc"
  }
}

resource "aws_internet_gateway" "principal" {
  vpc_id = aws_vpc.principal.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

# RDS exige que el subnet group cubra al menos 2 Availability Zones,
# aunque la instancia no sea Multi-AZ.
resource "aws_subnet" "publicas" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.principal.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.disponibles.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.environment}-publica-${count.index + 1}"
  }
}

resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.principal.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.principal.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rt-publica"
  }
}

resource "aws_route_table_association" "publica" {
  count = length(aws_subnet.publicas)

  subnet_id      = aws_subnet.publicas[count.index].id
  route_table_id = aws_route_table.publica.id
}
