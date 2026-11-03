// 只用于离线回归测试，不联网或启动外部模型。
import { appendFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const args = process.argv.slice(2);
if (process.env.FAKE_NPM_LOG) await appendFile(process.env.FAKE_NPM_LOG, `${JSON.stringify(args)}\n`);
if (args[0] === 'view') {
  if (process.env.FAKE_NPM_FAIL_METADATA) { process.stderr.write('simulated registry outage'); process.exit(2); }
  const result = args[2] === 'version' ? process.env.FAKE_NPM_VERSION : 'sha512-fixture';
  process.stdout.write(JSON.stringify(result));
} else if (args[0] === 'install') {
  if (process.env.FAKE_NPM_FAIL_INSTALL) { process.stderr.write('simulated installation failure'); process.exit(3); }
  const prefix = args[args.indexOf('--prefix') + 1];
  const version = args.find(arg => arg.startsWith('maestro-flow@')).slice('maestro-flow@'.length);
  const root = path.join(prefix, 'node_modules/maestro-flow');
  await mkdir(root, { recursive: true });
  await writeFile(path.join(root, 'package.json'), JSON.stringify({ name: 'maestro-flow', version, type: 'module' }));
  const resources = {
    '.codex/skills/maestro-next/SKILL.md': '# Fixture router',
    'workflows/run-mode.md': '# Fixture lifecycle',
    'ref/knowledge-closeout.md': '# Fixture closeout',
    'prepare/fixture.md': '# Fixture preparation',
  };
  if (process.env.FAKE_NPM_MISSING_ROUTER) delete resources['.codex/skills/maestro-next/SKILL.md'];
  for (const [relative, value] of Object.entries(resources)) {
    const target = path.join(root, relative);
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, value);
  }
  await mkdir(path.join(root, 'bin'), { recursive: true });
  await writeFile(path.join(root, 'bin/maestro.js'), `
    const args = process.argv.slice(2);
    const version = ${JSON.stringify(version)};
    if (args[0] === '--version') console.log(process.env.FAKE_CLI_BAD_VERSION ? '0.0.0' : version);
    else if (args[0] === 'capabilities') console.log(JSON.stringify({
      schema_version: 'maestro-capabilities/1.0', session_schema_writes: ['session/3.0'],
      execution_schema_writes: [], run_response_writes: ['run-response/1.2'],
      features: {session_run_minimal_v3: !process.env.FAKE_CLI_BAD_CAPABILITIES, entity_revision_cas: true,
        participant_identity: true, request_receipts_v2: true, execution_lease: false, operation_registry: false},
    }));
    else if (args[1] === '--help') {
      const help = {run:'next brief check complete', session:'open list status', update:'--check --migrate'};
      console.log(help[args[0]] ?? 'unknown');
    } else console.log(JSON.stringify({version, args, managed_home:process.env.MAESTRO_HOME}));
  `);
  await writeFile(path.join(prefix, 'package-lock.json'), JSON.stringify({ packages: {
    'node_modules/maestro-flow': { version, integrity: process.env.FAKE_NPM_BAD_INTEGRITY ? 'sha512-wrong' : 'sha512-fixture' },
  } }));
} else { process.stderr.write('unexpected fake npm command'); process.exit(4); }
