import { defineConfig } from '@playwright/test';

// These contracts run the actual Python nodes through a CLI adapter.
// No browser, Vite, FastAPI server, credentials or external services are needed.
export default defineConfig({
  testDir: './e2e/node-contracts',
  testMatch: '**/*.spec.ts',
  outputDir: 'test-results-nodes',
  fullyParallel: true,
  workers: 2,
  timeout: 45_000,
  retries: 0,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report-nodes', open: 'never' }]],
  projects: [{ name: 'python-nodes' }],
});
