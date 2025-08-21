import sys
import subprocess
from pathlib import Path
import shutil


def read_cli_args(args):
    if not args:
        print("❌ Project name is missing. Usage: qa-gen <project-name> [--force] [--dry-run] [--path <destination>]")
        sys.exit(2)

    project_name = args[0]
    force = False
    dry = False
    path = "."  # Default path is current working dir

    i = 1
    while i < len(args):
        if args[i] == "--force":
            force = True
        elif args[i] == "--dry-run":
            dry = True
        elif args[i] == "--path" and i + 1 < len(args):
            path = args[i + 1]
            i += 1  # Skip the path value on next loop
        i += 1

    print(f"Project: {project_name} | Force: {force} | Dry-run: {dry} | Path: {path}")
    return project_name, force, dry, path





def check_prerequisites():
    try:
        node_check = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, check=True
        )
        node_check_result = node_check.stdout.strip()
        major = int(node_check_result.lstrip("v").split(".")[0])
        if major < 18:
            print("❌ Node.js 18+ required.")
            sys.exit(1)
        print("✅ Checked Node.js...")
    except FileNotFoundError:
        print("❌ Node.js not found. Install Node 18+.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("❌ Node.js found but failed to run. Reinstall Node.")
        sys.exit(1)

    try:
        subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        print("✅ Checked npm...")
    except FileNotFoundError:
        print("❌ npm not found. Install npm.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("❌ npm found but failed to run. Reinstall npm.")
        sys.exit(1)

    return

def create_folders(project_name, dry_run=False):
    base = Path(project_name)
    relative_paths = [
        "tests/e2e",
        "tests/front_end/feature_one",
        "tests/back_end/feature_one",
        "tests/support/POMs/feature_one",
        "tests/support/utils",
    ]

    if dry_run:
        for path in relative_paths:
            folder_path = base / path
            print(f"⚙️ [DRY RUN] would create: < {folder_path} >")
        return
    else:
        for path in relative_paths:
            folder_path = base / path
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"📥 Created: < {folder_path} >")
        return

def ensure_root(project_name, dry_run=False):
    base = Path(project_name)
    if dry_run:
        print("⚙️ [DRY RUN] Would create root folder if missing:", base)
    else:
        if not base.exists():
            base.mkdir(parents=True)
            print("📥 Created:", base)
        else:
            print("✅ Exists:", base)
    return base


def init_node_project(project_root, dry_run=False):
    project_root = Path(project_root)
    if dry_run:
        print("⚙️ [DRY RUN] Would run: npm init -y")
        print("⚙️ [DRY RUN] Would run: npm install -D playwright @playwright/test typescript ts-node")
        if sys.platform.startswith("linux"):
            print("⚙️ [DRY RUN] Would run: npx playwright install --with-deps")
        else:
            print("⚙️ [DRY RUN] Would run: npx playwright install")
    else:
        try:
            subprocess.run(["npm", "init", "-y"], cwd=project_root, check=True)
            print("✅ Node.js project initialized.")
        
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr}")
            sys.exit(1)

        try:
            subprocess.run(["npm", "install", "-D", "@faker-js/faker"], cwd=project_root, check=True)
            print("✅ Faker.JS installed and ready to use.")
        
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr}")
            sys.exit(1)

        try:
            subprocess.run(["npm", "install", "dotenv"], cwd=project_root, check=True)
            print("✅ DOTENV installed and ready to use.")
        
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr}")
            sys.exit(1)

        try:
            subprocess.run(["npm", "install", "-D", "playwright", "@playwright/test", "typescript", "ts-node"], cwd=project_root, check=True)
            print("✅ Playwright is now installed.")

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr}")
            sys.exit(1)

        try:
            if sys.platform.startswith("linux"):
                subprocess.run(["npx", "playwright", "install", "--with-deps"], cwd=project_root, check=True)
                print("✅ Playwright system deps + browsers installed.")
            else:
                subprocess.run(["npx", "playwright", "install"], cwd=project_root, check=True)
                print("✅ Playwright browsers are now installed.")

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr}")
            sys.exit(1)
    
def remove_node_project(project_root, dry_run=False):
    project_root = Path(project_root)

    targets = [
        project_root / "node_modules",
        project_root / "package.json",
        project_root / "package-lock.json",
        project_root / "tsconfig.json",
        project_root / "playwright.config.ts",
        project_root / "tests",
        project_root / ".gitignore",
        project_root / "README.md"
    ]

    for target in targets:
        if dry_run:
            print(f"⚙️ [DRY RUN] Would remove: {target}")
        else:
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                print(f"🗑️ Removed directory: {target}")
            elif target.is_file():
                target.unlink(missing_ok=True)
                print(f"🗑️ Removed file: {target}")
            else:
                print(f"ℹ️ Nothing to remove at: {target}")

        




