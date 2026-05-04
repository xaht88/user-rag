import { test, expect } from '@playwright/test';

test.describe('RAG Chat Application Smoke Test', () => {
  test('should load the homepage', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:5173');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Verify the page loaded successfully
    await expect(page).toHaveTitle(/RAG Chat Application/i);
    
    // Check that the root element is rendered
    await expect(page.locator('#root')).toBeVisible();
  });

  test('should display chat interface elements', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    
    // Check for chat input field
    const chatInput = page.getByPlaceholder(/Введите вопрос/i);
    await expect(chatInput).toBeVisible();
    
    // Check for send button
    const sendButton = page.getByRole('button', { name: /Отправить/i });
    await expect(sendButton).toBeVisible();
  });

  test('should handle user input in chat', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    
    // Type a message
    const chatInput = page.getByPlaceholder(/Введите вопрос/i);
    await chatInput.fill('Тестовый запрос');
    
    // Verify the input was filled
    await expect(chatInput).toHaveValue('Тестовый запрос');
  });

  test('should display mock documents', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    
    // Check for document list
    const documentList = page.locator('ul');
    await expect(documentList).toBeVisible();
    
    // Check for document items (2 based on mock data)
    const documentItems = page.locator('li');
    await expect(documentItems).toHaveCount(2);
  });
});
