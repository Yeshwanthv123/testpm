# Feature Flow Diagram: Random Questions for Unknown Companies

## Complete User Journey

```
┌────────────────────────────────────────────────────────────────┐
│                    USER UPLOADS JD                             │
│                                                                │
│  Company: "Tesla" or "Facebook" or any unknown company        │
│  Experience: "8 years"                                        │
│  Role: Senior PM                                              │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
        ┌──────────────────────────────────┐
        │ Backend AI Analysis              │
        ├──────────────────────────────────┤
        │ Extract:                         │
        │ - company_name: "Tesla"          │
        │ - years_of_experience: "8 years" │
        │ - level: "Strategic"             │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │ Company Validation               │
        ├──────────────────────────────────┤
        │ Is "Tesla" in CSV?               │
        │                                  │
        │ NO ❌ → random_mode = TRUE       │
        └────────────┬─────────────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────────────┐
   │    Experience Level Normalization               │
   ├─────────────────────────────────────────────────┤
   │ Input: "8 years"                               │
   │ normalize_experience("8 years")                 │
   │                                                │
   │ Returns:                                       │
   │ • Bucket: "6-10"                              │
   │ • Role: "Senior PM"                           │
   │                                                │
   │ ✅ EXACTLY WHAT YOU WANTED!                    │
   └────────────┬────────────────────────────────────┘
                │
                ▼
    ┌────────────────────────────────────────┐
    │ Question Selection Logic               │
    ├────────────────────────────────────────┤
    │ random_mode = TRUE                    │
    │ wanted_experience = "6-10"            │
    │                                        │
    │ Query Tier 1:                         │
    │ SELECT 8 questions WHERE              │
    │   years_of_experience = "6-10" AND    │
    │   experience_level NOT IN              │
    │     (Principal, Director)              │
    │                                        │
    │ Possible Results from:                │
    │ • Google                              │
    │ • Meta                                │
    │ • Amazon                              │
    │ • Apple                               │
    │ • Microsoft                           │
    │ • Netflix                             │
    │ • Uber                                │
    │ • Airbnb                              │
    │ • Stripe                              │
    │ • Salesforce                          │
    │ • Freshworks                          │
    │ • Zoho                                │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Questions Returned with Company Info   │
    ├────────────────────────────────────────┤
    │ [                                      │
    │   {                                    │
    │     id: 123,                          │
    │     question: "How would you...",     │
    │     company: "Google",                │
    │     years_of_experience: "6-10",      │
    │     experience_level: "Senior PM",    │
    │     skills: [...]                     │
    │   },                                  │
    │   {                                   │
    │     id: 456,                          │
    │     question: "Design a feature...",  │
    │     company: "Amazon",                │
    │     years_of_experience: "6-10",      │
    │     experience_level: "Senior PM",    │
    │     skills: [...]                     │
    │   },                                  │
    │   ... (8 total questions)             │
    │ ]                                     │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Frontend Display                       │
    ├────────────────────────────────────────┤
    │                                        │
    │ ┌──────────────────────────────┐      │
    │ │ [🔗 Google]  Google          │      │
    │ │                              │      │
    │ │ Question 1 of 8              │      │
    │ │ How would you evaluate the   │      │
    │ │ success of a feature?        │      │
    │ │                              │      │
    │ │ [Strategy] [Analysis] [PM]   │      │
    │ └──────────────────────────────┘      │
    │                                        │
    │ ┌──────────────────────────────┐      │
    │ │ [📦 Amazon]  Amazon          │      │
    │ │                              │      │
    │ │ Question 2 of 8              │      │
    │ │ Design a feature that...     │      │
    │ │                              │      │
    │ │ [Design] [Growth] [Metrics]  │      │
    │ └──────────────────────────────┘      │
    │                                        │
    │ ... (6 more questions visible)        │
    │                                        │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ User Practices Interview               │
    ├────────────────────────────────────────┤
    │ • Sees company name + logo per Q      │
    │ • Gets feedback from AI               │
    │ • Learns about multiple companies     │
    │ • All questions match their level     │
    │   (6-10 years = Senior PM)            │
    └────────────────────────────────────────┘
```

## Experience Level Mapping Detail

```
User Says "8 Years"
       │
       ▼
normalize_experience("8 years")
       │
       ├─> Clean input: "8"
       ├─> Try numeric match: v = 8
       ├─> Check: 6 <= 8 <= 10? YES ✅
       │
       ▼
Return ("6-10", "Senior PM")
       │
       ├─> Bucket: "6-10"
       │   (will get questions marked with years_of_experience = "6-10")
       │
       └─> Role: "Senior PM"
           (will filter OUT Principal/Director questions)
```

## Random Selection Example Output

```
8 Questions Fetched (random from multiple companies):

1. [Google] "How would you approach market expansion?"
   Category: Strategic | Years: 6-10 | Level: Senior PM

2. [Amazon] "Design a recommendation algorithm"
   Category: Product Design | Years: 6-10 | Level: Senior PM

3. [Meta] "Analyze user engagement drop - what do you do?"
   Category: Metrics | Years: 6-10 | Level: Senior PM

4. [Stripe] "How do you prioritize roadmap items?"
   Category: Prioritization | Years: 6-10 | Level: Senior PM

5. [Microsoft] "What metrics matter for this feature?"
   Category: Metrics | Years: 6-10 | Level: Senior PM

6. [Uber] "Handle conflicting stakeholder priorities"
   Category: Leadership | Years: 6-10 | Level: Senior PM

7. [Salesforce] "Describe your go-to-market strategy"
   Category: Execution | Years: 6-10 | Level: Senior PM

8. [Netflix] "How would you evaluate success?"
   Category: Strategic | Years: 6-10 | Level: Senior PM
```

## Key Points ✅

1. **Company Unknown?** → No problem! Use random mode
2. **User says "8 years"?** → Maps to "6-10" bucket (Senior PM)
3. **8 Random Questions** → From any of 12 CSV companies
4. **All matched** → To user's experience level
5. **Visual attribution** → Logo + company name per question
6. **Seamless experience** → User doesn't know company wasn't matched!
