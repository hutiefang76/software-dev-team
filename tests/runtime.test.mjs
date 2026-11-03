import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const temporaryRoot = path.join(root, '.validation-tmp');
const script = path.join(root, 'skills/software-dev-team/scripts/maestro-runtime.mjs');
const fixture = path.join(root, 'tests/fixtures/npm-cli.mjs');

async function context(t) {
  await mkdir(temporaryRoot, { recursive: true });
  const directory = await mkdtemp(path.join(temporaryRoot, 'runtime-'));
  t.after(async () => {
    assert.equal(path.dirname(path.resolve(directory)), temporaryRoot);
    assert.ok(path.basename(directory).startsWith('runtime-'));
    await rm(directory, { recursive: true, force: true });
  });
  const cache = path.join(directory, 'cache with spaces');
  const log = path.join(directory, 'npm-calls.jsonl');
  return { directory, cache, log, env: { SOFTWARE_DEV_TEAM_NPM_CLI: fixture, FAKE_NPM_VERSION: '99.1.0', FAKE_NPM_LOG: log } };
}

async function invoke(ctx, args, environment = {}) {
  const separator = args.indexOf('--');
  const own = separator < 0 ? args : args.slice(0, separator);
  const forwarded = separator < 0 ? [] : args.slice(separator);
  const child = spawn(process.execPath, [script, ...own, '--cache-root', ctx.cache, ...forwarded], {
    shell: false, windowsHide: true, env: { ...process.env, ...ctx.env, ...environment },
  });
  let stdout = '';
  let stderr = '';
  child.stdout.on('data', data => { stdout += data; });
  child.stderr.on('data', data => { stderr += data; });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  return { code, stdout, stderr, value: code === 0 && stdout ? JSON.parse(stdout) : null };
}

async function state(ctx) { return JSON.parse(await readFile(path.join(ctx.cache, 'state.json'), 'utf8')); }
async function calls(ctx) { return (await readFile(ctx.log, 'utf8')).trim().split('\n').map(line => JSON.parse(line)); }

test('first use installs a stable release into an isolated cache', async t => {
  const ctx = await context(t);
  const result = await invoke(ctx, ['ensure']);
  assert.equal(result.code, 0, result.stderr);
  assert.equal(result.value.version, '99.1.0');
  assert.equal(result.value.update_status, 'installed');
  assert.equal((await state(ctx)).active_version, '99.1.0');
  assert.ok(result.value.managed_home.startsWith(ctx.cache));
  const install = (await calls(ctx)).find(args => args[0] === 'install');
  assert.ok(install.includes('--ignore-scripts'));
  assert.ok(install.includes('--registry=https://registry.npmjs.org/'));
  assert.ok(!install.includes('--global'));
});

test('fresh cache avoids network checks and installations', async t => {
  const ctx = await context(t);
  assert.equal((await invoke(ctx, ['ensure'])).code, 0);
  const before = await calls(ctx);
  const result = await invoke(ctx, ['ensure'], { FAKE_NPM_FAIL_METADATA: '1' });
  assert.equal(result.value.update_status, 'cached');
  assert.deepEqual(await calls(ctx), before);
});

test('an expired check automatically discovers a new release', async t => {
  const ctx = await context(t);
  await invoke(ctx, ['ensure']);
  const old = await state(ctx);
  old.checked_at = '2020-01-01T00:00:00.000Z';
  await writeFile(path.join(ctx.cache, 'state.json'), JSON.stringify(old));
  const result = await invoke(ctx, ['ensure'], { FAKE_NPM_VERSION: '99.3.0' });
  assert.equal(result.code, 0, result.stderr);
  assert.equal(result.value.version, '99.3.0');
  assert.equal(result.value.update_status, 'updated');
});

test('automatic update retains the old version for pinned work', async t => {
  const ctx = await context(t);
  await invoke(ctx, ['ensure']);
  const result = await invoke(ctx, ['ensure', '--refresh'], { FAKE_NPM_VERSION: '99.2.0' });
  assert.equal(result.code, 0, result.stderr);
  assert.equal(result.value.update_status, 'updated');
  assert.equal((await state(ctx)).active_version, '99.2.0');
  const pinned = await invoke(ctx, ['run', '--version', '99.1.0', '--', 'fixture'], {});
  assert.equal(pinned.code, 0, pinned.stderr);
  assert.equal(pinned.value.version, '99.1.0');
  assert.ok(pinned.value.managed_home.endsWith(path.join('99.1.0', 'home')));
});

test('failed update preserves the usable version and reports its failure', async t => {
  const ctx = await context(t);
  await invoke(ctx, ['ensure']);
  const result = await invoke(ctx, ['ensure', '--refresh'], { FAKE_NPM_VERSION: '99.2.0', FAKE_NPM_FAIL_INSTALL: '1' });
  assert.equal(result.code, 0, result.stderr);
  assert.equal(result.value.update_status, 'update_failed_using_cached');
  assert.match(result.value.warning, /installation failure/);
  assert.equal((await state(ctx)).active_version, '99.1.0');
  assert.ok(!(await readdir(path.join(ctx.cache, 'versions'))).some(name => name.startsWith('.stage-')));
});

test('registry failure uses cache but cannot pretend first installation succeeded', async t => {
  const ctx = await context(t);
  let result = await invoke(ctx, ['ensure'], { FAKE_NPM_FAIL_METADATA: '1' });
  assert.notEqual(result.code, 0);
  await invoke(ctx, ['ensure']);
  result = await invoke(ctx, ['ensure', '--refresh'], { FAKE_NPM_FAIL_METADATA: '1' });
  assert.equal(result.value.update_status, 'update_failed_using_cached');
  assert.equal(result.value.version, '99.1.0');
});

test('candidate CLI identity mismatch does not become active', async t => {
  const ctx = await context(t);
  const result = await invoke(ctx, ['ensure'], { FAKE_CLI_BAD_VERSION: '1' });
  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /CLI version mismatch/);
  assert.equal((await invoke(ctx, ['status'])).value.status, 'not_installed');
});

test('candidate without upstream resources is rejected', async t => {
  const ctx = await context(t);
  const result = await invoke(ctx, ['ensure'], { FAKE_NPM_MISSING_ROUTER: '1' });
  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /resource is missing/);
});

test('incompatible lifecycle capabilities do not replace the active version', async t => {
  const ctx = await context(t);
  await invoke(ctx, ['ensure']);
  const result = await invoke(ctx, ['ensure', '--refresh'], { FAKE_NPM_VERSION: '99.2.0', FAKE_CLI_BAD_CAPABILITIES: '1' });
  assert.equal(result.value.update_status, 'update_failed_using_cached');
  assert.equal(result.value.version, '99.1.0');
  assert.match(result.value.warning, /capabilities are incompatible/);
});

test('npm lock integrity must match registry metadata', async t => {
  const ctx = await context(t);
  const result = await invoke(ctx, ['ensure'], { FAKE_NPM_BAD_INTEGRITY: '1' });
  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /official release integrity/);
});

test('offline use requires a ready cache and does not contact npm', async t => {
  const ctx = await context(t);
  assert.notEqual((await invoke(ctx, ['ensure', '--offline'])).code, 0);
  await invoke(ctx, ['ensure']);
  const before = await calls(ctx);
  const result = await invoke(ctx, ['ensure', '--offline']);
  assert.equal(result.value.update_status, 'offline');
  assert.deepEqual(await calls(ctx), before);
});

test('live installation lock cannot be stolen', async t => {
  const ctx = await context(t);
  await mkdir(ctx.cache, { recursive: true });
  await writeFile(path.join(ctx.cache, 'install.lock'), JSON.stringify({ pid: process.pid }));
  const result = await invoke(ctx, ['ensure']);
  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /installation is active/);
  assert.equal(JSON.parse(await readFile(path.join(ctx.cache, 'install.lock'), 'utf8')).pid, process.pid);
});

test('version input rejects path traversal and shell fragments', async t => {
  const ctx = await context(t);
  for (const version of ['../../outside', '99.1.0 && echo bad', '99.1.0-beta']) {
    const result = await invoke(ctx, ['run', '--version', version, '--', '--version']);
    assert.notEqual(result.code, 0);
    assert.match(result.stderr, /Invalid stable version/);
  }
});

test('run requires an explicitly pinned version', async t => {
  const ctx = await context(t);
  const result = await invoke(ctx, ['run', '--', '--version']);
  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /run requires --version/);
});
