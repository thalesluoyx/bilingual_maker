# Environment Configuration Guide

## Setup Instructions

### 1. Install Dependencies

```bash
pip install python-dotenv
# or
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and replace the placeholder values with your actual API credentials:
   ```
   LLM_API_KEY=your-actual-api-key
   LLM_BASE_URL=your-actual-base-url
   LLM_MODEL=your-actual-model-name
   ```

### 3. Available API Configurations

The `.env.example` file includes templates for multiple API providers:

- **Zenmux Free Gemini 3** (Free tier)
- **ZenMux Pay Deepseek** (Paid service)
- **Volcengine Pay Deepseek** (Paid service, currently active)

Uncomment the configuration you want to use and fill in your credentials.

### 4. Security Notes

⚠️ **IMPORTANT**: 
- The `.env` file contains sensitive information and is automatically ignored by git
- Never commit `.env` file to version control
- Only commit `.env.example` with placeholder values
- Keep your API keys secure and do not share them

### 5. Customization

You can also customize translation settings in the `.env` file:

```
MAX_CONCURRENCY=5      # Number of concurrent translation requests
TIMEOUT_SECONDS=60     # Request timeout in seconds
RETRY_ATTEMPTS=3       # Number of retry attempts for failed requests
```
