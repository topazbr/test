import boto3
import sys

def validate_ip(ip_address, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)
    try:
        # Describe instances with filters to find matching instance by private IP
        response = ec2.describe_instances(
            Filters=[
                {"Name": "private-ip-address", "Values": [ip_address]},
                {"Name": "instance-state-name", "Values": ["running"]},
            ]
        )
        instances = response["Reservations"]
        if not instances:
            print(f"No running instance found with IP {ip_address}")
            sys.exit(1)
        instance_id = instances[0]["Instances"][0]["InstanceId"]
        print(f"Found running instance: {instance_id} for IP {ip_address}")
        return instance_id
    except Exception as e:
        print(f"Error validating IP {ip_address}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create AMI from EC2 instance.")
    parser.add_argument("--instance-ip", required=True, help="IP of the instance")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    args = parser.parse_args()

    # Validate IP and get the instance ID
    instance_id = validate_ip(args.instance_ip, region=args.region)

    print(f"Instance {instance_id} validated. Proceeding to create AMI...")
    # Continue with AMI creation logic...
