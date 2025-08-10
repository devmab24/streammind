#!/bin/bash

# Railway Deployment Script for StreamMind
echo "🚀 Deploying StreamMind to Railway"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check if Railway CLI is installed
check_railway_cli() {
    if command -v railway &> /dev/null; then
        print_status "Railway CLI found"
        return 0
    else
        print_error "Railway CLI not found"
        print_info "Install from: https://docs.railway.app/develop/cli"
        print_info "Run: npm install -g @railway/cli"
        return 1
    fi
}

# Login to Railway
railway_login() {
    print_info "Checking Railway authentication..."
    if railway whoami &> /dev/null; then
        print_status "Already logged in to Railway"
    else
        print_info "Please log in to Railway..."
        railway login
    fi
}

# Create Railway project
create_railway_project() {
    local project_name=${1:-streammind}
    
    print_info "Creating Railway project: $project_name"
    
    if railway init "$project_name"; then
        print_status "Railway project created: $project_name"
        return 0
    else
        print_error "Failed to create Railway project"
        return 1
    fi
}

# Add Redis service
add_redis_service() {
    print_info "Adding Redis service..."
    
    # Add Redis plugin
    if railway add --plugin redis; then
        print_status "Redis service added"
        return 0
    else
        print_error "Failed to add Redis service"
        return 1
    fi
}

# Set environment variables
set_railway_env() {
    print_info "Setting environment variables..."
    
    # Set basic config
    railway variables set \
        ENVIRONMENT=production \
        DEBUG=false \
        DEMO_MODE=true \
        MOCK_DATA=true \
        LOG_LEVEL=INFO
    
    # The Redis URL will be automatically set by Railway
    
    # Set API keys if provided
    if [ ! -z "$OPENAI_API_KEY" ]; then
        railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
        print_status "OpenAI API key set"
    fi
    
    if [ ! -z "$HUGGINGFACE_API_KEY" ]; then
        railway variables set HUGGINGFACE_API_KEY="$HUGGINGFACE_API_KEY"
        print_status "HuggingFace API key set"
    fi
    
    print_status "Environment variables configured"
}

# Create railway.json config
create_railway_config() {
    print_info "Creating railway.json config..."
    
    cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port \$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    
    print_status "railway.json created"
}

# Deploy to Railway
deploy_railway() {
    print_info "Deploying to Railway..."
    
    # Initialize git if not already done
    if [ ! -d ".git" ]; then
        git init
        print_status "Git repository initialized"
    fi
    
    # Add all files
    git add .
    git commit -m "Deploy StreamMind to Railway" || true
    
    # Deploy
    if railway up; then
        print_status "Deployment initiated!"
        
        # Get deployment URL
        sleep 5
        DEPLOY_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")
        
        if [ ! -z "$DEPLOY_URL" ] && [ "$DEPLOY_URL" != "null" ]; then
            print_status "🎉 StreamMind deployed successfully!"
            print_info "App URL: $DEPLOY_URL"
        else
            print_status "🎉 Deployment successful!"
            print_info "Check Railway dashboard for your app URL"
        fi
        
        return 0
    else
        print_error "Deployment failed"
        return 1
    fi
}

# Wait for deployment
wait_for_deployment() {
    print_info "Waiting for deployment to be ready..."
    
    for i in {1..20}; do
        if railway status | grep -q "SUCCESS"; then
            print_status "Deployment is ready!"
            return 0
        fi
        print_info "Waiting... ($i/20)"
        sleep 15
    done
    
    print_warning "Deployment may still be in progress. Check Railway dashboard."
    return 0
}

# Main deployment function
main() {
    local project_name="$1"
    
    echo
    print_info "Starting Railway deployment..."
    echo
    
    # Check prerequisites
    if ! check_railway_cli; then
        exit 1
    fi
    
    # Login to Railway
    railway_login
    
    # Create config file
    create_railway_config
    
    # Create project
    if [ ! -z "$project_name" ]; then
        create_railway_project "$project_name"
    else
        create_railway_project
    fi
    
    # Add Redis and set environment
    add_redis_service
    set_railway_env
    
    # Deploy
    if deploy_railway; then
        wait_for_deployment
        
        echo
        print_status "🎉 Railway deployment completed!"
        print_info "View your project: railway open"
        print_info "View logs: railway logs"
        print_info "Check status: railway status"
        echo
    else
        print_error "Deployment failed. Check the logs above."
        exit 1
    fi
}

# Run main function with arguments
main "$@"