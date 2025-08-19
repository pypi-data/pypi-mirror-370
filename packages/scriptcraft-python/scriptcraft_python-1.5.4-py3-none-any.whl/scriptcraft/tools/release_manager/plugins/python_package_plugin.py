"""
Python Package Release Plugin for Release Manager Tool.

This plugin handles releasing Python packages with version bumping, building, and PyPI uploading.
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
            check=True, encoding='utf-8', cwd=cwd
        )
        cu.log_and_print(f"✅ {description} completed")
        return result.stdout.strip() if result.stdout else ""
    except subprocess.CalledProcessError as e:
        cu.log_and_print(f"❌ {description} failed: {e}", level="error")
        cu.log_and_print(f"Error output: {e.stderr}", level="error")
        return None


def get_current_version() -> Optional[str]:
    """Get current version from _version.py file."""
    try:
        version_file = Path("implementations/python-package/scriptcraft/_version.py")
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'__version__ = "([^"]+)"', content)
            if match:
                return match.group(1)
        cu.log_and_print("❌ Could not find version in _version.py", level="error")
        return None
    except FileNotFoundError:
        cu.log_and_print("❌ _version.py file not found", level="error")
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
    """Update the _version.py file."""
    try:
        version_file = Path("implementations/python-package/scriptcraft/_version.py")
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace version line
        updated_content = re.sub(
            r'__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            content
        )
        
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        cu.log_and_print(f"✅ Updated _version.py to {new_version}")
        return True
    except Exception as e:
        cu.log_and_print(f"❌ Error updating _version.py: {e}", level="error")
        return False


def clean_build_artifacts() -> None:
    """Clean old build artifacts."""
    cu.log_and_print("🧹 Cleaning build artifacts...")
    artifacts = ["implementations/python-package/dist", "implementations/python-package/build", "implementations/python-package/*.egg-info"]
    for artifact in artifacts:
        artifact_path = Path(artifact)
        if artifact_path.exists():
            if artifact_path.is_dir():
                import shutil
                shutil.rmtree(artifact_path)
            else:
                artifact_path.unlink()
            cu.log_and_print(f"🗑️ Removed {artifact}")


def build_package() -> bool:
    """Build the Python package."""
    return run_command("python -m build", "Building package", cwd=Path("implementations/python-package")) is not None


def upload_to_pypi() -> bool:
    """Upload package to PyPI."""
    return run_command("python -m twine upload dist/*", "Uploading to PyPI", cwd=Path("implementations/python-package")) is not None


def get_commit_message(new_version: str, version_type: str) -> str:
    """Generate a commit message based on version type."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if version_type == "major":
        return f"🚀 Major Release: ScriptCraft Python v{new_version}\n\nBreaking changes and major new features"
    elif version_type == "minor":
        return f"✨ Feature Release: ScriptCraft Python v{new_version}\n\nNew features and improvements"
    else:  # patch
        return f"🐛 Bug Fix Release: ScriptCraft Python v{new_version}\n\nBug fixes and minor improvements"


def run_mode(input_paths: List[Path], output_dir: Path, domain: Optional[str] = None, 
             version_type: Optional[str] = None, auto_push: bool = False, 
             force: bool = False, custom_message: Optional[str] = None, 
             skip_pypi: bool = False, **kwargs) -> None:
    """
    Run Python package release mode.
    
    Args:
        input_paths: List of input paths (not used for this plugin)
        output_dir: Output directory (not used for this plugin)
        domain: Domain context (not used for this plugin)
        version_type: Type of version bump (major, minor, patch)
        auto_push: Whether to push to remote automatically
        force: Force release even if no changes
        custom_message: Custom commit message
        skip_pypi: Skip PyPI upload
        **kwargs: Additional arguments
    """
    cu.log_and_print("🚀 Running Python Package Release Mode...")
    
    # Validate version type
    if not version_type:
        cu.log_and_print("❌ Version type required for Python package release", level="error")
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
    
    cu.log_and_print(f"🔧 ScriptCraft Python Package Release Process")
    cu.log_and_print(f"🔄 Updating from {current_version} to {new_version}")
    cu.log_and_print("=" * 50)
    
    # Step 1: Update version file
    if not update_version_file(new_version):
        return
    
    # Step 2: Clean build artifacts
    clean_build_artifacts()
    
    # Step 3: Build package
    if not build_package():
        cu.log_and_print("❌ Build failed. Aborting release.", level="error")
        return
    
    # Step 4: Upload to PyPI (unless skipped)
    if not skip_pypi:
        if not upload_to_pypi():
            cu.log_and_print("❌ PyPI upload failed. Aborting release.", level="error")
            return
        cu.log_and_print("✅ Successfully uploaded to PyPI!")
    else:
        cu.log_and_print("⏭️ Skipping PyPI upload (--skip-pypi flag)")
    
    # Step 5: Stage all changes
    staging_result = run_command("git add .", "Staging all changes")
    if staging_result is None:
        cu.log_and_print("❌ Failed to stage changes. Aborting release.", level="error")
        return
    
    # Step 6: Check if there are changes to commit
    status = run_command("git status --porcelain", "Checking git status")
    if not status and not force:
        cu.log_and_print("⚠️ No changes to commit. Did you make any changes?", level="warning")
        cu.log_and_print("💡 Use --force flag to continue anyway", level="warning")
        return
    
    # Step 7: Commit with proper message
    commit_message = custom_message if custom_message else get_commit_message(new_version, version_type)
    commit_result = run_command(f'git commit -m "{commit_message}"', "Creating commit")
    if commit_result is None:
        cu.log_and_print("❌ Failed to create commit. Aborting release.", level="error")
        return
    
    # Step 8: Create git tag (check if it already exists)
    existing_tag = run_command(f"git tag -l v{new_version}", f"Checking if tag v{new_version} exists")
    if existing_tag:
        cu.log_and_print(f"⚠️ Tag v{new_version} already exists. Skipping tag creation.", level="warning")
    else:
        tag_result = run_command(f"git tag v{new_version}", f"Creating tag v{new_version}")
        if tag_result is None:
            cu.log_and_print("❌ Failed to create tag. Aborting release.", level="error")
            return
    
    # Step 9: Push to remote (if requested)
    if auto_push:
        cu.log_and_print("=" * 50)
        cu.log_and_print("🚀 Pushing to remote repository...")
        push_commits = run_command("git push origin master", "Pushing commits")
        push_tags = run_command(f"git push origin v{new_version}", f"Pushing tag v{new_version}")
        if push_commits is None or push_tags is None:
            cu.log_and_print("⚠️ Failed to push to remote, but release was successful locally", level="warning")
        else:
            cu.log_and_print("✅ Successfully pushed to remote repository!")
    
    # Success!
    cu.log_and_print("=" * 50)
    cu.log_and_print(f"🎉 Successfully released ScriptCraft Python v{new_version}!")
    
    # Show what was done
    cu.log_and_print("\n✅ Completed:")
    cu.log_and_print(f"   • Updated _version.py to {new_version}")
    cu.log_and_print(f"   • Cleaned build artifacts")
    cu.log_and_print(f"   • Built package")
    if not skip_pypi:
        cu.log_and_print(f"   • Uploaded to PyPI")
    cu.log_and_print(f"   • Committed all changes")
    cu.log_and_print(f"   • Created git tag v{new_version}")
    if auto_push:
        cu.log_and_print(f"   • Pushed to remote repository")
    
    # Show next steps
    cu.log_and_print("\n📝 Next steps:")
    if not auto_push:
        cu.log_and_print("   1. Push to remote repository:")
        cu.log_and_print(f"      git push origin master")
        cu.log_and_print(f"      git push origin v{new_version}")
    cu.log_and_print("   2. Test the new package:")
    cu.log_and_print(f"      pip install scriptcraft-python=={new_version}")
    cu.log_and_print("   3. Update embedded Python builds with new version")
    
    # Show current status
    cu.log_and_print(f"\n📊 Current status:")
    log_result = run_command("git log --oneline -1", "Latest commit")
    latest_tag = run_command("git describe --tags --abbrev=0", "Latest tag")
    if latest_tag:
        cu.log_and_print(f"Latest tag: {latest_tag}")
    else:
        cu.log_and_print("Latest tag: None")
