# delete-branches

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/11071/badge)](https://www.bestpractices.dev/projects/11071)
[![CI](https://github.com/tagdots/delete-branches/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots/delete-branches/actions/workflows/ci.yaml)
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/delete-branches/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/delete-branches-action)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/delete-branches/refs/heads/badges/badges/coverage.json)](https://github.com/tagdots/delete-branches/actions/workflows/cron-tasks.yaml)

<br>

**delete-branches** removes GitHub branches that have been inactive (without new commits) for longer than the idle period.

<br>

_**exemption**_
* default branch
* protected branches
* head branches in PR
* user-specified exclude branches

<br>

## ⭐ Why switch to delete-branches?
- we reduce your supply chain risks with `openssf best practices` in our SDLC and operations.
- we share evidence of `coverage run` test results in action (click _**Code Coverage**_ badge).

<br>

## 🏃 Running _delete-branches-action_ in GitHub action
Please visit our GitHub action ([delete-branches-action](https://github.com/marketplace/actions/delete-branches-action)) on the GitHub Marketplace.

<br>

## 🖥 Running _delete-branches_ locally

### Prerequisites
```
* Python (3.12+)
* GitHub fine-grained token (contents: write)
```

<br>

### Install _delete-branches_
```
~/work/hello-world $ workon hello-world
(hello-world) ~/work/hello-world $ export GH_TOKEN=github_pat_xxxxxxxxxxxxx
(hello-world) ~/work/hello-world $ pip install -U delete-branches
```

<br>

### 🔍 Example 1 - Run for help
```
(hello-world) ~/work/hello-world $ delete-branches --help
Usage: delete-branches [OPTIONS]

Options:
  --dry-run BOOLEAN        default: true
  --repo-url TEXT          e.g. https://github.com/{owner}/{repo}  [required]
  --exclude-branches TEXT  Branches excluded from deletion
  --max-idle-days TEXT     Delete branches older than max. idle days [required]
  --version                Show the version and exit.
  --help                   Show this message and exit.
```

<br>

### 🔍 Example 2 - MOCK delete branches with no commits longer than 10 days
**Summary**
1. exclude 3 branches: `'test-1'`, `'test-2'`, `'badges'`
1. remove branches without commits longer than 10 days

**Results**
1. refine excluded branches to `{'badges'}` because branches (`test-1` and `test-2`) do not exist
1. 3 branches are exempted from delete: `main`, `badges`, `pr-branch-01`
1. 6 branches are not exempted from delete and 2 out of 6 had no commits in the last 10 days
1. mock delete 2 branches
```
(hello-world) ~/work/hello-world $ delete-branches --dry-run true --max-idle-days 10 --repo-url https://github.com/tagdots/hello-world --exclude-branches "test-1, test-2, badges"

🚀 Starting to Delete GitHub Branches (dry-run: True, exclude-branches: {'test-1', 'test-2', 'badges'}, max-idle-days: 10)

Current Time (UTC): 2025-08-20 17:08:32

Refined User Exclude Branch(es): {'badges'}
Default Branch                 : main
Protected Branch               : main
Pull Request Head Branch       : pr-branch-01

Total Number of Branches                         : 9
Total Number of Branches (Exempt-From-Delete)    : 3
Total Number of Branches (Not-Exempt-From-Delete): 6

From 6 Not-Exempt-From-Delete Branch(es),  2 had no commits in the last 10 day(s)
-------------------------------------------------------------------------------------------------
(MOCK) Delete branch - last update UTC 2025-08-09 13:49:34: branch-test-001
(MOCK) Delete branch - last update UTC 2025-08-08 03:29:34: branch-test-005
```

<br>

### 🔍 Example 3 - Delete branches with no commits longer than 10 days
**Summary**
1. exclude 1 branch: `'badges'`
1. remove branches without commits longer than 10 days

**Results**
1. refine excluded branches to `{'badges'}`
1. 3 branches are exempted from delete: `main`, `badges`, `pr-branch-01`
1. 6 branches are not exempted from delete and 2 out of 6 had no commits in the last 10 days
1. delete 2 branches
```
(hello-world) ~/work/hello-world $ delete-branches --dry-run false --max-days 10 --repo-url https://github.com/tagdots/hello-world --exclude-branches "badges"

🚀 Starting to Delete GitHub Branches (dry-run: True, exclude-branches: {'badges'}, max-idle-days: 10)

Current Time (UTC): 2025-08-20 17:26:55

Refined User Exclude Branch(es): {'badges'}
Default Branch                 : main
Protected Branch               : main
Pull Request Head Branch       : pr-branch-01

Total Number of Branches                         : 9
Total Number of Branches (Exempt-From-Delete)    : 3
Total Number of Branches (Not-Exempt-From-Delete): 6

From 6 Not-Exempt-From-Delete Branch(es),  2 had no commits in the last 10 day(s)
-------------------------------------------------------------------------------------------------
✅ Delete branch - last update UTC 2025-08-09 13:49:34: branch-test-001
✅ Delete branch - last update UTC 2025-08-08 03:29:34: branch-test-005
```

<br>

## 🔧 delete-branches command line options

| Input | Description | Default | Required | Notes |
|-------|-------------|----------|----------|----------|
| `repo-url` | Repository URL | `None` | Yes | e.g. https://github.com/{owner}/{repo} |
| `dry-run` | Dry-Run | `True` | No | - |
| `max-idle-days` | Maximum number of days without commits | `None` | No | enter number of days |
| `exclude-branches` | Branches excluded from deletion | `None` | No | comma seperated branches e.g. "branch1, branch2" |

<br>

## 😕  Troubleshooting

Open an [issue][issues]

<br>

## 🙏  Contributing

For pull requests to be accepted on this project, you should follow [PEP8][pep8] when creating/updating Python codes.

See [Contributing][contributing]

<br>

## 🙌 Appreciation
If you find this project helpful, please ⭐ star it.  **Thank you**.

<br>

## 📚 References

[How to fork a repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

<br>

[contributing]: https://github.com/tagdots/delete-branches/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots/delete-branches/issues
[pep8]: https://google.github.io/styleguide/pyguide.html
