# Regional Leaderboard & Score Fixes - Complete Guide

## What Was Fixed

### 1. **Logout Button** ✅
- Now properly clears all auth tokens and state
- Redirects to login page
- Clears interview results and selected types

### 2. **Region Assignment During Onboarding** ✅
- After login, users MUST select a region during onboarding
- Region is stored in user profile and sent to backend
- Region is locked to user for consistent peer comparison

### 3. **PDF Download Score** ✅
- Overall Score displays actual interview score (not 0)
- Has fallback for different API response formats
- File downloads as HTML which can be printed to PDF

### 4. **Pie Chart Rendering** ✅
- Performance Distribution chart displays without overlapping labels
- Uses legend at bottom for clarity
- Shows distribution across 4 score categories

### 5. **Regional Leaderboard** ✅
- LeaderboardPage properly encodes region names with spaces in URL
- Shows users in selected region only
- Calculates scores based on regional peers

### 6. **Peer Comparison Stats** ✅
- Average Score: User's average across all interviews
- Percentile Rank: Where user ranks among peers in their region
- Improvement Rate: Progress compared to previous interviews

## How to Setup

### Step 1: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Step 2: Start Frontend
```bash
cd Frontend
npm run dev
```

### Step 3: Populate Test Data

**Option A - Using PowerShell (Windows):**
```powershell
cd scripts
.\populate_test_data.ps1
```

**Option B - Using Bash (Linux/Mac):**
```bash
cd scripts
bash populate_test_data.sh
```

**Option C - Manual API Calls:**
```bash
# Create test users with regions
curl -X POST http://localhost:8000/api/auth/admin/create-test-users

# OR migrate existing users to US region
curl -X POST http://localhost:8000/api/auth/admin/migrate-regions
```

### Step 4: Test the Flow

1. **Register New User**
   - Create account with email/password
   - **During onboarding, select a region** (required!)
   - Click "Next" to save profile

2. **Complete Interview**
   - Start an interview
   - Complete all questions
   - Review results with actual scores

3. **Check Results Page**
   - Interviews Completed: Shows total interviews
   - Average Score: Shows your average (not 0!)
   - Percentile Rank: Shows where you rank among regional peers
   - Improvement Rate: Shows if you improved over time

4. **View Regional Leaderboard**
   - Click "View Leaderboard"
   - Select a region (e.g., North America)
   - See users in that region ranked by score
   - Users show profile picture, score, percentile

5. **Download Report**
   - Click "Download Report"
   - Opens HTML file in browser
   - Can print to PDF or save
   - Overall Score shows actual interview score

## Test Credentials

After running `populate_test_data` script:

```
Email: test_us_1@example.com
Password: test123
Region: US (automatically assigned)
```

Other regions:
- `test_eu_1@example.com` → EU
- `test_asia_pacific_1@example.com` → Asia Pacific
- `test_br_1@example.com` → BR (South America)
- `test_africa_1@example.com` → Africa
- `test_ae_1@example.com` → AE (Middle East)

## Regional Codes

The system uses these region codes:
- `US` - North America (USA, Canada, Mexico)
- `EU` - Europe (EU, UK, Switzerland, Norway)
- `Asia Pacific` - India, China, Japan, Australia
- `BR` - South America (Brazil, Argentina, Chile)
- `Africa` - South Africa, Nigeria, Kenya
- `AE` - Middle East (UAE, Saudi Arabia, Israel)

## Troubleshooting

### "No users found" in Regional Leaderboard
- Run the population script to create test data
- Or login as a new user, select a region, and complete an interview

### Score shows 0 in PDF
- Ensure interview was completed successfully
- Check that evaluation endpoint is responding
- Try downloading again

### Percentile Rank shows 0%
- Need at least 2 users in the region to calculate percentile
- Run population script to create test data

### Logout not working
- Clear browser cache
- Try logout again
- Check browser console for errors

## Architecture

```
User Login
  ↓
Onboarding (REQUIRES Region Selection)
  ↓
Interview Setup
  ↓
Interview Questions
  ↓
AI Evaluation (generates score)
  ↓
Results Dashboard (shows peer comparison)
  ↓
Regional Leaderboard (filtered by user's region)
```

## Database Schema

**Users Table:**
- id: Primary key
- email: Unique email
- region: Selected region code (US, EU, Asia Pacific, etc.)
- experience: Years of experience level
- full_name: User's name
- profile_picture: Avatar image

**Evaluations Table:**
- id: Primary key
- user_id: Foreign key to User
- overall_score: Score 0-100
- details: JSON with per-question evaluations
- created_at: Timestamp

## API Endpoints

### Admin Endpoints
```bash
# Create test users
POST /api/auth/admin/create-test-users

# Migrate existing users to US region
POST /api/auth/admin/migrate-regions
```

### User Endpoints
```bash
# Get user profile
GET /api/auth/me

# Update profile (including region)
PATCH /api/auth/me
Body: { region: "US" }

# Get user's ranking/stats
GET /api/interview/my-ranking

# Get global leaderboard
GET /api/leaderboard/global?page=1&page_size=20

# Get regional leaderboard
GET /api/leaderboard/regional/{region}?page=1&page_size=20
```

## Next Steps

1. **Run population script** to create test data
2. **Test the complete flow** from login → interview → results
3. **Verify all stats** display correctly
4. **Check regional leaderboard** shows users from different regions
5. **Download and verify** PDF shows correct score

All fixes are now in place! The system is ready for testing.
