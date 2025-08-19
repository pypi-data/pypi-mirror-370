"""
Workspace Release Plugin for Release Manager Tool.

This plugin handles releasing workspaces with version bumping and git operations.
Based on the Mystic Empire release script pattern.
"""

import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# Import common utilities
from ....common import cu


def run_command(command: str, description: str, cwd: Optional[Path] = None) -> Optional[str]:
    """Run a command and handle errors."""
    cu.log_and_print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, 
            check=True, encoding='utf-8', errors='replace', cwd=cwd
        )
        cu.log_and_print(f"✅ {description} completed")
        return result.stdout.strip() if result.stdout else ""
    except subprocess.CalledProcessError as e:
        cu.log_and_print(f"❌ {description} failed: {e}", level="error")
        if e.stderr:
            # Handle potential encoding issues in stderr
            try:
                error_output = e.stderr
            except UnicodeDecodeError:
                error_output = e.stderr.encode('utf-8', errors='replace').decode('utf-8')
            cu.log_and_print(f"Error output: {error_output}", level="error")
        return None
    except UnicodeDecodeError as e:
        cu.log_and_print(f"❌ {description} failed due to encoding issue: {e}", level="error")
        return None


def get_current_version() -> Optional[str]:
    """Get current version from VERSION file."""
    try:
        version_file = Path('VERSION')
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        cu.log_and_print("❌ VERSION file not found", level="error")
        return None


def bump_version(current_version: str, version_type: str) -> Optional[str]:
    """Bump version number based on type."""
    major, minor, patch = map(int, current_version.split('.'))
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        cu.log_and_print("❌ Invalid version type. Use: major, minor, or patch", level="error")
        return None
    
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str) -> bool:
    """Update the VERSION file."""
    try:
        with open('VERSION', 'w', encoding='utf-8') as f:
            f.write(new_version + '\n')
        cu.log_and_print(f"✅ Updated VERSION file to {new_version}")
        return True
    except Exception as e:
        cu.log_and_print(f"❌ Error updating VERSION file: {e}", level="error")
        return False


def update_changelog(new_version: str, version_type: str) -> bool:
    """Update CHANGELOG.md with new version entry."""
    try:
        # Read current changelog
        changelog_file = Path('CHANGELOG.md')
        if not changelog_file.exists():
            cu.log_and_print("⚠️ CHANGELOG.md not found, skipping changelog update", level="warning")
            return True
        
        with open(changelog_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get current date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create new version entry template
        version_entry = f"""## [{new_version}] - {today}

### Added ✨
- [Add your new features here]

### Changed 🔄
- [Add your changes here]

### Fixed 🐛
- [Add your bug fixes here]

### Technical 🛠️
- [Add technical improvements here]

### Documentation 📚
- [Add documentation updates here]

"""
        
        # Handle [Unreleased] section replacement
        if "[Unreleased]" in content:
            # Replace [Unreleased] with new version and date
            content = content.replace("[Unreleased]", f"[{new_version}] - {today}")
            
            # Find the new version section and add template content after it
            pattern = rf'(## \[{new_version}\] - {today}\n)'
            replacement = rf'\1{version_entry}'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            # If no [Unreleased] section, add new version at the top after the header
            header_pattern = r'(# Changelog 📝\n\nAll notable changes.*?\n\n)'
            replacement = rf'\1{version_entry}'
            content = re.sub(header_pattern, replacement, content, flags=re.DOTALL)
        
        # Write updated changelog
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        cu.log_and_print(f"✅ Updated CHANGELOG.md with version {new_version}")
        return True
    except Exception as e:
        cu.log_and_print(f"❌ Error updating CHANGELOG.md: {e}", level="error")
        return False


def get_commit_message(new_version: str, version_type: str) -> str:
    """Generate a commit message based on version type."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if version_type == "major":
        return f"🚀 Major Release: Workspace v{new_version}\n\nBreaking changes and major new features"
    elif version_type == "minor":
        return f"✨ Feature Release: Workspace v{new_version}\n\nNew features and improvements"
    else:  # patch
        return f"🐛 Bug Fix Release: Workspace v{new_version}\n\nBug fixes and minor improvements"


def get_phase_name(version: str) -> str:
    """Get development phase name based on version."""
    major, minor, _ = map(int, version.split('.'))
    
    if major == 0:
        if minor <= 3:
            return "Foundation Phase"
        elif minor <= 6:
            return "Core Development Phase"
        elif minor <= 9:
            return "Polish Phase"
        else:
            return "Pre-release Phase"
    else:
        return "Release Phase"


def run_mode(input_paths: List[Path], output_dir: Path, domain: Optional[str] = None, 
             version_type: Optional[str] = None, auto_push: bool = False, 
             force: bool = False, custom_message: Optional[str] = None, 
             **kwargs) -> None:
    """
    Run workspace release mode.
    
    Args:
        input_paths: List of input paths (not used for this plugin)
        output_dir: Output directory (not used for this plugin)
        domain: Domain context (not used for this plugin)
        version_type: Type of version bump (major, minor, patch)
        auto_push: Whether to push to remote automatically
        force: Force release even if no changes
        custom_message: Custom commit message
        **kwargs: Additional arguments
    """
    cu.log_and_print("🚀 Running Workspace Release Mode...")
    
    # Validate version type
    if not version_type:
        cu.log_and_print("❌ Version type required for workspace release", level="error")
        cu.log_and_print("Usage: --version-type major|minor|patch", level="error")
        return
    
    if version_type not in ["major", "minor", "patch"]:
        cu.log_and_print(f"❌ Invalid version type: {version_type}", level="error")
        cu.log_and_print("Use: major, minor, or patch", level="error")
        return
    
    # Get current version
    current_version = get_current_version()
    if not current_version:
        return
    
    # Calculate new version
    new_version = bump_version(current_version, version_type)
    if not new_version:
        return
    
    cu.log_and_print(f"🎯 Workspace Release Process")
    cu.log_and_print(f"🔄 Updating from {current_version} to {new_version}")
    cu.log_and_print(f"📋 Phase: {get_phase_name(new_version)}")
    cu.log_and_print("=" * 50)
    
    # Step 1: Update VERSION file
    if not update_version_file(new_version):
        return
    
    # Step 2: Update CHANGELOG.md
    if not update_changelog(new_version, version_type):
        return
    
    # Step 3: Stage all changes
    staging_result = run_command("git add .", "Staging all changes")
    if staging_result is None:
        cu.log_and_print("❌ Failed to stage changes. Aborting release.", level="error")
        return
    
    # Step 4: Check if there are changes to commit
    status = run_command("git status --porcelain", "Checking git status")
    if not status and not force:
        cu.log_and_print("⚠️ No changes to commit. Did you make any changes?", level="warning")
        cu.log_and_print("💡 Use --force flag to continue anyway", level="warning")
        return
    
    # Step 5: Commit with proper message
    commit_message = custom_message if custom_message else get_commit_message(new_version, version_type)
    commit_result = run_command(f'git commit -m "{commit_message}"', "Creating commit")
    if commit_result is None:
        cu.log_and_print("❌ Failed to create commit. Aborting release.", level="error")
        return
    
    # Step 6: Create git tag (check if it already exists)
    existing_tag = run_command(f"git tag -l v{new_version}", f"Checking if tag v{new_version} exists")
    if existing_tag:
        cu.log_and_print(f"⚠️ Tag v{new_version} already exists. Skipping tag creation.", level="warning")
    else:
        tag_result = run_command(f"git tag v{new_version}", f"Creating tag v{new_version}")
        if tag_result is None:
            cu.log_and_print("❌ Failed to create tag. Aborting release.", level="error")
            return
    
    # Step 7: Push to remote (if requested)
    if auto_push:
        cu.log_and_print("=" * 50)
        cu.log_and_print("🚀 Pushing to remote repository...")
        push_commits = run_command("git push origin main", "Pushing commits")
        push_tags = run_command(f"git push origin v{new_version}", f"Pushing tag v{new_version}")
        if push_commits is None or push_tags is None:
            cu.log_and_print("⚠️ Failed to push to remote, but release was successful locally", level="warning")
        else:
            cu.log_and_print("✅ Successfully pushed to remote repository!")
    
    # Success!
    cu.log_and_print("=" * 50)
    cu.log_and_print(f"🎉 Successfully released Workspace v{new_version}!")
    cu.log_and_print(f"📋 Phase: {get_phase_name(new_version)}")
    
    # Show what was done
    cu.log_and_print("\n✅ Completed:")
    cu.log_and_print(f"   • Updated VERSION file to {new_version}")
    cu.log_and_print(f"   • Updated CHANGELOG.md with version {new_version}")
    cu.log_and_print(f"   • Committed all changes")
    cu.log_and_print(f"   • Created git tag v{new_version}")
    if auto_push:
        cu.log_and_print(f"   • Pushed to remote repository")
    
    # Show next steps
    cu.log_and_print("\n📝 Next steps:")
    cu.log_and_print("   1. Edit CHANGELOG.md to add actual changes for this release")
    if not auto_push:
        cu.log_and_print("   2. Push to remote repository:")
        cu.log_and_print(f"      git push origin main")
        cu.log_and_print(f"      git push origin v{new_version}")
    cu.log_and_print("   3. Create release on GitHub/GitLab (if using)")
    
    # Show current status
    cu.log_and_print(f"\n📊 Current status:")
    log_result = run_command("git log --oneline -1", "Latest commit")
    latest_tag = run_command("git describe --tags --abbrev=0", "Latest tag")
    if latest_tag:
        cu.log_and_print(f"Latest tag: {latest_tag}")
    else:
        cu.log_and_print("Latest tag: None")
