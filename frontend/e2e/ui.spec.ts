import { test, expect } from '@playwright/test'

test.describe('Navigation and Basic UI', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/portfolio|dashboard|app/i)
  })

  test('can navigate to login page', async ({ page }) => {
    await page.goto('/')
    const loginLink = page.locator('a', { hasText: /login|sign in/i })
    await loginLink.click()
    await expect(page).toHaveURL(/login|signin/)
  })

  test('can navigate to register page', async ({ page }) => {
    await page.goto('/')
    const registerLink = page.locator('a', { hasText: /register|sign up/i })
    await registerLink.click()
    await expect(page).toHaveURL(/register|signup/)
  })

  test('authenticated user can access dashboard', async ({ page }) => {
    await page.goto('/dashboard')
    const dashboard = page.locator('[role="main"], .dashboard, .container')
    await expect(dashboard).toBeVisible()
  })
})
