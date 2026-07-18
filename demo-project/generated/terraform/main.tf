terraform {
  required_version = ">= 1.5.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "app" {
  name = "demo-project:latest"
  build {
    context = ".."
  }
}

resource "docker_container" "app" {
  name  = "demo-project"
  image = docker_image.app.image
  ports {
    internal = 8080
    external = 8080
  }
}
