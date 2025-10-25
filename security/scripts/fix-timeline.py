#!/usr/bin/env python3
"""
Fix corrupted remediation timeline YAML file.
"""

import sys
from pathlib import Path
import yaml

def fix_timeline():
    """Fix the corrupted timeline file."""
    timeline_path = Path("security/findings/history/remediation-timeline.yml")
    
    if not timeline_path.exists():
        print("Timeline file not found")
        return
    
    # Create a clean timeline file
    clean_timeline = {
        "last_updated": "2025-10-25T01:18:35.000000+00:00",
        "findings": {},
        "remediation": {}
    }
    
    # Backup the corrupted file
    backup_path = timeline_path.with_suffix(".yml.corrupted")
    timeline_path.rename(backup_path)
    
    # Write clean timeline
    with timeline_path.open("w", encoding="utf-8") as f:
        yaml.dump(clean_timeline, f, default_flow_style=False, sort_keys=False)
    
    print(f"Fixed timeline file. Backup saved as {backup_path}")

if __name__ == "__main__":
    fix_timeline()