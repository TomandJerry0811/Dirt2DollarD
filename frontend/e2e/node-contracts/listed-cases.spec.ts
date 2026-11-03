import { test, expect } from '@playwright/test';
import { execFile } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

type Assertion = { path: string; op: string; value: unknown };
type ListedCase = {
  id: string; feature: string; scenario: string; node: string;
  source: Record<string, string>; fixture_note: string;
  input: unknown; assertions: Assertion[];
};
type Observation = {
  case_id: string; node: string; error: null | { type: string; message: string };
  context: Record<string, unknown> | null; calls: unknown; execution_status: string;
  adapter_error?: unknown;
};
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const catalog = JSON.parse(readFileSync(resolve(root, 'tests/playwright_node_cases.json'), 'utf8')) as { cases: ListedCase[] };
const execute = promisify(execFile);
const features = [...new Set(catalog.cases.map(c => c.feature))];
if (catalog.cases.length !== 189 || new Set(catalog.cases.map(c => c.id)).size !== 189) {
  throw new Error('The source manifest must contain exactly 189 unique TC IDs');
}

function at(value: unknown, path: string): unknown {
  return path.split('.').reduce<unknown>((v, key) =>
    v !== null && typeof v === 'object' ? (v as Record<string, unknown>)[key] : undefined, value);
}

function verify(result: Observation, assertion: Assertion, caseId: string): void {
  const actual = at(result, assertion.path);
  const message = `${caseId}: ${assertion.path} ${assertion.op} ${JSON.stringify(assertion.value)}`;
  switch (assertion.op) {
    case 'equal': expect.soft(actual, message).toEqual(assertion.value); break;
    case 'contains':
      if (typeof actual === 'string') expect.soft(actual, message).toContain(String(assertion.value));
      else expect.soft(actual, message).toContainEqual(assertion.value);
      break;
    case 'excludes': expect.soft(actual, message).not.toContain(String(assertion.value)); break;
    case 'length': expect.soft(actual, message).toHaveLength(Number(assertion.value)); break;
    case 'present': expect.soft(actual !== null && actual !== undefined, message).toBe(true); break;
    case 'matches': expect.soft(actual, message).toMatch(new RegExp(String(assertion.value), 'i')); break;
    case 'noCalls': expect.soft(actual ?? [], message).toEqual([]); break;
    case 'allBatchText': {
      const batches = actual as { text?: string }[] | undefined;
      expect.soft(Array.isArray(batches) && batches.length > 0 && batches.every(b => typeof b.text === 'string' && b.text.trim().length > 0), message).toBe(true);
      break;
    }
    case 'updatesIntact': {
      const context = actual as { client_updates?: { body: string }[]; summary_batches?: { text: string }[] } | undefined;
      const updates = context?.client_updates;
      const batches = context?.summary_batches;
      expect.soft(Array.isArray(updates) && Array.isArray(batches) && updates.length > 0 &&
        updates.every(update => batches.filter(batch => batch.text.includes(update.body)).length === 1), message).toBe(true);
      break;
    }
    default: throw new Error(`Unknown assertion operator: ${assertion.op}`);
  }
}

for (const feature of features) {
  test.describe(feature, () => {
    for (const scenario of catalog.cases.filter(c => c.feature === feature)) {
      test(`${scenario.id} | ${scenario.scenario}`, async ({}, testInfo) => {
        testInfo.annotations.push({ type: 'Sheet ID', description: scenario.id });
        testInfo.annotations.push({ type: 'Test layer', description: 'Real Python node; controlled repository/provider dependencies' });
        await test.step('Read sheet expectation and explicit fixtures', async () => {
          await testInfo.attach('sheet-case-and-fixtures', { body: JSON.stringify(scenario, null, 2), contentType: 'application/json' });
        });
        const result = await test.step('Execute actual Python node in an isolated process', async () => {
          let stdout: string, stderr: string;
          try {
            ({ stdout, stderr } = await execute(process.env.PLAYWRIGHT_PYTHON || 'python',
              ['-m', 'tests.playwright_nodes', scenario.id],
              { cwd: root, encoding: 'utf8', timeout: 35_000, maxBuffer: 12 * 1024 * 1024,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' } }));
          } catch (error) {
            const failure = error as Error & { stdout?: string; stderr?: string };
            await testInfo.attach('adapter-startup-error', { body: `${failure.message}\n${failure.stdout ?? ''}\n${failure.stderr ?? ''}`, contentType: 'text/plain' });
            throw new Error(`Python adapter failed for ${scenario.id}. Set PLAYWRIGHT_PYTHON to the interpreter with requirements-playwright.txt installed. See adapter-startup-error attachment.`);
          }
          if (stderr.trim()) await testInfo.attach('python-stderr', { body: stderr, contentType: 'text/plain' });
          const observed = JSON.parse(stdout) as Observation;
          expect(observed.adapter_error, 'An adapter error must never count as the expected node error').toBeUndefined();
          expect(observed.case_id).toBe(scenario.id);
          expect(observed.node).toBe(scenario.node);
          await testInfo.attach('actual-node-output', { body: JSON.stringify(observed, null, 2), contentType: 'application/json' });
          return observed;
        });
        await test.step('Assert the listed contract against observed outputs and calls', async () => {
          for (const assertion of scenario.assertions) verify(result, assertion, scenario.id);
        });
      });
    }
  });
}
