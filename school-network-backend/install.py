"""
Complete Installation & Setup Script
Installs dependencies and sets up your network automatically.
"""

import subprocess
import sys
import os

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_python_version():
    """Check if Python version is compatible."""
    print_header("🐍 Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ ERROR: Python 3.10+ required")
        print("   Please upgrade Python: https://www.python.org/downloads/")
        return False
    
    print("✅ Python version is compatible")
    return True


def install_dependencies():
    """Install required Python packages."""
    print_header("📦 Installing Dependencies")
    
    packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg[binary]",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "requests",  # For quick_setup.py
    ]
    
    print("Installing required packages...")
    print("This may take a few minutes...\n")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"  ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"  ⚠️  {package} - trying alternative method...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--user", package]
                )
                print(f"  ✅ {package} installed (user mode)")
            except:
                print(f"  ❌ Failed to install {package}")
                return False
    
    print("\n✅ All dependencies installed successfully!")
    return True


def check_database():
    """Check database configuration."""
    print_header("🗄️  Checking Database Configuration")
    
    if os.path.exists(".env"):
        print("✅ Found .env configuration file")
        
        with open(".env", "r") as f:
            content = f.read()
            if "DATABASE_URL" in content:
                print("✅ Database URL configured")
            else:
                print("⚠️  DATABASE_URL not found in .env")
    else:
        print("⚠️  No .env file found")
        print("   Using default PostgreSQL configuration")
    
    return True


def offer_quick_setup():
    """Offer to run quick setup."""
    print_header("🚀 Ready to Set Up Your Network")
    
    print("\nYour application is now ready!")
    print("\nNext steps:")
    print("  1. Start the application:")
    print("     python -m uvicorn main:app --reload")
    print("\n  2. In another terminal, run setup:")
    print("     python quick_setup.py")
    print("\n" + "=" * 70)
    
    choice = input("\nWould you like to run quick setup now? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🔄 Starting quick setup...\n")
        try:
            import requests
            
            # Check if app is running
            try:
                response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
                if response.status_code == 200:
                    # App is running, run quick_setup
                    subprocess.run([sys.executable, "quick_setup.py"])
                else:
                    print("⚠️  Application is not running yet.")
                    print("   Please start it first with: python -m uvicorn main:app --reload")
            except:
                print("⚠️  Application is not running yet.")
                print("\n📝 To complete setup:")
                print("   1. Open a terminal and run: python -m uvicorn main:app --reload")
                print("   2. Open another terminal and run: python quick_setup.py")
        except ImportError:
            print("⚠️  Setup module not found. Please run quick_setup.py manually.")


def main():
    """Main installation function."""
    print("\n╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🌐 NETWORK MONITOR - INSTALLATION" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Step 1: Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Step 2: Install dependencies
        if not install_dependencies():
            print("\n❌ Installation failed!")
            print("   Please install dependencies manually:")
            print("   pip install fastapi uvicorn sqlalchemy psycopg[binary] pydantic python-dotenv requests")
            sys.exit(1)
        
        # Step 3: Check database
        check_database()
        
        # Step 4: Offer quick setup
        offer_quick_setup()
        
        print("\n" + "=" * 70)
        print("✅ INSTALLATION COMPLETE!")
        print("=" * 70)
        print("\n📚 Documentation:")
        print("   • Quick Start: See START_HERE.md")
        print("   • Full Guide: See SETUP_GUIDE.md")
        print("\n🎉 You're all set! Happy monitoring!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Installation error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()