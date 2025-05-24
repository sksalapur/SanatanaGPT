# 🚀 Deploying SanatanaGPT to Streamlit Cloud

## 📋 Pre-deployment Checklist

### 1. 🔧 Update Copy Link URL
Before deploying, you need to update the base URL in `app.py`:

1. Open `app.py`
2. Find the `get_base_url()` function (around line 200)
3. Replace `"https://sanatanagpt.streamlit.app"` with your actual Streamlit Cloud URL
4. Your URL format will be: `https://your-app-name-your-github-username.streamlit.app`

```python
def get_base_url():
    # ... existing code ...
    return "https://your-actual-app-url.streamlit.app"  # ⚠️ UPDATE THIS
```

### 2. 📁 Required Files
Make sure you have these files in your repository:
- `app.py` (main application)
- `requirements.txt` (dependencies)
- `hindu_texts/` folder with your scripture files
- `.env` file (for local development only - don't commit this!)

### 3. 🔑 Environment Variables
In Streamlit Cloud, add your Google API key:
1. Go to your app settings
2. Click "Secrets"
3. Add: `GOOGLE_API_KEY = "your_api_key_here"`

## 🌐 Deployment Steps

### 1. 📤 Push to GitHub
```bash
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

### 2. 🚀 Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set main file as `app.py`
5. Click "Deploy"

### 3. 🔗 Update Copy Link URL
After deployment:
1. Note your app's URL (e.g., `https://sanatanagpt-username.streamlit.app`)
2. Update the URL in `get_base_url()` function
3. Commit and push the change
4. Streamlit will auto-redeploy

## ✅ Post-deployment Testing

### Test Copy Link Functionality:
1. Start a conversation
2. Expand the conversation in sidebar
3. Click "🔗 Copy Link"
4. Copy the generated link
5. Open in new tab/incognito to verify it works

### Expected Behavior:
- ✅ Link should open the specific conversation
- ✅ Should show "🔗 Opened shared conversation!" message
- ✅ Should switch to the correct conversation automatically

## 🔧 Troubleshooting

### Copy Link Not Working:
- ❌ **Problem**: Link shows localhost URL on cloud
- ✅ **Solution**: Update `get_base_url()` with correct cloud URL

### Shared Links Not Opening Conversations:
- ❌ **Problem**: URL parameters not being processed
- ✅ **Solution**: Check if conversation ID exists in session state

### Environment Variables:
- ❌ **Problem**: Google API key not found
- ✅ **Solution**: Add `GOOGLE_API_KEY` in Streamlit Cloud secrets

## 📱 Features After Deployment

### ✨ Working Features:
- 🤖 AI-powered Hindu scripture Q&A
- 💬 Multiple conversation management
- 🔗 Shareable conversation links
- 📚 Source citations with expandable details
- 🎯 Balanced search across scriptures
- 📊 Conversation statistics and history

### 🔗 Sharing Conversations:
Users can now:
1. Generate shareable links for any conversation
2. Send links to friends/family
3. Open shared conversations in new tabs
4. Continue conversations from shared links

## 🎉 Your App is Live!

Once deployed, your SanatanaGPT will be accessible worldwide at your Streamlit Cloud URL, with full conversation sharing capabilities! 