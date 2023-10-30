# Coworking Space Service Extension
The Coworking Space Service is a set of APIs that enables users to request one-time tokens and administrators to authorize access to a coworking space. This service follows a microservice pattern and the APIs are split into distinct services that can be deployed and managed independently of one another.

For this project, i am a DevOps engineer who will be collaborating with a team that is building an API for business analysts. The API provides business analysts basic analytics data on user activity in the service. The application they provide me functions as expected locally and i am expected to help build a pipeline to deploy it in Kubernetes.

## Getting Started

### Dependencies
#### Local Environment
1. Python Environment - run Python 3.6+ applications and install Python dependencies via `pip`
2. Docker CLI - build and run Docker images locally
3. `kubectl` - run commands against a Kubernetes cluster
4. `helm` - apply Helm Charts to a Kubernetes cluster
5. `psql` - use to test database connection

#### Remote Resources
1. AWS CodeBuild - build Docker images remotely
2. AWS ECR - host Docker images
3. Kubernetes Environment with AWS EKS - run applications in k8s
4. AWS CloudWatch - monitor activity and logs in EKS
5. GitHub - pull and clone code

### Setup

#### Note:
1. You must connect to AWS from your local machine via AWS Access Key ID, AWS Secret Access Key, and AWS Session Token.
2. Create ECR repository, CodeBuild project, EKS cluster and Node group. Note that the Instance type of the node group must match the CodeBuild environment image.
3. Use `aws eks update-kubeconfig --name <EKS_CLUSTER_NAME>` before running the commands below.

#### 1. Configure a Database
Set up a Postgres database using a Helm Chart.

1. Set up Bitnami Repo
```bash
helm repo add analytics-repo https://charts.bitnami.com/bitnami
```

2. Install PostgreSQL Helm Chart
```bash
helm install analytics-db analytics-repo/postgresql --set primary.persistence.enabled=false
```

This should set up a Postgre deployment at `analytics-db-postgresql.default.svc.cluster.local` in your Kubernetes cluster. You can verify it by running `kubectl svc`

By default, it will create a username `postgres`. The password can be retrieved with the following command:
```bash
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default analytics-db-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

echo $POSTGRES_PASSWORD
```

You shoud use the `echo -n $POSTGRES_PASSWORD | base64` command to get the password (base64) to use for database deployment file

<sup><sub>* The instructions are adapted from [Bitnami's PostgreSQL Helm Chart](https://artifacthub.io/packages/helm/bitnami/postgresql).</sub></sup>

3. Test Database Connection
The database is accessible within the cluster. This means that when you will have some issues connecting to it via your local environment. You can either connect to a pod that has access to the cluster _or_ connect remotely via [`Port Forwarding`](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/)

* Connecting Via Port Forwarding
```bash
kubectl port-forward --namespace default svc/analytics-db-postgresql 5432:5432 & PGPASSWORD=$POSTGRES_PASSWORD psql --host 127.0.0.1 -U postgres -d postgres -p 5432
```

4. Run Seed Files
We will need to run the seed files in `db/` in order to create the tables and populate them with data.

```bash
kubectl port-forward --namespace default svc/analytics-db-postgresql 5432:5432 & PGPASSWORD=$POSTGRES_PASSWORD psql --host 127.0.0.1 -U postgres -d postgres -p 5432 < <FILE_NAME.sql>
```

### 2. Running the Analytics Application Locally
In the `analytics/` directory:

1. Install dependencies
```bash
pip install -r requirements.txt
```
2. Run the application (see below regarding environment variables)
```bash
<ENV_VARS> python app.py
```

There are multiple ways to set environment variables in a command. They can be set per session by running `export KEY=VAL` in the command line or they can be prepended into your command.

* `DB_USERNAME`
* `DB_PASSWORD`
* `DB_HOST` (defaults to `127.0.0.1`)
* `DB_PORT` (defaults to `5432`)
* `DB_NAME` (defaults to `postgres`)

If we set the environment variables by prepending them, it would look like the following:
```bash
DB_USERNAME=postgres DB_PASSWORD=$POSTGRES_PASSWORD python app.py
```
The benefit here is that it's explicitly set. However, note that the `DB_PASSWORD` value is now recorded in the session's history in plaintext. There are several ways to work around this including setting environment variables in a file and sourcing them in a terminal session.

3. Verifying The Application
* Generate report for check-ins grouped by dates
`curl http://127.0.0.1:5153/api/reports/daily_usage`

* Generate report for check-ins grouped by users
`curl http://127.0.0.1:5153/api/reports/user_visits`

## Project Instructions
1. Set up a Postgres database with a Helm Chart.
2. Create a `Dockerfile` for the Python application. Use a base image that is Python-based.
3. Write a simple build pipeline with AWS CodeBuild to build and push a Docker image into AWS ECR.
4. Create a service and deployment using Kubernetes configuration files to deploy the application.
5. Check AWS CloudWatch for application logs.

### Deliverables
1. [Dockerfile](analytics/Dockerfile)
2. [Screenshot of AWS CodeBuild pipeline](images/3a-CodeBuild-pipeline.png)
3. [Screenshot of AWS ECR repository for the application's repository](images/3b-ECR-repository.png)
4. [Screenshot of kubectl get svc](images/5a-kubectl-get-svc.png)
5. [Screenshot of kubectl get pods](images/5b-kubectl-get-pods.png)
6. [Screenshot of kubectl describe svc <DATABASE_SERVICE_NAME>](images/5c-kubectl-describe-svc-database-service.png)
7. [Screenshot of kubectl describe deployment <SERVICE_NAME>](images/5d-kubectl-describe-deployment-service.png)
8. [All Kubernetes config files used for deployment (ie YAML files)](./images/)
9. [Screenshot of AWS CloudWatch logs for the application](images/6b-container-insight.png)


### Stand Out Suggestions
Please provide up to 3 sentences for each suggestion. Additional content in your submission from the standout suggestions do _not_ impact the length of your total submission.
1. When configuring Memory and CPU allocation in the Kubernetes deployment configuration, I chose the Instance Type for Node Group to be a1.large, because when deploying the application, there are some operations such as pulling docker images that will cause errors if we use "micro" Instance Types
2. In this project I used Instance type a1.large because if using smaller types, when application performance increases, it will not be able to run because of memory overflow.
3. I think to save costs, we should choose the appropriate Instance type. To know which one to choose, we should run the application locally first, then calculate and choose the appropriate Instance Type. We should also choose the appropriate number of EKS node groups because too many can cause redundancy and waste of resources.

### Best Practices
* Dockerfile uses an appropriate base image for the application being deployed. Complex commands in the Dockerfile include a comment describing what it is doing.
* The Docker images use semantic versioning with three numbers separated by dots, e.g. `1.2.1` and  versioning is visible in the screenshot. See [Semantic Versioning](https://semver.org/) for more details.