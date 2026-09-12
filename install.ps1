# Install this skill folder into Claude Code's personal skills directory
# (Windows counterpart to install.sh / install.command).
$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillName = "website-growth-engine"
$SkillsRoot = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $HOME ".claude\skills" }
$TargetDir = Join-Path $SkillsRoot $SkillName

New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null

if (Test-Path $TargetDir) {
    $Backup = "$TargetDir.backup.$(Get-Date -Format yyyyMMdd-HHmmss)"
    Write-Host "Existing install found at $TargetDir - backing it up to $Backup"
    Move-Item -Path $TargetDir -Destination $Backup
}

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -Path (Join-Path $SourceDir '*') -Destination $TargetDir -Recurse -Force

Write-Host ""
Write-Host "Installed website-growth-engine to: $TargetDir"
Write-Host "Open (or restart) Claude Code - it will now appear as an available skill."
