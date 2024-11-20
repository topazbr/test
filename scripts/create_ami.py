import argparse
import boto3
from datetime import datetime

def create_ami(instance_id, region="us-east-1"):
    ec2_client = boto3.client('ec2', region_name=region)
    ami_name = f"ft-node-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"Creating AMI for instance {instance_id} with name '{ami_name}'...")
    try:
        response = ec2_client.create_image(
            InstanceId=instance_id,
            Name=ami_name,
            NoReboot=True
        )
        ami_id = response["ImageId"]
        print(f"AMI creation initiated successfully. AMI ID: {ami_id}")
        return ami_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create AMI from EC2 instance")
    parser.add_argument("--instance-id", required=True, help="EC2 instance ID")
    args = parser.parse_args()
    create_ami(args.instance_id)
