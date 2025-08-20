# Release Manager 🚀

Automated release management for Python packages with plugin-based workflows. Supports version bumping, PyPI uploading, git operations, and custom release processes.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This tool was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
release_manager/
├── __init__.py              # Package interface and metadata
├── main.py                  # Main tool implementation
├── env.py                   # Environment detection
├── plugins/                 # Plugin system
│   ├── __init__.py         # Plugin registry and loading
│   ├── registry.py         # Plugin registry class
│   ├── python_package_plugin.py  # Python package releases
│   ├── workspace_plugin.py       # Workspace releases
│   └── pypi_plugin.py            # PyPI-only uploads
└── README.md               # This documentation
```

---

## 🚀 Usage

### Command Line

#### List Available Modes
```bash
python -m scriptcraft.tools.release_manager.main
```

#### Python Package Release
```bash
# Release with version bump and PyPI upload
python -m scriptcraft.tools.release_manager.main python_package --version-type minor

# Release without PyPI upload
python -m scriptcraft.tools.release_manager.main python_package --version-type patch --skip-pypi

# Release with auto-push
python -m scriptcraft.tools.release_manager.main python_package --version-type major --auto-push
```

#### Workspace Release
```bash
# Release workspace with version bump
python -m scriptcraft.tools.release_manager.main workspace --version-type minor

# Release with custom message
python -m scriptcraft.tools.release_manager.main workspace --version-type patch --custom-message "Hotfix: critical bug fix"
```

#### PyPI Upload Only
```bash
# Upload existing package to PyPI
python -m scriptcraft.tools.release_manager.main pypi
```

### Python API

```python
from scriptcraft.tools.release_manager import ReleaseManager

# Create tool instance
tool = ReleaseManager()

# List available modes
modes = tool.list_available_modes()
print(f"Available modes: {modes}")

# Run Python package release
tool.run(
    mode="python_package",
    version_type="minor",
    auto_push=True
)
```

---

## 🔌 Available Plugins

### 1. Python Package Plugin (`python_package`)
**Purpose**: Release Python packages with version bumping and PyPI upload

**Features**:
- ✅ Version bumping (major, minor, patch)
- ✅ Package building with `python -m build`
- ✅ PyPI upload with `twine`
- ✅ Git operations (commit, tag)
- ✅ Auto-push support

**Usage**:
```bash
python -m scriptcraft.tools.release_manager.main python_package --version-type minor
```

**Arguments**:
- `--version-type`: Required. Type of version bump (major, minor, patch)
- `--auto-push`: Optional. Automatically push to remote repository
- `--force`: Optional. Force release even if no changes
- `--custom-message`: Optional. Custom commit message
- `--skip-pypi`: Optional. Skip PyPI upload

### 2. Workspace Plugin (`workspace`)
**Purpose**: Release workspaces with version bumping and git operations

**Features**:
- ✅ Version bumping (major, minor, patch)
- ✅ VERSION file management
- ✅ CHANGELOG.md updates
- ✅ Git operations (commit, tag)
- ✅ Development phase detection

**Usage**:
```bash
python -m scriptcraft.tools.release_manager.main workspace --version-type minor
```

**Arguments**:
- `--version-type`: Required. Type of version bump (major, minor, patch)
- `--auto-push`: Optional. Automatically push to remote repository
- `--force`: Optional. Force release even if no changes
- `--custom-message`: Optional. Custom commit message

### 3. PyPI Plugin (`pypi`)
**Purpose**: Upload existing packages to PyPI without version changes

**Features**:
- ✅ Package validation with `twine check`
- ✅ PyPI upload
- ✅ No version changes

**Usage**:
```bash
python -m scriptcraft.tools.release_manager.main pypi
```

**Arguments**: None required

### 4. Workspace Sync Plugin (`workspace_sync`)
**Purpose**: Synchronize workspace and submodule repositories (replaces PowerShell scripts)

**Features**:
- ✅ Submodule repository updates
- ✅ Main workspace synchronization
- ✅ Git submodule reference management
- ✅ Cross-platform compatibility (replaces PowerShell)

**Usage**:
```bash
# Full workspace synchronization
python -m scriptcraft.tools.release_manager.main workspace_sync sync

# Update only submodule
python -m scriptcraft.tools.release_manager.main workspace_sync submodule_update

# With custom commit messages
python -m scriptcraft.tools.release_manager.main workspace_sync sync --commit-message "Update package" --workspace-commit-message "Sync submodule"
```

**Arguments**:
- `--commit-message`: Optional. Commit message for submodule changes
- `--workspace-commit-message`: Optional. Commit message for workspace changes

**Operations**:
- `sync` / `workspace_sync`: Full workspace synchronization (submodule + main repo)
- `submodule_update`: Update only the submodule repository

---

## 🔧 Plugin Development

### Creating Custom Plugins

1. **Create plugin file** in `plugins/` directory:
```python
# plugins/custom_my_plugin.py

def run_mode(input_paths, output_dir, domain=None, **kwargs):
    """Custom release mode implementation."""
    # Your release logic here
    pass
```

2. **Register plugin** in `plugins/__init__.py`:
```python
from .custom_my_plugin import run_mode as custom_mode

def load_builtin_plugins(registry):
    # ... existing plugins ...
    
    registry.register_plugin(
        "custom",
        custom_mode,
        {
            "description": "Custom release workflow",
            "version_types": ["major", "minor", "patch"],
            "supports_pypi": False,
            "supports_git": True
        }
    )
```

### Plugin Interface

All plugins must implement the `run_mode` function with this signature:

```python
def run_mode(
    input_paths: List[Path], 
    output_dir: Path, 
    domain: Optional[str] = None, 
    **kwargs
) -> None:
    """
    Run the release mode.
    
    Args:
        input_paths: List of input file paths
        output_dir: Output directory for artifacts
        domain: Optional domain context
        **kwargs: Additional plugin-specific arguments
    """
    pass
```

---

## 📋 Requirements

### System Requirements
- Python 3.8+
- Git repository
- Access to PyPI (for uploads)

### Python Dependencies
- `scriptcraft` package (for common utilities)
- `twine` (for PyPI uploads)
- `build` (for package building)

### File Requirements

#### For Python Package Plugin
- `scriptcraft/_version.py` with `__version__` variable
- Valid `pyproject.toml` or `setup.py`

#### For Workspace Plugin
- `VERSION` file with version number
- `CHANGELOG.md` (optional, will be created if missing)

#### For PyPI Plugin
- `dist/` directory with built package files

---

## 🚨 Error Handling

### Common Issues

1. **Version File Not Found**
   - **Cause**: Missing `_version.py` or `VERSION` file
   - **Solution**: Ensure version file exists and is readable

2. **Build Failure**
   - **Cause**: Package configuration issues
   - **Solution**: Check `pyproject.toml` or `setup.py` syntax

3. **PyPI Upload Failure**
   - **Cause**: Authentication or network issues
   - **Solution**: Verify PyPI credentials and network connectivity

4. **Git Operation Failure**
   - **Cause**: Repository issues or permissions
   - **Solution**: Check git status and repository permissions

### Error Messages

- `[RM001]`: Version file not found
- `[RM002]`: Invalid version type
- `[RM003]`: Build failure
- `[RM004]`: PyPI upload failure
- `[RM005]`: Git operation failure

---

## 📊 Performance

### Expected Performance
- **Version bumping**: < 1 second
- **Package building**: 5-30 seconds (depends on package size)
- **PyPI upload**: 10-60 seconds (depends on file size and network)
- **Git operations**: < 5 seconds

### Optimization Tips
- Use `--skip-pypi` for local-only releases
- Use `--force` when you know changes exist
- Build packages separately for faster iteration

---

## 🔄 Migration from PowerShell Scripts

### Replacing the `releasing/` Folder

The new `ReleaseManager` tool with the `workspace_sync` plugin replaces the PowerShell scripts in the `releasing/` folder:

| PowerShell Script | ReleaseManager Equivalent | Status |
|------------------|---------------------------|---------|
| `github_push.ps1` | `workspace_sync sync` | ✅ Replaced |
| `pypi.ps1` | `python_package` plugin | ✅ Replaced |
| `release_all.ps1` | `python_package` + `workspace_sync` | ✅ Replaced |

### Migration Steps

1. **Install the new tool**:
   ```bash
   pip install scriptcraft
   ```

2. **Replace PowerShell workflows**:
   ```bash
   # Old: & "releasing\github_push.ps1"
   # New:
   python -m scriptcraft.tools.release_manager.main workspace_sync sync
   
   # Old: & "releasing\pypi.ps1"
   # New:
   python -m scriptcraft.tools.release_manager.main python_package --version-type patch
   
   # Old: & "releasing\release_all.ps1"
   # New:
   python -m scriptcraft.tools.release_manager.main python_package --version-type patch
   python -m scriptcraft.tools.release_manager.main workspace_sync sync
   ```

3. **Benefits of migration**:
   - ✅ Cross-platform compatibility (Windows, macOS, Linux)
   - ✅ Python-based (consistent with ScriptCraft ecosystem)
   - ✅ Plugin architecture for extensibility
   - ✅ Better error handling and logging
   - ✅ Integration with ScriptCraft common utilities

### When to Keep the `releasing/` Folder

You can **safely delete the `releasing/` folder** after:
- ✅ Testing the new `ReleaseManager` tool
- ✅ Verifying all workflows work as expected
- ✅ Updating any CI/CD pipelines or automation scripts

**Note**: The `releasing/` folder is no longer needed for ScriptCraft releases.

## 🔄 Integration

### With ScriptCraft Pipeline System
```python
from scriptcraft.pipeline import Pipeline

pipeline = Pipeline()
pipeline.add_step("release", {
    "tool": "release_manager",
    "mode": "python_package",
    "version_type": "minor",
    "auto_push": True
})
```

### With Other Tools
The release manager can be integrated with:
- CI/CD pipelines
- Build automation systems
- Deployment workflows
- Quality assurance processes

---

## 📝 Release Notes

### Current Version (1.0.0)
- ✅ Plugin-based architecture
- ✅ Python package release support
- ✅ Workspace release support
- ✅ PyPI upload support
- ✅ Git integration
- ✅ Comprehensive error handling
- ✅ Workspace sync plugin (replaces PowerShell scripts)

### Future Enhancements
- 🔄 Multi-repository support
- 🔄 Release notes generation
- 🔄 Dependency update automation
- 🔄 Release rollback support
- 🔄 Advanced plugin system

---

## 🤝 Contributing

1. **Plugin Development**: Create plugins in `plugins/` directory
2. **Testing**: Test plugins with sample projects
3. **Documentation**: Update README and docstrings
4. **Code Review**: Follow ScriptCraft coding standards

---

## 📞 Support

- Check tool logs for detailed error information
- Review plugin documentation for specific modes
- Contact: ScriptCraft development team
- Issues: Report via GitHub issues

---

*Built with ScriptCraft - Data Processing Framework*
