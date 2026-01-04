# Archive Directory

This directory contains deprecated, experimental, and historical files from the FOLC-V3 project development.

## ⚠️ Warning

**Files in this directory are NOT actively maintained and may not work with the current system.**

These are preserved for:
- Historical reference
- Learning from earlier attempts
- Potential ideas for future development
- Understanding the project evolution

---

## File Descriptions

### UI Iterations

| File | Description | Status |
|------|-------------|--------|
| `foac_ui.py` | Original UI implementation | Superseded by v6 |
| `foac_ui_v2.py` | Second iteration with button improvements | Superseded by v6 |
| `foac_ui_v3.py` | Added menu system | Superseded by v6 |
| `foac_ui_v4.py` | Improved rendering | Superseded by v6 |
| `foac_ui_v5.py` | Context menu addition | Superseded by v6 |

**Current:** `/src/ui/foac_ui_v6.py` is the active version.

### Test Scripts

| File | Description | Purpose |
|------|-------------|---------|
| `input_test.py` | Button input testing | Hardware debugging |
| `input_test_v2.py` | Improved input testing | Hardware debugging |
| `screen_test.py` | Framebuffer test | Display verification |
| `log_buttons.py` | Button event logger | Hardware debugging |
| `find_buttons.py` | Input device discovery | Hardware debugging |

These were used during initial hardware exploration to understand the device's input/output systems.

### Alternative Implementations

| File | Description | Notes |
|------|-------------|-------|
| `flipper.pl` | Perl-based UI attempt | Proof of concept |
| `orbic_flipper.py` | Python UI experiment | Early prototype |

These represent different approaches tried before settling on the current architecture.

### Deployment Scripts (Old)

| File | Description | Replaced By |
|------|-------------|-------------|
| `dummy_service.sh` | Service test script | Current wrapper system |
| `install_cmds.sh` | Manual install commands | `tools/install_toolkit.sh` |
| `orbic_deploy.sh` | Old deployment script | `tools/orbic_manager.py` |
| `payload_install.sh` | Payload deployment | Integrated into main tools |
| `simple.script` | Basic test script | N/A |

---

## Why Keep These?

1. **Learning Resource:** Shows the iterative development process
2. **Code Salvage:** May contain useful functions for future features
3. **Documentation:** Explains "why" certain decisions were made
4. **Debugging:** Sometimes older versions help understand issues

---

## Using Archive Files

If you want to test or learn from these files:

```bash
# Copy to a test location (don't run directly)
cp archive/foac_ui_v3.py /tmp/test_ui.py

# Review the code
less archive/flipper.pl

# Compare with current version
diff archive/foac_ui_v5.py src/ui/foac_ui_v6.py
```

**Do NOT deploy these to your device** unless you know what you're doing!

---

## Clean Archive Policy

Files are moved here when:
- ✅ Superseded by newer version
- ✅ No longer compatible with current system
- ✅ Experimental feature abandoned
- ✅ Test/debug script no longer needed

Files are removed from archive when:
- ❌ Contains no useful code or concepts
- ❌ Duplicates functionality elsewhere
- ❌ After 6+ months with no reference

---

## Contributing

If you find useful code in these archives:

1. **Don't resurrect old files directly**
2. **Instead:** Extract the useful parts
3. **Integrate:** Adapt them to current architecture
4. **Test:** Verify with current system
5. **Document:** Explain what was salvaged and why

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

*This directory is a museum of development history. Visit to learn, but don't deploy!*
