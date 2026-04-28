import { test, expect } from '@playwright/test'

test('首页加载并显示精选标题', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('精选')
})

test('底部导航栏显示 4 个 Tab', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('精选')).toBeVisible()
  await expect(page.getByText('搜索')).toBeVisible()
  await expect(page.getByText('AI')).toBeVisible()
  await expect(page.getByText('设置')).toBeVisible()
})

test('点击搜索 Tab 切换到搜索页面', async ({ page }) => {
  await page.goto('/')
  await page.getByText('搜索').click()
  await expect(page.locator('h1')).toContainText('搜索')
})

test('点击 AI Tab 切换到 AI 对话页面', async ({ page }) => {
  await page.goto('/')
  await page.getByText('AI').click()
  await expect(page.locator('h1')).toContainText('AI 助手')
})

test('点击设置 Tab 切换到设置页面', async ({ page }) => {
  await page.goto('/')
  await page.getByText('设置').click()
  await expect(page.locator('h1')).toContainText('设置')
})