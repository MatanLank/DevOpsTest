## DevOpsTest
# GitHub Pull Request File Logger

This project is a service that logs all files changed in a GitHub repository when a pull request is merged. The service is built using AWS, Python, and Terraform.

## Features

- AWS Lambda function triggered by an API Gateway to log files changed in GitHub pull requests.
- Uses GitHub API to retrieve pull request details and changed files.
- GitHub access token is securely managed using AWS Secrets Manager.
- Terraform is used to deploy and manage AWS resources.

## Architecture

The service is triggered by a webhook via AWS API Gateway when a pull request is merged in a GitHub repository. The Lambda function then fetches the changed files using the GitHub API and logs them.

## AWS Resources

- **Lambda Function**: Executes the logic to fetch changed files from GitHub.
- **API Gateway**: Handles HTTP POST requests as webhook events from GitHub.
- **Secrets Manager**: Stores the GitHub access token securely.
- **IAM Roles and Policies**: Grant necessary permissions for Lambda and Secrets Manager.