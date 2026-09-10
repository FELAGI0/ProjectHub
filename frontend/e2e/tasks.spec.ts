import { test, expect } from '@playwright/test'

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard')
    const firstProject = page.locator('[role="row"]').first()
    await firstProject.click()
  })

  test('user can create a task', async ({ page }) => {
    const createButton = page.locator('button', { hasText: /create|new task|add task/i })
    await createButton.click()

    const titleInput = page.locator('input[placeholder*="title" i]')
    const prioritySelect = page.locator('select, [role="combobox"]').nth(0)
    const submitButton = page.locator('button', { hasText: /create|submit|save/i })

    await titleInput.fill(`Test Task ${Date.now()}`)
    await prioritySelect.click()
    await page.locator('text=/medium|high/i').first().click()
    await submitButton.click()

    await expect(page.locator('text=/created|success/i')).toBeVisible()
  })

  test('user can view tasks list', async ({ page }) => {
    const tasksList = page.locator('[role="list"], .tasks-container, table')
    await expect(tasksList).toBeVisible()
  })

  test('user can update task status', async ({ page }) => {
    const taskRow = page.locator('[role="row"]').first()
    const statusSelect = taskRow.locator('select, [role="combobox"]')
    await statusSelect.click()
    await page.locator('text=/in progress|done/i').first().click()

    await expect(page.locator('text=/updated|success/i')).toBeVisible()
  })

  test('user can delete task', async ({ page }) => {
    const taskRow = page.locator('[role="row"]').first()
    const deleteButton = taskRow.locator('button', { hasText: /delete|remove/i })
    await deleteButton.click()

    const confirmButton = page.locator('button', { hasText: /confirm|delete|yes/i })
    if (await confirmButton.isVisible()) {
      await confirmButton.click()
    }

    await expect(page.locator('text=/deleted|removed|success/i')).toBeVisible()
  })
})
