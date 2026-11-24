terraform {
  backend "s3" {
    bucket = "bucks-2404" # You must create this bucket in AWS first
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

#VPC - mainvpc
resource "aws_vpc" "mainvpc" {
  cidr_block       = var.vpc_cidr
  instance_tenancy = "default"

  tags = {
    Name = "main"
  }
}

#Security Groups for LoadBalancer
resource "aws_security_group" "securelb" {
  name        = "securelb"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = aws_vpc.mainvpc.id
}
resource "aws_vpc_security_group_ingress_rule" "inboundlb" {
  security_group_id = aws_security_group.securelb.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}
resource "aws_vpc_security_group_egress_rule" "outboundlb" {
  security_group_id = aws_security_group.securelb.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

#Public Subnet
resource "aws_subnet" "publica" {
  vpc_id     = aws_vpc.mainvpc.id
  cidr_block = var.publica
  availability_zone = "us-east-1a"

  tags = {
    Name = "Public"
  }
}
resource "aws_subnet" "publicb" {
  vpc_id     = aws_vpc.mainvpc.id
  cidr_block = var.publicb
  availability_zone = "us-east-1b"

  tags = {
    Name = "Public"
  }
}
#Private Subnet
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.mainvpc.id
  cidr_block = var.private
  availability_zone = "us-east-1a"

  tags = {
    Name = "Private"
  }
}


#Internet Gateway
resource "aws_internet_gateway" "igw"{
  vpc_id = aws_vpc.mainvpc.id

  tags = {
    Name = "main-igw"
  }
}







#ROUTE TABLE which sends traffic Internet gateway  -- PUBLIC
resource "aws_route_table" "pubroute" {
  vpc_id = aws_vpc.mainvpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}
#ASSOCIATION to PublicA
resource "aws_route_table_association" "publicaroute" {
  subnet_id      = aws_subnet.publica.id
  route_table_id = aws_route_table.pubroute.id
}

#Association to PublicB
resource "aws_route_table_association" "publicbroute" {
  subnet_id      = aws_subnet.publicb.id
  route_table_id = aws_route_table.pubroute.id
}






#EIp For NAT Gateway

resource "aws_eip" "eip" {
  domain   = "vpc"
}

#NAT Gateway for ECS Fargate to download Image from ECR
resource "aws_nat_gateway" "natecs" {
  allocation_id = aws_eip.eip.id
  connectivity_type = "public"
  subnet_id         = aws_subnet.publica.id
  depends_on    = [aws_internet_gateway.igw]
}


#ROUTE TABLE which sends traffic NAT Gateway  -- PRIVATE
resource "aws_route_table" "priroute" {
  vpc_id = aws_vpc.mainvpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.natecs.id
  }
}

#ASSOCIATION to Private
resource "aws_route_table_association" "privateroute" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.priroute.id
}




#Application Load Balancer with Target Group and Listners

resource "aws_lb" "front_end" {
    load_balancer_type= "application"
    security_groups = [aws_security_group.securelb.id]

    # Attach the ALB to both public subnets using their IDs
  subnets = [
    aws_subnet.publica.id,
    aws_subnet.publicb.id
]
}

resource "aws_lb_target_group" "front_end_blue" {
  name     = "TargetGroupBlue"
  port     = var.port
  protocol = "HTTP"
  vpc_id   = aws_vpc.mainvpc.id # Required argument
  target_type = "ip"
}

resource "aws_lb_target_group" "front_end_green" {
  name     = "TargetGroupGreen"
  port     = var.port
  protocol = "HTTP"
  vpc_id   = aws_vpc.mainvpc.id # Required argument
  target_type = "ip"
}
#
resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.front_end.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"

    forward {
      target_group {
        arn    = aws_lb_target_group.front_end_blue.arn
        weight = 100
      }
      target_group {
        arn    = aws_lb_target_group.front_end_green.arn
        weight = 0
      }
    }
  }
}

#ECR Repo Creation
resource "aws_ecr_repository" "practice" {
  name                 = "apprepo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

#ECS Security Group
resource "aws_security_group" "ecssg" {
  name        = "ecs-security-group"
  description = "Allow inbound traffic from ALB"
  vpc_id      = aws_vpc.mainvpc.id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.securelb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


#ECS Cluster, task definition, Service, Security Group

resource "aws_ecs_cluster" "cluster" {
  name = "white-hart"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

#Task Definition
resource "aws_ecs_task_definition" "mongo" {
  family = "service"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = "512"
  memory = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  container_definitions = jsonencode([
    {
      name      = "main"
      image     = "${aws_ecr_repository.practice.repository_url}:latest"
      cpu       = 512
      memory    = 1024
      essential = true
      portMappings = [
        {
          containerPort = 5000
        }
      ]
    }
  ])
}

#Service
resource "aws_ecs_service" "vetriservice" {
  name            = "vetri"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.mongo.arn
  launch_type = "FARGATE"
  desired_count   = 2
  wait_for_steady_state = false # Prevents Terraform from hanging before the first image is pushed

  network_configuration{
    subnets = [aws_subnet.private.id]
    security_groups = [aws_security_group.ecssg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.front_end_blue.arn
    container_name   = "main"
    container_port   = 5000
  }
}

# IAM TASK EXECUTION ROLE
# ==========================================
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Attach the AWS-managed policy required to pull ECR images
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


#PAYMENT CONTAINER 

#ECS Security Group - Ingress - Source set to Catalog Security group and Egress is for 0.0.0.0

resource "aws_security_group" "payment-sg" {
  name        = "payment-sg"
  description = "Payment Ecs connected to vpc and source is from catalog ecs as it should not connected to Internet"
  vpc_id      = aws_vpc.mainvpc.id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.ecssg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#Payment ECR
resource "aws_ecr_repository" "payment" {
  name                 = "payrepo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

#Payment ECS

#Task Definition
resource "aws_ecs_task_definition" "payment" {
  family = "payment-service"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = "512"
  memory = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  container_definitions = jsonencode([
    {
      name      = "main"
      image     = "${aws_ecr_repository.payment.repository_url}:latest"
      cpu       = 512
      memory    = 1024
      essential = true
      portMappings = [
        {
          containerPort = 5000
        }
      ]
    }
  ])
}

#Service
resource "aws_ecs_service" "paymentservice" {
  name            = "vetripayment"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.payment.arn
  launch_type = "FARGATE"
  desired_count   = 2
  wait_for_steady_state = false # Prevents Terraform from hanging before the first image is pushed

  network_configuration{
    subnets = [aws_subnet.private.id]
    security_groups = [aws_security_group.payment-sg.id]
  }
}
