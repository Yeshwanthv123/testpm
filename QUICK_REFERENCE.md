# Quick Reference: Experience-Level Based Question Filtering

## What Changed?

Your PM Bot now filters interview questions by **years of experience** instead of **job role**.

### Before ❌
- Asked users: "What is your current role?" (APM, PM, Senior PM, etc.)
- Filtered questions based on that role
- Old CSV: `PM_Questions_8000_expanded_clean_final5.csv`

### After ✅
- Asks users: "How many years of experience?" (0-2, 2-4, 5-8, 8+)
- Filters questions based on years of experience
- New CSV: `PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`

## Question Filtering Priority

When a user selects a company and experience level:

1. **First choice**: Questions from that company AND that experience level
2. **Second choice**: Questions from that company (any experience level)
3. **Third choice**: Questions for that experience level (any company)
4. **Last resort**: Any available questions

This ensures relevant questions are always returned!

## API Changes

### Before
```
GET /api/interview/questions?company=Google&role=PM&experience=0-2&session=abc123
```

### After
```
GET /api/interview/questions?company=Google&experience=0-2&session=abc123
```

The `role` parameter is no longer used or required.

## CSV Column Mapping

| CSV Column | Purpose | Example |
|-----------|---------|---------|
| Question | Question text | "How would you improve Airbnb's search..." |
| Company | Company name | Airbnb |
| Category | Question category | Strategic, Leadership, etc. |
| Complexity | Difficulty level | Easy, Medium, Hard |
| Experience Level | PM level (metadata) | APM, PM, Senior PM, etc. |
| **Years of Experience** | **Filter field** | **0-2, 2-4, 5-8, 8+** |

## User Profile Changes

### Before
```javascript
User {
  experience: "0-2",
  currentRole: "APM"  // ❌ Removed
}
```

### After
```javascript
User {
  experience: "0-2"   // ✅ Used for filtering
}
```

## How to Test Locally

1. **Load questions** (if using Docker):
   ```bash
   python app/load_questions.py
   ```

2. **Test API**:
   ```bash
   # Experience only
   curl "http://localhost:8000/api/interview/questions?experience=0-2"
   
   # Company + Experience
   curl "http://localhost:8000/api/interview/questions?company=Google&experience=5-8"
   
   # Company only
   curl "http://localhost:8000/api/interview/questions?company=Meta"
   ```

3. **Expected response**:
   ```json
   [
     {
       "id": 123,
       "question": "Your question text...",
       "company": "Google",
       "category": "Strategic",
       "complexity": "Easy",
       "experience_level": "APM",
       "years_of_experience": "0-2",
       "skills": ["Strategy", "Prioritization"]
     },
     ...
   ]
   ```

## Files to Delete (Old)

You can safely delete:
- ❌ `backend/PM_Questions_8000_expanded_clean_final5.csv` (old CSV - no longer used)

## Files to Keep (New)

- ✅ `backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv` (new CSV - required)

## Environment Setup

No special environment variables needed! The system automatically finds the new CSV in:
1. Environment variable: `PM_QUESTIONS_CSV`
2. Current directory: `PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`
3. Parent directory: `PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`
4. Docker /app: `/app/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv`

## Troubleshooting

### "No questions available" error
1. Check CSV file exists at expected path
2. Run `python app/load_questions.py` to load questions
3. Check database has questions: `SELECT COUNT(*) FROM questions;`

### Questions not matching experience level
1. Verify CSV has correct "Years of Experience" values (0-2, 2-4, 5-8, 8+)
2. Check that experience parameter matches exactly (case-sensitive)
3. System will still return questions if no exact match is found

### Company filtering not working
1. Verify company name matches CSV exactly (case-sensitive)
2. Check that CSV has questions for that company
3. System falls back to generic/any company if needed

## Support

Check `MIGRATION_SUMMARY.md` for detailed technical documentation.
