# Contributing to FOLC-V3

Thank you for your interest in contributing! This project aims to be a responsible, educational security research toolkit. We welcome contributions that align with this mission.

---

## 🎯 Project Goals

1. **Educational:** Help others learn about embedded Linux security
2. **Responsible:** Promote ethical use of security tools
3. **Practical:** Create useful functionality for authorized testing
4. **Well-Documented:** Maintain clear, comprehensive documentation

---

## 🤝 How to Contribute

### Types of Contributions

We welcome:

- **Bug fixes** - Stability and correctness improvements
- **New features** - Additional security tools or capabilities
- **Documentation** - Tutorials, guides, examples
- **Hardware research** - Device modifications, new exploits
- **Code quality** - Refactoring, optimization, testing
- **UI improvements** - Better interface design
- **Tool integration** - Adding new security tools to the toolkit

We do NOT accept:

- **Malicious code** - Backdoors, trojans, spyware
- **Illegal tools** - Software specifically designed for unauthorized access
- **Copyrighted content** - Proprietary code or documentation
- **Unethical features** - Tools that cannot be used responsibly

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/FOLC-V3.git
cd FOLC-V3
```

### 2. Set Up Development Environment

```bash
# Install development dependencies
# (This assumes you have a device to test on)
pip install -r requirements-dev.txt

# Create a branch for your feature
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow the coding standards (see below)
- Write clear commit messages
- Test your changes on actual hardware if possible
- Update documentation as needed

### 4. Submit a Pull Request

```bash
# Commit your changes
git add .
git commit -m "Add: Brief description of your changes"

# Push to your fork
git push origin feature/your-feature-name

# Open a pull request on GitHub
```

---

## 📝 Coding Standards

### Python Code

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

```python
# Use 4 spaces for indentation (no tabs)
def example_function(param1, param2):
    """Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
    """
    result = param1 + param2
    return result

# Class names: PascalCase
class WirelessTool:
    pass

# Functions/variables: snake_case
def scan_networks():
    network_list = []
    return network_list

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 10
```

### Shell Scripts

```bash
#!/bin/bash
# Brief description of what this script does

set -e  # Exit on error
set -u  # Exit on undefined variable

# Use descriptive variable names
DEVICE_PATH="/dev/fb0"
RETRY_COUNT=3

# Use functions for reusable code
function check_device() {
    if [ ! -e "$DEVICE_PATH" ]; then
        echo "Error: Device not found"
        return 1
    fi
}

# Add comments for complex logic
# This checks if ADB is connected before proceeding
if ! adb devices | grep -q "device$"; then
    echo "No device connected"
    exit 1
fi
```

### Documentation

- **Code comments:** Explain *why*, not *what*
- **Function docstrings:** Describe purpose, parameters, return values
- **README updates:** Keep documentation in sync with code
- **Examples:** Provide usage examples for new features

---

## 🧪 Testing

### Manual Testing

Before submitting a PR, test on real hardware:

1. **Basic Functionality:**
   ```bash
   # Test ADB connection
   adb devices
   
   # Test backdoor access
   adb forward tcp:9999 tcp:9999
   nc 127.0.0.1 9999
   ```

2. **UI Testing:**
   - Verify screen displays correctly
   - Test all button combinations
   - Check for crashes or hangs

3. **Tool Testing:**
   ```bash
   # Test WiFi scanning
   iw wlan0 scan
   
   # Test monitor mode
   airmon-ng start wlan0
   ```

4. **Edge Cases:**
   - What happens with no WiFi networks?
   - What if tcpdump fails?
   - How does it handle full disk?

### Test Checklist

- [ ] Code runs without errors
- [ ] UI displays properly on device screen
- [ ] No memory leaks (test with long-running processes)
- [ ] Handles errors gracefully
- [ ] Doesn't break existing functionality
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced

---

## 🔒 Security Considerations

### Security Review Checklist

Before submitting security-related changes:

- [ ] No hardcoded passwords or API keys
- [ ] User input is sanitized (especially shell commands)
- [ ] File permissions are appropriate
- [ ] No unnecessary privilege escalation
- [ ] Sensitive data is not logged
- [ ] Cryptographic operations use established libraries
- [ ] Code doesn't introduce new vulnerabilities

### Example of Safe Command Execution

```python
import subprocess
import shlex

# UNSAFE - Don't do this!
def unsafe_scan(ssid):
    cmd = f"iw wlan0 scan ssid {ssid}"
    subprocess.run(cmd, shell=True)  # Vulnerable to injection!

# SAFE - Do this instead
def safe_scan(ssid):
    cmd = ["iw", "wlan0", "scan", "ssid", ssid]
    subprocess.run(cmd, shell=False, check=True)  # Proper argument passing
```

---

## 📋 Pull Request Guidelines

### PR Description Template

```markdown
## Description
Brief summary of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Hardware research

## Testing
Describe how you tested this:
- Device: Orbic RC400L, Firmware v1.3.0
- Test environment: Ubuntu 22.04 with ADB 1.0.41
- Results: All features working as expected

## Screenshots
(If applicable, especially for UI changes)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tested on real hardware
- [ ] No security vulnerabilities introduced
- [ ] Ethical considerations addressed
```

### Review Process

1. **Automated Checks:** Code style, basic linting
2. **Maintainer Review:** Functionality, security, ethics
3. **Community Feedback:** Others may test and comment
4. **Approval:** Maintainer approves and merges

### Timeline

- Simple fixes: 1-3 days
- New features: 1-2 weeks
- Major changes: 2-4 weeks

---

## 🌟 Recognition

Contributors will be recognized in:

- **README.md** - Contributors section
- **Release notes** - Credit for specific features
- **Documentation** - Author attribution where applicable

---

## ⚖️ Ethical Guidelines

### What We Accept

✅ **Tools for authorized testing:**
```python
def scan_authorized_network(ssid):
    """Scan a network you have permission to test."""
    # Clear purpose: security assessment
```

✅ **Educational examples:**
```python
def demonstrate_packet_capture():
    """Shows how packet capture works for learning."""
    # Clearly labeled as educational
```

### What We Reject

❌ **Tools specifically for unauthorized access:**
```python
def auto_hack_wifi():  # NO!
    """Automatically breaks into WiFi networks."""
    # This would not be accepted
```

❌ **Malicious functionality:**
```python
def steal_credentials():  # NO!
    """Exfiltrates passwords."""
    # Clearly malicious intent
```

### Gray Areas

If you're unsure whether something is appropriate:

1. **Ask first:** Open a discussion issue
2. **Explain use case:** How would it be used ethically?
3. **Add safeguards:** Require explicit authorization flags
4. **Document risks:** Clear warnings about misuse

**Example:**
```python
def deauth_attack(target, authorized=False):
    """Send deauth frames for testing.
    
    WARNING: Only use on networks you own or have written
    permission to test. Unauthorized use is illegal.
    
    Args:
        target: Target MAC address
        authorized: Must be explicitly set to True
    """
    if not authorized:
        raise ValueError("Authorization flag required")
    # ... implementation
```

---

## 💬 Communication

### Discussion Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** General questions, ideas
- **Pull Requests:** Code review and discussion

### Code of Conduct

Be respectful:
- ✅ Constructive criticism
- ✅ Helpful suggestions
- ✅ Patient with newcomers
- ❌ Personal attacks
- ❌ Harassment
- ❌ Discriminatory language

---

## 🐛 Bug Reports

### Good Bug Report Template

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Run command X
2. Press button Y
3. Observe error Z

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- Device: Orbic RC400L
- Firmware: ORB400L_V1.3.0_BVZRT_R220518
- Host OS: Ubuntu 22.04
- ADB Version: 1.0.41

## Logs
```
Paste relevant log output here
```

## Additional Context
Any other relevant information.
```

---

## 💡 Feature Requests

### Good Feature Request Template

```markdown
## Feature Description
What feature would you like to see?

## Use Case
How would this be used? What problem does it solve?

## Ethical Considerations
How would this be used responsibly?

## Implementation Ideas
(Optional) Suggestions for how to implement this.

## Alternatives
Have you considered alternatives?
```

---

## 📚 Documentation Contributions

Documentation is just as important as code!

### What to Document

- **Tutorials:** Step-by-step guides for specific tasks
- **Troubleshooting:** Solutions to common problems
- **Hardware mods:** Instructions for physical modifications
- **Use cases:** Real-world examples of ethical use
- **Tool guides:** How to use specific security tools

### Documentation Style

- Write clearly and concisely
- Use examples liberally
- Include screenshots where helpful
- Warn about potential issues
- Link to external resources

---

## 🙏 Questions?

- **General questions:** GitHub Discussions
- **Bug reports:** GitHub Issues
- **Security concerns:** See SECURITY.md
- **Legal questions:** Consult a lawyer (we're not legal advisors)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE file).

---

**Thank you for contributing to FOLC-V3! Together we can build a powerful, responsible security research toolkit.**
