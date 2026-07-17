# Profile README operations guide

This repository is a **GitHub profile repository** because its name exactly matches the account name: `ccsalman545`. GitHub renders the root [`README.md`](../README.md) above the repositories list at [github.com/ccsalman545](https://github.com/ccsalman545).

The profile is designed to work as a clean static README immediately, with a few optional dynamic modules that make it feel alive over time.

## Repository layout

```text
ccsalman545/
├── README.md                              # Public profile shown on GitHub
├── .github/
│   └── scripts/
│       └── update_activity.py             # Standard-library activity renderer
└── docs/
    ├── PROFILE_SETUP.md                   # This operating guide
    └── workflow-templates/                # Copy into .github/workflows manually
        ├── generate-snake.yml             # Weekly contribution snake → output branch
        ├── update-activity.yml            # Daily public activity refresh
        └── update-blog.yml                # RSS/Atom latest-writing refresh
```

## First-time activation

1. **Merge the profile change into `main`.** GitHub only renders the profile README from the repository's default branch.
2. The GitHub App used for this PR cannot write live workflow files. As the repository owner, add them through GitHub’s web editor after merging:
   - open **Code → Add file → Create new file**;
   - create `.github/workflows/generate-snake.yml`, then paste the matching [`generate-snake.yml`](workflow-templates/generate-snake.yml) template;
   - repeat for [`update-activity.yml`](workflow-templates/update-activity.yml) and [`update-blog.yml`](workflow-templates/update-blog.yml).
3. In the repository, open **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**. Save the setting. The activity and blog jobs need permission to commit their README updates.
4. Open **Actions**, select **Generate contribution snake**, then choose **Run workflow** once. This creates or refreshes the `output` branch that hosts the snake SVGs. The README’s snake module will work as soon as this job succeeds.
5. To enable latest writing, open **Settings → Secrets and variables → Actions → Variables**, create `BLOG_RSS_URL`, and set it to a public RSS or Atom feed URL. Then run **Refresh latest writing** once. The workflow intentionally does nothing until this variable is present.
6. Optionally run **Refresh profile activity** once to seed the activity panel before the next scheduled run.
7. Open the profile in an incognito/private browser on a desktop and phone. This verifies the public view rather than a cached logged-in view.

> Do not put email credentials, personal tokens, or API keys in `README.md`, workflow files, or repository variables. The templates use GitHub’s scoped `GITHUB_TOKEN` only.

## Automation schedule

| Workflow template | Schedule (UTC) | What it changes | Required setup |
| :-- | :-- | :-- | :-- |
| [`generate-snake.yml`](workflow-templates/generate-snake.yml) | Sundays, 00:15 | Publishes two SVG snake files to `output` | Copy it to `.github/workflows`, then run once |
| [`update-activity.yml`](workflow-templates/update-activity.yml) | Daily, 02:17 | Replaces the `ACTIVITY` marker block in the README | Copy it to `.github/workflows`; Actions write permission |
| [`update-blog.yml`](workflow-templates/update-blog.yml) | Daily, 03:31 | Replaces the `BLOG-POST-LIST` marker block | Copy it to `.github/workflows`; write permission + `BLOG_RSS_URL` |

The activity script skips commits made to this profile repository so the feed does not become a loop of its own automated refreshes. It uses the public GitHub Events API and Python’s standard library only.

## Widget and badge sources

Every visual module is linked from the profile README and is intentionally sourced from a service with a public, documented URL.

| Module | Provider / source | Configuration in this profile |
| :-- | :-- | :-- |
| Hero banner | [Capsule Render](https://github.com/kyechan99/capsule-render) | Header text, blue/indigo gradient, descriptive subtitle |
| Animated roles | [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) | JetBrains Mono, 2.8-second rotation, six role messages |
| Technology / CTA badges | [Shields.io](https://shields.io/) | `flat-square` for the compact dashboard feel; `for-the-badge` for primary actions |
| GitHub stats and language summary | [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats) | Public data, GitHub-dark cards, icons and compact language list |
| Contribution streak | [streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) | GitHub-dark-blue theme |
| Activity graph | [github-readme-activity-graph](https://github.com/Ashutosh00710/github-readme-activity-graph) | Dark high-contrast line graph |
| Trophies | [github-profile-trophy](https://github.com/ryo-ma/github-profile-trophy) | One compact row with no frame |
| Profile view counter | [komarev profile counter](https://github.com/antonkomarev/github-profile-views-counter) | Optional public visit count |
| Contribution snake | [Platane/snk](https://github.com/Platane/snk) | Generated weekly after copying the template into `.github/workflows`, then published to `output` |
| Latest posts | [blog-post-workflow](https://github.com/gautamkrishnar/blog-post-workflow) | Uses the RSS/Atom URL in `BLOG_RSS_URL` after the template is activated |

### Theme and reliability notes

- The dashboard cards intentionally use a dark card surface. That creates reliable contrast when GitHub itself is in either Light or Dark mode.
- External badge/widget services can occasionally be rate-limited or unavailable. The important content remains plain Markdown text and links, so the profile is still useful without imagery.
- `count_private=true` on the stats URL cannot expose private contributions without the widget host being configured with a private token; no private token is supplied here. Public data remains the intended default.
- The profile-views badge is optional. Remove its line from the README if visit tracking is not wanted.

## Custom banner recommendations

The current banner is generated by Capsule Render, so there is no asset to maintain. For a distinctive custom banner later:

1. Design at **1280 × 320 px** (or 1600 × 400 px) with all text inside a centered **960 × 220 px safe area**. GitHub scales images down aggressively on mobile.
2. Use a deep navy base (`#0D1117`), one blue accent (`#58A6FF`), and one indigo accent (`#6E40C9`). Keep body text near `#F6F8FA` for contrast.
3. Include only the name, a short role, and one visual motif—such as PCB traces fading into a terminal grid. Do not bake small social links or dense technology lists into the image.
4. Export an optimized SVG or PNG below 500 KB and place it at `assets/profile-banner.png` if a local asset is preferred.
5. Replace the first Capsule Render image in `README.md` with:

   ```md
   [![Muhammed Salman CC — Embedded systems, Linux & intelligent hardware](assets/profile-banner.png)](https://muhammed-salman-cc.is-a.dev)
   ```

6. Check both GitHub themes, a narrow mobile viewport, and the profile page’s social preview before publishing.

**Suggested art direction:** a calm dark terminal canvas; subtle cobalt signal traces; a single FPGA/IC outline; no gradients behind small text; and generous empty space. It should feel like a precise engineering instrument, not a poster.

## Optional dynamic modules

Add only modules that have a genuine signal; an empty dashboard is worse than a smaller one.

| Module | Safe approach | What is needed |
| :-- | :-- | :-- |
| Latest articles | The RSS/Atom workflow template | Copy it into `.github/workflows` and set a public `BLOG_RSS_URL` repository variable |
| Recent commits/activity | The activity workflow template | Copy it into `.github/workflows`; then enable Actions write permission |
| WakaTime coding activity | [athul/waka-readme](https://github.com/athul/waka-readme) | A `WAKATIME_API_KEY` repository secret; never expose it in README |
| Holopin badges | [Holopin embed guide](https://www.holopin.io/) | A real Holopin board URL after badges are earned |
| Spotify now playing | [novatorem](https://github.com/novatorem/novatorem) | A public Spotify identity plus Spotify API credentials stored as secrets |
| Random developer quote | [quote-readme](https://github.com/PiyushSuthar/github-readme-quotes) | Optional image link; prefer a stable personal quote if consistency matters |
| Weather | A self-hosted or privacy-reviewed provider | Use only a city-level location; do not expose precise location data |
| Sponsor section | [GitHub Sponsors](https://github.com/sponsors) | A genuine sponsor profile before adding a funding badge |

## Content maintenance checklist

Review the README at the start of each semester or after any significant project release:

- Replace “exploring” badges with demonstrated skills only when the work is published.
- Keep project status labels (`active`, `experimenting`, `live`) accurate.
- Update the learning roadmap honestly—its value is clarity, not high percentages.
- Add a blog feed only after at least one public post exists.
- Remove external widgets that have become unreliable or no longer support the profile.
- Keep contact links and the portfolio URL current.
- Add a pinned repository only after its README, license, setup steps, and screenshots or diagrams are ready.

## Local checks

There is no build dependency for the profile README. Before committing, run:

```bash
python3 .github/scripts/update_activity.py
python3 -m py_compile .github/scripts/update_activity.py
git diff --check
git status --short
```

The first command needs network access to GitHub’s public Events API. In Actions it receives the short-lived `GITHUB_TOKEN` automatically. Locally it also works unauthenticated for normal use, subject to GitHub’s public rate limits.
