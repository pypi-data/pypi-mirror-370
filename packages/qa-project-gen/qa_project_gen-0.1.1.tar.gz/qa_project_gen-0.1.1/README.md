# Playwright Project Setup CLI Tool

A Python CLI tool that quickly scaffolds a complete Playwright test automation project with TypeScript, organized structure, and QA best practices.

## Features

- **Quick Setup**: Creates a full Playwright project in seconds
- **Organized Structure**: Separates E2E, frontend, backend tests with POM pattern
- **Multi-browser**: Pre-configured for Chromium, Firefox, and WebKit
- **Test Data**: Faker.js integration for dynamic test data
- **TypeScript**: Full TypeScript support with proper configuration
- **Best Practices**: Includes fixtures, utilities, and Page Object Models
- **Custom Location**: Use `--path` to specify where to generate your project
- **Safe Execution**: Preview changes with `--dry-run` or force overwrites with `--force`

## Prerequisites

- Python 3.7+
- Node.js 18+
- npm

## Installation & Usage

### Option 1: Install via pip (Coming Soon)

```bash
pip install qa-gen
qa-gen my-project
```

### Option 2: Clone and Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/qa_automation_project_setup.git
cd qa_automation_project_setup

# Run the CLI tool
python main.py my-test-project

# With options
python main.py my-test-project --force --dry-run --path /your/target/path
```

## Command Options

```bash
python main.py <project-name> [options]

Options:
  --force        Overwrite existing files
  --dry-run      Preview what would be created without making changes
  --clean        Remove generated files from a project
  --path <dir>   Choose custom path to generate the project
```

## Examples

```bash
# Create a new project
qa-gen new-playwright-tests

# Use a custom location
qa-gen test-project --path /home/user/projects

# Preview without creating anything
qa-gen project-name --dry-run

# Overwrite an existing project
qa-gen my-existing-project --force

# Clean an existing project
qa-gen outdated-project --path /home/user/old_projects --clean
```

## Generated Project Structure

```
my-test-project/
├── playwright.config.ts           # Playwright configuration
├── tsconfig.json                  # TypeScript configuration
├── package.json                   # Node.js dependencies
├── .gitignore                     # Git ignore patterns
├── README.md                      # Project documentation
└── tests/
    ├── e2e/                       # End-to-end tests
    ├── front_end/feature_one/     # Frontend UI tests
    ├── back_end/feature_one/      # Backend API tests
    └── support/
        ├── POMs/feature_one/      # Page Object Models
        └── utils/                 # Test utilities
            ├── helpers.ts         # Common functions
            ├── test-data.ts       # Test data with Faker.js
            └── fixtures.ts        # Playwright fixtures
```

## What Gets Installed

The CLI automatically installs the following npm packages:
- `playwright` - Browser automation framework
- `@playwright/test` - Test runner and assertions
- `typescript` - TypeScript support
- `ts-node` - Run TS files directly
- `@faker-js/faker` - Realistic test data
- `dotenv` - Environment variables

## Running Tests in Your New Project

```bash
cd my-test-project

# Run all tests
npx playwright test

# Run tests in a folder
npx playwright test tests/front_end

# Run with browser UI
npx playwright test --headed

# View the test report
npx playwright show-report
```

---

Built with ❤️ to help QA Engineers move faster and write better tests.

README generated with GPT-4.