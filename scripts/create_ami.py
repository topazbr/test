import boto3
import time
from datetime import datetime

# Initialize boto3 clients for EC2, Auto Scaling, and Launch Templates
ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')
launch_templates = boto3.client('ec2')


# Function to create an AMI from a stopped EC2 instance
def create_ami_from_instance(instance_id):
    # Get the current time to use as part of the AMI name
    date_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    ami_name = f"ft-node-{date_time}"

    try:
        # Create AMI
        response = ec2.create_image(
            InstanceId=instance_id,
            Name=ami_name,
            NoReboot=True  # Don't reboot the instance
        )

        # Return the created AMI ID
        ami_id = response['ImageId']
        print(f"AMI created with ID: {ami_id}")
        return ami_id
    except Exception as e:
        print(f"Error creating AMI: {e}")
        return None


# Function to get the latest launch configuration from Auto Scaling
def get_latest_launch_configuration():
    try:
        response = autoscaling.describe_launch_configurations()

        if 'LaunchConfigurations' in response:
            # Sort by creation time to get the latest one
            sorted_configs = sorted(response['LaunchConfigurations'], key=lambda x: x['CreatedTime'], reverse=True)
            latest_config = sorted_configs[0]
            print(f"Latest Launch Configuration: {latest_config['LaunchConfigurationName']}")
            return latest_config
        else:
            print("No launch configurations found.")
            return None
    except Exception as e:
        print(f"Error fetching launch configurations: {e}")
        return None


# Function to copy the latest launch configuration and update it with the new AMI
def copy_launch_configuration(latest_config, ami_id):
    try:
        # Generate a new launch configuration name based on current date-time
        new_name = f"launch-config-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

        # Create the new launch configuration using the selected AMI
        response = autoscaling.create_launch_configuration(
            LaunchConfigurationName=new_name,
            ImageId=ami_id,
            KeyName=latest_config['KeyName'],
            SecurityGroups=latest_config['SecurityGroups'],
            InstanceType=latest_config['InstanceType'],
            IamInstanceProfile=latest_config.get('IamInstanceProfile', ''),
            AssociatePublicIpAddress=latest_config.get('AssociatePublicIpAddress', False),
            UserData=latest_config.get('UserData', ''),
            EbsOptimized=latest_config.get('EbsOptimized', False),
            InstanceMonitoring=latest_config.get('InstanceMonitoring', {}),
            BlockDeviceMappings=latest_config.get('BlockDeviceMappings', [])
        )

        print(f"New Launch Configuration created with name: {new_name}")
        return new_name
    except Exception as e:
        print(f"Error copying launch configuration: {e}")
        return None


# Function to update the Auto Scaling group with the new launch configuration
def update_auto_scaling_group(auto_scaling_group_name, launch_configuration_name):
    try:
        response = autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=auto_scaling_group_name,
            LaunchConfigurationName=launch_configuration_name
        )
        print(f"Auto Scaling Group updated with Launch Configuration: {launch_configuration_name}")
    except Exception as e:
        print(f"Error updating Auto Scaling Group: {e}")


# Function to update the Launch Template with the new AMI
def update_launch_template(template_name, ami_id):
    try:
        # Modify the launch template to create a new version
        response = launch_templates.create_launch_template_version(
            LaunchTemplateName=template_name,
            VersionDescription=f"Version created on {datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
            LaunchTemplateData={
                'ImageId': ami_id
            }
        )

        new_version_id = response['LaunchTemplateVersion']['VersionNumber']
        print(f"Launch Template updated to new version: {new_version_id}")

        # Set the new version as the default version
        launch_templates.modify_launch_template(
            LaunchTemplateName=template_name,
            DefaultVersion=new_version_id
        )

        print(f"Launch Template version {new_version_id} set as default.")
    except Exception as e:
        print(f"Error updating Launch Template: {e}")


# Main function that automates all the steps
def main():
    # Get the instance ID of the stopped EC2 instance (replace with your instance ID)
    instance_id = 'i-1234567890abcdef0'  # Example, you can find this programmatically if needed

    # Step 1: Create AMI from the stopped EC2 instance
    ami_id = create_ami_from_instance(instance_id)
    if not ami_id:
        return

    # Step 2: Get the latest Launch Configuration
    latest_config = get_latest_launch_configuration()
    if not latest_config:
        return

    # Step 3: Copy the Launch Configuration and update it with the new AMI
    new_launch_config_name = copy_launch_configuration(latest_config, ami_id)
    if not new_launch_config_name:
        return

    # Step 4: Update the Auto Scaling Group with the new Launch Configuration
    auto_scaling_group_name = 'FormTitan-auto-scale-group'  # Replace with your Auto Scaling Group name
    update_auto_scaling_group(auto_scaling_group_name, new_launch_config_name)

    # Step 5: Update the Launch Template with the new AMI
    launch_template_name = 'TitanServerPROD'  # Replace with your Launch Template name
    update_launch_template(launch_template_name, ami_id)


if __name__ == '__main__':
    main()
