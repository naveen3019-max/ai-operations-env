# Real Email Integration Setup Guide

This guide explains how to connect the AI Operations Assistant Environment to real Gmail and Outlook accounts.

## Prerequisites

Install the required dependencies:

```powershell
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client requests msal
```

---

## Gmail Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it "AI Operations")
3. Wait for project creation to complete

### Step 2: Enable Gmail API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on it and press **Enable**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth 2.0 Desktop App**
3. Select **Desktop application** as the application type
4. Download the JSON file as `gmail_credentials.json`
5. Place `gmail_credentials.json` in your project root directory:
   ```
   c:\Users\navee\OneDrive\Desktop\Scalr\gmail_credentials.json
   ```

### Step 4: Run Gmail Integration

```powershell
# First time will open browser for authentication
python real_email_example.py --provider gmail

# Subsequent runs will use cached token
python real_email_example.py --provider gmail
```

**What happens:**
- Browser opens for login (you'll see "localhost refused to connect" - safe to ignore)
- Token is cached in `token.pickle` for future use
- Fetches first 10 unread emails
- Processes them through the environment
- Agent classifies, replies, escalates emails

---

## Outlook Setup

### Step 1: Register Application in Azure

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **+ New registration**
4. Fill in:
   - **Name**: "AI Operations Assistant"
   - **Supported account types**: "Accounts in any organizational directory and personal Microsoft accounts"
5. Click **Register**

### Step 2: Get Client ID

1. Copy the **Application (client) ID** from the overview page
2. You'll need this for authentication

### Step 3: Set Client ID Environment Variable

**On PowerShell:**

```powershell
$env:OUTLOOK_CLIENT_ID = "your-application-client-id"
```

**Or permanently (add to profile):**

```powershell
[Environment]::SetEnvironmentVariable('OUTLOOK_CLIENT_ID', 'your-application-client-id', 'User')
```

### Step 4: Run Outlook Integration

```powershell
# With environment variable set
python real_email_example.py --provider outlook
```

**What happens:**
- Browser opens for Microsoft login
- Grants permission to access your Outlook inbox
- Fetches first 10 unread emails
- Processes them through the environment

---

## Usage Examples

### Process Real Gmail Emails

```powershell
python real_email_example.py --provider gmail
```

**Output:**
```
[OK] Gmail authentication successful!
[OK] Fetched 5 unread emails from Gmail
[OK] Loaded 5 real emails into environment

Step 1: classify_email -> reward: 0.250
Step 2: reply_email -> reward: 0.350
...
[RESULTS]
  Steps taken: 8
  Total reward: 1.950
```

### Process Real Outlook Emails

```powershell
python real_email_example.py --provider outlook
```

### Use Simulated Environment (Default)

```powershell
python real_email_example.py
# Or
python real_email_example.py --provider simulated
```

---

## How It Works

### Email Fetching Pipeline

```
Real Email Account (Gmail/Outlook)
         ↓
Email Provider (API)
         ↓
Parse to Email Model
         ↓
Categorize (Spam/Product/Support/Billing/Feedback)
         ↓
Load into Environment
         ↓
Agent Processing
         ↓
Action Rewards
```

### Email Categorization

The system automatically categorizes emails:

| Category | Keywords |
|----------|----------|
| SPAM | spam, unsubscribe, promotional, offer |
| BILLING | invoice, payment, charge, bill |
| SUPPORT | support, help, issue, problem |
| FEEDBACK | feedback, review, suggestion |
| PRODUCT | (default) |

### Agent Actions

Once emails are loaded, the baseline agent can:

1. **classify_email** - Classify email category (learns from rewards)
2. **reply_email** - Send automated responses
3. **escalate_ticket** - Mark as urgent/escalate
4. **close_ticket** - Mark as resolved
5. **schedule_meeting** - Create calendar events
6. **delete_email** - Remove emails

---

## Advanced Usage

### Custom Email Filtering

Modify `fetch_emails()` to filter specific emails:

```python
# In email_integration.py, modify Gmail or Outlook provider:

def fetch_emails(self, limit: int = 10) -> List[Email]:
    # Add filter for specific senders
    if isinstance(self, GmailProvider):
        url = self.service.users().messages().list(
            userId='me',
            q='from:boss@company.com is:unread',  # Only from boss
            maxResults=limit
        ).execute()
```

### Process Emails by Folder

```python
# For Gmail - process specific label
result = service.users().messages().list(
    userId='me',
    q='label:Support is:unread',
    maxResults=limit
).execute()

# For Outlook - process specific folder
url = 'https://graph.microsoft.com/v1.0/me/mailfolders/Support/messages'
```

### Send AI-Generated Replies

```python
# Extend the environment to use AI-generated responses
from baseline import AIOperationsAgent

agent = AIOperationsAgent()
state = env.state()
action = agent.act(state)

# If action is reply_email:
if hasattr(action, 'reply_email'):
    reply_text = generate_smart_reply(action.reply_email.body)
    provider.send_reply(message_id, reply_text)
```

---

## Troubleshooting

### "Gmail credentials file not found"

**Solution:** Download `gmail_credentials.json` from Google Cloud Console and place in project root.

```powershell
# Verify it exists:
Test-Path .\gmail_credentials.json
```

### "Authentication failed" for Outlook

**Solution:** Check that `OUTLOOK_CLIENT_ID` is set:

```powershell
# Verify environment variable:
$env:OUTLOOK_CLIENT_ID

# If empty, set it:
$env:OUTLOOK_CLIENT_ID = "your-client-id"
```

### "ImportError: No module named 'google.auth'"

**Solution:** Install Google libraries:

```powershell
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "ImportError: No module named 'msal'"

**Solution:** Install Microsoft libraries:

```powershell
pip install requests msal
```

### "No unread emails found"

**Solution:** The system falls back to simulated environment. To test:

1. Send yourself test emails
2. Mark them as unread
3. Run the script again

---

## Security Notes

1. **Never commit credentials files** - Add to `.gitignore`:
   ```
   gmail_credentials.json
   token.pickle
   .env
   ```

2. **Protect Client IDs** - Use environment variables, not hardcoded values

3. **Token Storage** - Tokens are stored locally in:
   - Gmail: `token.pickle`
   - Outlook: Session-based (memory)

4. **Permissions** - The app only requests:
   - Gmail: Modify emails (reply/classify)
   - Outlook: Read/write mail, schedule meetings

---

## Next Steps

### 1. Train Custom Agent

Instead of the rule-based baseline, train an ML agent:

```python
from baseline import AIOperationsAgent

# Train on real emails
agent = AIOperationsAgent()
real_emails = gmail_provider.fetch_emails(100)
agent.train(real_emails, episodes=50)

# Evaluate on live emails
performance = agent.evaluate(real_emails)
```

### 2. Deploy as Email Service

Create a scheduled service that:
- Cron job: Process emails hourly
- Webhook: Handle incoming emails
- API: Query agent decisions

### 3. Multi-Account Management

Process emails across multiple Gmail/Outlook accounts:

```python
accounts = [
    {'provider': 'gmail', 'credentials': 'account1_creds.json'},
    {'provider': 'gmail', 'credentials': 'account2_creds.json'},
    {'provider': 'outlook', 'client_id': 'id1'},
]

for account in accounts:
    provider = get_email_provider(**account)
    emails = provider.fetch_emails()
    # Process each account independently
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation:
   - [Gmail API Docs](https://developers.google.com/gmail/api/guides)
   - [Microsoft Graph API Docs](https://docs.microsoft.com/en-us/graph/overview)
