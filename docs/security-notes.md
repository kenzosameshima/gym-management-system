# Security Notes

## Frontend npm audit

`npm audit` reports two moderate vulnerabilities:

- Package: `esbuild <=0.24.2`
- Path: transitive dependency through `vite <=6.4.1`
- Advisory: `GHSA-67mh-4wv8-2f99`
- Proposed npm fix: `npm audit fix --force`
- Impact of proposed fix: installs Vite 8, a breaking major upgrade

This affects Vite development server behavior. The production frontend image builds static assets and serves them through Nginx, so this is not part of the runtime production container surface.

`npm audit fix` was executed without `--force` and did not resolve the issue. Do not run `--force` automatically; handle the Vite major upgrade as a planned tooling task.
