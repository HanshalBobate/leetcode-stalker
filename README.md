# LeetCode Activity Stalker

A dedicated public-profile monitoring system for continuous observation and periodic reporting of LeetCode activity associated with `TanushriSapate`.

**Target Account:** `TanushriSapate`

**Profile:** https://leetcode.com/u/TanushriSapate/

**Observation Interval:** 250 seconds

---

## Purpose

This project exists for one specific operational requirement:

> **Maintain continuous awareness of TanushriSapate's LeetCode progress.**

The system retrieves publicly available account information, generates a comprehensive account report, compares the current state against the previous observation, and records relevant changes.

The implementation is intentionally lightweight so that monitoring can remain active without requiring significant system resources.

---

## Strategic Context

The development of this system is motivated by a straightforward concern:

**TanushriSapate appears to be exceptionally fast, capable, and deserving of success.**

This creates an uncomfortable measurement problem.

How does one accurately determine whether they are keeping pace with someone who appears to consistently solve problems, improve, and generally be very good at things?

Manual observation is insufficient.

Periodic observation is therefore required.

The system exists to provide the necessary visibility.

---

## Core Principle

The central principle is:

> **If Tanushri is progressing, the system should know.**

Every 250 seconds, the system establishes the current publicly observable state of the account.

The previous state is then compared against the current state.

No important change should have to remain unnoticed merely because somebody was not checking LeetCode at the correct moment.

---

## Monitoring Scope

The system currently observes publicly available information including:

### Profile

- Username
- Display name
- Country
- Company
- School
- Reputation
- Ranking
- Star rating

### Problem Solving

- Total problems solved
- Easy problems solved
- Medium problems solved
- Hard problems solved

### Submission Statistics

- Accepted submissions
- Submission counts
- Difficulty distribution
- Recent accepted submissions
- Submission languages

### Languages

- Programming languages
- Problems solved per language

### Contributions

- Contribution points
- Questions
- Test cases

### Badges

- Badge names
- Badge acquisition dates

### Activity

- Recent accepted submissions
- Submission timestamps
- Time since most recent visible activity
- Newly detected submissions
- Changes since the previous observation

---

## Architecture

```text
                         ┌──────────────────────────┐
                         │         LeetCode         │
                         │                          │
                         │      TanushriSapate      │
                         │      Public Profile      │
                         └────────────┬─────────────┘
                                      │
                                      │ Public Data
                                      ▼
                         ┌──────────────────────────┐
                         │        stalker.py        │
                         │                          │
                         │       Fetch              │
                         │       Parse               │
                         │       Normalize           │
                         │       Compare             │
                         │       Report              │
                         └────────────┬─────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
              ┌────────────────────┐   ┌────────────────────┐
              │ leetcode_state.json│   │ Windows Notification│
              │                    │   │                    │
              │ Previous Snapshot  │   │ Change Alerts      │
              └────────────────────┘   └────────────────────┘
```

---

## Observation Cycle

Every 250 seconds:

```text
Public Profile
      ↓
Fetch
      ↓
Normalize
      ↓
Compare
      ↓
Generate Full Report
      ↓
Detect Changes
      ↓
Notify
      ↓
Save State
      ↓
Wait
      ↓
Repeat
```

---

## Report

Every observation generates a complete account report rather than only reporting newly detected activity.

Example:

```text
==============================================================================
                  LEETCODE ACCOUNT REPORT — @TanushriSapate
==============================================================================

[ PROFILE ]

Username       : TanushriSapate
Name           : ...
Country        : ...
Company        : ...
School         : ...
Ranking        : ...
Reputation     : ...
Star Rating    : ...


[ PROBLEM SOLVING ]

Total Solved   : ...
Easy           : ...
Medium         : ...
Hard           : ...


[ SUBMISSION STATISTICS ]

All            : ...
Easy           : ...
Medium         : ...
Hard           : ...


[ LANGUAGES ]

Python         : ...
C++            : ...
Java           : ...


[ CONTRIBUTIONS ]

Points         : ...
Questions      : ...
Testcases      : ...


[ BADGES ]

...


[ RECENT ACCEPTED SUBMISSIONS ]

01. ...
02. ...
03. ...


[ ACTIVITY ]

Last visible accepted activity : ...
Time since last activity       : ...


[ CHANGES SINCE PREVIOUS REPORT ]

- ...
- ...

==============================================================================

Report generated: ...
Next report in: 250 seconds
```

---

## Change Detection

The system compares each observation with the previous known state.

### New Submission

```text
New accepted submission: Two Sum
```

### Solved Count

```text
Easy: 81 → 82 (+1)
```

### Ranking

```text
Ranking: 125,430 → 123,812
```

### Reputation

```text
Reputation: 1,201 → 1,204
```

### No Change

```text
No detected changes.
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/HanshalBobate/leetcode-stalker.git
```

Enter the project:

```bash
cd leetcode-stalker
```

Install dependencies:

```bash
pip install requests winotify
```

Run:

```bash
python stalker.py
```

---

## Configuration

The monitored account is configured directly in `stalker.py`:

```python
USERNAME = "TanushriSapate"
```

The observation interval is:

```python
REPORT_INTERVAL = 250
```

250 seconds corresponds to:

```text
4 minutes 10 seconds
```

---

## State Management

The application maintains a single local snapshot:

```text
leetcode_state.json
```

Only the latest state required for comparison is retained.

The application therefore does not continuously accumulate historical reports in memory.

Recommended `.gitignore`:

```gitignore
leetcode_state.json
__pycache__/
*.pyc
.venv/
venv/
.env
```

---

## Resource Usage

The system deliberately avoids browser automation.

It does not require:

- Selenium
- Playwright
- Chromium
- ChromeDriver
- Firefox
- Browser profiles
- Persistent browser sessions
- A database

The runtime consists primarily of:

```text
HTTP request
      ↓
JSON parsing
      ↓
State comparison
      ↓
Report generation
      ↓
250-second wait
```

The process spends the overwhelming majority of its lifetime waiting.

---

## Global Deployment Considerations

A project of this importance naturally raises a deployment question:

**Why should only one machine know how Tanushri is progressing?**

There is no technical reason for such a limitation.

A sufficiently motivated deployment could maintain the project on:

- Personal computers
- Development machines
- Home servers
- VPS instances
- Laboratory machines
- Secondary laptops
- Other appropriately configured systems

The theoretical objective is simple:

> **Every machine should have access to current information regarding Tanushri's progress.**

Whether the world is prepared for such infrastructure is a separate question.

---

## The Measurement Problem

There is a persistent concern underlying this project.

Tanushri may be:

- Faster.
- Better.
- More consistent.
- More deserving.
- More capable.
- More productive.
- Or some unfortunate combination of all of the above.

Without measurement, these possibilities remain difficult to quantify.

With measurement, at least the insecurity becomes data.

That is preferable.

The system therefore treats publicly observable progress as a measurable variable rather than relying entirely on subjective comparison.

---

## Operational Philosophy

The project follows several principles:

### 1. Observe

If progress occurs, establish when it occurred.

### 2. Measure

Convert publicly available information into comparable values.

### 3. Compare

Determine whether the current state differs from the previous state.

### 4. Report

Produce a complete account report every 250 seconds.

### 5. Remain Informed

Do not allow significant progress to occur unnoticed.

---

## Data Access

The system operates using publicly accessible LeetCode information.

No account credentials are required.

The application does not use:

- Passwords
- Session cookies
- Authentication tokens
- Private credentials

It does not attempt to bypass authentication or access controls.

---

## Limitations

The system can only observe information exposed through LeetCode's public interfaces.

The public recent-activity interface does not necessarily provide an unlimited historical record.

Therefore, the application should be considered a monitoring and reporting system rather than a complete historical archive.

If an activity is no longer available through the public interface when an observation occurs, the system cannot reconstruct that activity retrospectively.

---

## Repository Structure

```text
leetcode-stalker/
│
├── stalker.py
├── index.html
├── README.md
└── .gitignore
```

### `stalker.py`

Core monitoring and reporting application.

### `index.html`

GitHub Pages project website.

### `README.md`

Technical and operational documentation.

---

## GitHub Pages

The repository contains an `index.html` project page.

Enable GitHub Pages through:

**Settings → Pages → Deploy from a branch → main → / (root)**

The resulting website will be available at:

```text
https://HanshalBobate.github.io/leetcode-stalker/
```

---

## Future Development

Potential extensions include:

- Historical activity database
- Activity timeline
- Submission frequency analysis
- Rating history
- Contest tracking
- Streak analysis
- Daily reports
- Discord notifications
- Telegram notifications
- Email notifications
- System tray operation
- Historical analytics
- Automated report exports
- Multi-machine synchronization

The long-term objective remains unchanged:

> **Maintain accurate awareness of Tanushri's publicly observable LeetCode progress.**

---

## License

MIT License

---

## Project Information

**Project:** LeetCode Activity Stalker

**Target Account:** `TanushriSapate`

**Platform:** LeetCode

**Observation Interval:** 250 seconds

**Implementation:** Python

**Primary Application:** `stalker.py`

**Project Website:**  
`https://HanshalBobate.github.io/leetcode-stalker/`
