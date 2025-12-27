# Script: auth_and_push.ps1
# Uso: executa autenticação com GitHub CLI via token e faz push para origin/main
# NÃO cole tokens em chats públicos. Revogue tokens expostos primeiro.

param(
    [string]$RepoPath = "C:\Users\igorb\OneDrive\Documents\Merry OK"
)

Set-Location -Path $RepoPath

Write-Output "Configuring credential helper (manager-core)..."
git config --global credential.helper manager-core

Write-Output "Ensure GitHub CLI (gh) is installed:"
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Output "gh not found. Install GitHub CLI from https://cli.github.com/ and re-run this script."
    exit 1
}

# Prompt securely for token
$secure = Read-Host -Prompt "Cole seu novo GitHub PAT (entrada oculta)" -AsSecureString
# Convert SecureString to plain text for piping to gh
$ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$token = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

Write-Output "Logging in with gh using provided token..."
# Pipe token to gh auth login --with-token
$token | gh auth login --with-token

Write-Output "Auth status:" 
gh auth status --show-token

Write-Output "Attempting git push origin main..."
# Ensure we are on main (do not force rename)
$branch = git rev-parse --abbrev-ref HEAD
Write-Output "Current branch: $branch"

# Trigger small change to force CI if needed
if (-not (Test-Path .gh-action-trigger)) {
    "trigger" | Out-File -FilePath .gh-action-trigger -Encoding utf8 -Force
    git add .gh-action-trigger
    git commit -m "Trigger CI" -q || Write-Output "No changes to commit"
}

# Push
git push origin $branch

Write-Output "If push succeeded, check Actions tab on GitHub to see workflow runs."
Write-Output "Remember to revoke any previously exposed tokens at https://github.com/settings/tokens"
