# Windows Server 2022 EC2 Deployment for emailer-simple-tool Testing

This deployment creates a modern Windows Server 2022 EC2 instance where PySide6 works perfectly, providing an alternative to the WorkSpaces environment for testing your emailer-simple-tool.

## 🎯 Why Windows Server 2022 EC2?

- ✅ **Modern Windows**: Full support for PySide6 and Python 3.12
- ✅ **RDP Access**: Connect graphically from your Mac
- ✅ **Internet Access**: Download and install software freely
- ✅ **Full Control**: Administrator access to install anything
- ✅ **Cost Effective**: Pay only when running (~$1-2/day)

## 📋 Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **EC2 Key Pair** in eu-west-1 region
3. **Microsoft Remote Desktop** app on your Mac (from App Store)

### Create EC2 Key Pair (if needed)

```bash
# Create new key pair
aws ec2 create-key-pair \
    --key-name emailer-windows-key \
    --query 'KeyMaterial' \
    --output text > ~/.ssh/emailer-windows-key.pem

# Set correct permissions
chmod 400 ~/.ssh/emailer-windows-key.pem
```

## 🚀 Quick Deployment

```bash
# Deploy the Windows Server 2022 instance
./deploy-windows-ec2.sh
```

The script will:
1. ✅ Detect your public IP for secure RDP access
2. ✅ Create VPC, subnets, and security groups
3. ✅ Launch Windows Server 2022 instance
4. ✅ Install Python 3.12, Chrome, and useful tools
5. ✅ Provide RDP connection details and Administrator password

## 🖥️ Connecting to Your Windows Instance

### Option 1: Microsoft Remote Desktop (Recommended)

1. **Install** Microsoft Remote Desktop from Mac App Store
2. **Open** the app and click "Add PC"
3. **Enter** the public IP provided by the deployment script
4. **Username**: `Administrator`
5. **Password**: Provided by the deployment script

### Option 2: Built-in RDP Client

```bash
# Use the public IP from deployment output
open rdp://YOUR_PUBLIC_IP
```

## 🛠️ Setting Up emailer-simple-tool

Once connected to your Windows instance:

### 1. Open PowerShell as Administrator

### 2. Install your tool with PySide6 support

```powershell
# Install emailer-simple-tool with GUI support
pip install emailer-simple-tool[gui]

# Verify PySide6 is installed
python -c "import PySide6; print('✅ PySide6 available')"
```

### 3. Test the GUI

```powershell
# Launch the GUI - should work perfectly!
emailer-simple-tool gui
```

### 4. Install additional tools (optional)

```powershell
# Git for version control
choco install -y git

# Visual Studio Code
choco install -y vscode

# Python development tools
pip install jupyter ipython
```

## 💰 Cost Management

### Estimated Costs (eu-west-1)

| Instance Type | vCPU | RAM | Cost/Hour | Cost/Day (8h) | Cost/Month (24/7) |
|---------------|------|-----|-----------|---------------|-------------------|
| t3.small      | 2    | 2GB | $0.0208   | $0.17         | $15               |
| t3.medium     | 2    | 4GB | $0.0416   | $0.33         | $30               |
| t3.large      | 2    | 8GB | $0.0832   | $0.67         | $60               |

**Additional costs:**
- EBS Storage (50GB): ~$4/month
- Data Transfer: ~$1-5/month

### 💡 Cost Optimization Tips

#### Stop Instance When Not Using
```bash
# Stop instance (keeps EBS, stops compute charges)
aws ec2 stop-instances --instance-ids i-1234567890abcdef0 --region eu-west-1

# Start when needed
aws ec2 start-instances --instance-ids i-1234567890abcdef0 --region eu-west-1

# Get current status
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --region eu-west-1 --query 'Reservations[0].Instances[0].State.Name'
```

#### Automatic Scheduling (Optional)
Set up CloudWatch Events to automatically stop/start on schedule:

```bash
# Stop every day at 6 PM UTC
aws events put-rule --name "stop-windows-instance" --schedule-expression "cron(0 18 * * ? *)"

# Start every day at 8 AM UTC  
aws events put-rule --name "start-windows-instance" --schedule-expression "cron(0 8 * * ? *)"
```

## 🔧 Instance Management

### Get Instance Information

```bash
# Get instance details
aws cloudformation describe-stacks \
    --stack-name emailer-windows-server-2022 \
    --region eu-west-1 \
    --query 'Stacks[0].Outputs'

# Get current public IP (changes after stop/start)
aws ec2 describe-instances \
    --instance-ids YOUR_INSTANCE_ID \
    --region eu-west-1 \
    --query 'Reservations[0].Instances[0].PublicIpAddress'
```

### Retrieve Administrator Password

```bash
# If you need to get the password again
aws ec2 get-password-data \
    --instance-id YOUR_INSTANCE_ID \
    --priv-launch-key ~/.ssh/emailer-windows-key.pem \
    --region eu-west-1
```

### Security Group Management

```bash
# Update allowed IP for RDP access
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 3389 \
    --cidr YOUR_NEW_IP/32
```

## 🗑️ Cleanup

When you're done testing:

```bash
# Delete entire stack and stop all charges
./cleanup-windows-ec2.sh
```

This will delete:
- ✅ EC2 Instance
- ✅ VPC and networking
- ✅ Security groups
- ✅ EBS volumes
- ✅ All associated resources

## 🔍 Troubleshooting

### Can't Connect via RDP

1. **Check Security Group**: Ensure your IP is allowed on port 3389
2. **Check Instance State**: Must be "running"
3. **Check Public IP**: Changes after stop/start
4. **Firewall**: Ensure your network allows outbound RDP (port 3389)

### Password Issues

1. **Wait**: Password generation takes 5-10 minutes after launch
2. **Key Pair**: Ensure you have the correct private key file
3. **Permissions**: Private key must have 400 permissions

### Performance Issues

1. **Instance Type**: Upgrade to t3.medium or larger for better GUI performance
2. **EBS**: Consider upgrading to gp3 with higher IOPS
3. **Network**: Ensure good internet connection for RDP

## 🆚 Comparison: WorkSpaces vs EC2

| Feature | WorkSpaces | EC2 Windows 2022 |
|---------|------------|------------------|
| **OS** | Windows Server 2016 | Windows Server 2022 |
| **PySide6 Support** | ❌ (DLL issues) | ✅ Full support |
| **Cost (8h/day)** | $25-35/month | $15-30/month |
| **Setup Time** | 10-15 minutes | 5-10 minutes |
| **Flexibility** | Limited | Full admin access |
| **Internet Access** | ✅ | ✅ |
| **Persistence** | ✅ Always on | ⚠️ Manual start/stop |

## 🎯 Recommended Workflow

1. **Deploy** EC2 instance when you need to test
2. **Develop/Test** your emailer-simple-tool with full PySide6 support
3. **Stop** instance when done for the day
4. **Start** again when needed (IP may change)
5. **Cleanup** completely when project is finished

This gives you a modern Windows environment with full PySide6 support at a fraction of the cost of keeping WorkSpaces running 24/7!
