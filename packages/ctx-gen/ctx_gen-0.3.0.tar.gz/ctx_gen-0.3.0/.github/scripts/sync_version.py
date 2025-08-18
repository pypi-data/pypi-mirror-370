#!/usr/bin/env python3
"""Synchronize version numbers across project files"""

import re
import sys
from pathlib import Path
import yaml


def get_project_version():
    """Get version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return None

    content = pyproject_path.read_text()
    match = re.search(r'^version = "(.+)"', content, re.MULTILINE)
    return match.group(1) if match else None


def update_bug_report_template(version):
    """Update version options in bug report template"""
    template_path = Path(".github/ISSUE_TEMPLATE/bug_report.yml")

    if not template_path.exists():
        print(f"⚠️  Bug report template not found: {template_path}")
        return False

    # Read YAML file
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        data = yaml.safe_load(content)

    # Parse version number
    major, minor, patch = version.split(".")

    # Generate version options
    version_options = [
        "Latest (main branch)",
        f"{version} (current)",
    ]

    # Add previous minor versions
    current_minor = int(minor)
    if current_minor > 0:
        version_options.append(f"{major}.{current_minor - 1}.x")
    if current_minor > 1:
        version_options.append(f"{major}.{current_minor - 2}.x")

    # For 0.x versions, add more options
    if major == "0":
        if current_minor > 2:
            version_options.append(f"{major}.{current_minor - 3}.x")

    version_options.append("Other (specify in comments)")

    # Update version dropdown in body
    updated = False
    for item in data.get("body", []):
        if item.get("id") == "version" and item.get("type") == "dropdown":
            item["attributes"]["options"] = version_options
            updated = True
            break

    if updated:
        # Preserve original format, manually build YAML
        # because yaml.dump might change formatting
        new_content = content

        # Find version dropdown section and replace options
        pattern = r"(- type: dropdown\s+id: version.*?options:\s*)(```math.*?```|\n(?:\s+- .+\n)+)"

        # Build new options string
        options_str = "\n".join(f"        - {opt}" for opt in version_options)

        def replacer(match):
            return match.group(1) + "\n" + options_str + "\n"

        new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

        # Write back to file
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ Updated bug report template with version {version}")
        return True
    else:
        print("⚠️  Could not find version dropdown in bug report template")
        return False


def check_version_consistency():
    """Check version consistency across all files"""
    version = get_project_version()
    if not version:
        print("❌ Could not find version in pyproject.toml")
        return False

    print(f"📦 Current version: {version}")

    # Check __init__.py
    init_path = Path("src/ctx_gen/__init__.py")
    if init_path.exists():
        init_content = init_path.read_text()
        init_match = re.search(r'__version__ = "(.+)"', init_content)
        init_version = init_match.group(1) if init_match else None

        if init_version == version:
            print(f"✅ __init__.py version matches: {init_version}")
        else:
            print(f"❌ __init__.py version mismatch: {init_version} != {version}")
            return False

    # Check if README.md mentions the version
    readme_path = Path("README.md")
    if readme_path.exists():
        readme_content = readme_path.read_text()
        if f"ctx-gen {version}" in readme_content or f"v{version}" in readme_content:
            print(f"✅ README.md mentions version {version}")
        else:
            print(f"⚠️  README.md doesn't mention current version {version}")

    return True


def main():
    """Main function"""
    # First check version consistency
    if not check_version_consistency():
        sys.exit(1)

    # Get version and update template
    version = get_project_version()
    if version:
        success = update_bug_report_template(version)
        if not success:
            sys.exit(1)
    else:
        print("❌ Could not find version")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure PyYAML is installed
    try:
        import yaml
    except ImportError:
        print("❌ PyYAML is required. Install with: pip install pyyaml")
        sys.exit(1)

    main()
