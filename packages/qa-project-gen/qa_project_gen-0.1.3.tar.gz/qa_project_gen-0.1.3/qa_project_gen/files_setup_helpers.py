from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))



def render_template(template_name: str, dest_path: Path, context=None, dry_run=False, force=False):
    context = context or {}

    if dry_run:
        print(f"⚙️ [DRY RUN] Would render template: {template_name} → {dest_path}")
        return

    template = env.get_template(template_name)
    content = template.render(**context)

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists() and not force:
        print(f"⏭️ Skipped (exists): {dest_path}")
        return

    dest_path.write_text(content, encoding="utf-8")
    if dest_path.exists() and force:
        print(f"✏️ Overwrote: {dest_path}")
    else:
        print(f"📝 Rendered: {dest_path}")


def create_files_from_templates(project_root: Path, dry_run=False, force=False, context=None):
    context = context or {}
    templates = {
        "playwright.config.ts.j2": "playwright.config.ts",
        "tsconfig.json.j2": "tsconfig.json",
        ".gitignore.j2": ".gitignore",
        "README.md.j2": "README.md",
        "tests/e2e/e2e_example.spec.ts.j2": "tests/e2e/e2e_example.spec.ts.j2",
        "tests/front_end/feature_one/example_frontend.spec.ts.j2": "tests/front_end/feature_one/example_frontend.spec.ts",
        "tests/back_end/feature_one/example_backend.spec.ts.j2": "tests/back_end/feature_one/example_backend.spec.ts",
        "tests/support/POMs/feature_one/example.page.ts.j2": "tests/support/POMs/feature_one/example.page.ts",
        "tests/support/utils/helpers.ts.j2": "tests/support/utils/helpers.ts",
        "tests/support/utils/test-data.ts.j2": "tests/support/utils/test-data.ts",
        "tests/support/utils/fixtures.ts.j2": "tests/support/utils/fixtures.ts"
    }

    for template_file, output_file in templates.items():
        render_template(template_file, project_root / output_file, context, dry_run, force)
