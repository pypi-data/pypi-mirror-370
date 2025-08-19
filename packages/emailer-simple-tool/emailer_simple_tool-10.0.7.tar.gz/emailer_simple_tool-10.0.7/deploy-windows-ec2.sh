#!/bin/bash

# Deploy Windows Server 2022 EC2 instance for emailer-simple-tool testing
# This creates a modern Windows environment where PySide6 works perfectly
# NO KEY PAIR REQUIRED - uses password authentication

set -e

# Configuration
STACK_NAME="emailer-windows-server-2022"
REGION="eu-west-1"
TEMPLATE_FILE="ec2-windows-2022.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Windows Server 2022 EC2 instance for emailer-simple-tool testing${NC}"
echo -e "${GREEN}✅ No Key Pair required - using password authentication${NC}"
echo "=================================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Get current AWS identity
CURRENT_USER=$(aws sts get-caller-identity --query 'Arn' --output text)
echo -e "${GREEN}✅ AWS Identity: ${CURRENT_USER}${NC}"

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}❌ Template file $TEMPLATE_FILE not found!${NC}"
    exit 1
fi

# Get current public IP for RDP access
echo -e "${YELLOW}🌐 Getting your current public IP for RDP access...${NC}"
CURRENT_IP=$(curl -s https://checkip.amazonaws.com || curl -s https://ipinfo.io/ip || echo "")

if [ -n "$CURRENT_IP" ]; then
    ALLOWED_CIDR="${CURRENT_IP}/32"
    echo -e "${GREEN}✅ Your public IP: $CURRENT_IP${NC}"
    echo -e "${YELLOW}🔒 RDP access will be restricted to: $ALLOWED_CIDR${NC}"
else
    echo -e "${YELLOW}⚠️  Could not detect your public IP. Using 0.0.0.0/0 (less secure)${NC}"
    ALLOWED_CIDR="0.0.0.0/0"
fi

# Prompt for instance type
echo ""
echo -e "${YELLOW}💻 Available instance types:${NC}"
echo "  t3.small   - 2 vCPU, 2GB RAM   (~$15/month)"
echo "  t3.medium  - 2 vCPU, 4GB RAM   (~$30/month) [RECOMMENDED]"
echo "  t3.large   - 2 vCPU, 8GB RAM   (~$60/month)"
echo "  m5.large   - 2 vCPU, 8GB RAM   (~$70/month)"

read -p "🖥️  Enter instance type [t3.medium]: " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.medium}

# Prompt for Administrator password
echo ""
echo -e "${YELLOW}🔑 Set Administrator password for RDP access:${NC}"
echo -e "${BLUE}💡 Requirements: 8-41 characters, letters, numbers, and special characters${NC}"
read -s -p "🔒 Enter Administrator password [TempPass123!]: " ADMIN_PASSWORD
echo ""
ADMIN_PASSWORD=${ADMIN_PASSWORD:-TempPass123!}

# Validate password length
if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
    echo -e "${RED}❌ Password must be at least 8 characters long!${NC}"
    exit 1
fi

# Deploy the stack
echo ""
echo -e "${BLUE}🚀 Deploying CloudFormation stack...${NC}"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Allowed CIDR: $ALLOWED_CIDR"
echo "Password: [HIDDEN]"

aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --parameter-overrides \
        InstanceType="$INSTANCE_TYPE" \
        AllowedCIDR="$ALLOWED_CIDR" \
        AdminPassword="$ADMIN_PASSWORD" \
    --capabilities CAPABILITY_IAM \
    --tags \
        Project=emailer-simple-tool \
        Environment=testing \
        Owner="$(whoami)" \
        CreatedBy=deploy-script

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Stack deployed successfully!${NC}"
    
    # Get outputs
    echo ""
    echo -e "${BLUE}📋 Getting stack outputs...${NC}"
    
    INSTANCE_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
        --output text)
    
    PUBLIC_IP=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \
        --output text)
    
    PUBLIC_DNS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PublicDNS`].OutputValue' \
        --output text)
    
    echo -e "${GREEN}✅ Instance ID: $INSTANCE_ID${NC}"
    echo -e "${GREEN}✅ Public IP: $PUBLIC_IP${NC}"
    echo -e "${GREEN}✅ Public DNS: $PUBLIC_DNS${NC}"
    
    # Wait for instance to be running
    echo ""
    echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
    aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"
    echo -e "${GREEN}✅ Instance is now running!${NC}"
    
    # Wait for user data to complete
    echo -e "${YELLOW}⏳ Waiting for Windows setup to complete (this may take 5-10 minutes)...${NC}"
    sleep 120  # Give Windows time to boot and run user data
    
    # Connection instructions
    echo ""
    echo -e "${BLUE}🖥️  RDP CONNECTION INSTRUCTIONS${NC}"
    echo "=================================="
    echo -e "${GREEN}Server: $PUBLIC_IP:3389${NC}"
    echo -e "${GREEN}Username: Administrator${NC}"
    echo -e "${GREEN}Password: $ADMIN_PASSWORD${NC}"
    echo ""
    echo -e "${YELLOW}📱 Connection Methods:${NC}"
    echo -e "${GREEN}1. Microsoft Remote Desktop (Mac App Store)${NC}"
    echo "   - Open Microsoft Remote Desktop"
    echo "   - Click 'Add PC'"
    echo "   - Enter PC name: $PUBLIC_IP"
    echo "   - Username: Administrator"
    echo "   - Password: $ADMIN_PASSWORD"
    echo ""
    echo -e "${GREEN}2. Built-in RDP client:${NC}"
    echo "   open rdp://$PUBLIC_IP"
    echo ""
    echo -e "${GREEN}3. AWS Systems Manager (command line):${NC}"
    echo "   aws ssm start-session --target $INSTANCE_ID --region $REGION"
    
    # Software information
    echo ""
    echo -e "${BLUE}📦 PRE-INSTALLED SOFTWARE${NC}"
    echo "========================="
    echo -e "${GREEN}✅ Python 3.12 (latest)${NC}"
    echo -e "${GREEN}✅ Google Chrome${NC}"
    echo -e "${GREEN}✅ 7-Zip${NC}"
    echo -e "${GREEN}✅ Notepad++${NC}"
    echo -e "${GREEN}✅ Chocolatey package manager${NC}"
    
    # Cost reminder
    echo ""
    echo -e "${RED}💰 COST REMINDER${NC}"
    echo "================"
    echo -e "${YELLOW}⚠️  This instance costs ~$30-54/month if running 24/7${NC}"
    echo -e "${GREEN}💡 STOP when not using: aws ec2 stop-instances --instance-ids $INSTANCE_ID --region $REGION${NC}"
    echo -e "${GREEN}💡 START when needed: aws ec2 start-instances --instance-ids $INSTANCE_ID --region $REGION${NC}"
    
    # Next steps
    echo ""
    echo -e "${BLUE}🎯 NEXT STEPS${NC}"
    echo "============="
    echo -e "${GREEN}1. Connect via RDP using the instructions above${NC}"
    echo -e "${GREEN}2. Open PowerShell as Administrator${NC}"
    echo -e "${GREEN}3. Install your tool: pip install emailer-simple-tool[gui]${NC}"
    echo -e "${GREEN}4. Test the GUI: emailer-simple-tool gui${NC}"
    echo -e "${GREEN}5. PySide6 should work perfectly on Windows Server 2022!${NC}"
    echo ""
    echo -e "${YELLOW}💡 A README.txt file with this info is on the desktop${NC}"
    
else
    echo -e "${RED}❌ Stack deployment failed!${NC}"
    exit 1
fi
