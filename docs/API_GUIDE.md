# 🤖 Google Gemini API Integration Guide

This guide explains how the Hindu Scriptures Q&A system integrates with Google Gemini AI and how to optimize its performance.

## 🔑 API Setup

### Getting Your API Key

1. **Visit [Google AI Studio](https://makersuite.google.com/app/apikey)**
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy the generated key**
5. **Add to your environment:**
   - **Local:** Add to `.env` file
   - **Streamlit Cloud:** Add to app secrets

### API Key Security

⚠️ **Important Security Notes:**

- **Never commit** your API key to version control
- **Use environment variables** or secrets management
- **Regenerate keys** if accidentally exposed
- **Monitor usage** to detect unauthorized access

## 🧠 How the AI Integration Works

### 1. Text Processing Pipeline

```
User Question → Text Search → Relevant Passages → AI Analysis → Answer
```

### 2. Gemini Model Configuration

The app uses **Gemini 1.5 Flash** for optimal performance:

```python
model = genai.GenerativeModel('gemini-1.5-flash')
```

**Why Gemini 1.5 Flash?**
- ✅ **Fast response times** (1-3 seconds)
- ✅ **Cost-effective** for frequent queries
- ✅ **Good context understanding**
- ✅ **Supports long text inputs**

### 3. Prompt Engineering

The system uses carefully crafted prompts:

```python
prompt = f"""You are a knowledgeable scholar of Hindu scriptures. 
Based on the following excerpts from Hindu texts, please provide 
a comprehensive and accurate answer to the question.

CONTEXT FROM HINDU SCRIPTURES:
{context}

QUESTION: {query}

Please provide a detailed answer based on the provided context...
"""
```

## ⚡ Performance Optimization

### 1. Caching Strategy

The app uses Streamlit caching to improve performance:

```python
@st.cache_resource
def setup_gemini():
    # Cached API setup

@st.cache_data
def load_hindu_texts():
    # Cached text loading
```

### 2. Context Management

**Optimal passage selection:**
- **Default:** 3 passages per query
- **Range:** 1-5 passages (configurable)
- **Balance:** More context vs. faster responses

### 3. Rate Limiting

**Google Gemini API Limits:**
- **Free tier:** 15 requests per minute
- **Paid tier:** Higher limits available
- **Best practice:** Implement user-side rate limiting

## 📊 API Usage Monitoring

### Tracking Usage

Monitor your API usage at [Google AI Studio](https://makersuite.google.com/):

1. **Go to your API dashboard**
2. **Check usage statistics**
3. **Monitor quota consumption**
4. **Set up billing alerts**

### Cost Optimization

**Tips to reduce API costs:**

1. **Efficient prompts:** Keep prompts concise but informative
2. **Smart caching:** Cache frequently asked questions
3. **Passage filtering:** Only send relevant text to the API
4. **Batch processing:** Group similar queries when possible

## 🔧 Advanced Configuration

### Custom Model Parameters

You can customize the Gemini model behavior:

```python
generation_config = {
    "temperature": 0.7,  # Creativity level (0.0-1.0)
    "top_p": 0.8,       # Nucleus sampling
    "top_k": 40,        # Top-k sampling
    "max_output_tokens": 1024,  # Response length
}

model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=generation_config
)
```

### Safety Settings

Configure content safety filters:

```python
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]
```

## 🚨 Error Handling

### Common API Errors

#### 1. **Quota Exceeded (429)**
```python
except Exception as e:
    if "quota" in str(e).lower():
        return "API quota exceeded. Please try again later."
```

#### 2. **Invalid API Key (401)**
```python
if "invalid" in str(e).lower():
    return "Invalid API key. Please check your configuration."
```

#### 3. **Network Issues**
```python
except requests.exceptions.RequestException:
    return "Network error. Please check your connection."
```

### Robust Error Handling

```python
def generate_answer_with_retry(model, query, passages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error after {max_retries} attempts: {str(e)}"
            time.sleep(2 ** attempt)  # Exponential backoff
```

## 📈 Performance Metrics

### Response Time Optimization

**Target metrics:**
- **Text search:** < 0.5 seconds
- **API call:** 1-3 seconds
- **Total response:** < 5 seconds

### Quality Metrics

**Measuring answer quality:**
- **Relevance:** Does the answer address the question?
- **Accuracy:** Is the information correct?
- **Completeness:** Are all aspects covered?
- **Citations:** Are sources properly referenced?

## 🔄 Alternative Models

### Other Gemini Models

1. **Gemini 1.5 Pro:**
   - Higher quality responses
   - Slower and more expensive
   - Better for complex queries

2. **Gemini 1.0 Pro:**
   - Legacy model
   - Good for simple queries
   - Lower cost

### Model Selection Strategy

```python
def select_model(query_complexity):
    if len(query.split()) > 20:  # Complex query
        return 'gemini-1.5-pro'
    else:  # Simple query
        return 'gemini-1.5-flash'
```

## 🛡️ Security Best Practices

### API Key Management

1. **Environment variables:** Never hardcode keys
2. **Secrets rotation:** Regularly update API keys
3. **Access control:** Limit key permissions
4. **Monitoring:** Track unusual usage patterns

### Data Privacy

- **No storage:** API calls don't store user data
- **Encryption:** Use HTTPS for all API calls
- **Compliance:** Follow data protection regulations

## 📚 Additional Resources

- **[Google AI Studio](https://makersuite.google.com/)** - API management
- **[Gemini API Documentation](https://ai.google.dev/)** - Technical docs
- **[Pricing Information](https://ai.google.dev/pricing)** - Cost details
- **[Safety Guidelines](https://ai.google.dev/docs/safety_guidance)** - Content policies

---

*🤖 Harness the power of AI to explore ancient wisdom! 🕉️* 