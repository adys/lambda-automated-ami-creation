import boto3
import logging
from datetime import datetime, timedelta
import time

BACKUP_TAG = 'backup-enabled'
BACKUP_TAG_RETENTION = 'backup-retention'
DEFAULT_RETENTION_DAYS = 7
AMI_PREFIX = 'lambda-'
AMI_INSTANCE_TAG = 'instance'
AMI_CREATION_TAG = 'creation-timestamp'

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

EC2 = boto3.client('ec2')

def findInstances():
    """ Finds instances that have the backup tag """
    reservations = EC2.describe_instances(
        Filters = [{
            'Name': 'tag-key', 'Values': [BACKUP_TAG]}
        ]).get('Reservations', [])
    return reservations

def deregisterOldImages(instance_name,retention_days):
    """ Deregisters AMIs that are older than retention period """
    all_images = EC2.describe_images(
        Filters = [{
            'Name': 'tag:' + AMI_INSTANCE_TAG,
            'Values': [instance_name]}
        ])
    for image in all_images['Images']:
        for tag in image["Tags"]:
            if tag['Key'] == AMI_CREATION_TAG:
                creation_timestamp = tag['Value']
        creation_datetime = datetime.utcfromtimestamp(float(creation_timestamp))
        retention = datetime.utcnow() - timedelta(days=int(retention_days))
        if creation_datetime < retention:
            LOGGER.info('Deregistering ' + image['ImageId'] + ' AMI which is older than ' + str(retention_days) + ' days ...')
            EC2.deregister_image(ImageId=image['ImageId'])
            if image['RootDeviceType'] == 'ebs':
                for device_map in image['BlockDeviceMappings']:
                    snapshot_id = device_map['Ebs']['SnapshotId']
                    LOGGER.info('Deleting ' + snapshot_id + ' snapshot used by ' + image['ImageId'] + ' AMI ...')
                    EC2.delete_snapshot(SnapshotId=snapshot_id)

def handle(event, context):
    """ Creates AMIs of all the instances that have the backup tag """
    retention_days = DEFAULT_RETENTION_DAYS
    reservations = findInstances()
    instance_name = ''
    now_unix = time.time()

    for reservation in reservations:
        for instance in reservation["Instances"]:
            for tag in instance["Tags"]:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                if tag['Key'] == BACKUP_TAG_RETENTION:
                    retention_days = tag['Value']
            LOGGER.info('Creating AMI of ' + instance["InstanceId"] + ' [ ' + instance_name + ' ] instance ...')
            ami_image = EC2.create_image(InstanceId=instance['InstanceId'], Name=AMI_PREFIX + instance_name + '-' + datetime.utcnow().strftime('%Y-%m-%d') + '-' + str(int(now_unix)), NoReboot=True, DryRun=False)
            EC2.create_tags(
                Resources = [ami_image['ImageId']],
                Tags = [{
                        'Key': AMI_INSTANCE_TAG,
                        'Value': instance_name },
                    {
                        'Key': AMI_CREATION_TAG,
                        'Value': str(now_unix) }
                    ])
            LOGGER.info(ami_image['ImageId'] + ' AMI of ' + instance['InstanceId'] + ' [ ' + instance_name + ' ] instance has been created')
            deregisterOldImages(instance_name,retention_days)
    return
