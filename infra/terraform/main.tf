terraform {
  required_version = ">= 1.6"
  required_providers { google = { source = "hashicorp/google", version = "~> 6.0" } }
}
variable "project_id" { type = string }
variable "region" { type = string default = "us-central1" }
provider "google" { project = var.project_id region = var.region }
resource "google_sql_database_instance" "dragonfly" {
  name = "dragonfly-postgres"
  database_version = "POSTGRES_16"
  region = var.region
  settings {
    tier = "db-custom-2-7680"
    backup_configuration { enabled = true point_in_time_recovery_enabled = true }
    ip_configuration { ipv4_enabled = false private_network = "projects/\${var.project_id}/global/networks/default" }
  }
  deletion_protection = true
}
resource "google_cloud_run_v2_service" "api" {
  name = "dragonfly-api"
  location = var.region
  template { containers { image = "us-docker.pkg.dev/\${var.project_id}/dragonfly/api:latest" } }
}
resource "google_cloud_run_v2_service" "web" {
  name = "dragonfly-web"
  location = var.region
  template { containers { image = "us-docker.pkg.dev/\${var.project_id}/dragonfly/web:latest" } }
}
