#!/bin/bash

# Cleanup Simple WorkSpaces Test Environment
# Removes WorkSpace and Simple AD to stop all charges

set -e

STACK_NAME="simple-workspaces-test"
REGION="eu-west-1"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🗑️  Simple WorkSpaces Cleanup${NC}"
echo "============================="
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found.${NC}"
    exit 1
fi

# Check credentials
if ! aws sts get-caller-identity --region $REGION &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured.${NC}"
    exit 1
fi

# Check if stack exists
if ! aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Stack '$STACK_NAME' not found.${NC}"
    echo "Nothing to clean up."
    exit 0
fi

# Get Directory ID
DIRECTORY_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`DirectoryId`].OutputValue' \
    --output text 2>/dev/null || echo "N/A")

# Find WorkSpaces
if [ "$DIRECTORY_ID" != "N/A" ]; then
    WORKSPACES=$(aws workspaces describe-workspaces \
        --region "$REGION" \
        --query "Workspaces[?DirectoryId=='$DIRECTORY_ID'].WorkspaceId" \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$WORKSPACES" ] && [ "$WORKSPACES" != "None" ]; then
        echo -e "${YELLOW}💻 Found WorkSpaces: $WORKSPACES${NC}"
    fi
fi

echo ""
echo -e "${RED}⚠️  WARNING: This will delete:${NC}"
if [ -n "$WORKSPACES" ] && [ "$WORKSPACES" != "None" ]; then
    echo "• WorkSpace(s): $WORKSPACES"
fi
echo "• Simple AD directory"
echo "• VPC and networking"
echo "• All test data"
echo ""

read -p "Delete everything? (type 'DELETE' to confirm): " CONFIRM
if [ "$CONFIRM" != "DELETE" ]; then
    echo -e "${YELLOW}⏹️  Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🗑️  Starting cleanup...${NC}"

# Terminate WorkSpaces
if [ -n "$WORKSPACES" ] && [ "$WORKSPACES" != "None" ]; then
    echo "1. Terminating WorkSpaces..."
    for workspace_id in $WORKSPACES; do
        aws workspaces terminate-workspaces \
            --terminate-workspace-requests WorkspaceId="$workspace_id" \
            --region "$REGION" || echo "   Failed to terminate $workspace_id"
    done
    
    echo "   Waiting for termination..."
    sleep 30
fi

# Deregister directory
if [ "$DIRECTORY_ID" != "N/A" ]; then
    echo "2. Deregistering directory..."
    aws workspaces deregister-workspace-directory \
        --directory-id "$DIRECTORY_ID" \
        --region "$REGION" 2>/dev/null || echo "   Already deregistered"
    sleep 10
fi

# Delete CloudFormation stack
echo "3. Deleting infrastructure..."
aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$REGION"

echo ""
echo -e "${YELLOW}⏳ Monitoring deletion (5-10 minutes)...${NC}"

# Monitor deletion
while true; do
    STATUS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null || echo "STACK_NOT_FOUND")
    
    if [ "$STATUS" = "STACK_NOT_FOUND" ]; then
        echo -e "${GREEN}✅ Cleanup completed!${NC}"
        break
    elif [ "$STATUS" = "DELETE_FAILED" ]; then
        echo -e "${RED}❌ Deletion failed. Check AWS console.${NC}"
        exit 1
    else
        echo -e "${YELLOW}⏳ Status: $STATUS${NC}"
        sleep 30
    fi
done

# Clean up local files
rm -f workspace-connection.txt

echo ""
echo -e "${GREEN}🎉 All resources deleted!${NC}"
echo "========================"
echo ""
echo -e "${GREEN}💰 You will no longer be charged for:${NC}"
echo "• WorkSpace compute time"
echo "• Simple AD directory"
echo "• VPC resources"
echo ""
echo -e "${BLUE}📊 Final charges may appear for time resources were active.${NC}"
echo -e "${GREEN}✨ Test environment cleanup complete!${NC}"
