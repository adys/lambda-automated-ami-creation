TODO: create README file

vim variables.tf
# https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html

S3_BUCKET_NAME=<bucket_name>
sed -i "s/S3_BUCKET_NAME/${S3_BUCKET_NAME}/" variables.tf
terraform apply --target aws_s3_bucket.lambda-source
cd lambda/ && zip create-ami-v0.1.zip main.py && cd ..
aws s3 cp lambda/create-ami-v0.1.zip s3://${S3_BUCKET_NAME}/
terraform apply
