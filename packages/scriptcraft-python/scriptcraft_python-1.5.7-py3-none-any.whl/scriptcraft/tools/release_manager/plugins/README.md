# Release Manager Plugin Domain Separation

## 🎯 **Plugin Responsibilities**

### **python_package_plugin.py**
**Domain**: Python Package Releases
- ✅ Version bumping in `_version.py`
- ✅ Package building with `python -m build`
- ✅ PyPI upload with `twine`
- ✅ Git operations (commit, tag) for package changes
- ✅ Submodule handling for `implementations/python-package`
- ❌ Should NOT handle workspace-level operations

### **workspace_plugin.py**
**Domain**: Workspace Releases
- ✅ Version bumping in `VERSION` file
- ✅ CHANGELOG.md updates
- ✅ Git operations (commit, tag) for workspace changes
- ❌ Should NOT handle package-specific operations

### **pypi_plugin.py**
**Domain**: PyPI Upload Only
- ✅ Package validation with `twine check`
- ✅ PyPI upload of existing packages
- ❌ Should NOT handle version changes or git operations

### **workspace_sync_plugin.py**
**Domain**: Workspace Synchronization
- ✅ Submodule repository updates
- ✅ Main workspace synchronization
- ✅ Git submodule reference management
- ❌ Should NOT handle version changes or PyPI operations

## 🔧 **Git Branch Configuration**

**Current Branch**: `main`
- All plugins should use `git push origin main`
- No plugins should hardcode `master`

## 📦 **Submodule Handling**

**Submodule Path**: `implementations/python-package`
- `python_package_plugin`: Handles submodule changes during package releases
- `workspace_sync_plugin`: Handles submodule synchronization
- Other plugins: Should NOT modify submodule content

## 🚨 **Common Issues & Solutions**

### **Git Commit Failures**
- **Cause**: Submodule changes not properly staged
- **Solution**: Use `git add .` and handle submodule updates

### **Branch Name Issues**
- **Cause**: Hardcoded `master` instead of `main`
- **Solution**: Use `git push origin main`

### **Plugin Overlap**
- **Cause**: Multiple plugins handling same operations
- **Solution**: Clear domain separation as defined above
