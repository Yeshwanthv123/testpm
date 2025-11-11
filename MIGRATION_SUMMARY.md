# PM Bot Question System Migration Summary

## Overview
The question filtering system has been successfully migrated from **role-based filtering** to **experience-level-based filtering**. All questions will now be filtered by:
- **Primary filter**: Years of experience (0-2, 2-4, 5-8, 8+)
- **Secondary filter**: Company (Google, Meta, Airbnb, Generic, etc.)

## Key Changes

### 1. **Backend Changes**

#### A. Question Loading (`backend/app/load_questions.py`)
**Old behavior**: Loaded from `PM_Questions_8000_expanded_clean_final5.csv`
**New behavior**: Loads from `PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`

Changes:
- ✅ Removed old CSV file path references
- ✅ Now extracts these fields from new CSV:
  - `question` → Question text
  - `Company` → Company filter
  - `Category` → Question category
  - `Complexity` → Question difficulty
  - `Experience Level` → PM level (APM, PM, Senior PM, etc.)
  - `Years of Experience` → Years range for filtering (0-2, 2-4, 5-8, 8+)

#### B. Question Filtering Logic (`backend/app/routers/interview.py`)
**Old behavior**: 
- Filtered by `role` (APM, PM, Senior PM, etc.)
- Mapped experience_level column to role filter

**New behavior**:
- Filters by `years_of_experience` (0-2, 2-4, 5-8, 8+)
- Much simpler, more direct filtering
- Removed role normalization logic

**Filter priority** (improved):
1. Company + Experience Level (most specific)
2. Company + any experience (company matters)
3. Experience level + any company (experience matters)
4. Any question (fallback)

#### C. API Endpoint (`/api/interview/questions`)
**Old signature**:
```
GET /api/interview/questions?company=Google&role=PM&experience=0-2&session=xxx
```

**New signature**:
```
GET /api/interview/questions?company=Google&experience=0-2&session=xxx
```

Changes:
- ✅ Removed `role` query parameter
- ✅ `experience` now maps directly to `years_of_experience` column
- ✅ `company` filtering works as before

#### D. User Model & Auth (`backend/app/models.py` & `backend/app/routers/auth.py`)
Changes:
- ✅ User model already has `experience` field ✓
- ✅ Removed `currentRole` from UserUpdate schema
- ✅ Updated `/auth/me` endpoint (no longer returns currentRole)
- ✅ Updated `/auth/patch /me` endpoint (no longer accepts currentRole)

### 2. **Frontend Changes**

#### A. API Types (`Frontend/src/utils/api.ts`)
**Old FetchQuestionsParams**:
```typescript
{ company?: string; role?: string; experience?: string; }
```

**New FetchQuestionsParams**:
```typescript
{ company?: string; experience?: string; }
```

Changes:
- ✅ Removed `role` parameter
- ✅ Updated all API call sites to use experience instead of role
- ✅ Fixed 4 error response objects to use `null` instead of `role ?? null`

#### B. Interview Setup (`Frontend/src/components/InterviewSetup.tsx`)
Changes:
- ✅ Removed `normalizeRole()` function (no longer needed)
- ✅ Updated `handleStartInterview()` to pass experience instead of role
- ✅ Updated `handleProceedWithJD()` to use experience
- ✅ Removed role extraction from JD analysis
- ✅ Validation now requires experience instead of currentRole

#### C. User Types (`Frontend/src/types/index.ts`)
**Old User interface**:
```typescript
{
  id: number;
  full_name: string;
  email: string;
  experience: string;
  targetCompanies: string[];
  region: string;
  currentRole: string;  // ❌ REMOVED
}
```

**New User interface**:
```typescript
{
  id: number;
  full_name: string;
  email: string;
  experience: string;  // ✅ KEPT - primary filter
  targetCompanies: string[];
  region: string;
}
```

### 3. **Docker Setup**

#### Fixed `docker-entrypoint.sh`
- ✅ Added missing Python command for first case
- ✅ Now properly loads questions from new CSV on container startup

## Migration Checklist

- [x] Backend: Load new CSV file with experience_level and years_of_experience
- [x] Backend: Update _pick_questions() filtering logic
- [x] Backend: Update /api/interview/questions endpoint
- [x] Backend: Remove role from UserUpdate schema
- [x] Frontend: Update API types (remove role parameter)
- [x] Frontend: Update fetchInterviewQuestions() calls
- [x] Frontend: Update InterviewSetup component
- [x] Frontend: Remove normalizeRole() function
- [x] Frontend: Update User type
- [x] Docker: Fix entrypoint script
- [x] Remove old CSV file references

## Testing Checklist

After deployment, test these scenarios:

### Scenario 1: Company + Experience Selection
```
Request: GET /api/interview/questions?company=Google&experience=0-2
Expected: Returns questions from Google dataset for 0-2 years of experience
```

### Scenario 2: Only Experience Selection
```
Request: GET /api/interview/questions?experience=5-8
Expected: Returns questions for 5-8 years (any company)
```

### Scenario 3: Only Company Selection
```
Request: GET /api/interview/questions?company=Meta
Expected: Returns questions from Meta dataset (any experience level)
```

### Scenario 4: No Filters
```
Request: GET /api/interview/questions
Expected: Returns random questions from any company/experience
```

### Scenario 5: Invalid Experience
```
Request: GET /api/interview/questions?experience=10-15
Expected: Returns questions with no specific filter match
```

## Files Modified

### Backend
- `backend/app/load_questions.py` - Updated CSV loading logic
- `backend/app/routers/interview.py` - Updated filtering logic, removed role handling
- `backend/app/routers/auth.py` - Removed currentRole from user profile
- `backend/docker-entrypoint.sh` - Fixed question loading command

### Frontend
- `Frontend/src/utils/api.ts` - Updated API types and calls
- `Frontend/src/components/InterviewSetup.tsx` - Removed role selection
- `Frontend/src/types/index.ts` - Updated User interface

### CSV Files
- ✅ `PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv` - New source (used)
- ❌ `PM_Questions_8000_expanded_clean_final5.csv` - Old source (can be deleted)

## CSV Format Reference

The new CSV has these columns:
```
Question | Company | Category | Complexity | Experience Level | Years of Experience
```

Example:
```
"As a APM at Airbnb..." | "Airbnb" | "Strategic" | "Easy" | "APM" | "0-2"
```

**Mapping**:
- `Experience Level` column: Used for context/metadata (APM, PM, Senior PM, etc.)
- `Years of Experience` column: Used for filtering (0-2, 2-4, 5-8, 8+)

## Deployment Notes

1. **Database Migration**: None required (no schema changes)
2. **Environment Variables**: No changes needed
3. **CSV Loading**: Must run `python app/load_questions.py` or use Docker entrypoint
4. **Frontend Build**: Standard build, no special configuration needed
5. **Backward Compatibility**: Old API calls with `role` parameter will be silently ignored

## Future Improvements

Consider these enhancements:
- [ ] Add caching for frequently-accessed question sets
- [ ] Implement A/B testing for different question distributions
- [ ] Add analytics tracking for question performance by experience level
- [ ] Consider fuzzy matching for company names (e.g., "Google" vs "Alphabet")
- [ ] Add bulk question update API
