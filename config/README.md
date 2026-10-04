# Contribution graph config

`contrib-allowlist.json` is a JSON array of **owner logins** (people or orgs you control):

```json
["gauzpan"]
```

## What gets counted

The match is on the repository **owner**, not on individual repositories.

- Every repo owned by a listed login is counted, automatically, including new repos you create later. You never list repos one by one.
- Commits, pull requests, issues and PR reviews all count.
- Anything owned by someone else (your employer, open-source projects) is **not** counted, which is the point.
- Owners containing `nutanix` are always dropped, even if you add them here by mistake. The run log reports how many contributions were dropped, never which repos.

## Adding more

- **Personal orgs:** add the org login, for example `["gauzpan", "my-side-org"]`.
- **Private personal repos:** create a fine-grained token scoped to your own account only, save it as the repo secret `CONTRIB_TOKEN`, and private activity under the listed owners is counted too. Without it, only public repos are visible to the workflow.
- Matching is case-insensitive and exact. `gauzpan` does not match `gauzpan-labs`.

## GitHub's own limits

- Commits count only when made on a repo's default branch (or `gh-pages`), the same rule as GitHub's own graph.
- GitHub returns at most 100 repos per request. The script splits the date range to get past that, and prints `truncated_windows` in the log if a single day ever overflows.
- Days use UTC shifted by `CONTRIB_UTC_OFFSET_MINUTES` (set to 330, IST, in the workflow).
