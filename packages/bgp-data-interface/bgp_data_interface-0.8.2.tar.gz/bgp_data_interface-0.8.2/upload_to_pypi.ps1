# upload_to_pypi script
# This script updates the version in pyproject.toml,
# commits and pushes to gitlab,
# builds a new distribution,
# and uploads it to PyPI
#
# Usage: .\upload_to_pypi.ps1 -NewVersion "0.7.5" -CommitMessage "Release version 0.7.5"
#

param (
    [Parameter(Mandatory=$true)]
    [string]$NewVersion,

    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

Set-Variable -Name "PYPI_TOKEN_PATH" -Value "../pypi_token.txt" -Option Constant






# Updates the new version in pyproject.toml
function UpdateNewVersion() {
    $tomlPath = "pyproject.toml"
    $content = Get-Content $tomlPath

    # Replace the line that starts with 'version ='
    $content = $content | ForEach-Object {
        if ($_ -match '^\s*version\s*=\s*".*"') {
            "version = `"$NewVersion`""
        } else {
            $_
        }
    }

    # Write the updated content back to the file
    Set-Content -Path $tomlPath -Value $content

    Write-Host "Updated version in $tomlPath to $NewVersion."
}







# Commit and push to gitlab
function CommitAndPush() {
    git add .
    git commit -m $CommitMessage
    git push origin main

    Write-Host "Changes committed and pushed to GitLab."
}






function BuildAndUploadToPyPI() {
    # Delete old distributions
    if (Test-Path "dist") {
        Remove-Item -Path "dist" -Recurse
    }

    # Build a new distribution
    py -m build

    # Ensure the PyPI token is set in the environment variable
    $token = Get-Content $PYPI_TOKEN_PATH | Select-Object -First 1
    $env:TWINE_PASSWORD = $token

    # Upload the new distribution to PyPI
    py -m twine upload -u __token__ dist/*

    Write-Host "New distribution built and uploaded to PyPI."
}




# Run the script
UpdateNewVersion
CommitAndPush
BuildAndUploadToPyPI
