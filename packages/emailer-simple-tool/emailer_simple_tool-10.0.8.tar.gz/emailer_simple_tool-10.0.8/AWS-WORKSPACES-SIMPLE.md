# AWS WorkSpaces Simple Testing Environment

This directory contains a streamlined setup to deploy a cost-effective AWS WorkSpaces Windows 10 desktop for testing the emailer-simple-tool software.

## 🎯 Purpose

Deploy a Windows 10 desktop environment in AWS to test your emailer-simple-tool software on Windows without needing a local Windows machine.

## 💰 Cost Optimization - Simple Approach

This setup uses the simplest possible configuration:
- **Region**: EU-West-1 (Ireland) - typically cheapest in Europe
- **Directory**: Simple AD Small - **FREE when used with WorkSpaces!**
- **Bundle**: Value bundle - cheapest Windows 10 option
- **Running Mode**: AUTO_STOP - stops after 60 minutes of inactivity
- **Storage**: Minimum volumes (80GB root, 10GB user)

**Estimated Monthly Cost**: ~$25-35 USD
- WorkSpace (Value bundle, AUTO_STOP): ~$25-35/month
- Simple AD (Small): **FREE** (when used with WorkSpaces)
- Data transfer: minimal for testing

**💡 Key Benefit**: Simple AD is completely FREE when used with WorkSpaces, making this much cheaper than the original $62-76/month estimate!

## 📁 Files

- `simple-workspaces.yaml` - CloudFormation template (Simple AD + VPC)
- `deploy-simple.sh` - One-command deployment script
- `cleanup-simple.sh` - One-command cleanup script
- `AWS-WORKSPACES-SIMPLE.md` - This documentation

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   # Install AWS CLI (if not already installed)
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Configure credentials
   aws configure
   ```

2. **AWS Account with appropriate permissions**
   - WorkSpaces permissions
   - CloudFormation permissions
   - EC2 and VPC permissions
   - Directory Service permissions

3. **jq installed** (for JSON parsing)
   ```bash
   # macOS
   brew install jq
   
   # Linux
   sudo apt-get install jq  # or yum install jq
   ```

### Deploy WorkSpaces Environment

1. **Run the deployment script**
   ```bash
   ./deploy-simple.sh
   ```

2. **Provide username when prompted**
   - Default: `testuser`
   - Or enter your preferred username

3. **Wait for deployment** (typically 15-20 minutes)
   - Infrastructure creation: ~5 minutes
   - WorkSpace provisioning: ~10-15 minutes

### Connect to WorkSpace

1. **Download WorkSpaces Client**
   - Visit: https://clients.amazonworkspaces.com/
   - Download for your platform (Windows, Mac, Linux)

2. **Connect using provided credentials**
   - Registration code (provided after deployment)
   - Username and password (provided after deployment)
   - Connection info also saved to `workspace-connection.txt`

### Test Your Software

1. **Install Python on WorkSpace**
   ```powershell
   # Option 1: Using winget (recommended)
   winget install Python.Python.3.12
   
   # Option 2: Download from python.org
   # Visit https://python.org and download installer
   ```

2. **Install your emailer-simple-tool**
   ```powershell
   pip install emailer-simple-tool[gui]
   ```

3. **Test the application**
   ```powershell
   emailer-simple-tool gui
   ```

### Cleanup When Done

**Important**: Always cleanup to avoid ongoing charges!

```bash
./cleanup-simple.sh
```

## 🔧 Manual Deployment (Alternative)

If you prefer to deploy manually:

```bash
# 1. Deploy infrastructure
aws cloudformation deploy \
    --template-file simple-workspaces.yaml \
    --stack-name simple-workspaces-test \
    --region eu-west-1 \
    --parameter-overrides UserName=testuser \
    --capabilities CAPABILITY_IAM

# 2. Get outputs
DIRECTORY_ID=$(aws cloudformation describe-stacks \
    --stack-name simple-workspaces-test \
    --region eu-west-1 \
    --query 'Stacks[0].Outputs[?OutputKey==`DirectoryId`].OutputValue' \
    --output text)

SUBNETS=$(aws cloudformation describe-stacks \
    --stack-name simple-workspaces-test \
    --region eu-west-1 \
    --query 'Stacks[0].Outputs[?OutputKey==`SubnetIds`].OutputValue' \
    --output text)

# 3. Register directory with WorkSpaces
aws workspaces register-workspace-directory \
    --directory-id $DIRECTORY_ID \
    --subnet-ids $(echo $SUBNETS | tr ',' ' ') \
    --enable-internet-access \
    --region eu-west-1

# 4. Create user
aws ds create-user \
    --directory-id $DIRECTORY_ID \
    --user-name testuser \
    --password "UserPass123!" \
    --given-name "Test" \
    --surname "User" \
    --region eu-west-1

# 5. Create WorkSpace
aws workspaces create-workspaces \
    --workspaces "DirectoryId=$DIRECTORY_ID,UserName=testuser,BundleId=wsb-bh8rsxt14,WorkspaceProperties={RunningMode=AUTO_STOP,RunningModeAutoStopTimeoutInMinutes=60,RootVolumeSizeGib=80,UserVolumeSizeGib=10,ComputeTypeName=VALUE}" \
    --region eu-west-1
```

## 📊 What Gets Created

### Network Infrastructure
- **VPC** with public subnets in 2 AZs
- **Internet Gateway** for public access
- **Route Tables** and basic networking

### Directory Service
- **Simple AD** (Small) - **FREE when used with WorkSpaces**
- **Domain**: test.local
- **User account** with provided credentials

### WorkSpace
- **Windows 10** with Value bundle (cheapest option)
- **AUTO_STOP** mode for cost savings (stops after 60 minutes)
- **Minimum storage** (80GB root, 10GB user)
- **Internet access** enabled for software downloads

## 🛡️ Security Considerations

### Default Security
- WorkSpace has internet access (required for testing email functionality)
- Simple AD with basic security
- Default Windows 10 security settings
- User account with standard permissions

### For Production Use
- Use AWS Managed Microsoft AD for production
- Implement proper security groups and NACLs
- Enable CloudTrail and monitoring
- Use stronger passwords and MFA
- Restrict internet access as needed

## 🔍 Troubleshooting

### Common Issues

1. **Deployment Fails**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity --region eu-west-1
   
   # Check CloudFormation events
   aws cloudformation describe-stack-events \
       --stack-name simple-workspaces-test \
       --region eu-west-1
   ```

2. **Cannot Connect to WorkSpace**
   - Verify registration code and credentials in `workspace-connection.txt`
   - Check WorkSpace status: should be "AVAILABLE"
   - Ensure WorkSpace client is latest version
   - Check network connectivity

3. **WorkSpace Performance Issues**
   - Value bundle has limited resources (1 vCPU, 2GB RAM)
   - Consider upgrading to Standard bundle if needed
   - Check network latency to EU-West-1

4. **User Login Issues**
   - Password: `UserPass123!` (case sensitive)
   - Username: as specified during deployment
   - Try waiting 5-10 minutes after WorkSpace shows "AVAILABLE"

### Getting Help

1. **Check WorkSpace Status**
   ```bash
   aws workspaces describe-workspaces --region eu-west-1
   ```

2. **Check Directory Status**
   ```bash
   aws ds describe-directories --region eu-west-1
   ```

3. **AWS Console**
   - CloudFormation: https://console.aws.amazon.com/cloudformation/
   - WorkSpaces: https://console.aws.amazon.com/workspaces/
   - Directory Service: https://console.aws.amazon.com/directoryservicev2/

## 💡 Cost Optimization Tips

### Minimize Costs
1. **Use AUTO_STOP mode** - WorkSpace stops when inactive
2. **Set short timeout** - 60 minutes (minimum allowed)
3. **Delete when not needed** - use cleanup script regularly
4. **Monitor usage** - check AWS billing dashboard

### Usage Patterns
- **Short testing sessions**: Perfect for this setup
- **Daily development**: Consider ALWAYS_ON mode
- **Occasional testing**: AUTO_STOP is ideal

## 📋 Testing Checklist

### Before Deployment
- [ ] AWS CLI installed and configured
- [ ] Appropriate AWS permissions verified
- [ ] Understanding of estimated costs (~$25-35/month)
- [ ] jq installed for JSON parsing

### After Deployment
- [ ] WorkSpace client downloaded and installed
- [ ] Successfully connected to WorkSpace
- [ ] Python installed on WorkSpace
- [ ] Emailer-simple-tool installed and tested
- [ ] Connection info saved locally

### Testing Your Software
- [ ] GUI launches successfully
- [ ] Can create campaigns
- [ ] Can configure SMTP settings
- [ ] Can send test emails
- [ ] Picture generator works (if used)
- [ ] All features work as expected on Windows

### Before Cleanup
- [ ] All important data backed up from WorkSpace
- [ ] Testing completed successfully
- [ ] Ready to delete all resources
- [ ] No ongoing work in progress

### After Cleanup
- [ ] Stack deletion confirmed in AWS console
- [ ] No ongoing charges verified in billing
- [ ] All resources removed
- [ ] Local connection files cleaned up

## 🔗 Useful Links

- [AWS WorkSpaces Documentation](https://docs.aws.amazon.com/workspaces/)
- [WorkSpaces Client Downloads](https://clients.amazonworkspaces.com/)
- [AWS Pricing Calculator](https://calculator.aws/)
- [Simple AD Documentation](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_simple_ad.html)

## 🎯 Testing Your Emailer Tool

### Installation Steps
1. Connect to WorkSpace
2. Open PowerShell as Administrator
3. Install Python: `winget install Python.Python.3.12`
4. Restart PowerShell to refresh PATH
5. Install your tool: `pip install emailer-simple-tool[gui]`
6. Launch GUI: `emailer-simple-tool gui`

### What to Test
- **GUI Functionality**: All tabs and features
- **Campaign Creation**: Create test campaigns
- **SMTP Configuration**: Test email settings
- **Picture Generator**: Create personalized images
- **Email Sending**: Send test emails (dry run first)
- **File Operations**: Import/export functionality
- **Windows-Specific**: File paths, fonts, etc.

### Performance Notes
- Value bundle: 1 vCPU, 2GB RAM, 80GB storage
- Suitable for GUI testing and light development
- May be slower for large campaigns or complex operations
- Upgrade to Standard bundle if needed

---

**Note**: This setup is optimized for testing purposes. The Simple AD directory is completely FREE when used with WorkSpaces, making this the most cost-effective way to get a Windows environment for testing your software.

**Total Cost**: ~$25-35/month for the WorkSpace only!
