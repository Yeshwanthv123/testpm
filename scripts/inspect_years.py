from backend.load_questions import _canonicalize_years
import csv
s=set()
with open('backend/PM_Questions_FINAL_12x2000_Formatted_Final_HUMANIZED.csv','r',encoding='utf-8-sig') as f:
    r=csv.DictReader(f)
    for row in r:
        s.add(_canonicalize_years(row.get('Years of Experience')))
print('Unique normalized buckets:')
for x in sorted(x for x in s if x):
    print(x)
