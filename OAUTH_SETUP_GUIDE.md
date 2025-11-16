# Google OAuth Setup Guide

## Problem
The application is showing "Access blocked: Authorization Error" with "Error 401: invalid_client" when attempting to sign in with Google. This indicates that Google OAuth credentials are not properly configured.

## Solution

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter a project name (e.g., "PM Bot")
5. Click "CREATE"

### Step 2: Enable OAuth 2.0
1. In the left sidebar, click "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
3. If prompted to configure consent screen, click "CONFIGURE CONSENT SCREEN"
4. Select "External" user type
5. Fill in the required fields:
   - App name: "PM Bot"
   - User support email: Your email
   - Developer contact: Your email
6. Click "SAVE AND CONTINUE"
7. Skip the scopes page (click SAVE AND CONTINUE)
8. Skip test users page (click SAVE AND CONTINUE)
9. Review and click "BACK TO DASHBOARD"

### Step 3: Create OAuth 2.0 Credentials
1. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
2. Select "Web application"
3. Under "Authorized JavaScript origins", add:
   - `http://localhost:3000` (for local development)
   - `http://localhost:8000` (backend)
   - Your production domain (if deploying)
4. Under "Authorized redirect URIs", add:
   - `http://localhost:8000/oauth/google/callback` (for local development)
   - Your production callback URL
5. Click "CREATE"
6. Copy the "Client ID" and "Client secret"

### Step 4: Configure Environment Variables

#### Backend (.env)
Update `backend/.env` with your credentials:

```env
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
OAUTH_REDIRECT_BASE=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

Replace:
- `your-client-id-here` with the Client ID from Step 3
- `your-client-secret-here` with the Client Secret from Step 3

#### Frontend (.env if needed)
If you have a frontend .env file, ensure it has:
```env
VITE_API_BASE=http://localhost:8000
```

### Step 5: Restart Services
1. Stop the backend server (Ctrl+C)
2. Restart with the new environment variables
3. Test Google sign-in from the login page

## Testing
1. Navigate to http://localhost:3000
2. Click "Sign in with Google"
3. Complete the Google authentication flow
4. You should be redirected back to the application

## Troubleshooting

### "invalid_client" error
- Double-check that your Client ID and Client Secret are correct
- Ensure you've restarted the backend after updating .env
- Check that `OAUTH_REDIRECT_BASE` matches your actual backend URL

### "Redirect URI mismatch" error
- The callback URL you're accessing must exactly match what you configured in Google Cloud Console
- For local development, it should be: `http://localhost:8000/oauth/google/callback`

### "access_type=offline" not returning refresh token
- This is expected for user-initiated flows. Refresh tokens are handled by the session.

## Security Notes
- Never commit .env files with real credentials to version control
- Use environment variables in production (set via CI/CD or deployment platform)
- Rotate credentials if they're ever exposed

## Support
If you encounter issues:
1. Check the browser console for error messages
2. Check the backend logs for detailed errors
3. Verify all URLs match exactly (case-sensitive, http vs https)
