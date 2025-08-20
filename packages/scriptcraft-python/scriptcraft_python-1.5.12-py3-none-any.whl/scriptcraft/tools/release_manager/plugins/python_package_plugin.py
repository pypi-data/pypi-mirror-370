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


def _get_workspace_version_strategy() -> str:
    """Determine workspace versioning strategy: mirror | independent | none.

    Priority: ENV WORKSPACE_VERSION_STRATEGY > config.framework.packaging.workspace_version_strategy > 'mirror'
    """
    import os

    # 1) Environment override
    env_value = os.environ.get("WORKSPACE_VERSION_STRATEGY")
    if env_value:
        return env_value.strip().lower()

    # 2) Config value if available
    try:
        config = cu.get_config()
        if config is not None:
            framework_cfg = config.get_framework_config() if hasattr(config, 'get_framework_config') else None
            packaging = getattr(framework_cfg, 'packaging', None)
            if isinstance(packaging, dict):
                value = packaging.get('workspace_version_strategy')
                if isinstance(value, str) and value.strip():
                    return value.strip().lower()
    except Exception:
        # Fallback below on any issue
        pass

    # 3) Default
    return 'mirror'


def get_current_version() -> Optional[str]:
    """Get current version from _version.py file."""
    try:
        version_file = Path("scriptcraft/_version.py")
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
        version_file = Path("scriptcraft/_version.py")
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
    artifacts = ["dist", "build", "*.egg-info"]
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
    return run_command("python -m build", "Building package") is not None


def upload_to_pypi() -> bool:
    """Upload package to PyPI."""
    return run_command("python -m twine upload dist/*", "Uploading to PyPI") is not None


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
    
    cu.log_and_print(f"🔧 ScriptCraft Python Package Release Process")
    cu.log_and_print("=" * 50)
    
    # Store original directory for later restoration
    import os
    original_cwd = os.getcwd()
    submodule_dir = Path("implementations/python-package")
    
    cu.log_and_print(f"📁 Working in submodule directory: {submodule_dir}")
    os.chdir(submodule_dir)
    
    # Get current version (now that we're in the submodule directory)
    current_version = get_current_version()
    if not current_version:
        return
    
    # Calculate new version
    new_version = bump_version(current_version, version_type)
    if not new_version:
        return
    
    cu.log_and_print(f"🔄 Updating from {current_version} to {new_version}")
    
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
    
    # Step 5: Stage all changes (we're now in the submodule directory)
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
        cu.log_and_print("💡 Check git status and ensure changes are staged", level="error")
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
        push_commits = run_command("git push origin main", "Pushing commits")
        push_tags = run_command(f"git push origin v{new_version}", f"Pushing tag v{new_version}")
        if push_commits is None or push_tags is None:
            cu.log_and_print("⚠️ Failed to push to remote, but release was successful locally", level="warning")
        else:
            cu.log_and_print("✅ Successfully pushed to remote repository!")
    
    # Step 10: Return to original directory and update main workspace
    cu.log_and_print("📁 Returning to main workspace...")
    os.chdir(original_cwd)
    
    # Update the submodule reference in the main workspace
    cu.log_and_print("🔄 Updating submodule reference in main workspace...")
    submodule_update = run_command("git submodule update --remote implementations/python-package", "Updating submodule reference")
    if submodule_update is None:
        cu.log_and_print("⚠️ Failed to update submodule reference", level="warning")
    
    # Stage and commit the submodule update in main workspace
    main_staging = run_command("git add implementations/python-package", "Staging submodule update")
    if main_staging is None:
        cu.log_and_print("⚠️ Failed to stage submodule update", level="warning")
    else:
        main_commit = run_command(f'git commit -m "📦 Update python-package submodule to v{new_version}"', "Committing submodule update")
        if main_commit is None:
            cu.log_and_print("⚠️ Failed to commit submodule update", level="warning")
        
        # Push main workspace changes if auto_push is enabled
        if auto_push:
            main_push = run_command("git push origin main", "Pushing main workspace changes")
            if main_push is None:
                cu.log_and_print("⚠️ Failed to push main workspace changes", level="warning")

    # Workspace versioning strategy handling
    strategy = _get_workspace_version_strategy()
    cu.log_and_print(f"🧭 Workspace version strategy: {strategy}")
    if strategy == 'mirror':
        # Write VERSION file, commit, tag, and push (if requested)
        try:
            Path("VERSION").write_text(f"{new_version}\n", encoding='utf-8')
            staged = run_command("git add VERSION", "Staging workspace VERSION file")
            if staged is None:
                cu.log_and_print("⚠️ Failed to stage VERSION file", level="warning")
            else:
                committed = run_command(f'git commit -m " Workspace v{new_version} (mirror python-package)"', "Committing workspace VERSION")
                # Create tag if it doesn't exist
                existing_ws_tag = run_command(f"git tag -l v{new_version}", f"Checking workspace tag v{new_version}")
                if not existing_ws_tag:
                    _ = run_command(f"git tag v{new_version}", f"Creating workspace tag v{new_version}")
                # Push if requested
                if auto_push:
                    _ = run_command("git push origin main", "Pushing workspace VERSION commit")
                    _ = run_command(f"git push origin v{new_version}", f"Pushing workspace tag v{new_version}")
        except Exception as e:
            cu.log_and_print(f"⚠️ Workspace mirroring failed: {e}", level="warning")
    elif strategy in ('independent', 'none'):
        cu.log_and_print("ℹ️ Skipping workspace version mirroring (strategy independent/none)")
    
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
        cu.log_and_print(f"      git push origin main")
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
