# License Header Updates Requirements

## Overview

Update all source code files from AGPL v3 license headers to Apache 2.0 license headers as part of the core licensing change documented in ADR-019.

## Context

As part of the TUI separation strategy, we're changing the core functionality from AGPL v3 to Apache 2.0 to enable:
- Tight coupling between open core and closed TUI
- Corporate adoption (many organizations prohibit AGPL)
- Compatibility with proprietary TUI components

## Scope

### Files to Update

**Core Package Files** (watchgate-core/):
- All `.py` files in `watchgate/` directory tree
- Configuration files, build scripts
- Any other source files with AGPL headers

**Main Package Files**:
- Root level Python files  
- Build and configuration scripts
- Any files that will be part of Apache 2.0 licensed distribution

**Exclude from Updates**:
- TUI files in `watchgate-tui/` (will have proprietary headers)
- Third-party dependencies
- Generated files

### Current AGPL Header Format

Most files currently have headers like:
```python
# Copyright (c) 2024 [Your Name]
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

### Target Apache 2.0 Header Format

```python
# Copyright (c) 2024 [Your Name]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

## Detailed Requirements

### 1. License Header Update Script

**File**: `scripts/update-license-headers.py`

```python
#!/usr/bin/env python3
"""Update license headers from AGPL to Apache 2.0"""

import re
import sys
from pathlib import Path
from typing import List, Optional

# Apache 2.0 header template
APACHE_HEADER_TEMPLATE = '''# Copyright (c) {year} {copyright_holder}
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''

# TUI proprietary header template
PROPRIETARY_HEADER_TEMPLATE = '''# Copyright (c) {year} {copyright_holder}
# Proprietary Software - All Rights Reserved
# Free to use but not for redistribution
'''

class LicenseUpdater:
    def __init__(self, copyright_holder: str, year: str = "2024"):
        self.copyright_holder = copyright_holder
        self.year = year
        
    def detect_current_header(self, content: str) -> Optional[str]:
        """Detect type of current license header"""
        if "GNU Affero General Public License" in content:
            return "AGPL"
        elif "Apache License" in content:
            return "Apache"
        elif "Proprietary Software" in content:
            return "Proprietary"
        elif "Copyright" in content[:500]:  # Check first 500 chars
            return "Other"
        return None
    
    def extract_header_region(self, content: str) -> tuple[str, str, str]:
        """Extract header, main content, and determine boundaries"""
        lines = content.split('\n')
        
        # Find header boundaries
        header_start = 0
        header_end = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip shebang and encoding declarations
            if i == 0 and stripped.startswith('#!'):
                continue
            if stripped.startswith('# -*- coding:') or stripped.startswith('# coding:'):
                continue
                
            # Look for copyright or license indicators
            if any(keyword in stripped for keyword in ['Copyright', 'License', 'GNU', 'Apache']):
                if header_start == 0:
                    header_start = i
                header_end = i
            elif header_start > 0 and not stripped.startswith('#') and stripped:
                # Found non-comment, non-empty line after header
                break
        
        if header_start == 0 and header_end == 0:
            # No header found
            return "", content, 0
        
        header_lines = lines[header_start:header_end + 1]
        remaining_lines = lines[header_end + 1:]
        
        # Handle module docstrings that come after headers
        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines = remaining_lines[1:]
        
        header = '\n'.join(header_lines)
        remainder = '\n'.join(remaining_lines)
        
        return header, remainder, header_start
    
    def update_file_header(self, file_path: Path, target_license: str) -> bool:
        """Update license header in a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"Skipping {file_path}: {e}")
            return False
        
        current_license = self.detect_current_header(content)
        if current_license is None:
            print(f"No license header found in {file_path}")
            return False
        
        if current_license == target_license:
            print(f"Already {target_license} license: {file_path}")
            return True
        
        # Extract current header and content
        old_header, remainder, header_start = self.extract_header_region(content)
        
        if not old_header:
            print(f"Could not parse header in {file_path}")
            return False
        
        # Generate new header
        if target_license == "Apache":
            new_header = APACHE_HEADER_TEMPLATE.format(
                year=self.year,
                copyright_holder=self.copyright_holder
            ).strip()
        elif target_license == "Proprietary":
            new_header = PROPRIETARY_HEADER_TEMPLATE.format(
                year=self.year,
                copyright_holder=self.copyright_holder
            ).strip()
        else:
            print(f"Unknown target license: {target_license}")
            return False
        
        # Preserve any shebang or encoding
        lines = content.split('\n')
        preamble = []
        for line in lines[:header_start]:
            if line.startswith('#!') or 'coding:' in line:
                preamble.append(line)
            else:
                break
        
        # Reconstruct file
        new_content = '\n'.join(preamble + [new_header, remainder])
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        print(f"Updated {file_path}: {current_license} → {target_license}")
        return True
    
    def update_directory(self, directory: Path, target_license: str, 
                        patterns: List[str] = None) -> tuple[int, int]:
        """Update all files in directory matching patterns"""
        if patterns is None:
            patterns = ["*.py"]
        
        updated = 0
        failed = 0
        
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    if self.update_file_header(file_path, target_license):
                        updated += 1
                    else:
                        failed += 1
        
        return updated, failed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Update license headers")
    parser.add_argument("--copyright-holder", required=True,
                       help="Copyright holder name")
    parser.add_argument("--year", default="2024",
                       help="Copyright year")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be updated without making changes")
    
    args = parser.parse_args()
    
    updater = LicenseUpdater(args.copyright_holder, args.year)
    
    # Update core files to Apache 2.0
    core_dir = Path("watchgate-core")
    if core_dir.exists():
        print(f"Updating core files to Apache 2.0...")
        if not args.dry_run:
            updated, failed = updater.update_directory(core_dir, "Apache")
            print(f"Core: {updated} updated, {failed} failed")
    
    # Update TUI files to Proprietary
    tui_dir = Path("watchgate-tui")
    if tui_dir.exists():
        print(f"Updating TUI files to Proprietary...")
        if not args.dry_run:
            updated, failed = updater.update_directory(tui_dir, "Proprietary")
            print(f"TUI: {updated} updated, {failed} failed")
    
    # Update root files to Apache 2.0
    root_files = [
        Path("pyproject.toml"),
        # Add other root files that need license headers
    ]
    
    for file_path in root_files:
        if file_path.exists() and file_path.suffix == ".py":
            if not args.dry_run:
                updater.update_file_header(file_path, "Apache")


if __name__ == "__main__":
    main()
```

### 2. License File Updates

**Update root LICENSE file**:
```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

[Full Apache 2.0 license text]
```

**Create watchgate-core/LICENSE**:
Same Apache 2.0 content as root.

**Create watchgate-tui/LICENSE.PROPRIETARY**:
```
Watchgate TUI - Proprietary Freeware License

Copyright (c) 2024 [Your Name]

Permission is hereby granted to use this software free of charge, subject to 
the following conditions:

1. The software may be used for any legal purpose
2. The software may NOT be redistributed as part of commercial products
3. The software may NOT be rebranded or white-labeled  
4. The software may NOT be included in competitive products

This software is provided "as is" without warranty of any kind.

Violators will be pursued under copyright law.
```

### 3. Validation and Testing

**File**: `scripts/validate-license-headers.py`

```python
#!/usr/bin/env python3
"""Validate license headers are correct and consistent"""

import sys
from pathlib import Path
from collections import defaultdict


def check_file_license(file_path: Path) -> str:
    """Check what license a file has"""
    try:
        content = file_path.read_text(encoding='utf-8')
    except:
        return "ERROR"
    
    if "Apache License" in content:
        return "Apache"
    elif "GNU Affero General Public License" in content:
        return "AGPL"
    elif "Proprietary Software" in content:
        return "Proprietary"
    elif "Copyright" in content[:500]:
        return "Other"
    else:
        return "None"


def main():
    results = defaultdict(list)
    
    # Check core files
    core_dir = Path("watchgate-core")
    if core_dir.exists():
        for py_file in core_dir.rglob("*.py"):
            license_type = check_file_license(py_file)
            results[f"Core-{license_type}"].append(str(py_file))
    
    # Check TUI files
    tui_dir = Path("watchgate-tui")  
    if tui_dir.exists():
        for py_file in tui_dir.rglob("*.py"):
            license_type = check_file_license(py_file)
            results[f"TUI-{license_type}"].append(str(py_file))
    
    # Report results
    errors = 0
    
    print("License Header Validation Report")
    print("=" * 40)
    
    for category, files in sorted(results.items()):
        print(f"\n{category}: {len(files)} files")
        
        # Check for problems
        if "Core-AGPL" in category or "Core-Other" in category or "Core-None" in category:
            print("  ❌ ERROR: Core files should have Apache license")
            errors += len(files)
        elif "TUI-AGPL" in category or "TUI-Apache" in category or "TUI-None" in category:
            print("  ❌ ERROR: TUI files should have Proprietary license")
            errors += len(files)
        elif "Core-Apache" in category or "TUI-Proprietary" in category:
            print("  ✅ OK")
        
        # Show first few files for debugging
        for file_path in files[:5]:
            print(f"    {file_path}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")
    
    if errors > 0:
        print(f"\n❌ {errors} files have incorrect licenses")
        return 1
    else:
        print("\n✅ All files have correct licenses")
        return 0


if __name__ == "__main__":
    sys.exit(main())
```

### 4. Integration with Build Process

**Update build scripts** to validate licenses:

```bash
# In scripts/build-packages.sh, add:
echo "Validating license headers..."
python scripts/validate-license-headers.py
if [[ $? -ne 0 ]]; then
    echo "License validation failed!"
    exit 1
fi
```

## Success Criteria

- [ ] All core files have Apache 2.0 headers
- [ ] All TUI files have proprietary headers  
- [ ] No AGPL headers remain in codebase
- [ ] License validation script passes
- [ ] Build process includes license validation
- [ ] Legal compliance verified

## Dependencies

- **Copyright holder name** - Need to determine exact legal entity name
- **Year range** - Decide if using single year (2024) or range (2024-2025)
- **Legal review** - Confirm header format meets legal requirements

## Questions to Resolve

1. **Copyright Holder**: What is the exact legal entity name to use?
2. **Year Format**: Single year (2024) or range (2024-2025)?
3. **File Coverage**: Do we update ALL files or just Python source?
4. **Timing**: Before or after Phase 3 build system implementation?

## Implementation Timeline

- **Week 1**: Resolve copyright holder and year questions
- **Week 2**: Implement and test license update script
- **Week 3**: Run script on codebase and validate results
- **Week 4**: Integrate with build process and CI/CD

## Rollback Plan

- Git provides complete rollback capability
- License update script can be modified to reverse changes
- Individual files can be reverted if needed

## Legal Considerations

- Ensure Apache 2.0 headers meet Apache Foundation requirements
- Verify proprietary license terms are legally sound
- Consider adding NOTICE file for Apache 2.0 compliance
- Document license change rationale for future reference