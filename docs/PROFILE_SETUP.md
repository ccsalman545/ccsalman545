# Profile README operations guide

This repository is a **GitHub profile repository** because its name matches the account name exactly: `ccsalman545`. GitHub renders the root [`README.md`](../README.md) above the repositories list at [github.com/ccsalman545](https://github.com/ccsalman545).

The profile is a **static README with dynamic modules**. Plain Markdown carries all the meaning; scheduled workflows refresh the numbers, the repository table, and the activity feed so the page stays honest without manual edits.

## Repository layout

```text
ccsalman545/
├── README.md                        # Public profile shown on GitHub
├── assets/                          # Hand-built, theme-aware SVG artwork
│   ├── banner-dark.svg              # 1280×320 hero, dark theme
│   ├── banner-light.svg             # 1280×320 hero, light theme
│   ├── divider-dark.svg             # Section rule, dark theme
│   └── divider-light.svg            # Section rule, light theme
├── data/                            # Generated Shields.io endpoint payloads
│   ├── stars.json forks.json repos.json
│   └── followers.json languages.json updated.json
├── .github/
│   └── scripts/
│       ├── profile_common.py        # Shared API + marker helpers (stdlib only)
│       ├── update_activity.py       # Daily public-activity renderer
│       ├── update_repos.py          # Weekly repo table, counters, badge data
│       ├── check_readme.py          # Pre-merge structural validator
│       └── featured.json            # Curated ordering for the repo table
├── scripts/
│   └── enable-automation.sh         # Copies the workflow templates into place
└── docs/
    ├── PROFILE_SETUP.md             # This operating guide
    └── workflow-templates/          # Workflows, installed by the script above
```

> The workflows are not committed under `.github/workflows/`. GitHub blocks
> automated tooling from creating files there, so they ship as templates and
> [`scripts/enable-automation.sh`](../scripts/enable-automation.sh) installs them
> using your own credentials.

## Activation checklist

Everything ships ready to run. Work through this list once.

1. **Merge the change into `main`.** GitHub only renders the profile README from the default branch.
2. **Install the workflows.** Because GitHub does not let bots write to `.github/workflows/`, run:

   ```bash
   bash scripts/enable-automation.sh
   git add .github/workflows
   git commit -m "ci: enable profile automation"
   git push
   ```

   Re-run the script any time a template changes; it only copies what differs.
3. Open **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**. The activity, repository, snake, and blog jobs commit their own changes.
4. Open **Actions → Generate contribution snake → Run workflow** once. This creates the `output` branch that hosts both snake SVGs; the module renders as soon as the job succeeds.
5. Open **Actions → Refresh featured repositories → Run workflow** once. This seeds the counters and the repository table immediately instead of waiting for Monday.
6. Open **Actions → Refresh profile activity → Run workflow** once to seed the activity feed.
7. Check the profile in a private window on desktop and phone, in both GitHub Light and GitHub Dark.

> Never put email credentials, personal tokens, or API keys in `README.md`, workflow files, or repository variables. Everything here uses GitHub's scoped `GITHUB_TOKEN`, except WakaTime, which uses a repository **secret**.

## Automation schedule

| Workflow | Schedule (UTC) | What it changes |
| :-- | :-- | :-- |
| [`update-activity.yml`](workflow-templates/update-activity.yml) | Daily 02:17 | `<!-- ACTIVITY -->` block from the Events API |
| [`update-repos.yml`](workflow-templates/update-repos.yml) | Mondays 04:23 | `<!-- REPOS -->` table, `<!-- COUNTERS -->` badges, `data/*.json` |
| [`generate-snake.yml`](workflow-templates/generate-snake.yml) | Sundays 00:15 | Pushes both snake SVGs to the `output` branch |
| [`update-blog.yml`](workflow-templates/update-blog.yml) | Daily 03:31 | `<!-- BLOG-POST-LIST -->` block — only when `BLOG_RSS_URL` is set |
| [`waka-readme.yml`](workflow-templates/waka-readme.yml) | Daily 03:41 | `waka` block — only when `ENABLE_WAKATIME` is `true` |
| [`profile-checks.yml`](workflow-templates/profile-checks.yml) | Push / PR to `main` | Validates markers, assets, and generator idempotency |

Schedules only take effect once the templates are installed via `scripts/enable-automation.sh`.

Each scheduled job is guarded by its own `concurrency` group and commits only when its block actually changes, so the history stays readable.

## Optional modules

| Module | How to switch it on |
| :-- | :-- |
| Latest articles | **Settings → Secrets and variables → Actions → Variables** → create `BLOG_RSS_URL` with a public RSS/Atom URL. Then run *Refresh latest writing*. |
| Coding activity (WakaTime) | Create the `WAKATIME_API_KEY` repository **secret**, then the `ENABLE_WAKATIME` repository **variable** set to `true`. Then run *Refresh coding activity*. |
| Profile view counter | Already on. Delete the `komarev.com/ghpvc` badge from the header if visit tracking is not wanted. |
| Sponsor button | Add a `FUNDING.yml` only after a genuine [GitHub Sponsors](https://github.com/sponsors) profile exists. |

Add modules only when they have a real signal. An empty dashboard is worse than a smaller one.

## How the dynamic blocks work

### Featured repositories and counters

`update_repos.py` reads the public repositories API and writes three things.

- The **repository table** is built from a curated ordering in [`featured.json`](../.github/scripts/featured.json), then topped up with the most recently pushed repositories that have a description or topics. Scratch repositories created from a template — no description, no topics, no stars — are kept off the profile.
- The **counter badges** are regenerated with the current numbers baked in, so they render even if a badge service is having a bad day.
- **`data/*.json`** files are published in Shields' `endpoint` schema. Any other repository can then embed a live badge, for example:

  ```md
  [![Stars](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fccsalman545%2Fccsalman545%2Fmain%2Fdata%2Fstars.json)](https://github.com/ccsalman545?tab=repositories)
  ```

To change which repositories lead the table, edit `pinned` in `featured.json`. The list also accepts a runtime override through the `FEATURED_REPOS` environment variable (comma-separated names).

### Activity feed

`update_activity.py` reads the public Events API and renders the most recent meaningful events. Two filters keep it useful:

- commits to this profile repository are skipped, so the feed never becomes a loop of its own automated refreshes;
- creating a default branch (`main`, `master`, `develop`) is skipped, because that is an artefact of initialising a repository rather than news.

Events on repositories that carry a description, topics, or stars are ranked first. If that yields too few items the newest remaining events top the list up, so the panel is never empty.

## Theme-aware rendering

Every card and piece of artwork ships two variants and is swapped with `<picture>` plus a `prefers-color-scheme` media query:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img src="assets/banner-dark.svg" alt="…" width="100%">
</picture>
```

The result looks native in both GitHub themes. When you add a new card, follow the same pattern rather than picking one theme and hoping for the best.

## Custom artwork

The banner is a hand-written SVG, so there is no binary asset to maintain and it stays sharp at any scale.

- **Canvas:** 1280 × 320 px. Keep all text inside a centred 960 × 220 px safe area — GitHub scales images down hard on mobile.
- **Palette:** navy base `#0D1117`, blue accent `#58A6FF`, indigo accent `#6E40C9`, body text near `#F6F8FA`. Light variant: white base, `#0969DA` accent, `#3D4854` body text.
- **Type:** monospace throughout, matching the terminal framing.
- **Keep it calm:** one motif (PCB traces into an IC), generous empty space, no gradients behind small text, no baked-in social links.

`banner-dark.svg` and `banner-light.svg` must stay structurally identical — same coordinates, different colours — or the theme swap will visibly jump.

## Widget sources

Every remote widget is a service with a public, documented URL. If one becomes unreliable, remove that line; the prose underneath still stands on its own.

| Module | Provider | Notes |
| :-- | :-- | :-- |
| Animated roles | [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) | Two colour variants matched to each theme |
| Badges | [Shields.io](https://shields.io/) | `flat-square` in the body, `for-the-badge` for primary actions |
| Stats & languages | [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) | `theme=github_dark` / `theme=default` |
| Contribution streak | [streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) | `theme=github-dark-blue` / `theme=github-light` |
| Trophies | [github-profile-trophy](https://github.com/ryo-ma/github-profile-trophy) | `theme=onedark` / `theme=flat`, one row |
| Activity graph | [github-readme-activity-graph](https://github.com/Ashutosh00710/github-readme-activity-graph) | Explicit colours per theme |
| Contribution snake | [Platane/snk](https://github.com/Platane/snk) | Generated weekly onto the `output` branch |
| Profile views | [komarev counter](https://github.com/antonkomarev/github-profile-views-counter) | Optional; remove if unwanted |
| Latest posts | [blog-post-workflow](https://github.com/gautamkrishnar/blog-post-workflow) | Needs `BLOG_RSS_URL` |
| Coding activity | [waka-readme](https://github.com/athul/waka-readme) | Needs `WAKATIME_API_KEY` + `ENABLE_WAKATIME` |

`count_private=true` on the stats URL cannot expose private contributions unless the widget host itself is configured with a private token. No token is supplied here, so public data remains the default.

## Content maintenance checklist

Review at the start of each semester, or after any significant release.

- Replace “exploring” badges with demonstrated skills only once the work is published.
- Keep project status labels (`active`, `experimenting`, `live`) accurate.
- Update the learning roadmap honestly — its value is clarity, not high percentages.
- Add a blog feed only after at least one public post exists.
- Re-pin the featured list in `featured.json` when a new project becomes the headline.
- Delete external widgets that have stopped working; do not leave broken images.
- Keep the portfolio URL, email, and LinkedIn links current.

## Local checks

There are no dependencies to install. Before committing:

```bash
python3 -m compileall -q .github/scripts
python3 .github/scripts/check_readme.py
python3 .github/scripts/update_activity.py     # needs network
python3 .github/scripts/update_repos.py        # needs network
git diff --check && git status --short
```

The two generator scripts talk to the public GitHub API. They work unauthenticated within GitHub's public rate limit and use `GITHUB_TOKEN` automatically when one is present. Both are idempotent: running them twice in a row leaves no diff, which is exactly what the `profile-checks` workflow asserts.

To point the scripts at a different account without editing them:

```bash
PROFILE_USERNAME=someone-else python3 .github/scripts/update_repos.py
```
