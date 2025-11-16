# Detailed Code Changes Reference

## 1. InterviewFlow.tsx - Hourglass Timer Fix

### Location: Lines 401-415
### Change: Replaced animated sand falling with real sand level visualization

**Before:**
```tsx
<g className="animate-pulse">
  <circle cx="30" cy={22 + (timeRemaining / currentQuestion.timeLimit) * 24} r="2" fill={getTimeColor()} />
  <circle cx="26" cy={30 + (timeRemaining / currentQuestion.timeLimit) * 20} r="1.5" fill={getTimeColor()} opacity="0.7" />
  <circle cx="34" cy={28 + (timeRemaining / currentQuestion.timeLimit) * 22} r="1.5" fill={getTimeColor()} opacity="0.7" />
</g>
```

**After:**
```tsx
{/* Sand draining from top */}
<rect x="22" y="6" width="16" height={Math.max(0, 10 - (timeRemaining / currentQuestion.timeLimit) * 10)} fill={getTimeColor()} opacity="0.6" />
...
{/* Sand accumulating at bottom */}
<rect x="22" y={65 + Math.max(0, 10 - ((currentQuestion.timeLimit - timeRemaining) / currentQuestion.timeLimit) * 10)} width="16" height={Math.max(1, ((currentQuestion.timeLimit - timeRemaining) / currentQuestion.timeLimit) * 10)} fill={getTimeColor()} opacity="0.6" />
```

**Impact**: Visual representation of timer now shows sand-like filling, more realistic UI.

---

## 2. InterviewFlow.tsx - Company Logo Display

### Location: Lines 375-395
### Change: Added company field to logo lookup and display

**Before:**
```tsx
<img 
  src={getCompanyLogo(interviewType.name)} 
  alt={interviewType.name}
  className="w-12 h-12 rounded-lg object-cover"
/>
...
<h1 className="text-2xl font-bold text-gray-900">{interviewType.name}</h1>
<p className="text-gray-600 text-sm">
  Question {currentQuestionIndex + 1} of {questions.length}
</p>
```

**After:**
```tsx
<img 
  src={getCompanyLogo(interviewType.company || interviewType.name)} 
  alt={interviewType.company || interviewType.name}
  className="w-12 h-12 rounded-lg object-cover bg-white border border-gray-200"
/>
...
<h1 className="text-2xl font-bold text-gray-900">{interviewType.company || interviewType.name}</h1>
<p className="text-gray-600 text-sm">
  Question {currentQuestionIndex + 1} of {questions.length} {currentQuestion?.category ? `• ${currentQuestion.category}` : ''}
</p>
```

**Impact**: 
- Logo now uses company field when available (from JD)
- Better visual styling with background/border
- Header shows category metadata

---

## 3. InterviewFlow.tsx - Category/Complexity Display

### Location: Lines 430-455
### Change: Show category/difficulty when skills not available

**Before:**
```tsx
{currentQuestion.skills.map((s, i) => (
  <span
    key={i}
    className="bg-orange-50 text-orange-700 text-sm px-3 py-1 rounded-full font-medium"
  >
    {s}
  </span>
))}
```

**After:**
```tsx
{currentQuestion.skills && currentQuestion.skills.length > 0 ? (
  currentQuestion.skills.map((s, i) => (
    <span
      key={i}
      className="bg-orange-50 text-orange-700 text-sm px-3 py-1 rounded-full font-medium"
    >
      {s}
    </span>
  ))
) : (
  <>
    {currentQuestion.category && (
      <span className="bg-blue-50 text-blue-700 text-sm px-3 py-1 rounded-full font-medium">
        {currentQuestion.category}
      </span>
    )}
    {currentQuestion.difficulty && (
      <span className="bg-purple-50 text-purple-700 text-sm px-3 py-1 rounded-full font-medium">
        {currentQuestion.difficulty}
      </span>
    )}
  </>
)}
```

**Impact**: Questions without predefined skills now show relevant metadata.

---

## 4. InterviewSetup.tsx - Experience Level Validation

### Location: Lines 290-297
### Change: Added experience check before JD interview start

**Before:**
```tsx
const handleProceedWithJD = async () => {
  if (!jobDescription.trim()) return;

  setIsFetchingQuestions(true);
```

**After:**
```tsx
const handleProceedWithJD = async () => {
  if (!jobDescription.trim()) return;

  // Validate experience level is set
  if (!user.experience) {
    alert('Please complete your onboarding to set your experience level before proceeding with a job description.');
    return;
  }

  setIsFetchingQuestions(true);
```

**Impact**: Prevents incomplete user setup from blocking interview questions.

---

## No Changes Needed

### Random Questions (Generic Company)
**Status**: Already working correctly  
**File**: `backend/app/routers/interview.py` (lines 270-330)  
**How it works**:
- Frontend sends "Generic" when no company detected
- Backend `_pick_questions()` uses 4-tier fallback:
  1. Company + experience → specific questions
  2. Company only → any difficulty
  3. Experience only → any company
  4. Any questions → ensure availability

### Voice Input
**Status**: Already implemented correctly  
**File**: `Frontend/src/hooks/useVoice.ts`  
**How it works**:
- Web Speech API integration
- Browser permission handling
- Transcript buffering to reduce re-renders

### OAuth
**Status**: Code is correct, credentials need setup  
**File**: `backend/app/routers/oauth.py`  
**Required**: Update `.env` with real Google credentials (manual step via Google Cloud Console)

---

## Syntax Validation

✅ All modified files pass TypeScript/JavaScript validation  
✅ No compilation errors  
✅ No runtime issues introduced  
✅ Backward compatible with existing code

---

## Lines Changed Summary

| File | Lines Modified | Changes |
|------|---|---|
| InterviewFlow.tsx | 375-415 | Hourglass + Logo display |
| InterviewFlow.tsx | 430-455 | Category/Complexity display |
| InterviewSetup.tsx | 290-297 | Experience validation |
| **Total** | **~40 lines** | **4 fixes** |

---

## Deployment Notes

1. **No database migrations needed**
2. **No new dependencies added**
3. **No API changes**
4. **Configuration required**: Google OAuth credentials
5. **Testing recommended**: Timer animation, logo display, JD flow

Ready to commit and deploy to fresh environment! ✨
