#!/bin/bash

# DigitalOcean Deployment Script for Intelligent Hotel Scraper

echo "🚀 Deploying Intelligent Hotel Scraper to DigitalOcean..."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI not found. Please install it first:"
    echo "   Visit: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is authenticated
if ! doctl auth list &> /dev/null; then
    echo "❌ Not authenticated with DigitalOcean. Please run:"
    echo "   doctl auth init"
    exit 1
fi

echo "✅ DigitalOcean CLI configured"

# Deploy the application
echo "📦 Creating DigitalOcean App..."

# Check if app.yaml exists
if [ ! -f "app.yaml" ]; then
    echo "❌ app.yaml not found. Please ensure you're in the project root directory."
    exit 1
fi

# Create the app
APP_ID=$(doctl apps create --spec app.yaml --format ID --no-header)

if [ $? -eq 0 ]; then
    echo "✅ App created successfully with ID: $APP_ID"
    echo "🔗 App URL will be available after deployment completes"
    
    # Wait for deployment
    echo "⏳ Waiting for deployment to complete..."
    doctl apps get $APP_ID --wait
    
    # Get app info
    echo "📋 App Information:"
    doctl apps get $APP_ID
    
    echo ""
    echo "🎉 Deployment complete!"
    echo "📊 Monitor your app:"
    echo "   doctl apps get $APP_ID"
    echo "   doctl apps logs $APP_ID"
    
    echo ""
    echo "🔧 To update your app:"
    echo "   doctl apps update $APP_ID --spec app.yaml"
    
    echo ""
    echo "📝 Next steps:"
    echo "1. (Optional) Set environment variables in the DigitalOcean dashboard:"
    echo "   - HUGGINGFACE_TOKEN (optional, for advanced models)"
    echo "   - SENTRY_DSN (for error tracking, optional)"
    echo "   Note: Free AI is enabled by default - no paid API keys required!"
    echo ""
    echo "2. Monitor logs for any issues:"
    echo "   doctl apps logs $APP_ID --type run"
    echo ""
    echo "3. Test the API endpoints once deployment is complete"
    
else
    echo "❌ Failed to create app. Please check your app.yaml file and try again."
    exit 1
fi
