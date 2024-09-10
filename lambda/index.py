import boto3
import json
import logging
import urllib.request
import urllib.error

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
        # Log the received event
        logger.info(f"Received event: {json.dumps(event, indent=2)}")

        # Get GitHub token from Secrets Manager
        github_token = get_github_token()

        body = event['body']
        repo_name = body['repository']['name']
        pull_request = body['pull_request']
        files_url = pull_request['url'] + "/files"  # GitHub API endpoint for files changed

        # Make a GET request to the GitHub API to fetch the changed files
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        req = urllib.request.Request(files_url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch files: {response.status}, {response.read().decode('utf-8')}")

                response_data = response.read().decode('utf-8')
                changed_files = json.loads(response_data)
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP Error: {e.code}, {e.read().decode('utf-8')}")
        except urllib.error.URLError as e:
            raise Exception(f"URL Error: {str(e)}")

        # Extract file names
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