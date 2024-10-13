variable project {default="runna-task-public"}

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
    google-beta = {
      source = "hashicorp/google-beta"
    }
  }
  required_version = ">= 0.14.8"
  backend "gcs" {}
}

provider "google" {
    project = "runna-task-public"
    region = "europe-west2"
    zone = "europe-west2-a"
    impersonate_service_account = "sa-runna-task-public@runna-task-public.iam.gserviceaccount.com"
}