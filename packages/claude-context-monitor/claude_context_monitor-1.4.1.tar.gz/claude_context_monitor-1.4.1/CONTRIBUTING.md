# Contributing to Claude Context Monitor

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start for Contributors

### Prerequisites
- Claude Code installed and working
- Python 3.8+
- Git
- Basic understanding of shell scripting

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/claude-context-monitor.git
cd claude-context-monitor

# Install in development mode (creates symlinks)
./dev-install.sh

# Test the installation
claude-context-config info
```

## 🏗️ Project Structure

```
claude-context-monitor/
├── enhanced-status.py          # Main status line script
├── status-monitor.py           # Simple status variant
├── global-status-wrapper.sh   # Entry point wrapper
├── configure-global-status.sh # Configuration management
├── config.sh                   # Default configuration
├── handoff.md                  # Global command definition
├── install.sh                  # Installation script
├── uninstall.sh               # Uninstallation script
├── dev-install.sh             # Development installation
├── test/                      # Test scripts and fixtures
├── docs/                      # Documentation
└── examples/                  # Usage examples
```

## 🧪 Testing

### Run All Tests
```bash
./test/run-tests.sh
```

### Test Individual Components
```bash
./test/test-status.sh           # Test status line
./test/test-handoff.sh          # Test handoff generation
./test/test-install.sh          # Test installation
```

### Manual Testing
```bash
# Test status line with different plans
CLAUDE_PLAN=pro ./enhanced-status.py detailed
CLAUDE_PLAN=max ./enhanced-status.py compact

# Test configuration
claude-context-config info
claude-context-config compact
```

## 📝 Coding Standards

### Shell Scripts
- Use `set -euo pipefail` for safety
- Follow [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- Add descriptive comments for complex logic
- Use meaningful variable names

### Python Scripts  
- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include docstrings for functions
- Handle exceptions gracefully

### Example Code Style
```bash
#!/bin/bash
# Description of what this script does

set -euo pipefail

# Global variables in CAPS
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions with descriptive names
function check_requirements() {
    # Check if required tools are available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 required"
        return 1
    fi
}
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**:
   - Operating system and version
   - Claude Code version
   - Python version
   - Shell type and version

2. **Steps to Reproduce**:
   ```
   1. Run command X
   2. Observe behavior Y
   3. Expected behavior Z
   ```

3. **Relevant Output**:
   ```bash
   # Include command output, error messages, etc.
   claude-context-config info
   # Output here...
   ```

4. **Additional Context**:
   - Any custom configuration
   - Other Claude Code extensions
   - Recent changes to setup

## ✨ Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** first
2. **Describe the use case** clearly
3. **Explain the benefits** to users
4. **Consider implementation complexity**

### Good Feature Request Template
```markdown
## Feature Request: [Brief Title]

### Problem
Describe the problem this feature would solve.

### Proposed Solution  
Describe your preferred solution.

### Alternatives
Describe alternatives you've considered.

### Additional Context
Screenshots, mockups, related issues, etc.
```

## 🔄 Pull Request Process

### Before Submitting
1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with tests
4. **Test thoroughly** on your system
5. **Update documentation** if needed
6. **Follow coding standards**

### Pull Request Checklist
- [ ] Tests pass (`./test/run-tests.sh`)
- [ ] Code follows style guidelines
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear
- [ ] No breaking changes (or clearly documented)

### Pull Request Template
```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
Describe the tests you ran and how to reproduce them.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have added tests that prove my fix is effective
- [ ] Documentation has been updated
```

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### 🔧 Core Functionality
- Better token usage calculation algorithms
- Support for more Claude Code versions
- Performance optimizations
- Error handling improvements

### 🎨 User Experience
- Additional status line formats
- Better configuration management
- Improved installation experience
- Enhanced documentation

### 🧪 Testing
- Automated testing framework
- Cross-platform compatibility testing
- Integration tests with different Claude Code versions
- Performance benchmarks

### 📖 Documentation
- Usage examples and tutorials
- Troubleshooting guides
- API documentation
- Video demonstrations

## 🏷️ Release Process

Maintainers handle releases, but contributors should be aware of the process:

1. **Version Bumping**: Following [Semantic Versioning](https://semver.org/)
2. **Changelog Updates**: Document all changes
3. **Testing**: Comprehensive testing across platforms
4. **Release Notes**: Clear communication of changes

## ❓ Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: We provide detailed feedback on pull requests

## 🙏 Recognition

All contributors are recognized in our README and release notes. We appreciate every contribution, from bug fixes to documentation improvements!

---

**Thank you for contributing to Claude Context Monitor!** 🎉