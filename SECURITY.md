# Security Policy

## Overview

FOLC-V3 is a security research toolkit designed for authorized penetration testing and educational purposes. This document outlines our security practices, responsible disclosure policy, and legal considerations.

---

## 🔒 Security Considerations

### Risks of Using This Toolkit

1. **Device Security:**
   - The backdoor on port 9999 provides unrestricted root access
   - Anyone with physical USB access can connect to your device
   - The device becomes a potential attack vector if compromised

2. **Network Security:**
   - Monitor mode and packet injection can interfere with nearby networks
   - Captured packets may contain sensitive information
   - Deauthentication attacks are detectable and may be logged

3. **Legal Risks:**
   - Unauthorized network access is illegal in most jurisdictions
   - Carrier ToS violations may result in service termination
   - Possession of hacking tools may be restricted in some areas

4. **Operational Security:**
   - The device may be identifiable via MAC address or IMEI
   - Some attacks generate distinctive traffic patterns
   - Logs on target networks may record your activities

---

## 🛡️ Recommended Security Practices

### Physical Security

1. **Access Control:**
   - Keep the device physically secure at all times
   - Do not leave unattended in public spaces
   - Consider encrypting the `/data` partition (advanced)

2. **Screen Lock:**
   - Implement a PIN/password on the device if possible
   - Use the long-press power button to quickly blank the screen

### Network Security

1. **Backdoor Protection:**
   - The netcat backdoor is localhost-only by design
   - Never expose port 9999 to external networks
   - Consider adding authentication if exposing remotely

2. **Traffic Encryption:**
   - Use VPN when exfiltrating captured data
   - Avoid transmitting sensitive data in cleartext
   - Be aware that carrier may monitor cellular traffic

3. **MAC Address Randomization:**
   ```bash
   # Randomize MAC before scanning
   ip link set wlan0 down
   macchanger -r wlan0
   ip link set wlan0 up
   ```

### Data Protection

1. **Captured Packets:**
   - Store .pcap files securely
   - Delete captures after analysis
   - Never share captures containing PII without scrubbing

2. **Logs:**
   - Review and sanitize logs regularly
   - Disable verbose logging in production use
   - Rotate logs to prevent disk filling

---

## 🐛 Vulnerability Reporting

### Scope

We accept security reports for:

1. **Vulnerabilities in FOLC-V3 code:**
   - Remote code execution
   - Privilege escalation beyond root
   - Information disclosure
   - Denial of service

2. **Vulnerabilities in the Orbic device:**
   - Previously unknown exploits
   - Firmware vulnerabilities
   - Hardware security issues

3. **Improvements to security practices:**
   - Better operational security
   - Risk mitigation strategies
   - Secure coding practices

### Out of Scope

- Social engineering attacks
- Physical attacks requiring device disassembly
- Issues requiring user to run malicious code
- Carrier network vulnerabilities (report to carrier)
- Third-party tool vulnerabilities (report to maintainers)

---

## 📬 Responsible Disclosure

### How to Report

**DO NOT open public GitHub issues for security vulnerabilities!**

Instead, please:

1. **Email:** Send details to the repository owner via GitHub
2. **Encrypted:** Use PGP if possible (key available on request)
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested mitigation (if any)
   - Your contact information

### What to Expect

1. **Acknowledgment:** We'll respond within 48 hours
2. **Assessment:** We'll evaluate severity and impact
3. **Fix Timeline:** Critical issues prioritized (target: 7-14 days)
4. **Disclosure:** We'll coordinate public disclosure with you
5. **Credit:** You'll be credited in release notes (if desired)

### Disclosure Timeline

- **Day 0:** Vulnerability reported
- **Day 1-2:** Acknowledgment sent
- **Day 3-7:** Investigation and verification
- **Day 7-30:** Fix development and testing
- **Day 30+:** Coordinated public disclosure

We follow a **90-day disclosure policy** maximum.

---

## ⚖️ Legal Considerations

### Responsible Use

This toolkit should only be used:

1. **On Your Own Networks:**
   - Devices you own
   - Networks you administer
   - With proper authorization

2. **For Authorized Testing:**
   - Contracted penetration testing
   - Bug bounty programs
   - Security research with permission

3. **Educational Purposes:**
   - Learning about embedded Linux
   - Understanding WiFi security
   - Studying exploit development

### Prohibited Uses

**DO NOT use this toolkit for:**

1. **Unauthorized Access:**
   - Hacking into networks without permission
   - Intercepting communications
   - Bypassing authentication

2. **Malicious Activities:**
   - Denying service to legitimate users
   - Stealing credentials or data
   - Distributing malware

3. **ToS Violations:**
   - Violating carrier agreements
   - Exceeding data caps through testing
   - Reselling modified devices

### Legal Status by Jurisdiction

#### United States
- **CFAA:** Computer Fraud and Abuse Act - Unauthorized access is federal crime
- **Wiretap Act:** Intercepting communications requires consent
- **State Laws:** Vary by state, some stricter than federal

#### European Union
- **Computer Misuse Act:** Unauthorized access criminalized in UK
- **GDPR:** Data protection regulations apply to captured data
- **Network & Information Security Directive:** Infrastructure protection

#### Other Jurisdictions
- **Australia:** Cybercrime Act 2001
- **Canada:** Criminal Code Section 342.1
- **Check your local laws** before using this toolkit

---

## 🏛️ Ethical Guidelines

### Principles

1. **Do No Harm:**
   - Minimize impact on production networks
   - Avoid disrupting legitimate users
   - Stop testing if issues arise

2. **Respect Privacy:**
   - Don't capture or store personal data unnecessarily
   - Sanitize all shared data
   - Follow data protection regulations

3. **Obtain Consent:**
   - Get written authorization before testing
   - Document scope of testing
   - Report findings responsibly

4. **Professional Conduct:**
   - Follow industry standards (OWASP, PTES)
   - Maintain confidentiality
   - Be transparent about capabilities and limitations

### Red Lines

**Never:**
- Test production systems without authorization
- Retain data from unauthorized scans
- Share exploits for malicious purposes
- Claim this toolkit is "undetectable" or "legal everywhere"

---

## 🔐 Hardening Your Device

### Additional Security Measures

1. **Change Default Credentials:**
   ```bash
   # If you add SSH, change root password
   passwd root
   ```

2. **Firewall Rules:**
   ```bash
   # Only allow ADB from specific IP
   iptables -A INPUT -p tcp --dport 5555 -s 192.168.1.100 -j ACCEPT
   iptables -A INPUT -p tcp --dport 5555 -j DROP
   ```

3. **Disable Backdoor When Not Needed:**
   ```bash
   # Kill netcat listener
   pkill -f "nc.*9999"
   ```

4. **Enable Audit Logging:**
   ```bash
   # Log all commands in chroot
   echo 'export PROMPT_COMMAND="history -a"' >> ~/.bashrc
   ```

5. **Encrypt Sensitive Data:**
   ```bash
   # Use GPG for captured packets
   gpg -c capture.pcap
   shred -u capture.pcap
   ```

---

## 📋 Security Checklist

Before conducting security testing:

- [ ] I have written authorization to test the target network
- [ ] I understand the legal implications in my jurisdiction
- [ ] I have a testing plan and defined scope
- [ ] I have documented my setup and methodology
- [ ] I will minimize impact on production systems
- [ ] I will protect any data I capture
- [ ] I will report findings responsibly
- [ ] I have backup/restore capability for the device
- [ ] I accept full responsibility for my actions

---

## 🆘 Incident Response

If you believe your device has been compromised:

1. **Disconnect:** Remove from all networks immediately
2. **Preserve Evidence:** Don't delete logs or modify system
3. **Document:** Record what you observed and when
4. **Reset:** Perform factory reset (see INSTALL.md)
5. **Report:** If malicious activity detected, report to authorities

---

## 📚 Additional Resources

- **OWASP Testing Guide:** https://owasp.org/www-project-web-security-testing-guide/
- **PTES Technical Guidelines:** http://www.pentest-standard.org/
- **NIST Cybersecurity Framework:** https://www.nist.gov/cyberframework
- **EFF Surveillance Self-Defense:** https://ssd.eff.org/

---

## 📞 Contact

For security concerns:
- **GitHub:** Open a security advisory (not a regular issue)
- **Email:** Contact repository owner privately

For legal questions:
- **Consult a lawyer** - We are not legal advisors

---

**Remember: Security is everyone's responsibility. Use this toolkit ethically and legally.**

*Last Updated: January 2026*
