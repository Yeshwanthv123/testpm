# Script to populate test data for regional leaderboard testing
# Run this after the backend is started

param(
    [string]$ApiUrl = "http://localhost:8000"
)

Write-Host "Populating test data..." -ForegroundColor Green
Write-Host ""

# Step 1: Create test users across regions
Write-Host "1. Creating test users with regions..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/api/auth/admin/create-test-users" `
        -Method POST `
        -ContentType "application/json" `
        -UseBasicParsing
    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
    Write-Host "✓ Test users created" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to create test users: $_" -ForegroundColor Red
}

Write-Host ""

# Step 2: Migrate existing users to 'US' region
Write-Host "2. Migrating existing users to 'US' region..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/api/auth/admin/migrate-regions" `
        -Method POST `
        -ContentType "application/json" `
        -UseBasicParsing
    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host
    Write-Host "✓ Users migrated" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to migrate users: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Test data population complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "1. Login with any test user (test_us_1@example.com, password: test123)" -ForegroundColor Yellow
Write-Host "2. Select a region during onboarding" -ForegroundColor Yellow
Write-Host "3. View the regional leaderboard with users" -ForegroundColor Yellow
