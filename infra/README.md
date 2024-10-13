### Initialise GCP Sandbox Environment

Below is a reference for the steps taken to set up a sandbox environment on GCP. *Note that GCP & BigQuery was chosen for ease due to my existing personal accounts. The principles can also be applied to AWS & Redshift*.

1. Login to GCP (validate with `gcloud auth list`)
```bash
gcloud auth login
```
2. Create a project to host the resources (validate with `gcloud projects list`)
```bash
gcloud projects create runna-task-public
```
3. Set the project to use (validate with `gcloud config list`)
```bash
gcloud config set project runna-task-public
```
4. Create a IAM Service Account for the project (validate with `gcloud iam service-accounts list`)
```bash
gcloud iam service-accounts create sa-runna-task-public \
    --description=”Runna”
```
5. Grant roles to the service account (validate with `gcloud projects get-iam-policy runna-task-public`)
```bash
gcloud projects add-iam-policy-binding runna-task-public \
    --member="serviceAccount:sa-runna-task-public@runna-task-public.iam.gserviceaccount.com" \
    --role="roles/editor"
```
6. Gather, edit and set IAM Policy for local impersonation
```bash
gcloud iam service-accounts get-iam-policy sa-runna-task-public@runna-task-public.iam.gserviceaccount.com \
    --format=json > policy.json

jq '. |= . + {"bindings": [{"members": ["user:samueltobyknight@gmail.com"], "role": "roles/iam.serviceAccountTokenCreator"}]}' policy.json > updated_policy.json

cp -f updated_policy.json policy.json
rm -f updated_policy.json

gcloud iam service-accounts set-iam-policy sa-runna-task-public@runna-task-public.iam.gserviceaccount.com \
    policy.json

rm -f policy.json
```
7. Create Storage of Terraform state
```bash
gcloud storage buckets create gs://runna-task-public-tf-state \
    --impersonate-service-account=sa-runna-task-public@runna-task-public.iam.gserviceaccount.com \
    --location=europe-west2
```
8. Initialise Terraform
```bash
terraform init --backend-config=backend.hcl
```
8. Plan/Apply Terraform
```bash
terraform <CMD>
```

*Ensure you have the IAM Service Account Credentials API enabled on GCP for above*.