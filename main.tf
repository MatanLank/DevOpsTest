provider "aws" {
  region = "us-west-2"
}

resource "aws_lambda_function" "example" {
  filename         = "lambda_function.zip"
  function_name    = "example_lambda_function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "index.handler"
  runtime          = "python3.9"

  source_code_hash = filebase64sha256("lambda_function.zip")
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com",
        },
      },
    ],
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn  = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

output "lambda_function_name" {
  value = aws_lambda_function.example.function_name
}

resource "aws_api_gateway_rest_api" "api" {
  name        = "example-api"
  description = "API for Lambda function"
}

resource "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "webhook"
}

resource "aws_api_gateway_method" "post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.root.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.root.id
  http_method             = aws_api_gateway_method.post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/${aws_lambda_function.example.arn}/invocations"
}

resource "aws_api_gateway_deployment" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"

  depends_on = [
    aws_api_gateway_integration.lambda,
  ]
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.example.function_name
  principal     = "apigateway.amazonaws.com"

  # The source ARN is the ARN of the API Gateway stage.
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

resource "aws_iam_policy" "secrets_manager_access" {
  name = "secrets_manager_access_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow",
        Resource = "arn:aws:secretsmanager:us-west-2:622395351311:secret:github_access_token-*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_manager_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

output "api_endpoint" {
  value = "${aws_api_gateway_deployment.api.invoke_url}/webhook"
}
