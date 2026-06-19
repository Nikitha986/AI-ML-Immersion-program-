# Simple PowerShell script to test the matching API endpoints
$base = "http://127.0.0.1:8000"

Write-Host "Testing POST /match_text..."
$payload = @{ resume_text = "python sql machine learning"; jd_text = "python machine learning" } | ConvertTo-Json
try {
    $res = Invoke-RestMethod -Method Post -Uri "$base/match_text" -ContentType 'application/json' -Body $payload
    Write-Host "Response (match_text):"
    $res | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "Error calling /match_text:" $_.Exception.Message
}

Write-Host "`nTesting POST /rank_job..."
$payload2 = @{ job_id = "J001" } | ConvertTo-Json
try {
    $res2 = Invoke-RestMethod -Method Post -Uri "$base/rank_job" -ContentType 'application/json' -Body $payload2
    Write-Host "Response (rank_job):"
    $res2 | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "Error calling /rank_job:" $_.Exception.Message
}

Write-Host "`nDone. If you see JSON responses, the API is working."
