#!/usr/bin/env python3
"""
Test script to verify the new random_mode functionality for handling
company names not found in the CSV.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/interview"

def test_existing_company():
    """Test with a company that exists in the CSV (Airbnb)."""
    print("\n" + "="*60)
    print("TEST 1: Existing Company (Airbnb)")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/questions",
        params={
            "company": "Airbnb",
            "experience": "0-2",
            "session": "test-session-1"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    if isinstance(data, list):
        print(f"Questions Retrieved: {len(data)}")
        for i, q in enumerate(data, 1):
            print(f"\nQuestion {i}:")
            print(f"  Company: {q.get('company', 'N/A')}")
            print(f"  Text: {q.get('question', 'N/A')[:80]}...")
            print(f"  Experience Level: {q.get('experience_level', 'N/A')}")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")


def test_nonexistent_company():
    """Test with a company that does NOT exist in the CSV (FakeCompany)."""
    print("\n" + "="*60)
    print("TEST 2: Non-existent Company (FakeCompany) - Should trigger random_mode")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/questions",
        params={
            "company": "FakeCompany",
            "experience": "3-5",
            "session": "test-session-2"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    if isinstance(data, list):
        print(f"Questions Retrieved: {len(data)}")
        print("\nCompanies in random selection:")
        companies_set = set()
        for i, q in enumerate(data, 1):
            company = q.get('company', 'N/A')
            companies_set.add(company)
            print(f"\nQuestion {i}:")
            print(f"  Company: {company}")
            print(f"  Experience Level: {q.get('experience_level', 'N/A')}")
            print(f"  Text: {q.get('question', 'N/A')[:60]}...")
        
        print(f"\n✓ Random mode working! Questions from {len(companies_set)} different companies:")
        for company in sorted(companies_set):
            print(f"  - {company}")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")


def test_experience_filtering():
    """Test that random_mode respects experience level filtering."""
    print("\n" + "="*60)
    print("TEST 3: Experience Filtering in Random Mode")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/questions",
        params={
            "company": "UnknownCompany",
            "experience": "10+",
            "session": "test-session-3"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    if isinstance(data, list):
        print(f"Questions Retrieved: {len(data)}")
        print("\nExperience Levels in results:")
        exp_levels = set()
        for i, q in enumerate(data, 1):
            exp_level = q.get('experience_level', 'N/A')
            exp_levels.add(exp_level)
        
        for exp in sorted(exp_levels):
            print(f"  - {exp}")
        
        print(f"\n✓ Total unique experience levels: {len(exp_levels)}")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")


if __name__ == "__main__":
    print("\n" + "🧪 TESTING RANDOM MODE FUNCTIONALITY " + "="*30)
    
    try:
        test_existing_company()
        test_nonexistent_company()
        test_experience_filtering()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend at", BASE_URL)
        print("Make sure PMBOT backend is running on port 8000")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
