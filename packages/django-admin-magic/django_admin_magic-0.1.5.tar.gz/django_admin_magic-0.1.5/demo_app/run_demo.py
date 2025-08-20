#!/usr/bin/env python
"""
Run script for the Django Auto Admin demo.
This script starts the development server with helpful information.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_demo():
    """Run the demo server."""
    demo_dir = Path(__file__).parent
    os.chdir(demo_dir)

    print("🚀 Starting Django Auto Admin Demo...")
    print("\n📋 Demo Information:")
    print("• Main Demo Page: http://127.0.0.1:8000/")
    print("• Django Admin: http://127.0.0.1:8000/admin/")
    print("• Admin Login: admin / admin123")
    print("\n🔄 Starting development server...")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    # Start the development server
    try:
        subprocess.run(["python", "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Demo server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        return False

    return True


if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
