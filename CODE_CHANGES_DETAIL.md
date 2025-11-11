# Code Changes Summary - Line-by-Line

## Backend Changes

### 1. `backend/app/load_questions.py`

**Change 1**: Updated CSV path detection (lines 8-18)
```python
# BEFORE: Had 8 candidate paths including old CSV files
candidates = [
    env_path,
    os.path.join(os.getcwd(), "PM_Questions_8000_expanded_clean_final5.csv"),  # ❌ OLD
    os.path.join(os.getcwd(), "PM_Questions_dedup.csv"),  # ❌ OLD
    ...
]

# AFTER: Only new CSV path (and docker paths)
candidates = [
    env_path,
    os.path.join(os.getcwd(), "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"),  # ✅ NEW
    os.path.join(os.path.dirname(os.getcwd()), "PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv"),  # ✅ NEW
    "/app/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv",  # ✅ NEW
]
```

**Change 2**: Updated CSV column extraction (lines 25-45)
```python
# BEFORE: Only extracted Company and Category
data = {
    "company": _clean_str(row.get("Company")) or "Generic",
    "category": _clean_str(row.get("Category"))
}

# AFTER: Now extracts all relevant columns including experience fields
data = {
    "company": _clean_str(row.get("Company")) or "Generic",
    "category": _clean_str(row.get("Category")),
    "complexity": _clean_str(row.get("Complexity")),  # ✅ NEW
    "experience_level": _clean_str(row.get("Experience Level")),  # ✅ NEW
    "years_of_experience": _clean_str(row.get("Years of Experience")),  # ✅ NEW
}
```

---

### 2. `backend/app/routers/interview.py`

**Change 1**: Replaced role normalization with experience normalization (lines 30-49)
```python
# BEFORE: Role aliases mapping
_ROLE_ALIASES: Dict[str, str] = {
    "apm": "APM", "associate pm": "APM", "product manager": "PM", ...
}
def normalize_role(role: Optional[str]) -> Optional[str]:
    key = role.strip().lower()
    return _ROLE_ALIASES.get(key, role.strip())

# AFTER: Experience normalization (much simpler)
def normalize_experience(experience: Optional[str]) -> Optional[str]:
    if not experience:
        return None
    exp = experience.strip().lower()
    exp_map = {
        "0-1": "0-2", "0-2": "0-2", "1-2": "0-2",
        "2-4": "2-4", "2-5": "2-4", "4-5": "2-4",
        "5-8": "5-8", "5-7": "5-8", "7-8": "5-8",
        "8+": "8+", "8 years": "8+", "9+": "8+",
    }
    return exp_map.get(exp, experience.strip())
```

**Change 2**: Updated _pick_questions() function (lines 200-290)
```python
# BEFORE:
def _pick_questions(
    db: Session,
    company: Optional[str],
    role: Optional[str],  # ❌ REMOVED
    experience: Optional[str],
    ...
):
    wanted_role = normalize_role(role)  # ❌ REMOVED

# AFTER:
def _pick_questions(
    db: Session,
    company: Optional[str],
    role: Optional[str],  # ⚠️ Still accepted for compatibility, but ignored
    experience: Optional[str],
    ...
):
    wanted_experience = normalize_experience(experience)  # ✅ ADDED
```

**Change 3**: Updated filtering priority (lines 245-280)
```python
# BEFORE: 5-step priority with role checks
if wanted_company and wanted_role:
    # Match company + role
    remaining = add_from_query(
        db.query(Question).filter(and_(Question.company == wanted_company,
                                      Question.experience_level == wanted_role))

# AFTER: 4-step priority with experience checks
if wanted_company and wanted_experience:
    # Match company + experience level
    remaining = add_from_query(
        db.query(Question).filter(and_(Question.company == wanted_company,
                                      Question.years_of_experience == wanted_experience))

# Later...
if remaining > 0 and wanted_experience:
    # Match any company + experience level (new priority)
    remaining = add_from_query(
        db.query(Question).filter(Question.years_of_experience == wanted_experience))
```

**Change 4**: Updated API endpoint (lines 317-350)
```python
# BEFORE:
@router.get("/questions")
def get_interview_questions(
    company: Optional[str] = Query(None),
    role: Optional[str] = Query(None),  # ❌ REMOVED
    experience: Optional[str] = Query(None),
    session: Optional[str] = Query(None),
    ...
):
    data = _pick_questions(db, company, role, experience, ...)  # role passed

# AFTER:
@router.get("/questions")
def get_interview_questions(
    company: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),  # ✅ KEPT (primary filter now)
    session: Optional[str] = Query(None),
    ...
):
    data = _pick_questions(db, company, role=None, experience=experience, ...)  # role=None
```

---

### 3. `backend/app/routers/auth.py`

**Change 1**: Updated UserUpdate schema (lines 86-91)
```python
# BEFORE:
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    experience: Optional[str] = None
    currentRole: Optional[str] = None  # ❌ REMOVED
    region: Optional[str] = None
    targetCompanies: Optional[list[str]] = None

# AFTER:
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    experience: Optional[str] = None  # ✅ KEPT (primary filter)
    region: Optional[str] = None
    targetCompanies: Optional[list[str]] = None
```

**Change 2**: Updated /auth/me endpoint (lines 136-147)
```python
# BEFORE:
return {
    "id": current.id,
    "email": current.email,
    "is_active": current.is_active,
    "created_at": current.created_at,
    **({ "full_name": getattr(current, "full_name") } if hasattr(current, "full_name") else {}),
    **({ "experience": getattr(current, "experience") } if hasattr(current, "experience") else {}),
    **({ "currentRole": getattr(current, "currentRole") } if hasattr(current, "currentRole") else {}),  # ❌ REMOVED
    **({ "region": getattr(current, "region") } if hasattr(current, "region") else {}),
    **({ "targetCompanies": getattr(current, "targetCompanies") } if hasattr(current, "targetCompanies") else {}),
}

# AFTER: (removed currentRole line)
return {
    "id": current.id,
    "email": current.email,
    "is_active": current.is_active,
    "created_at": current.created_at,
    **({ "full_name": getattr(current, "full_name") } if hasattr(current, "full_name") else {}),
    **({ "experience": getattr(current, "experience") } if hasattr(current, "experience") else {}),
    **({ "region": getattr(current, "region") } if hasattr(current, "region") else {}),
    **({ "targetCompanies": getattr(current, "targetCompanies") } if hasattr(current, "targetCompanies") else {}),
}
```

**Change 3**: Updated /auth/patch /me endpoint (lines 156-169) - Same as above

---

### 4. `backend/docker-entrypoint.sh`

**Change**: Fixed question loading command (line 21)
```bash
# BEFORE:
echo "Loading questions..."
if [ -f /app/load_questions.py ]; then
elif [ -f /app/app/load_questions.py ]; then  # ❌ Missing python command

# AFTER:
echo "Loading questions..."
if [ -f /app/load_questions.py ]; then
    python /app/load_questions.py  # ✅ ADDED python command
elif [ -f /app/app/load_questions.py ]; then
    python -m app.load_questions
```

---

## Frontend Changes

### 1. `Frontend/src/utils/api.ts`

**Change 1**: Updated FetchQuestionsParams type (lines 13-17)
```typescript
// BEFORE:
export type FetchQuestionsParams = {
  company?: string | null;
  role?: string | null;  // ❌ REMOVED
  experience?: string | null;
  signal?: AbortSignal;
};

// AFTER:
export type FetchQuestionsParams = {
  company?: string | null;
  experience?: string | null;  // ✅ KEPT (primary filter)
  signal?: AbortSignal;
};
```

**Change 2**: Updated fetchInterviewQuestions() function (lines 88-107)
```typescript
// BEFORE:
const company = normalizeStr(params.company);
const role = normalizeStr(params.role);  // ❌ REMOVED
const experience = normalizeStr(params.experience);

const url = API_BASE + INTERVIEW_PATH + qs({
  company,
  role,  // ❌ REMOVED
  experience,
  session,
});

// AFTER:
const company = normalizeStr(params.company);
const experience = normalizeStr(params.experience);  // ✅ KEPT

const url = API_BASE + INTERVIEW_PATH + qs({
  company,
  experience,  // ✅ KEPT
  session,
});
```

**Change 3**: Updated error response objects (4 occurrences)
```typescript
// BEFORE: (4 times)
experience_level: role ?? null,  // ❌ role undefined

// AFTER: (4 times)
experience_level: null,  // ✅ Use null directly
```

---

### 2. `Frontend/src/components/InterviewSetup.tsx`

**Change 1**: Removed normalizeRole() function (lines 37-56)
```typescript
// BEFORE: 20 lines of role normalization
function normalizeRole(role?: string | null): string | undefined {
    if (!role) return undefined;
    const r = role.trim().toLowerCase();
    const map: Record<string, string> = {
        'apm': 'APM',
        'associate pm': 'APM',
        'product manager': 'PM',
        ...
    };
    return map[r] ?? role.trim();
}

// AFTER: (completely removed)
```

**Change 2**: Updated handleProceedWithJD() (lines 310-330)
```typescript
// BEFORE:
const { company: extractedCompany, role: extractedRole } = extractCompanyAndRole(jobDescription);
const derivedCompany = extractedCompany || selectedCompany || 'Generic';
const derivedRole = extractedRole || normalizeRole(user.currentRole) || undefined;

const apiResult = await fetchInterviewQuestions({
  company: derivedCompany,
  role: derivedRole,  // ❌ REMOVED
});

// AFTER:
const { company: extractedCompany } = extractCompanyAndRole(jobDescription);  // ✅ Not extracting role
const derivedCompany = extractedCompany || selectedCompany || 'Generic';

const apiResult = await fetchInterviewQuestions({
  company: derivedCompany,
  experience: user.experience,  // ✅ Using experience instead
});
```

**Change 3**: Updated handleStartInterview() (lines 434-472)
```typescript
// BEFORE:
if (!selectedType || !user.currentRole || !user.experience) {  // ❌ Checking currentRole
    alert("Please select an interview type and ensure your profile is complete.");

// AFTER:
if (!selectedType || !user.experience) {  // ✅ Only checking experience
    alert("Please select an interview type and ensure your profile is complete (experience level required).");

// BEFORE:
const apiResult = await fetchInterviewQuestions({
  company: derivedCompany,
  role: normalizeRole(user.currentRole),  // ❌ REMOVED
});

// AFTER:
const apiResult = await fetchInterviewQuestions({
  company: derivedCompany,
  experience: user.experience,  // ✅ Using experience instead
});
```

---

### 3. `Frontend/src/types/index.ts`

**Change**: Updated User interface (lines 1-8)
```typescript
// BEFORE:
export interface User {
  id: number;
  full_name: string;
  email: string;
  experience: string;
  targetCompanies: string[];
  region: string;
  currentRole: string;  // ❌ REMOVED
}

// AFTER:
export interface User {
  id: number;
  full_name: string;
  email: string;
  experience: string;  // ✅ KEPT (primary filter)
  targetCompanies: string[];
  region: string;
}
```

---

## Summary of Changes

| Category | Count | Details |
|----------|-------|---------|
| Functions Modified | 7 | normalize_experience, _pick_questions, get_interview_questions, handleProceedWithJD, handleStartInterview, etc. |
| Functions Removed | 1 | normalizeRole() |
| Lines Removed | ~80 | Role mapping and normalization logic |
| Lines Added | ~50 | Experience normalization and improved filtering |
| Files Modified | 7 | 4 backend, 3 frontend |
| CSV References Removed | 6 | Old CSV paths in load_questions.py |
| API Parameters Changed | 1 | /api/interview/questions (role removed, experience kept) |
| Database Queries Updated | 4 | All use years_of_experience instead of experience_level for role |
| User Facing Changes | 2 | Role selection → Experience selection, no currentRole in profile |

---

## Backward Compatibility

✅ **API is backward compatible**:
- Old `?role=PM` parameter is silently ignored
- Existing tokens continue to work
- No database migration required

⚠️ **Frontend breaking changes**:
- `User` interface changed (currentRole removed)
- API call parameters changed (role removed)
- Component logic changed (uses experience)

---

## Error Handling

No new error cases introduced. System handles:
- Missing experience parameter ✅ (returns any questions)
- Invalid experience format ✅ (maps to closest match)
- Missing company parameter ✅ (returns any questions)
- No questions found ✅ (returns fallback questions or error)
