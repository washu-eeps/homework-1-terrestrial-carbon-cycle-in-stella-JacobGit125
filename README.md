[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gw1UnQDR)
# HW1: Terrestrial Carbon Cycle Modeling

**EEPS 3230 Biogeochemistry — Spring 2026**

---

## Quick Links

- [Assignment Instructions](#assignment-overview) — What to do
- [Git & GitHub Guide](#git--github-guide) — How to submit (start here if new to Git!)
- [Grading](#grading) — How you'll be evaluated

---

## Assignment Overview

In this homework, you will extend a three-box terrestrial carbon cycle model to explore how feedbacks shape the global carbon cycle. You will:

1. **Calibrate** the model against synthetic atmospheric CO2 data
2. **Add a feedback mechanism** (choose one of three options)
3. **Design emission scenarios** using the built-in scenario selector

**See the full assignment handout (HW1_Terrestrial_Carbon.docx on Canvas) for detailed instructions.**

### Files in This Repository

| File | Description |
|------|-------------|
| `hw1_starter.stmx` | Your starting model — **make a copy with your name** |
| `README.md` | This file |

### What to Submit

Your completed model file: `hw1_yourname.stmx`

Commit and push this file to your repository before the deadline.

---

## Git & GitHub Guide

If you're new to Git and GitHub, don't worry! This section walks you through everything step by step.

### What is Git?

**Git** is a version control system that tracks changes to your files over time. Think of it like "track changes" in Word, but much more powerful:

- See the history of every change you've made
- Go back to earlier versions if something breaks
- Safely experiment without losing your work

**GitHub** is a website that hosts your Git repositories online, allowing you to:

- Submit assignments
- Back up your work
- Collaborate with others (in future courses)

### Step 1: Create a GitHub Account

If you don't already have one:

1. Go to [github.com](https://github.com)
2. Click **Sign up**
3. Use your `@wustl.edu` email (you get free Pro features with a student account!)
4. Choose a professional username (employers may see this someday)

### Step 2: Install Git

**Mac:**
1. Open Terminal (Applications → Utilities → Terminal)
2. Type `git --version` and press Enter
3. If not installed, you'll be prompted to install it (click Install)

**Windows:**
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer (accept all defaults)
3. Use "Git Bash" for running Git commands

### Step 3: Configure Git (One-Time Setup)

Open Terminal (Mac) or Git Bash (Windows) and run these commands, replacing with your info:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@wustl.edu"
```

### Step 4: Accept the Assignment

1. Click the GitHub Classroom assignment link (on Canvas)
2. Authorize GitHub Classroom if prompted
3. Find your name in the roster and click it
4. Click **Accept this assignment**
5. Wait for your personal repository to be created
6. Click the repository link to open it

### Step 5: Clone Your Repository

"Cloning" downloads the repository to your computer.

1. On your repository page, click the green **Code** button
2. Copy the HTTPS URL
3. Open Terminal/Git Bash and navigate to where you want to work:
   ```bash
   cd ~/Documents
   ```
4. Clone the repository:
   ```bash
   git clone https://github.com/washu-eeps/hw1-yourname.git
   ```
5. Enter the folder:
   ```bash
   cd hw1-yourname
   ```

### Step 6: Do Your Work

1. Open `hw1_starter.stmx` in Stella
2. **Save As** → `hw1_yourname.stmx` (use your actual name!)
3. Complete the assignment following the handout
4. Save your work frequently

### Step 7: Track Your Changes (Optional but Recommended)

As you work, you can save "snapshots" of your progress. This is useful if you want to go back to an earlier version.

**Check what's changed:**
```bash
git status
```

**Save a snapshot (commit):**
```bash
git add hw1_yourname.stmx
git commit -m "Completed Part 1 calibration"
```

The message in quotes describes what you changed. Make it meaningful!

**Example workflow:**
```bash
# After completing calibration
git add hw1_yourname.stmx
git commit -m "Calibrated GPP_base to 110"

# After adding feedback mechanism
git add hw1_yourname.stmx
git commit -m "Added Q10 temperature feedback"

# After finishing scenarios
git add hw1_yourname.stmx
git commit -m "Implemented 3 emission scenarios"
```

### Step 8: Submit Your Work (Push)

When you're ready to submit, "push" your commits to GitHub:

```bash
git push
```

You may be asked for your GitHub username and password. For the password, you'll need a **Personal Access Token** (GitHub no longer accepts regular passwords):

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. Give it a name like "EEPS 3230"
4. Select the `repo` scope
5. Click **Generate token**
6. **Copy the token immediately** (you won't see it again!)
7. Use this token as your password when pushing

**Tip:** On Mac, you can store credentials in Keychain. On Windows, Git Credential Manager should handle this automatically after the first push.

### Verifying Your Submission

After pushing:

1. Go to your repository on GitHub
2. Confirm your `.stmx` file is there
3. Click on **Actions** to see if the autograder ran
4. A green checkmark means all checks passed!

---

## Common Git Commands

| Command | What it does |
|---------|--------------|
| `git status` | Show what files have changed |
| `git add filename` | Stage a file for commit |
| `git commit -m "message"` | Save a snapshot with a description |
| `git push` | Upload your commits to GitHub |
| `git pull` | Download updates from GitHub |
| `git log --oneline` | See your commit history |

---

## Troubleshooting

### "Permission denied" when pushing
- Make sure you're using a Personal Access Token, not your password
- Check that you accepted the assignment and the repo is yours

### "Your branch is ahead/behind"
- Run `git pull` first, then `git push`

### Made a mistake?
- If you haven't committed yet: just fix the file and save
- If you committed but haven't pushed: ask for help (we can undo it)
- If you already pushed: make another commit with the fix (that's fine!)

### Stella backup files cluttering your repo?
- The `.gitignore` file should prevent `.stmx~` files from being tracked
- If you see them, don't add them to Git

---

## Grading

Your model will be automatically checked for required elements:

| Component | Weight |
|-----------|--------|
| Base model structure | 20% |
| Calibration | 25% |
| Feedback mechanism | 25% |
| Scenario design | 20% |
| Mass conservation | 10% |

### Required Named Elements

**All students:**
- Stocks: `Atmosphere`, `Vegetation`, `SOM`
- Flows: `GPP`, `Autotrophic_Respiration`, `Litterfall`, `Heterotrophic_Respiration`, `Emissions`
- Converters: `GPP_base`, `Scenario`, `Total_Carbon`, `RMSE`

**Plus one feedback set:**
- Option A: `Temperature`, `Q10`, `T_ref`
- Option B: `Available_N`, `Kn`
- Option C: `Deforestation_Rate` + `Deforestation` flow

---

## Getting Help

- **Office hours:** Check Canvas for times
- **Ed Discussion:** Post questions there
- **Git issues:** Come to office hours — we'll help you debug!

---

## Due Date

Class 12 — Check Canvas for the exact date and time.

---

*EEPS 3230 Biogeochemistry — Washington University in St. Louis*
