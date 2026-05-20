# OpenRouter Setup Guide

This guide explains how to use OpenRouter as an alternative to LM Studio for document extraction.

## Why OpenRouter?

1. **No GPU Required** - Runs on cloud infrastructure
2. **Multiple Models** - Access to GPT-4, Claude, and other vision models
3. **Pay-per-use** - Only pay for what you use
4. **No Setup** - No local model downloads or configuration

## Quick Start

### 1. Get an API Key

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-`)

### 2. Configure Environment

Edit your `.env` file:

```env
# OpenRouter configuration
LM_STUDIO_BASE_URL=https://openrouter.ai/api/v1
LM_STUDIO_MODEL=openai/gpt-4o-mini
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Model Selection

Recommended models for document extraction:

#### Budget Option: `openai/gpt-4o-mini`
- Cost: ~$0.15 per 1M tokens
- Good accuracy for most documents
- Fast response times

#### Performance Option: `openai/gpt-4o`
- Cost: ~$2.50-5.00 per 1M tokens
- Best accuracy
- Handles complex documents well

#### Alternative: `anthropic/claude-3-haiku-20240307`
- Cost: ~$0.25 per 1M tokens
- Fast and efficient
- Good vision capabilities

### 4. Test the Setup

Run the test script:

```bash
python test_openrouter.py
```

Expected output:
```
Testing OpenRouter integration...
API Key present: Yes
Base URL: https://openrouter.ai/api/v1
Model: openai/gpt-4o-mini

Testing connection...
Health check: PASSED

Testing text-only request...
Response received: {"test": "success", "provider": "openrouter"}...
JSON parsed: {'test': 'success', 'provider': 'openrouter'}

OpenRouter integration test completed successfully!
```

### 5. Run the Application

Start the backend:
```bash
source .venv/bin/activate
python main.py --backend
```

The system will now use OpenRouter instead of LM Studio for all VLM operations.

## Cost Estimation

Typical costs per document:
- Simple invoice (1 page): ~$0.01-0.02
- Complex form (5 pages): ~$0.05-0.10
- Large document (20 pages): ~$0.20-0.40

Costs vary based on:
- Model selection
- Document complexity
- Number of extraction passes

## Troubleshooting

### API Key Issues

If you see "OPENROUTER_API_KEY not set":
1. Check your `.env` file has the key
2. Ensure no quotes around the key
3. Restart the application

### Connection Errors

If connection fails:
1. Check internet connectivity
2. Verify API key is valid
3. Check OpenRouter status page

### Model Not Available

If model errors occur:
1. Check model name is exact
2. Verify model supports vision
3. Try alternative model

## Advanced Configuration

### Using Other Providers

The patch supports multiple providers:

#### OpenAI
```env
LM_STUDIO_BASE_URL=https://api.openai.com/v1
LM_STUDIO_MODEL=gpt-4-vision-preview
OPENAI_API_KEY=sk-your-openai-key
```

#### Azure OpenAI
```env
LM_STUDIO_BASE_URL=https://your-resource.openai.azure.com/
LM_STUDIO_MODEL=your-deployment-name
OPENAI_API_KEY=your-azure-key
```

### Environment Variables

All OpenRouter settings:

```env
# Required
LM_STUDIO_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Model selection
LM_STUDIO_MODEL=openai/gpt-4o-mini

# Optional tuning
LM_STUDIO_MAX_TOKENS=10000
LM_STUDIO_TEMPERATURE=0.1
LM_STUDIO_TIMEOUT=120
LM_STUDIO_MAX_RETRIES=3
```

## Switching Back to LM Studio

To revert to LM Studio:

1. Edit `.env`:
```env
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen/qwen3-vl-8b
# Comment out: OPENROUTER_API_KEY=...
```

2. Restart the application

## Security Notes

1. **Never commit API keys** to version control
2. **Use environment variables** for keys
3. **Monitor usage** on OpenRouter dashboard
4. **Set spending limits** in OpenRouter account

## Support

- OpenRouter Discord: https://discord.gg/openrouter
- OpenRouter Docs: https://openrouter.ai/docs
- Model comparison: https://openrouter.ai/models