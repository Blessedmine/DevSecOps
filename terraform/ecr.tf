resource "aws_ecr_repository" "app" {
  name                 = "devsecops-demo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "devsecops-demo"
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}