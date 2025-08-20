variable "datetime_tag" {
  default = formatdate("YYYYMMDD-hhmmss", timestamp())
}

variable "DOCKERHUB_USERNAME" {
  type = string
}

group "default" {
  targets = ["default"]
}

target "default" {
  context = "."
  dockerfile = ".devcontainer/Dockerfile"
  target = "default"
  tags = ["${DOCKERHUB_USERNAME}/ties-ci:${datetime_tag}", "${DOCKERHUB_USERNAME}/ties-ci:latest"]
  output = [{ type = "registry" }]
  platforms = ["linux/amd64", "linux/arm64"]
}
