#!/usr/bin/env python
"""
Setup script for the Django Auto Admin demo.
This script will:
1. Require uv package manager
2. Install dependencies with uv
3. Run migrations (pre-created)
4. Create sample data
5. Create a superuser
6. Start the development server.
"""

import os
import subprocess
import sys
from pathlib import Path

import django


def check_uv():
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "❌ The 'uv' package manager is required for this demo.\n"
            "Install it from https://github.com/astral-sh/uv or with:\n"
            "  curl -Ls https://astral.sh/uv/install.sh | sh\n"
        )
        return False


def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True


def setup_demo():
    """Set up the demo environment."""
    demo_dir = Path(__file__).parent
    os.chdir(demo_dir)

    print("🚀 Setting up Django Auto Admin Demo...")

    # Step 1: Check for uv
    print("\n🔎 Checking for uv package manager...")
    if not check_uv():
        return False

    # Step 2: Install dependencies with uv
    print("\n📦 Installing dependencies with uv...")
    if not run_command("uv pip install -r requirements.txt"):
        print("Failed to install dependencies")
        return False

    # Step 3: Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")
    django.setup()

    # Step 4: Run migrations (pre-created)
    print("\n🗄️ Running migrations...")
    if not run_command("python manage.py migrate"):
        print("Failed to run migrations")
        return False

    # Step 5: Create superuser
    print("\n👤 Creating superuser...")
    if not run_command("python manage.py createsuperuser_auto"):
        print("Failed to create superuser")
        return False

    print("\n✅ Demo setup complete!")
    print("\n🎯 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Open: http://127.0.0.1:8000/")
    print("3. Admin: http://127.0.0.1:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123")

    return True


if __name__ == "__main__":
    success = setup_demo()
    sys.exit(0 if success else 1)
