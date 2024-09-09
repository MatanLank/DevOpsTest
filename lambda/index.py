import json

def handler(event, context):
    try:
        body = json.loads(event['body'])
        repo_name = body.get('repository', {}).get('name')
        pull_request = body.get('pull_request', {})
        changes = pull_request.get('changed_files', 0)
        print(f"Repository: {repo_name}")
        print(f"Files changed: {changes}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Success'})
        }
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error processing event'})
        }
