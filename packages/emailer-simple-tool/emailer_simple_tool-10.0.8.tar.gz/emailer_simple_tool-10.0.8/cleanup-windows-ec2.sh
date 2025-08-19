#!/bin/bash

# Cleanup Windows Server 2022 EC2 stack to avoid ongoing charges
# This deletes the entire CloudFormation stack and all associated resources

set -e

# Configuration
STACK_NAME="emailer-windows-server-2022"
REGION="eu-west-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🗑️  Cleaning up Windows Server 2022 EC2 stack${NC}"
echo "=============================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Check if stack exists
if ! aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Stack '$STACK_NAME' not found in region '$REGION'${NC}"
    echo -e "${GREEN}✅ Nothing to clean up!${NC}"
    exit 0
fi

# Get stack information
echo -e "${BLUE}📋 Getting stack information...${NC}"

INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -n "$INSTANCE_ID" ]; then
    echo -e "${YELLOW}🖥️  Instance ID: $INSTANCE_ID${NC}"
    
    # Get instance state
    INSTANCE_STATE=$(aws ec2 describe-instances \
        --instance-ids "$INSTANCE_ID" \
        --region "$REGION" \
        --query 'Reservations[0].Instances[0].State.Name' \
        --output text 2>/dev/null || echo "unknown")
    
    echo -e "${YELLOW}📊 Instance State: $INSTANCE_STATE${NC}"
fi

# Confirmation prompt
echo ""
echo -e "${RED}⚠️  WARNING: This will DELETE the entire Windows Server 2022 stack!${NC}"
echo -e "${YELLOW}📋 Resources to be deleted:${NC}"
echo "   - EC2 Instance ($INSTANCE_ID)"
echo "   - VPC and networking components"
echo "   - Security Groups"
echo "   - EBS volumes"
echo "   - All associated resources"
echo ""
echo -e "${GREEN}💰 This will STOP all charges for this stack.${NC}"
echo ""

read -p "❓ Are you sure you want to delete the stack? (type 'yes' to confirm): " CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo -e "${YELLOW}❌ Cleanup cancelled.${NC}"
    exit 0
fi

# Delete the stack
echo ""
echo -e "${RED}🗑️  Deleting CloudFormation stack...${NC}"

aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$REGION"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Stack deletion initiated!${NC}"
    
    # Wait for deletion to complete
    echo -e "${YELLOW}⏳ Waiting for stack deletion to complete...${NC}"
    echo -e "${BLUE}💡 This may take 5-10 minutes...${NC}"
    
    aws cloudformation wait stack-delete-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Stack deleted successfully!${NC}"
        echo ""
        echo -e "${GREEN}💰 All resources have been deleted and charges stopped.${NC}"
        echo -e "${BLUE}📊 You can verify in the AWS Console that all resources are gone.${NC}"
    else
        echo -e "${RED}❌ Stack deletion may have failed or is still in progress.${NC}"
        echo -e "${YELLOW}💡 Check the CloudFormation console for details.${NC}"
    fi
    
else
    echo -e "${RED}❌ Failed to initiate stack deletion!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🎯 CLEANUP COMPLETE${NC}"
echo "=================="
echo -e "${GREEN}✅ Windows Server 2022 stack has been deleted${NC}"
echo -e "${GREEN}✅ All charges for this stack have stopped${NC}"
echo -e "${BLUE}💡 You can redeploy anytime with: ./deploy-windows-ec2.sh${NC}"
