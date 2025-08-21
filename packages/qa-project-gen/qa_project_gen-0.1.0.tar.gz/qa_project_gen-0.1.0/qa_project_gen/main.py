from .project_setup_helpers import *
from .files_setup_helpers import *
from pathlib import Path
import sys

def main():
    project_name, force, dry_run, custom_path = read_cli_args(sys.argv[1:])
    project_root = Path(custom_path) / project_name

    if "--clean" in sys.argv[1:]:
        remove_node_project(project_root, dry_run)
        return

    check_prerequisites()
    project_root = ensure_root(project_root, dry_run)
    init_node_project(project_root, dry_run)
    create_folders(project_root, dry_run)



    create_files_from_templates(project_root, dry_run, force, context={"project_name": project_name})



    print("\n🚀 Done! Your Playwright testing project is ready.")
    if dry_run:
        print("🧪 This was a dry run. No actual files were written.")
    else:
        print(f"📁 Navigate to: {project_name}")
        print("💡 Run tests with: `npx playwright test`")

if __name__ == "__main__":
    main()
