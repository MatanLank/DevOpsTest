import boto3
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize boto3 client for Secrets Manager
secrets_client = boto3.client('secretsmanager')

def get_github_token():
    secret_name = "github_access_token"
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret

def handler(event, context):
    try:
        # Get GitHub token from Secrets Manager
        github_token = get_github_token()

        # Parse the GitHub event payload
        body = json.loads(event['body'])
        repo_name = body.get('repository', {}).get('name')
        pull_request = body.get('pull_request', {})
        files_url = pull_request.get('url') + "/files"  # GitHub API endpoint for files changed

        # Make a GET request to the GitHub API to fetch the changed files
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(files_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch files: {response.status_code}, {response.text}")

        changed_files = response.json()
        file_names = [file['filename'] for file in changed_files]
        
        # Log the repository name and the files that were changed
        logger.info(f"Repository: {repo_name}")
        logger.info(f"Files changed: {', '.join(file_names)}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success', 'files': file_names})
        }
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error processing event'})
        }
