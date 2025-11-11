# Implementation Verification Checklist

## Pre-Deployment Verification

Run through this checklist before deploying to production.

### 1. Backend Code Verification

#### A. Load Questions Script
- [ ] Confirm `backend/app/load_questions.py` uses new CSV path
- [ ] Verify it extracts all 6 columns from CSV correctly
- [ ] Check it handles missing values gracefully

```bash
# Test locally
python backend/app/load_questions.py
# Expected: "Loaded questions. Read=X, Inserted=Y, Skipped=Z"
```

#### B. Question Filtering Logic
- [ ] Confirm `_pick_questions()` filters by `years_of_experience`
- [ ] Verify filtering priority is correct (company+exp → company → exp → any)
- [ ] Check `normalize_experience()` function handles all cases (0-2, 2-4, 5-8, 8+)

#### C. API Endpoint
- [ ] `/api/interview/questions` accepts `experience` parameter
- [ ] `/api/interview/questions` does NOT require `role` parameter
- [ ] Endpoint returns questions with all expected fields

```bash
# Test endpoint
curl -X GET "http://localhost:8000/api/interview/questions?experience=0-2&company=Google"
# Expected: JSON array with questions
```

#### D. User Model & Auth
- [ ] User profile accepts `experience` field
- [ ] User profile rejects `currentRole` field (or ignores it)
- [ ] `/auth/me` endpoint does not return `currentRole`
- [ ] `/auth/patch /me` endpoint accepts `experience` updates

```bash
# Test auth
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Should NOT have "currentRole" in response
```

### 2. Frontend Code Verification

#### A. API Types
- [ ] `FetchQuestionsParams` does NOT have `role` property
- [ ] `QuestionDTO` still has all expected question fields
- [ ] No TypeScript errors in api.ts

```bash
cd Frontend
npm run build
# Should complete without errors
```

#### B. Interview Setup Component
- [ ] `normalizeRole()` function is removed
- [ ] `handleStartInterview()` passes `experience` not `role`
- [ ] `handleProceedWithJD()` passes `experience` not `role`
- [ ] No TypeScript errors in InterviewSetup.tsx

#### C. User Type
- [ ] `User` interface has `experience` field
- [ ] `User` interface does NOT have `currentRole` field
- [ ] No TypeScript errors in types/index.ts

### 3. Data Verification

#### A. CSV File Verification
- [ ] New CSV exists: `PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`
- [ ] CSV has these columns: Question, Company, Category, Complexity, Experience Level, Years of Experience
- [ ] Sample rows verified for correct data

```bash
# Check CSV
head -5 "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"
# Should show header and a few questions
```

#### B. Questions in Database
- [ ] All questions loaded into `questions` table
- [ ] Sample queries return expected results

```sql
-- Check database
SELECT COUNT(*) FROM questions;  -- Should be ~12000
SELECT DISTINCT years_of_experience FROM questions;  -- Should include 0-2, 2-4, 5-8, 8+
SELECT DISTINCT company FROM questions;  -- Should include company names
```

### 4. Integration Testing

#### A. Scenario 1: Company + Experience
```bash
curl "http://localhost:8000/api/interview/questions?company=Google&experience=0-2&session=test123"
# Should return questions from Google for 0-2 years
```

#### B. Scenario 2: Experience Only
```bash
curl "http://localhost:8000/api/interview/questions?experience=5-8&session=test123"
# Should return questions for 5-8 years (any company)
```

#### C. Scenario 3: Company Only
```bash
curl "http://localhost:8000/api/interview/questions?company=Meta&session=test123"
# Should return questions from Meta (any experience)
```

#### D. Scenario 4: No Filters
```bash
curl "http://localhost:8000/api/interview/questions?session=test123"
# Should return random questions
```

#### E. Scenario 5: User Profile
```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Update profile with experience
curl -X PATCH "http://localhost:8000/auth/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"experience":"2-4"}'

# Get profile (should NOT have currentRole)
curl "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Frontend Integration Testing

#### A. Build & Run
```bash
cd Frontend
npm install
npm run build
npm run dev
```

#### B. User Flow Test
- [ ] Navigate to Interview Setup
- [ ] User's experience level is shown (not role)
- [ ] Company selection works
- [ ] Questions are fetched with correct parameters
- [ ] Questions display correctly

### 6. Docker Testing

#### A. Build Image
```bash
docker-compose build
# Should complete without errors
```

#### B. Run Containers
```bash
docker-compose up
# Should start without errors
# Logs should show "Loading questions..." and "Starting server..."
```

#### C. Test Endpoints
```bash
# Inside container or from host
curl "http://localhost:8000/api/interview/questions?experience=0-2"
# Should return questions
```

### 7. Performance Testing

- [ ] Loading 12000 questions completes in < 30 seconds
- [ ] API responds to question requests in < 1 second
- [ ] No database connection errors
- [ ] Memory usage is reasonable

### 8. Security Testing

- [ ] CORS headers are correct
- [ ] Authentication tokens are validated
- [ ] No SQL injection vulnerabilities
- [ ] Sensitive data is not exposed in API responses

## Sign-Off

- **Backend Ready**: ☐ (Date: _______)
- **Frontend Ready**: ☐ (Date: _______)
- **Database Ready**: ☐ (Date: _______)
- **All Tests Pass**: ☐ (Date: _______)
- **Ready for Deployment**: ☐ (Date: _______)

## Common Issues & Solutions

### Issue: "No questions available"
**Solution**: 
1. Verify CSV file path is correct
2. Run `python app/load_questions.py`
3. Check database: `SELECT COUNT(*) FROM questions;`

### Issue: "Questions not filtered correctly"
**Solution**:
1. Check experience parameter format matches CSV (0-2, 2-4, 5-8, 8+)
2. Verify questions exist in database for selected filters
3. Check API logs for parameter values

### Issue: "Frontend can't fetch questions"
**Solution**:
1. Verify backend is running on correct port
2. Check CORS settings
3. Inspect network request for correct parameters
4. Check browser console for errors

### Issue: "User profile doesn't save experience"
**Solution**:
1. Verify `experience` field is in UserUpdate schema
2. Check PATCH endpoint is working
3. Verify database column exists

## Rollback Plan

If issues arise:

1. **Revert to old CSV** (if keeping old CSV):
   ```python
   # Edit load_questions.py to use old CSV path
   candidates = ["PM_Questions_8000_expanded_clean_final5.csv", ...]
   python app/load_questions.py
   ```

2. **Revert code**: Use git to checkout previous version
   ```bash
   git checkout HEAD~1 -- backend/app/routers/interview.py
   git checkout HEAD~1 -- Frontend/src/utils/api.ts
   ```

3. **Restart services**: Rebuild and restart containers

## Additional Notes

- Database schema does NOT require migration (all fields already exist)
- No breaking changes for authenticated users
- API is backward compatible (old `role` parameter is simply ignored)
- Questions are immediately available after `load_questions.py` runs
