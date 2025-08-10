#!/bin/bash

# Heroku Deployment Script for StreamMind
echo "🚀 Deploying StreamMind to Heroku"
echo "================================="

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

# Check if Heroku CLI is installed
check_heroku_cli() {
    if command -v heroku &> /dev/null; then
        print_status "Heroku CLI found"
        return 0
    else
        print_error "Heroku CLI not found"
        print_info "Install from: https://devcenter.heroku.com/articles/heroku-cli"
        return 1
    fi
}

# Login to Heroku
heroku_login() {
    print_info "Checking Heroku authentication..."
    if heroku auth:whoami &> /dev/null; then
        print_status "Already logged in to Heroku"
    else
        print_info "Please log in to Heroku..."
        heroku login
    fi
}

# Create Heroku app
create_heroku_app() {
    local app_name=${1:-streammind-$(date +%s)}
    
    print_info "Creating Heroku app: $app_name"
    
    if heroku create "$app_name"; then
        print_status "Heroku app created: $app_name"
        echo "$app_name" > .heroku-app-name
        return 0
    else
        print_error "Failed to create Heroku app"
        return 1
    fi
}

# Add Heroku Redis addon
add_redis_addon() {
    local app_name=$(cat .heroku-app-name 2>/dev/null)
    
    if [ -z "$app_name" ]; then
        print_error "No Heroku app found"
        return 1
    fi
    
    print_info "Adding Redis addon..."
    
    # Add Heroku Redis (free plan)
    if heroku addons:create heroku-redis:mini -a "$app_name"; then
        print_status "Redis addon added"
        
        # Get Redis URL and set as environment variable
        REDIS_URL=$(heroku config:get REDIS_URL -a "$app_name")
        heroku config:set REDIS_URL="$REDIS_URL" -a "$app_name"
        
        return 0
    else
        print_error "Failed to add Redis addon"
        return 1
    fi
}

# Set environment variables
set_env_vars() {
    local app_name=$(cat .heroku-app-name 2>/dev/null)
    
    if [ -z "$app_name" ]; then
        print_error "No Heroku app found"
        return 1
    fi
    
    print_info "Setting environment variables..."
    
    # Set basic config
    heroku config:set \
        ENVIRONMENT=production \
        DEBUG=false \
        DEMO_MODE=true \
        MOCK_DATA=true \
        LOG_LEVEL=INFO \
        -a "$app_name"
    
    # Set API keys if provided
    if [ ! -z "$OPENAI_API_KEY" ]; then
        heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" -a "$app_name"
        print_status "OpenAI API key set"
    fi
    
    if [ ! -z "$HUGGINGFACE_API_KEY" ]; then
        heroku config:set HUGGINGFACE_API_KEY="$HUGGINGFACE_API_KEY" -a "$app_name"
        print_status "HuggingFace API key set"
    fi
    
    print_status "Environment variables configured"
}

# Create Procfile for Heroku
create_procfile() {
    print_info "Creating Procfile..."
    
    cat > Procfile << EOF
web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT
EOF
    
    print_status "Procfile created"
}

# Create runtime.txt for Python version
create_runtime() {
    print_info "Creating runtime.txt..."
    
    cat > runtime.txt << EOF
python-3.11.7
EOF
    
    print_status "runtime.txt created"
}

# Deploy to Heroku
deploy_app() {
    local app_name=$(cat .heroku-app-name 2>/dev/null)
    
    if [ -z "$app_name" ]; then
        print_error "No Heroku app found"
        return 1
    fi
    
    print_info "Deploying to Heroku..."
    
    # Initialize git if not already done
    if [ ! -d ".git" ]; then
        git init
        print_status "Git repository initialized"
    fi
    
    # Add Heroku remote
    heroku git:remote -a "$app_name"
    
    # Add all files
    git add .
    git commit -m "Deploy StreamMind to Heroku" || true
    
    # Push to Heroku
    if git push heroku main || git push heroku master; then
        print_status "Deployment successful!"
        
        # Get app URL
        APP_URL=$(heroku apps:info -a "$app_name" | grep "Web URL" | awk '{print $3}')
        
        print_status "🎉 StreamMind deployed successfully!"
        print_info "App URL: $APP_URL"
        print_info "Logs: heroku logs -a $app_name --tail"
        
        return 0
    else
        print_error "Deployment failed"
        return 1
    fi
}

# Wait for app to be ready
wait_for_app() {
    local app_name=$(cat .heroku-app-name 2>/dev/null)
    local app_url="https://$app_name.herokuapp.com"
    
    print_info "Waiting for app to be ready..."
    
    for i in {1..30}; do
        if curl -s "$app_url/health" > /dev/null; then
            print_status "App is ready!"
            return 0
        fi
        sleep 10
    done
    
    print_warning "App may still be starting. Check logs if needed."
    return 0
}

# Main deployment function
main() {
    local app_name="$1"
    
    echo
    print_info "Starting Heroku deployment..."
    echo
    
    # Check prerequisites
    if ! check_heroku_cli; then
        exit 1
    fi
    
    # Login to Heroku
    heroku_login
    
    # Create deployment files
    create_procfile
    create_runtime
    
    # Create app if name provided, otherwise use existing
    if [ ! -z "$app_name" ] && [ ! -f ".heroku-app-name" ]; then
        create_heroku_app "$app_name"
    elif [ ! -f ".heroku-app-name" ]; then
        create_heroku_app
    else
        print_status "Using existing Heroku app: $(cat .heroku-app-name)"
    fi
    
    # Setup Redis and environment
    add_redis_addon
    set_env_vars
    
    # Deploy
    if deploy_app; then
        wait_for_app
        
        local final_app_name=$(cat .heroku-app-name)
        echo
        print_status "🎉 Deployment completed!"
        print_info "Your StreamMind app is live at:"
        print_info "https://$final_app_name.herokuapp.com"
        echo
        print_info "Useful commands:"
        echo "  - View logs: heroku logs -a $final_app_name --tail"
        echo "  - Open app: heroku open -a $final_app_name"
        echo "  - Scale: heroku ps:scale web=1 -a $final_app_name"
        echo
    else
        print_error "Deployment failed. Check the logs above."
        exit 1
    fi
}

# Run main function with arguments
main "$@"