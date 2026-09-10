import { test, expect } from '@playwright/test'

test.describe('Member Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard')
    const firstProject = page.locator('[role="row"]').first()
    await firstProject.click()

    const membersTab = page.locator('a, button', { hasText: /members|people/i })
    if (await membersTab.isVisible()) {
      await membersTab.click()
    }
  })

  test('user can add member to project', async ({ page }) => {
    const addButton = page.locator('button', { hasText: /add|invite|new member/i })
    await addButton.click()

    const emailInput = page.locator('input[type="email"]')
    const roleSelect = page.locator('select, [role="combobox"]')
    const submitButton = page.locator('button', { hasText: /add|invite|submit/i })

    await emailInput.fill(`member-${Date.now()}@example.com`)
    await roleSelect.click()
    await page.locator('text=/member|admin/i').first().click()
    await submitButton.click()

    await expect(page.locator('text=/added|success/i')).toBeVisible()
  })

  test('user can view members list', async ({ page }) => {
    const membersList = page.locator('[role="list"], .members-container, table')
    await expect(membersList).toBeVisible()
  })

  test('user can change member role', async ({ page }) => {
    const memberRow = page.locator('[role="row"]').first()
    const roleSelect = memberRow.locator('select, [role="combobox"]')
    await roleSelect.click()
    await page.locator('text=/admin|member/i').first().click()

    await expect(page.locator('text=/updated|success/i')).toBeVisible()
  })

  test('user can remove member from project', async ({ page }) => {
    const memberRow = page.locator('[role="row"]').first()
    const removeButton = memberRow.locator('button', { hasText: /remove|delete|kick/i })
    await removeButton.click()

    const confirmButton = page.locator('button', { hasText: /confirm|remove|yes/i })
    if (await confirmButton.isVisible()) {
      await confirmButton.click()
    }

    await expect(page.locator('text=/removed|deleted|success/i')).toBeVisible()
  })
})
