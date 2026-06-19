---
name: marketing-harness
description: >-
  Use this skill to operate thin marketing-harness scripts from a product repo:
  read YAML/JSON metadata, validate brand.lock/campaign YAML, dry-run or render
  through a local image skill/CLI provider, and publish only reviewed marketing
  artifacts into repo-owned public assets.
---

# Marketing Harness

This folder is the reusable skill payload. It should stay thin: `SKILL.md`,
small scripts, references, and templates. The runtime lives under `scripts/`;
do not add a top-level `src/` package or tests inside an installed skill
payload. A valid skill payload may have `scripts/`, `references/`, `assets/`,
and `agents/`.

Preserve the boundary:

```text
brand memory -> brand.lock.yaml -> campaign.yaml -> render -> human asset review -> publish
```

Never put visual style prompt text in campaign files. Campaigns describe content
and deliverables only.

## Metadata First

This skill is for AI agents. Do not rely on hard-coded product paths. Start by
finding or creating a small metadata file in the product repo, then pass it to
the adapter scripts.

Template:

```yaml
project:
  id: my-product
  root: .
  marketingRoot: packages/branding/marketing

brand:
  lock: packages/branding/marketing/brand.lock.yaml
  campaigns: packages/branding/marketing/campaigns
  references: packages/branding/marketing/references

campaign:
  name: launch
  path: packages/branding/marketing/campaigns/launch.campaign.yaml

artifacts:
  scratch: packages/branding/.harness/out
  approved: packages/branding/public/marketing

policy:
  requireHumanApprovalBeforeRender: true
  requireHumanApprovalBeforePublish: true
  allowRootWorkspaceBootstrap: false
```

`assets/marketing-harness-template.yaml` contains a copyable starter. If the
repo already has its own marketing/branding layout, match it instead of moving
files to a generic root-level directory.

## Resolve Roots

Keep these roots separate:

- **Project root:** the user's current product repo.
- **Marketing root:** the product-owned source location from metadata, such as
  `packages/branding/marketing`.
- **Scratch output:** the product-owned temporary render location from metadata,
  such as `packages/branding/.harness/out`.
- **Approved assets:** the product-owned location for reviewed public assets.
- **Skill root:** this installed `skills/marketing-harness` folder.

Do not create root-level `workspace/`, `outputs/`, `published/`, or `releases/`
by default. Use metadata paths.

The launcher is:

```bash
python3 "$SKILL_ROOT/scripts/harness.py"
```

It runs the bundled scripts in this skill. There is no `uvx` remote runtime
fallback and no ancestor checkout discovery.

Run the initial check from the project root:

```bash
sh "$SKILL_ROOT/scripts/check_harness.sh" --metadata packages/branding/marketing.harness.yaml .
```

In command examples below, `$HARNESS` means the launcher command above. It runs
while keeping relative paths rooted in the current product repo.

For a fresh product repo, preview the local project folders:

```bash
sh "$SKILL_ROOT/scripts/bootstrap_project.sh" --metadata packages/branding/marketing.harness.yaml .
```

Add `--write` only after reviewing the plan:

```bash
sh "$SKILL_ROOT/scripts/bootstrap_project.sh" --metadata packages/branding/marketing.harness.yaml --write .
```

The bootstrap script is create-only. It does not edit `.gitignore` or
`.gitattributes`, and it does not delete existing files. Use `--with-example`
only when the user explicitly wants the bundled CodeFox example copied under
the metadata marketing root.

## Common Defaults

- Always dry-run before live render.
- Publish channel is `repo`.
- Do not commit automatically.
- Do not call image APIs or publish until the user has approved the cost/action.

For exact command sequences, read `references/workflows.md`. For schema
contracts, read `references/contracts.md`.

## Style Production

When a design skill, Claude, Codex, or a human produces style, freeze the result
as a reviewed `brand.lock.yaml` proposal before render. Style production is not
a harness command; use the most relevant local design skill or a human-provided
brief and references, then write or update a proposal file under the
metadata-declared marketing root.

Selection order for design producers:

1. If the user names a local design skill, prefer it.
2. Otherwise prefer an already-installed local brand/frontend/visual design skill.
3. If none exists, stop and ask the user to install/specify one or provide a
   reviewed brief and references.

Do not download, clone, or install a remote design skill as an implicit fallback.
Proposal review flow:

```bash
$HARNESS validate --metadata packages/branding/marketing.harness.yaml \
  --brand packages/branding/marketing/proposals/<name>.lock.yaml

$HARNESS render \
  --metadata packages/branding/marketing.harness.yaml \
  --brand packages/branding/marketing/proposals/<name>.lock.yaml \
  --dry-run
```

Only after review should the user or agent copy the accepted proposal to the
official `brand.lock.yaml` path.

## Rendering And Publishing

Before live render, confirm API usage and possible cost. The harness has one
live image entrypoint: a local image skill/CLI. Its credentials belong in the
environment; never print, commit, or copy them into configuration files. Ensure
the local `gpt-image` CLI is installed or `HARNESS_SKILL_CLI_COMMAND` points to
an equivalent command. `provider.model` is optional; when omitted, this skill
does not pass `--model` and lets the image provider choose its default.

Live generation:

```bash
$HARNESS validate --metadata packages/branding/marketing.harness.yaml
$HARNESS render --metadata packages/branding/marketing.harness.yaml
```

After live render, inspect generated files, dimensions, text quality,
`manifest.json`, and `run.lock.json`. Show output paths and ask for explicit
human asset acceptance before any command with `--publish`, unless the user
explicitly pre-approved auto-publish.

After acceptance:

```bash
$HARNESS publish --metadata packages/branding/marketing.harness.yaml --publish
```

The approved asset directory should come from metadata. It may be a public
package directory, a separate asset git repository, or a submodule. The repo
publish channel stores generated assets, `manifest.json`, and `run.lock.json`
there. It never edits `.gitattributes` and never runs `git add`, `commit`, or
`push`.

Safe smoke test:

```bash
$HARNESS render --metadata packages/branding/marketing.harness.yaml --dry-run
$HARNESS publish --metadata packages/branding/marketing.harness.yaml
```

## Verification

After code or workflow changes:

```bash
uv run ruff check .
uv run pytest
python3 skills/marketing-harness/scripts/harness.py validate \
  skills/marketing-harness/examples/codefox/packages/branding/marketing/campaigns/example.campaign.yaml \
  --brand skills/marketing-harness/examples/codefox/packages/branding/marketing/brand.lock.yaml
python3 skills/marketing-harness/scripts/harness.py render \
  skills/marketing-harness/examples/codefox/packages/branding/marketing/campaigns/example.campaign.yaml \
  --brand skills/marketing-harness/examples/codefox/packages/branding/marketing/brand.lock.yaml \
  --dry-run
```

Check that no API key, authorization header, machine-specific path, or raw image
base64 payload is stored in tracked files.
