import { test, expect } from '@jupyterlab/galata';

/**
 * Don't load JupyterLab webpage before running the tests.
 * This is required to ensure we capture all log messages.
 */
test.use({ autoGoto: false });

test.describe('Sage Agent Extension', () => {
  test('should load the extension', async ({ page, baseURL }) => {
    // Navigate to JupyterLab
    await page.goto(`${baseURL}`);

    // Wait for JupyterLab to be ready
    await page.waitForSelector('#jp-main-dock-panel');

    // Click on the command palette button
    await page.click(
      '#jp-MainMenu .jp-Menu-item[data-command="apputils:activate-command-palette"]'
    );

    // Type the command to open the AI chat
    await page.fill('.jp-CommandPalette-input', 'AI Chat');

    // Wait for the command to appear in the list and click it
    await page.waitForSelector('li[data-command="sage-ai:open-chat"]');
    await page.click('li[data-command="sage-ai:open-chat"]');

    // Check that the chat panel is visible
    await page.waitForSelector('.sage-ai-chatbox');

    // Verify that welcome message is displayed
    // const welcomeText = await page.textContent('.sage-ai-system-message');
    // expect(welcomeText).toContain('Welcome to AI Chat');
  });
});
