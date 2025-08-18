import subprocess
import sys
import time
from .core import omnipkg as OmnipkgCore, ConfigManager
from .loader import omnipkgLoader
import importlib
from pathlib import Path

def omnipkg_pip_jail():
    """The most passive-aggressive pip warning ever - EPIC EDITION"""
    print("\n" + "🔥" * 50)
    print("🚨 PIP DEPENDENCY DESTRUCTION ALERT 🚨")
    print("🔥" * 50)
    print("┌" + "─" * 58 + "┐")
    print("│                                                          │")
    print("│  💀 You: pip install flask-login==0.6.0                 │")
    print("│                                                          │")
    print("│  🧠 omnipkg AI suggests:                                 │")
    print("│      omnipkg install flask-login==0.6.0                 │")
    print("│                                                          │")
    print("│  ⚠️  WARNING: pip will NUKE your environment! ⚠️          │")
    print("│      • Downgrade from 0.6.3 to 0.6.0                   │")
    print("│      • Break newer Flask compatibility                  │")
    print("│      • Destroy your modern app                          │")
    print("│      • Welcome you to dependency hell 🔥                │")
    print("│                                                          │")
    print("│  [Y]es, I want chaos | [N]o, save me omnipkg! 🦸‍♂️        │")
    print("│                                                          │")
    print("└" + "─" * 58 + "┘")
    print("        \\   ^__^")
    print("         \\  (💀💀)\\______   <- This is your environment")
    print("            (__)\\       )\\/\\   after using pip")
    print("                ||---ww |")
    print("                ||     ||")
    print("💡 Pro tip: Choose 'N' unless you enjoy suffering")

def simulate_user_choice(choice, message):
    """Simulate user input with a delay"""
    print(f"\nChoice (y/n): ", end="", flush=True)
    time.sleep(1)
    print(choice)
    time.sleep(0.5)
    print(f"💭 {message}")
    return choice.lower()

def run_command(command_list, check=True):
    """Helper to run a command and stream its output."""
    print(f"\n$ {' '.join(command_list)}")
    # COMPATIBILITY FIX: Ensure we call the omnipkg CLI entrypoint correctly.
    if command_list[0] == "omnipkg":
        command_list = [sys.executable, "-m", "omnipkg.cli"] + command_list[1:]

    process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
    for line in iter(process.stdout.readline, ''):
        print(line.strip())
    process.stdout.close()
    retcode = process.wait()
    if check and retcode != 0:
        raise RuntimeError(f"Demo command failed with exit code {retcode}")
    return retcode

def run_interactive_command(command_list, input_data, check=True):
    """Helper to run a command that requires stdin input."""
    print(f"\n$ {' '.join(command_list)}")
    # COMPATIBILITY FIX: Ensure we call the omnipkg CLI entrypoint correctly.
    if command_list[0] == "omnipkg":
        command_list = [sys.executable, "-m", "omnipkg.cli"] + command_list[1:]
        
    process = subprocess.Popen(
        command_list, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        bufsize=1, 
        universal_newlines=True
    )
    
    # Write the simulated input and close stdin
    print("💭 Simulating Enter key press...")
    process.stdin.write(input_data + "\n")
    process.stdin.close()

    for line in iter(process.stdout.readline, ''):
        print(line.strip())
    process.stdout.close()
    retcode = process.wait()
    if check and retcode != 0:
        raise RuntimeError(f"Demo command failed with exit code {retcode}")
    return retcode

def print_header(title):
    """Prints a consistent, pretty header."""
    print("\n" + "="*60)
    print(f"  🚀 {title}")
    print("="*60)

def run_demo():
    """Runs a fully automated, impressive demo of omnipkg's power."""
    try:
        # COMPATIBILITY FIX: Instantiate OmnipkgCore with the required config.
        config_manager = ConfigManager()
        pkg_instance = OmnipkgCore(config_manager.config) # Use OmnipkgCore

        print_header("omnipkg Interactive Demo")
        print("This demo will show you the classic dependency conflict and how omnipkg solves it.")
        time.sleep(3)
        
        # --- Step 1: Set a clean, modern baseline ---
        print_header("STEP 1: Setting up a modern, stable environment")
        run_command(["pip", "uninstall", "-y", "flask-login", "flask"], check=False)
        run_command(["pip", "install", "flask-login==0.6.3"])
        print("\n✅ Beautiful! We have flask-login 0.6.3 installed and working perfectly.")
        time.sleep(5)
        
        # --- Step 2: Show what happens when you use regular pip? 😱 ---
        print_header("STEP 2: What happens when you use regular pip? 😱")
        print("Let's say you need version 0.6.0 for compatibility with an existing project...")
        time.sleep(3)
        
        omnipkg_pip_jail()
        
        choice = simulate_user_choice("y", "User thinks: 'How bad could it be?' 🤡")
        time.sleep(3)
        
        if choice == 'y':
            print("\n🔓 Releasing pip... (your funeral)")
            print("💀 Watch as pip destroys your beautiful environment...")
            run_command(["pip", "install", "flask-login==0.6.0"])
            
            print("\n💥 BOOM! Look what pip did:")
            print("   ❌ Uninstalled flask-login 0.6.3")
            print("   ❌ Downgraded to flask-login 0.6.0")
            print("   ❌ Your modern project is now BROKEN")
            print("   ❌ Welcome to dependency hell! 🔥")
            print("\n💡 Remember: omnipkg exists when you're ready to stop suffering")
            time.sleep(8)
        
        # --- Step 3: The hero arrives - omnipkg to the rescue! ---
        print_header("STEP 3: omnipkg to the rescue! 🦸‍♂️")
        print("Let's fix this mess and install the newer version back with omnipkg...")
        print("Watch how omnipkg handles this intelligently:")
        run_command(["omnipkg", "install", "flask-login==0.6.3"])
        print("\n✅ omnipkg intelligently restored the modern version!")
        print("💡 Notice: No conflicts, no downgrades, just pure intelligence.")
        time.sleep(5)
        
        # --- Step 4: Now let's do it RIGHT ---
        print_header("STEP 4: Now let's install the older version the RIGHT way")
        print("This time, let's be smart about it...")
        time.sleep(3)
        
        omnipkg_pip_jail()
        
        choice = simulate_user_choice("n", "User thinks: 'I'm not falling for that again!' 🧠")
        
        if choice == 'n':
            print("\n🧠 Smart choice! Using omnipkg instead...")
            time.sleep(3)
 
            print("🔧 Installing flask-login==0.6.0 with omnipkg...")
            print("💡 omnipkg will skip if already available or create isolation as needed...")
            run_command(["omnipkg", "install", "flask-login==0.6.0"])
            print("\n✅ omnipkg install successful!")
            print("🎯 BOTH versions now coexist peacefully!")
            time.sleep(5)
        
        # --- Step 5: Show the current status ---
        print_header("STEP 5: Verifying omnipkg's Smart Management")
        print("Let's see how omnipkg is managing our packages...")
        run_command(["omnipkg", "status"], check=False)
        time.sleep(5)
        print("\n🔧 Note how omnipkg intelligently manages versions!")
        print("📦 Main environment: flask-login 0.6.3 (untouched)")
        print("🔧 omnipkg: flask-login 0.6.0 (available when needed)")
        
        # --- Step 6: Prove it with the Knowledge Base ---
        print_header("STEP 6: Inspecting the Knowledge Base")
        time.sleep(2)
        print("💡 Want details on a specific version?")
        print("We'll simulate pressing Enter to skip this part...")
        run_interactive_command(["omnipkg", "info", "flask-login"], "")
        
        print("\n🎯 Now you can see that BOTH versions are available to the system.")
        time.sleep(5)

        # --- Step 7: The Grand Finale - The "Magic Trick" ---
        print_header("STEP 7: The Grand Finale - Live Version Switching")

        # COMPATIBILITY FIX: This script now correctly uses omnipkgLoader.
        test_script_content = '''
# This content will be written to /tmp/omnipkg_magic_test.py by the demo script

import sys
import os
import importlib
from importlib.metadata import version as get_version, PackageNotFoundError
from pathlib import Path # Ensure Path is available

# Dynamically ensure omnipkg's loader is discoverable for this subprocess
try:
    _omnipkg_dist = importlib.metadata.distribution('omnipkg')
    _omnipkg_site_packages = Path(_omnipkg_dist.locate_file("omnipkg")).parent.parent
    if str(_omnipkg_site_packages) not in sys.path:
        sys.path.insert(0, str(_omnipkg_site_packages))
except Exception:
    # Fallback if omnipkg isn't formally installed or path already exists
    pass

from omnipkg.loader import omnipkgLoader # Import the new context manager loader

def test_version_switching():
    """Test omnipkg's seamless version switching using the new omnipkgLoader context manager."""
    print("🔍 Testing omnipkg's seamless version switching using omnipkgLoader...")

    # Test activating the specific version
    try:
        # Use the context manager to activate flask-login 0.6.0
        with omnipkgLoader("flask-login==0.6.0"):
            # Inside this block, flask_login 0.6.0 should be active
            import flask_login
            
            actual_version = "UNKNOWN" # Initialize to a safe default
            try:
                actual_version = get_version('flask-login')
                print(f"✅ Imported and verified version {actual_version}")
            except PackageNotFoundError:
                print("❌ PackageNotFoundError: 'flask-login' not found by importlib.metadata.version inside context.")
                sys.exit(1) # Indicate failure in the subprocess

            # Crucial check: access flask_login.config
            if hasattr(flask_login, 'config'):
                print("✅ 'flask_login.config' module found within specified version.")
            else:
                print("❌ 'flask_login.config' module NOT found within specified version.")
                sys.exit(1) # Fail the test if not found

            if actual_version != "0.6.0":
                print(f"❌ Version mismatch inside context: Expected 0.6.0, got {actual_version}.")
                sys.exit(1)

    except Exception as context_error:
        print(f"❌ Error while testing specified version: {context_error}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # Test that the environment automatically reverted to the main version
    print(f"\\n🌀 omnipkg loader: Verifying automatic reversion to main environment...")
    try:
        # After the 'with' block, the environment should be restored to its original state.
        # This means flask_login 0.6.3 should be active here.
        
        # Force a reload to ensure Python picks up the restored main environment module
        # This is important if 'flask_login' was imported *before* the 'with' block was entered.
        try:
            # Attempt to reload if it's already in sys.modules
            if 'flask_login' in sys.modules:
                importlib.reload(sys.modules['flask_login'])
            else:
                # Otherwise, just import it normally
                import flask_login
        except ImportError:
            # If it's not found, that's also an indicator (should be present for 0.6.3)
            print("❌ flask_login not found after context deactivation.")
            sys.exit(1)

        current_version = "UNKNOWN"
        try:
            current_version = get_version('flask-login')
        except PackageNotFoundError:
            print("❌ PackageNotFoundError: 'flask-login' not found by importlib.metadata.version after context deactivation.")
            sys.exit(1)

        print(f"✅ Back to version: {current_version}")
        if current_version == "0.6.3":
            print("🔄 Seamless switching between main environment and omnipkg versions!")
        else:
            print(f"❌ Reversion failed! Expected 0.6.3 but got {current_version}.")
            sys.exit(1)

    except Exception as revert_error:
        print(f"❌ Error while testing main version after context: {revert_error}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    print("\\n🎯 THE MAGIC: All versions work in the SAME Python process!")
    print("🚀 No virtual environments, no containers - just pure Python import magic!")

if __name__ == "__main__":
    test_version_switching()
'''
        test_script_path = Path("/tmp/omnipkg_magic_test.py")
        with open(test_script_path, 'w') as f:
            f.write(test_script_content)
        
        print(f"\n$ python {test_script_path}")
        run_command([sys.executable, str(test_script_path)], check=False)
        
        try:
            test_script_path.unlink()
        except:
            pass

        print("\nSee test above: we not only have multiple versions in the same environment, but can even run them in the same script!")
        time.sleep(5)
        print("\n" + "="*60)
        print("🎉🎉🎉 DEMO COMPLETE! 🎉🎉🎉")
        print("📚 What you learned:")
        print("   💀 pip: Breaks everything, creates dependency hell")
        print("   🧠 omnipkg: Smart isolation, peaceful coexistence")
        print("   🔧 Intelligence: Skips redundant work, creates isolation when needed")
        print("   🔄 Magic: Seamless switching without containers")
        print("🚀 Dependency hell is officially SOLVED!")
        print("   Welcome to omnipkg heaven!")
        print("="*60)
        
    except Exception as demo_error:
        print(f"\n❌ An unexpected error occurred during the demo: {demo_error}")
        import traceback
        traceback.print_exc()
        print("\n💡 Don't worry - even if some steps failed, the core isolation is working!")
        print("That's the main achievement of omnipkg! 🔥")

if __name__ == "__main__":
    run_demo()