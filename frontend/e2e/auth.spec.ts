import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can register', async ({ page }) => {
    await page.goto('/')

    const registerLink = page.locator('a', { hasText: /register/i })
    if (await registerLink.isVisible()) {
      await registerLink.click()
    }

    const emailInput = page.locator('input[type="email"]')
    const usernameInput = page.locator('input[name="username"], input[placeholder*="username" i]')
    const passwordInput = page.locator('input[type="password"]')
    const submitButton = page.locator('button', { hasText: /register|sign up/i })

    await emailInput.fill(`test-${Date.now()}@example.com`)
    await usernameInput.fill(`testuser${Date.now()}`)
    await passwordInput.fill('TestPassword123!')

    await submitButton.click()

    await expect(page).toHaveURL(/\/dashboard|\/projects/)
  })

  test('user can login', async ({ page }) => {
    await page.goto('/')

    const emailInput = page.locator('input[type="email"]')
    const passwordInput = page.locator('input[type="password"]')
    const submitButton = page.locator('button', { hasText: /login|sign in/i })

    await emailInput.fill('test@example.com')
    await passwordInput.fill('password123')

    await submitButton.click()

    await expect(page).toHaveURL(/\/dashboard|\/projects/)
  })

  test('user can logout', async ({ page }) => {
    await page.goto('/dashboard')

    const logoutButton = page.locator('button', { hasText: /logout|sign out/i })
    await logoutButton.click()

    await expect(page).toHaveURL('/')
  })

  test('login shows validation errors', async ({ page }) => {
    await page.goto('/')

    const submitButton = page.locator('button', { hasText: /login|sign in/i })
    await submitButton.click()

    const errorMessages = page.locator('text=/required|invalid/i')
    await expect(errorMessages).toBeVisible()
  })
})
