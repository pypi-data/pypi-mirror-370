
# Rhaid v0.7.0 (Camwood Inc.)

## Why Rhaid is #1

- **Comprehensive hygiene**: Scans and fixes Python, JS/TS, Markdown, TOML, Terraform, and more.
- **AI guardrails**: Baseline-aware, suppressions, and smart fixers.
- **Fast & scalable**: Parallel scanning, caching, and baseline support for large repos.
- **Extensible**: Easy to add custom rules/fixers and plugins.
- **Multi-platform**: CLI, VS Code extension, Gradio app, and CI/CD workflows.
- **Open & documented**: MIT licensed, with developer guides and API docs.

## Usage Examples

### CLI
```sh
rhaid --path . --mode scan --json
rhaid --path src/ --mode fix --backup --rules "+format:*,+json:*" --fix-only "+format:*"
```

### VS Code Extension
- Install from Marketplace or build from source.
- Use "Rhaid: Scan Workspace" and "Rhaid: Fix Current File" commands.
- Diagnostics and quick fixes in the editor.

### Gradio App
- Upload a ZIP or enter a Git repo URL.
- Choose scan or fix mode, add extra args if needed.
- Download results as JSON and ZIP.

### CI/CD (GitHub Actions)
- Use `.github/workflows/rhaid_pr.yml` for baseline-aware PR checks.
- Use `.github/workflows/rhaid_sweep.yml` for automated hygiene sweeps.

## Contributing & Extending

- See `rhaid/rules.py` for rule/fixer API and examples.
- Add new rules/fixers with the `@rule` and `@fixer` decorators.
- For plugins, place your modules in a `plugins/` directory (future support).
- Run tests with `pytest`.


## API Reference

- `@rule(id: str)`: Decorator to register a rule. See `rhaid/rules.py`.
- `@fixer(id: str)`: Decorator to register a fixer.
- `load_plugins(plugin_dir: str)`: Dynamically load plugins.
- `run_rules(path, content, ctx)`: Run all rules on file content.
- `apply_fixers(path, content, issues, ctx)`: Apply all fixers to file content.

## Troubleshooting

- If the CLI or extension can't find the Rhaid binary, check your PATH or set `rhaid.pathToBinary`.
- For Gradio app errors, ensure dependencies are installed and repo URLs are public.
- For CI/CD, check workflow logs and the `rhaid_report.json` artifact for details.

## Security & Privacy

- No code is sent externally unless using LLM features.
- Secret scanning covers AWS keys, GitHub PATs, and private keys; expand patterns as needed.
- For sensitive code, run Rhaid locally or in your CI/CD.

---
MIT License — (c) 2025 Camwood Inc.
