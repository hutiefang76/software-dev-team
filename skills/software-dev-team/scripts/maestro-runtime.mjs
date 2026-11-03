#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { access, cp, mkdir, mkdtemp, open, readFile, realpath, rename, rm, writeFile } from 'node:fs/promises';
import { constants } from 'node:fs';
import { homedir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const policy = JSON.parse(await readFile(path.join(skillRoot, 'references/runtime-policy.json'), 'utf8'));
const stableVersion = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/;
const readyFile = '.software-dev-team-ready.json';

function assertVersion(value) {
  if (!stableVersion.test(value ?? '')) throw new Error(`Invalid stable version: ${value}`);
  return value;
}

function checkNode() {
  const actual = process.versions.node.split('.').map(Number);
  const required = policy.minimum_node.split('.').map(Number);
  for (let index = 0; index < 3; index += 1) {
    if (actual[index] > required[index]) return;
    if (actual[index] < required[index]) throw new Error(`Node.js >= ${policy.minimum_node} is required; found ${process.versions.node}`);
  }
}

function defaultCacheRoot() {
  if (process.env.SOFTWARE_DEV_TEAM_CACHE) return path.resolve(process.env.SOFTWARE_DEV_TEAM_CACHE);
  if (process.env.CODEX_HOME) return path.resolve(process.env.CODEX_HOME, 'cache/software-dev-team');
  if (process.env.XDG_CACHE_HOME) return path.resolve(process.env.XDG_CACHE_HOME, 'software-dev-team');
  if (process.platform === 'win32' && process.env.LOCALAPPDATA) return path.resolve(process.env.LOCALAPPDATA, 'software-dev-team');
  return path.join(homedir(), '.cache/software-dev-team');
}

async function exists(file) {
  try { await access(file, constants.F_OK); return true; }
  catch (error) { if (error.code === 'ENOENT') return false; throw error; }
}

async function readJson(file, fallback = null) {
  try { return JSON.parse(await readFile(file, 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return fallback; throw error; }
}

async function writeJsonAtomic(file, value) {
  const temporary = `${file}.${process.pid}.${randomUUID()}.tmp`;
  try {
    await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
    await rename(temporary, file);
  } finally { await rm(temporary, { force: true }); }
}

async function capture(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { ...options, shell: false, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    let errors = '';
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; child.kill(); }, options.timeoutMs ?? 240000);
    child.stdout.on('data', chunk => { output = (output + chunk).slice(-2000000); });
    child.stderr.on('data', chunk => { errors = (errors + chunk).slice(-12000); });
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.on('close', code => {
      clearTimeout(timer);
      if (timedOut) reject(new Error(`Command timed out: ${path.basename(command)}`));
      else if (code !== 0) reject(new Error(`Command failed (${code}): ${errors.trim() || output.trim()}`));
      else resolve(output.trim());
    });
  });
}

async function findNpmCli() {
  const explicit = process.env.SOFTWARE_DEV_TEAM_NPM_CLI;
  if (explicit) {
    const selected = path.resolve(explicit);
    if (!(await exists(selected))) throw new Error('SOFTWARE_DEV_TEAM_NPM_CLI does not exist');
    return selected;
  }
  const candidates = [process.env.npm_execpath];
  const executableDirectory = path.dirname(process.execPath);
  const directories = [executableDirectory, ...(process.env.PATH ?? '').split(path.delimiter).filter(Boolean)];
  for (const directory of directories) {
    candidates.push(path.join(directory, 'node_modules/npm/bin/npm-cli.js'));
    candidates.push(path.resolve(directory, '../lib/node_modules/npm/bin/npm-cli.js'));
    try { candidates.push(await realpath(path.join(directory, 'npm'))); }
    catch (error) { if (!['ENOENT', 'ENOTDIR'].includes(error.code)) throw error; }
  }
  for (const candidate of candidates) {
    if (candidate?.endsWith('npm-cli.js') && await exists(candidate)) return candidate;
  }
  throw new Error('npm-cli.js not found. Install npm with Node.js or set SOFTWARE_DEV_TEAM_NPM_CLI to its real path.');
}

async function npm(args, cacheRoot) {
  const npmCli = await findNpmCli();
  return capture(process.execPath, [npmCli, ...args, '--fetch-timeout=30000', '--fetch-retries=1', `--registry=${policy.registry}`, `--cache=${path.join(cacheRoot, 'npm')}`]);
}

function versionRoot(cacheRoot, version) {
  return path.join(cacheRoot, 'versions', assertVersion(version));
}

function locations(root) {
  const packageRoot = path.join(root, 'node_modules', policy.package);
  return {
    package_root: packageRoot,
    entrypoint: path.join(packageRoot, 'bin/maestro.js'),
    skill_root: path.join(packageRoot, '.codex/skills'),
    router_skill: path.join(packageRoot, '.codex/skills/maestro-next/SKILL.md'),
    managed_home: path.join(root, 'home'),
  };
}

async function ready(cacheRoot, version) {
  if (!stableVersion.test(version ?? '')) return false;
  const root = versionRoot(cacheRoot, version);
  const marker = await readJson(path.join(root, readyFile));
  if (marker?.version !== version) return false;
  const files = locations(root);
  const packageJson = await readJson(path.join(files.package_root, 'package.json'));
  return packageJson?.name === policy.package && packageJson.version === version &&
    await exists(files.entrypoint) && await exists(files.router_skill) &&
    await exists(path.join(files.managed_home, 'workflows/run-mode.md'));
}

async function smoke(root, version) {
  const files = locations(root);
  const packageJson = await readJson(path.join(files.package_root, 'package.json'));
  if (packageJson?.name !== policy.package || packageJson.version !== version) throw new Error('Installed package identity does not match the requested release');
  const required = [files.router_skill, path.join(files.package_root, 'workflows/run-mode.md'), path.join(files.package_root, 'ref/knowledge-closeout.md')];
  for (const file of required) if (!(await exists(file))) throw new Error(`Required upstream resource is missing: ${path.relative(root, file)}`);
  await mkdir(files.managed_home, { recursive: true });
  const environment = { ...process.env, MAESTRO_HOME: files.managed_home };
  const cliVersion = await capture(process.execPath, [files.entrypoint, '--version'], { env: environment });
  if (cliVersion !== version) throw new Error(`CLI version mismatch: requested ${version}, reported ${cliVersion}`);
  const capabilities = JSON.parse(await capture(process.execPath, [files.entrypoint, 'capabilities', '--json'], { env: environment }));
  const requiredFeatures = ['session_run_minimal_v3', 'entity_revision_cas', 'participant_identity', 'request_receipts_v2'];
  if (capabilities.schema_version !== 'maestro-capabilities/1.0' ||
      !capabilities.session_schema_writes?.includes('session/3.0') ||
      !capabilities.run_response_writes?.includes('run-response/1.2') ||
      !Array.isArray(capabilities.execution_schema_writes) || capabilities.execution_schema_writes.length !== 0 ||
      requiredFeatures.some(feature => capabilities.features?.[feature] !== true) ||
      capabilities.features?.execution_lease !== false || capabilities.features?.operation_registry !== false) {
    throw new Error('Upstream lifecycle capabilities are incompatible with this adapter');
  }
  for (const [command, words] of [['run', ['next', 'brief', 'check', 'complete']], ['session', ['open', 'list', 'status']], ['update', ['--check', '--migrate']]]) {
    const help = await capture(process.execPath, [files.entrypoint, command, '--help'], { env: environment });
    if (words.some(word => !help.includes(word))) throw new Error(`Upstream ${command} command is incompatible with this adapter`);
  }
  return files;
}

async function installVersion(cacheRoot, version, integrity) {
  const versions = path.join(cacheRoot, 'versions');
  await mkdir(versions, { recursive: true });
  if (await ready(cacheRoot, version)) { await smoke(versionRoot(cacheRoot, version), version); return; }
  const destination = versionRoot(cacheRoot, version);
  if (await exists(destination)) throw new Error(`Incomplete version directory exists: ${destination}; inspect it before retrying`);
  const staging = await mkdtemp(path.join(versions, `.stage-${version}-`));
  try {
    await writeFile(path.join(staging, 'package.json'), JSON.stringify({ name: 'software-dev-team-managed-runtime', private: true, version: '0.0.0' }));
    await npm(['install', '--prefix', staging, '--save-exact', '--ignore-scripts', '--no-audit', '--no-fund', `${policy.package}@${version}`], cacheRoot);
    const lock = await readJson(path.join(staging, 'package-lock.json'));
    const record = lock?.packages?.[`node_modules/${policy.package}`];
    if (record?.version !== version || record.integrity !== integrity) throw new Error('npm lockfile does not match the official release integrity');
    const files = await smoke(staging, version);
    for (const resource of ['workflows', 'prepare', 'ref']) {
      await cp(path.join(files.package_root, resource), path.join(files.managed_home, resource), { recursive: true, force: false, errorOnExist: true });
    }
    const architecture = path.join(files.package_root, 'resources/arch-kb');
    if (await exists(architecture)) await cp(architecture, path.join(files.managed_home, 'arch-kb'), { recursive: true, force: false, errorOnExist: true });
    await writeJsonAtomic(path.join(staging, readyFile), { version, integrity, installed_at: new Date().toISOString(), checks: 'cli-resources-capabilities' });
    await rename(staging, destination);
  } finally {
    // 仅清理本次 mkdtemp 创建且仍在版本目录内的暂存路径。
    if (path.dirname(path.resolve(staging)) !== path.resolve(versions) || !path.basename(staging).startsWith(`.stage-${version}-`)) throw new Error('Refusing to clean an unexpected staging path');
    await rm(staging, { recursive: true, force: true });
  }
}

async function acquireLock(cacheRoot) {
  const lockPath = path.join(cacheRoot, 'install.lock');
  try {
    const handle = await open(lockPath, 'wx');
    await handle.writeFile(JSON.stringify({ pid: process.pid, created_at: new Date().toISOString() }));
    await handle.close();
    return async () => rm(lockPath, { force: true });
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const lock = await readJson(lockPath);
    if (Number.isInteger(lock?.pid) && lock.pid > 0) {
      try { process.kill(lock.pid, 0); }
      catch (processError) {
        if (processError.code === 'ESRCH') { await rm(lockPath, { force: true }); return acquireLock(cacheRoot); }
      }
    }
    throw new Error('Another runtime installation is active. Keep using the pinned version or retry after it completes.');
  }
}

function receipt(cacheRoot, state, updateStatus, extra = {}) {
  return { status: 'ready', package: policy.package, version: state.active_version, update_status: updateStatus, checked_at: state.checked_at ?? null,
    cache_root: cacheRoot, ...locations(versionRoot(cacheRoot, state.active_version)), ...extra };
}

async function ensure(cacheRoot, options) {
  const statePath = path.join(cacheRoot, 'state.json');
  let state = await readJson(statePath, {});
  let usable = await ready(cacheRoot, state.active_version);
  if (options.offline) {
    if (!usable) throw new Error('No usable cached Maestro version is available for offline use');
    return receipt(cacheRoot, state, 'offline');
  }
  const elapsed = Date.now() - Date.parse(state.checked_at ?? '');
  if (usable && !options.refresh && Number.isFinite(elapsed) && elapsed >= 0 && elapsed < policy.check_interval_hours * 3600000) return receipt(cacheRoot, state, 'cached');
  await mkdir(cacheRoot, { recursive: true });
  let release;
  try { release = await acquireLock(cacheRoot); }
  catch (error) {
    if (usable) return receipt(cacheRoot, state, 'busy_using_cached', { warning: error.message });
    throw error;
  }
  try {
    state = await readJson(statePath, {});
    usable = await ready(cacheRoot, state.active_version);
    const latest = assertVersion(JSON.parse(await npm(['view', `${policy.package}@${policy.channel}`, 'version', '--json'], cacheRoot)));
    const integrity = JSON.parse(await npm(['view', `${policy.package}@${latest}`, 'dist.integrity', '--json'], cacheRoot));
    if (typeof integrity !== 'string' || !integrity.startsWith('sha512-')) throw new Error('Official release integrity is missing or unsupported');
    if (latest === policy.tested_version && integrity !== policy.tested_integrity) throw new Error('Tested release integrity changed unexpectedly');
    await installVersion(cacheRoot, latest, integrity);
    const previous = state.active_version;
    state = { active_version: latest, checked_at: new Date().toISOString(), registry: policy.registry };
    await writeJsonAtomic(statePath, state);
    return receipt(cacheRoot, state, !previous ? 'installed' : previous === latest ? 'up_to_date' : 'updated');
  } catch (error) {
    if (!usable) throw error;
    state = { ...state, checked_at: new Date().toISOString(), last_update_error: error.message };
    await writeJsonAtomic(statePath, state);
    return receipt(cacheRoot, state, 'update_failed_using_cached', { warning: error.message });
  } finally { await release(); }
}

function parseOptions(argv) {
  const separator = argv.indexOf('--');
  const options = { cacheRoot: defaultCacheRoot(), refresh: false, offline: false, version: null, cliArgs: separator < 0 ? [] : argv.slice(separator + 1) };
  const own = separator < 0 ? argv : argv.slice(0, separator);
  for (let index = 0; index < own.length; index += 1) {
    const value = own[index];
    if (value === '--refresh') options.refresh = true;
    else if (value === '--offline') options.offline = true;
    else if (['--cache-root', '--version'].includes(value)) {
      const next = own[++index];
      if (!next || next.startsWith('--')) throw new Error(`Missing value for ${value}`);
      if (value === '--cache-root') options.cacheRoot = path.resolve(next);
      else options.version = assertVersion(next);
    } else throw new Error(`Unknown option: ${value}`);
  }
  if (options.offline && options.refresh) throw new Error('--offline and --refresh cannot be combined');
  return options;
}

async function runPinned(options) {
  if (!options.version || !options.cliArgs.length) throw new Error('run requires --version <receipt version> -- <official CLI arguments>');
  if (!(await ready(options.cacheRoot, options.version))) throw new Error(`Pinned runtime is not installed and ready: ${options.version}`);
  const files = locations(versionRoot(options.cacheRoot, options.version));
  const child = spawn(process.execPath, [files.entrypoint, ...options.cliArgs], {
    shell: false, windowsHide: true, stdio: 'inherit', env: { ...process.env, MAESTRO_HOME: files.managed_home },
  });
  child.on('error', error => { process.stderr.write(`${error.message}\n`); process.exitCode = 1; });
  const result = await new Promise(resolve => child.on('close', code => resolve(code ?? 1)));
  process.exitCode = result;
}

async function main() {
  checkNode();
  const [command = 'ensure', ...rest] = process.argv.slice(2);
  if (['--help', 'help'].includes(command)) {
    process.stdout.write('Usage: node maestro-runtime.mjs ensure|status|run [--cache-root PATH] [--refresh|--offline] [--version VERSION -- CLI_ARGS]\n');
    return;
  }
  const options = parseOptions(rest);
  if (command === 'run') { await runPinned(options); return; }
  if (command === 'status') {
    const state = await readJson(path.join(options.cacheRoot, 'state.json'), {});
    const value = await ready(options.cacheRoot, state.active_version) ? receipt(options.cacheRoot, state, 'not_checked') : { status: 'not_installed', cache_root: options.cacheRoot };
    process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
    return;
  }
  if (command !== 'ensure') throw new Error(`Unknown command: ${command}`);
  if (options.version || options.cliArgs.length) throw new Error('ensure does not accept --version or CLI arguments');
  process.stdout.write(`${JSON.stringify(await ensure(options.cacheRoot, options), null, 2)}\n`);
}

main().catch(error => {
  process.stderr.write(`${JSON.stringify({ status: 'error', error: error.message })}\n`);
  process.exitCode = 1;
});
