# Installing this skill

This folder *is* the skill. "Installing" it just means putting a copy where Claude Code looks for personal skills: `~/.claude/skills/website-growth-engine/`. You never need to reference this exact folder path again afterward — Claude Code finds it there automatically in every project.

## macOS — no folder navigation needed

1. Get the archive (`website-growth-engine.tar.gz`) onto your Mac — AirDrop, email, or a cloud drive all work. It's a `.tar.gz` rather than a `.zip` because that format keeps the "this file can run" permission on the installer script intact; a zip built on Windows would lose it.
2. Double-click the archive in Finder to extract it (Archive Utility opens `.tar.gz` the same as `.zip`). Finder will make a `website-growth-engine` folder next to it.
3. Open that extracted folder and double-click **`install.command`**.
   - If macOS shows "cannot be opened because it is from an unidentified developer," Control-click (or right-click) `install.command` and choose **Open**, then confirm.
4. A Terminal window runs the install and tells you it's done. You can close it and delete the extracted folder and the archive — the copy that matters now lives in `~/.claude/skills/website-growth-engine/`.
5. Open (or restart) Claude Code. The skill is available in any project from here on.

## macOS/Linux — Terminal

```bash
cd path/to/website-growth-engine
bash install.sh
```

## Windows — PowerShell

```powershell
cd path\to\website-growth-engine
./install.ps1
```

## Re-installing / updating

Re-running the installer is safe: it moves any existing install aside to a timestamped `.backup.<date>` folder before copying the new version in, so nothing is silently overwritten.

## Uninstalling

Delete `~/.claude/skills/website-growth-engine/` (and any `.backup.*` copies you no longer want).

## Building the distributable archive yourself

If you change this folder and want a fresh archive to hand to another machine, run `bash package_release.sh`; it writes `website-growth-engine.tar.gz` next to this folder, with the installer scripts' executable permission preserved inside the archive.
