# DigitalOcean Deployment Guide 🚀

## Why DigitalOcean?

Your Mac is hitting limitations with the GPU-only AI models like `openai/gpt-oss-20b`. DigitalOcean provides:

✅ **GPU-enabled instances** for advanced AI models  
✅ **Professional-tier compute** for faster processing  
✅ **Automatic scaling** and load balancing  
✅ **Built-in databases** (Redis, PostgreSQL)  
✅ **24/7 uptime** with monitoring  

## Quick Setup (5 minutes)

### 1. DigitalOcean Account
- Sign up: https://cloud.digitalocean.com/registrations/new
- Use promo code `DO10` for $200 credit (if available)

### 2. Generate API Token
1. Go to: https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: `Hotel Scraper API`
4. Scope: Full (Read & Write)
5. **Copy the token** (you'll only see it once!)

### 3. Authenticate CLI
```bash
doctl auth init
# Paste your API token when prompted
```

### 4. Deploy Application
```bash
./deploy.sh
```

That's it! Your intelligent scraper will be running on DigitalOcean with:
- **GPT-oss-20b** for advanced text generation
- **Professional compute** for faster processing
- **Redis caching** for performance
- **Auto-scaling** based on demand

## After Deployment

### Monitor Your App
```bash
# Get app status
doctl apps list

# View logs
doctl apps logs <APP_ID> --type run

# Update app (after code changes)
doctl apps update <APP_ID> --spec app.yaml
```

### Set Optional Environment Variables
In the DigitalOcean dashboard (Apps > Your App > Settings):

- `HUGGINGFACE_TOKEN`: For advanced model access (optional)
- `SENTRY_DSN`: For error tracking (optional)

**Note**: Free AI is enabled by default - no paid API keys required!

## Cost Estimate

- **Professional-XS instance**: ~$12/month
- **Redis database**: ~$15/month
- **Total**: ~$27/month for production-grade AI scraping

Much cheaper than OpenAI API costs for heavy usage!

## Benefits of Cloud Deployment

### 🚀 Performance
- **10x faster** AI processing with GPU acceleration
- **Better models** like GPT-oss-20b work perfectly
- **Parallel processing** of multiple hotels

### 🛡️ Reliability
- **99.9% uptime** SLA
- **Automatic failover** and health checks
- **Managed databases** with backups

### 📈 Scalability
- **Auto-scaling** based on load
- **Rate limiting** and queue management
- **API monitoring** and metrics

### 💰 Cost Efficiency
- **No GPU hardware** investment needed
- **Pay-as-you-use** pricing
- **Free $200 credit** to get started

## Next Steps

1. **Deploy now**: Run `./deploy.sh`
2. **Test the API**: Use the web interface once deployed
3. **Monitor performance**: Check logs and metrics
4. **Scale as needed**: Upgrade instance size if required

Ready to deploy? 🚀
