### lambda - start ###

resource "aws_lambda_function" "create-ami" {
  function_name = "create-ami"
  s3_bucket     = "${aws_s3_bucket.lambda-source.id}"
  s3_key        = "create-ami-v0.1.zip"
  role          = "${aws_iam_role.lambda-create-ami.arn}"
  handler       = "main.handle"
  runtime       = "python2.7"
  timeout       = 30
  tags {
    Name      = "create-ami"
    Terraform = "true"
  }
}

resource "aws_lambda_permission" "create-ami" {
  statement_id  = "create-ami-AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "create-ami"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.create-ami.arn}"
  depends_on    = ["aws_lambda_function.create-ami"]
}

### lambda - end ###


### s3 - start ###

resource "aws_s3_bucket" "lambda-source" {
  bucket        = "${var.s3-bucket-lambda-source}"
  force_destroy = false
  versioning {
    enabled = true
  }
  tags {
    Name      = "${var.s3-bucket-lambda-source}"
    Terraform = "true"
  }
}

### s3 - end ###


### cloudwatch - start ###

resource "aws_cloudwatch_event_rule" "create-ami" {
  name                = "create-ami-schedule"
  schedule_expression = "${var.create-ami-schedule}"
}

resource "aws_cloudwatch_event_target" "create-ami" {
  rule = "${aws_cloudwatch_event_rule.create-ami.name}"
  arn  = "${aws_lambda_function.create-ami.arn}"
}

### cloudwatch - end ###


### iam - start ###

resource "aws_iam_role" "lambda-create-ami" {
  name               = "lambda-create-ami"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "lambda-create-ami" {
  name   = "lambda-create-ami"
  role   = "${aws_iam_role.lambda-create-ami.id}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ec2:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

### iam - end ###
