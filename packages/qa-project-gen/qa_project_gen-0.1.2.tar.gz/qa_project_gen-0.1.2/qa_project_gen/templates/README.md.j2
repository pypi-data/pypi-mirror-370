# Playwright Test Automation Project

## QA Usage Guide

### Test ID Strategy
This project uses `data-e2e` attributes for reliable element selection:
```html
<button data-e2e="login-submit">Login</button>
<input data-e2e="email-field" type="email">
```

Configure in `playwright.config.ts`:
```typescript
use: {
  testIdAttribute: 'data-e2e',
  // ...
}
```

### Page Object Model (POM) Pattern
POMs separate locators from actions for maintainable tests:

**Locator Section:**
```typescript
//////////  LOCATORS //////////
getPageTitle = () => this.page.locator('h2', { hasText: "Test TEXT" });
getEmailField = () => this.page.getByTestId('email-field');
getSubmitButton = () => this.page.getByTestId('login-submit');
```

**Actions Section:**
```typescript
//////////  ACTIONS //////////
public async loginUser(email: string, password: string) {
  await this.getEmailField().fill(email);
  await this.page.getByTestId('password-field').fill(password);
  await this.getSubmitButton().click();
  await this.page.waitForLoadState('networkidle');
}
```

### Test Organization Best Practices

1. **Feature-based Structure:** Organize tests by application features
2. **Separation of Concerns:** Keep UI tests, API tests, and POMs separate
3. **Data Management:** Use `test-data.ts` for consistent test data across tests
4. **Fixtures:** Leverage fixtures for authentication tokens and shared setup

### Running Tests

```bash
# Install dependencies
npm install

# Run all tests
npx playwright test

# Run specific test suite
npx playwright test tests/front_end
npx playwright test tests/back_end

# Run tests in headed mode
npx playwright test --headed

# Run tests with specific browser
npx playwright test --project=chromium
```

### Test Data Usage
```typescript
import { testData } from '../support/utils/test-data';

// Use predefined data
await loginPage.loginUser(testData.auth.admin.email, testData.auth.admin.password);

// Use dynamic Faker data
const newContact = testData.contact; // Generates fresh data each run
```

### Authentication with Fixtures
```typescript
import { test, expect } from '../support/utils/fixtures';

test('authenticated test', async ({ page, authToken }) => {
  // authToken fixture automatically available
  await page.setExtraHTTPHeaders({
    'Authorization': `Bearer ${authToken}`
  });
});
```

Happy Testing! 🎭