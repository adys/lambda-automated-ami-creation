variable "aws_region" {
  default = "us-east-1"
}

variable "s3-bucket-lambda-source" {
  description = "S3 bucket lambda package"
  default     = "S3_BUCKET_NAME"
}

variable "create-ami-schedule" {
  description = "create-ami schedule"
  default     = "cron(0 6 * * ? *)"
}
