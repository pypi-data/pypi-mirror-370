#!/bin/bash

# Simple WorkSpaces with Simple AD - Minimal Setup for Testing
# Simple AD is FREE when used with WorkSpaces!

set -e

STACK_NAME="simple-workspaces-test"
REGION="eu-west-1"
TEMPLATE="simple-workspaces.yaml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Simple WorkSpaces Test Setup${NC}"
echo "================================"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check credentials
if ! aws sts get-caller-identity --region $REGION &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured.${NC}"
    exit 1
fi

# Get username
read -p "Enter username for WorkSpace (default: testuser): " USERNAME
USERNAME=${USERNAME:-testuser}

echo ""
echo -e "${YELLOW}📦 Deploying infrastructure (VPC + Simple AD)...${NC}"

# Deploy CloudFormation
aws cloudformation deploy \
    --template-file "$TEMPLATE" \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --parameter-overrides UserName="$USERNAME" \
    --capabilities CAPABILITY_IAM

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Infrastructure ready!${NC}"
    
    # Get outputs
    DIRECTORY_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`DirectoryId`].OutputValue' \
        --output text)
    
    SUBNETS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`SubnetIds`].OutputValue' \
        --output text)
    
    ALIAS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`DirectoryAlias`].OutputValue' \
        --output text)
    
    echo ""
    echo -e "${YELLOW}🔧 Setting up WorkSpaces...${NC}"
    
    # Register directory
    echo "1. Registering directory with WorkSpaces..."
    aws workspaces register-workspace-directory \
        --directory-id "$DIRECTORY_ID" \
        --subnet-ids $(echo $SUBNETS | tr ',' ' ') \
        --enable-internet-access \
        --region "$REGION" 2>/dev/null || echo "   (Already registered)"
    
    sleep 5
    
    # Create user
    echo "2. Creating user in Simple AD..."
    aws ds create-user \
        --directory-id "$DIRECTORY_ID" \
        --user-name "$USERNAME" \
        --password "UserPass123!" \
        --given-name "Test" \
        --surname "User" \
        --region "$REGION" 2>/dev/null || echo "   (User may already exist)"
    
    # Create WorkSpace
    echo "3. Creating WorkSpace (this takes 10-15 minutes)..."
    WORKSPACE_RESULT=$(aws workspaces create-workspaces \
        --workspaces "DirectoryId=$DIRECTORY_ID,UserName=$USERNAME,BundleId=wsb-bh8rsxt14,WorkspaceProperties={RunningMode=AUTO_STOP,RunningModeAutoStopTimeoutInMinutes=60,RootVolumeSizeGib=80,UserVolumeSizeGib=10,ComputeTypeName=VALUE}" \
        --region "$REGION" \
        --output json)
    
    if [ $? -eq 0 ]; then
        WORKSPACE_ID=$(echo "$WORKSPACE_RESULT" | jq -r '.PendingRequests[0].WorkspaceId // "unknown"')
        
        echo ""
        echo -e "${GREEN}🎉 WorkSpace creation started!${NC}"
        echo "============================="
        echo ""
        echo -e "${YELLOW}📱 Connection Info:${NC}"
        echo "WorkSpace ID: $WORKSPACE_ID"
        echo "Registration Code: $ALIAS"
        echo "Username: $USERNAME"
        echo "Password: UserPass123!"
        echo ""
        echo -e "${YELLOW}🔗 How to Connect:${NC}"
        echo "1. Download WorkSpaces client: https://clients.amazonworkspaces.com/"
        echo "2. Install and launch the client"
        echo "3. Enter registration code: $ALIAS"
        echo "4. Login with: $USERNAME / UserPass123!"
        echo ""
        echo -e "${YELLOW}⏳ WorkSpace Status: Creating (10-15 minutes)${NC}"
        echo ""
        echo "Check status with:"
        echo "aws workspaces describe-workspaces --workspace-ids $WORKSPACE_ID --region $REGION"
        echo ""
        echo -e "${YELLOW}🧪 Testing Your Emailer Tool:${NC}"
        echo "1. Connect to WorkSpace"
        echo "2. Open PowerShell as Administrator"
        echo "3. Install Python: winget install Python.Python.3.12"
        echo "4. Install your tool: pip install emailer-simple-tool[gui]"
        echo "5. Launch GUI: emailer-simple-tool gui"
        echo ""
        echo -e "${GREEN}💰 Cost: ~\$25-35/month (Simple AD is FREE with WorkSpaces!)${NC}"
        echo -e "${YELLOW}🗑️  Cleanup when done: ./cleanup-simple.sh${NC}"
        
        # Save connection info to file
        cat > workspace-connection.txt << EOF
WorkSpace Connection Information
===============================

Registration Code: $ALIAS
Username: $USERNAME
Password: UserPass123!
WorkSpace ID: $WORKSPACE_ID

Download client: https://clients.amazonworkspaces.com/

To test your emailer-simple-tool:
1. Connect to WorkSpace
2. Install Python: winget install Python.Python.3.12
3. Install tool: pip install emailer-simple-tool[gui]
4. Run: emailer-simple-tool gui

Cleanup: ./cleanup-simple.sh
EOF
        
        echo ""
        echo -e "${GREEN}📄 Connection info saved to: workspace-connection.txt${NC}"
        
    else
        echo -e "${RED}❌ WorkSpace creation failed${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Infrastructure deployment failed${NC}"
    exit 1
fi
