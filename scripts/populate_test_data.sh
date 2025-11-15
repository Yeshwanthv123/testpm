#!/bin/bash

# Script to populate test data for regional leaderboard testing
# Run this after the backend is started

API_URL="${API_URL:-http://localhost:8000}"

echo "Populating test data..."
echo ""

# Step 1: Create test users across regions
echo "1. Creating test users with regions..."
curl -X POST "$API_URL/api/auth/admin/create-test-users" \
  -H "Content-Type: application/json" \
  -s | jq '.'

echo ""
echo "2. Migrating existing users to 'US' region..."
curl -X POST "$API_URL/api/auth/admin/migrate-regions" \
  -H "Content-Type: application/json" \
  -s | jq '.'

echo ""
echo "✅ Test data population complete!"
echo ""
echo "You can now:"
echo "1. Login with any test user (test_us_1@example.com, etc.)"
echo "2. Select a region during onboarding"
echo "3. View the regional leaderboard with users"
