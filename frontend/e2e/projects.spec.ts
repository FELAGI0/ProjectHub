import { test, expect } from '@playwright/test'

test.describe('Project Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard')
  })

  test('user can create a project', async ({ page }) => {
    const createButton = page.locator('button', { hasText: /create|new project/i })
    await createButton.click()

    const projectNameInput = page.locator('input[placeholder*="name" i], input[placeholder*="project" i]')
    const descriptionInput = page.locator('textarea, input[placeholder*="description" i]')
    const submitButton = page.locator('button', { hasText: /create|submit|save/i })

    await projectNameInput.fill(`Test Project ${Date.now()}`)
    await descriptionInput.fill('Test project description')
    await submitButton.click()

    await expect(page.locator('text=/project created|success/i')).toBeVisible()
  })

  test('user can view projects list', async ({ page }) => {
    const projectsList = page.locator('[role="list"], .projects-container, table')
    await expect(projectsList).toBeVisible()
  })

  test('user can update project', async ({ page }) => {
    const projectRow = page.locator('[role="row"]').first()
    const editButton = projectRow.locator('button', { hasText: /edit/i })
    await editButton.click()

    const nameInput = page.locator('input[placeholder*="name" i]')
    await nameInput.fill(`Updated Project ${Date.now()}`)

    const saveButton = page.locator('button', { hasText: /save|submit/i })
    await saveButton.click()

    await expect(page.locator('text=/updated|success/i')).toBeVisible()
  })

  test('user can delete project', async ({ page }) => {
    const projectRow = page.locator('[role="row"]').first()
    const deleteButton = projectRow.locator('button', { hasText: /delete|remove/i })
    await deleteButton.click()

    const confirmButton = page.locator('button', { hasText: /confirm|delete|yes/i })
    if (await confirmButton.isVisible()) {
      await confirmButton.click()
    }

    await expect(page.locator('text=/deleted|removed|success/i')).toBeVisible()
  })
})
