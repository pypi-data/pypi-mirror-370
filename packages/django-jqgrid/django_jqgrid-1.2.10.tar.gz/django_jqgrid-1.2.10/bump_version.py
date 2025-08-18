#!/usr/bin/env python3
"""
Version Bumping Utility for Django-jqGrid Package

Simple utility to bump version numbers in the package.
Can be used standalone or called from the main publishing script.
"""
import re
import sys
import argparse
from pathlib import Path


class VersionBumper:
    def __init__(self, package_dir: Path = None):
        self.package_dir = package_dir or Path(__file__).parent
        self.init_file = self.package_dir / "django_jqgrid" / "__init__.py"
    
    def get_current_version(self) -> str:
        """Get current version from __init__.py"""
        if not self.init_file.exists():
            print(f"❌ Error: {self.init_file} not found")
            sys.exit(1)
        
        with open(self.init_file, 'r') as f:
            content = f.read()
        
        version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
        if not version_match:
            print("❌ Error: Version not found in __init__.py")
            sys.exit(1)
        
        return version_match.group(1)
    
    def set_version(self, new_version: str):
        """Update version in __init__.py"""
        with open(self.init_file, 'r') as f:
            content = f.read()
        
        new_content = re.sub(
            r"__version__\s*=\s*['\"][^'\"]+['\"]",
            f"__version__ = '{new_version}'",
            content
        )
        
        with open(self.init_file, 'w') as f:
            f.write(new_content)
    
    def parse_version(self, version: str) -> tuple:
        """Parse version string into major, minor, patch"""
        parts = version.split('.')
        if len(parts) != 3:
            print(f"❌ Error: Invalid version format '{version}'. Expected X.Y.Z")
            sys.exit(1)
        
        try:
            return tuple(map(int, parts))
        except ValueError:
            print(f"❌ Error: Version parts must be numbers: '{version}'")
            sys.exit(1)
    
    def bump_version(self, bump_type: str, custom_version: str = None) -> str:
        """Bump version based on type or set custom version"""
        current = self.get_current_version()
        
        if custom_version:
            # Validate custom version format
            self.parse_version(custom_version)
            new_version = custom_version
        else:
            major, minor, patch = self.parse_version(current)
            
            if bump_type == 'major':
                new_version = f"{major + 1}.0.0"
            elif bump_type == 'minor':
                new_version = f"{major}.{minor + 1}.0"
            elif bump_type == 'patch':
                new_version = f"{major}.{minor}.{patch + 1}"
            else:
                print(f"❌ Error: Invalid bump type '{bump_type}'. Use: major, minor, patch")
                sys.exit(1)
        
        print(f"📈 Bumping version: {current} → {new_version}")
        self.set_version(new_version)
        print(f"✅ Version updated successfully!")
        
        return new_version


def main():
    parser = argparse.ArgumentParser(description='Bump version for django-jqgrid package')
    
    parser.add_argument('bump_type', nargs='?', choices=['major', 'minor', 'patch'],
                       help='Type of version bump')
    parser.add_argument('--custom', '-c', metavar='VERSION',
                       help='Set custom version (e.g., 2.1.0)')
    parser.add_argument('--show', '-s', action='store_true',
                       help='Show current version without changing it')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    
    bumper = VersionBumper()
    current = bumper.get_current_version()
    
    if args.show:
        print(f"Current version: {current}")
        return
    
    # Handle custom version
    if args.custom:
        new_version = args.custom
        bumper.parse_version(new_version)  # Validate format
        
        if args.dry_run:
            print(f"Would bump version: {current} → {new_version}")
        else:
            bumper.set_version(new_version)
            print(f"📈 Version set: {current} → {new_version}")
            print(f"✅ Version updated successfully!")
        return
    
    # Require either bump_type or custom or show
    if not args.bump_type and not args.custom and not args.show:
        parser.error("Must specify --show, --custom, or a bump type (major/minor/patch)")
    
    # Handle positional argument (bump type or custom version)
    if args.bump_type:
        # Check if it looks like a version number
        if '.' in args.bump_type:
            # Treat as custom version
            new_version = args.bump_type
            bumper.parse_version(new_version)  # Validate format
            
            if args.dry_run:
                print(f"Would set version: {current} → {new_version}")
            else:
                bumper.set_version(new_version)
                print(f"📈 Version set: {current} → {new_version}")
                print(f"✅ Version updated successfully!")
        else:
            # Treat as bump type
            if args.dry_run:
                major, minor, patch = bumper.parse_version(current)
                
                if args.bump_type == 'major':
                    new_version = f"{major + 1}.0.0"
                elif args.bump_type == 'minor':
                    new_version = f"{major}.{minor + 1}.0"
                elif args.bump_type == 'patch':
                    new_version = f"{major}.{minor}.{patch + 1}"
                
                print(f"Would bump version: {current} → {new_version}")
            else:
                new_version = bumper.bump_version(args.bump_type)


if __name__ == "__main__":
    main()