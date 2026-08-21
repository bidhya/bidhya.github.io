---
tags:
  - Claude Code
  - AI Agents
  - HPC
  - Developer Tooling
  - Reproducibility
---

# Claude Code Across a Laptop and an HPC Cluster

*What travels, what doesn't, and how to build permissions you can actually trust.*

*Verified against Claude Code v2.1.222, August 2026. Permission and sandbox behaviour changes fast; check the version before trusting the specifics.*

Our group's compute loop looks like this. Write and test code on a laptop, where iteration is cheap. Push to the cluster through GitHub or `rsync`. Run there, because that is where the cores, the memory, and the multi-terabyte project storage live. Then stay on the cluster to diagnose: read the logs, inspect the outputs, work out why run 14 disagrees with run 13.

Claude Code is useful at both ends of that loop, and the diagnosis end is where it earns the most. But when you install it on the cluster it arrives knowing nothing. No project context, no permission guardrails, none of the accumulated understanding from months of sessions on the laptop.

This is not a bug, and the fix is not to copy your home directory across. The fix is to understand that Claude Code keeps state in **three separate systems**, each with a different answer to the question *does this cross machine boundaries?*

Get it wrong and you either work blind on the cluster, or, worse, run an agent there with no guardrails on hardware you share with everyone else at your institution.

---

## The three systems

| System | What it holds | Does it travel? |
|---|---|---|
| **Settings** | permissions, model preferences | **Only if you track it in git** |
| **Context** (`CLAUDE.md`) | how your project works | **Only if you track it in git** |
| **Auto memory** | facts Claude accumulates itself | **Never, by default** |

The pattern is already visible. Nothing travels because it is Claude Code state. Things travel because they are **files in your repository**, and your repository is the thing you already `git push` between machines. Everything else lives in `$HOME`, and your `$HOME` on the cluster is a different directory on a different filesystem owned by a different account.

That single sentence resolves most of the confusion. The rest of this is the consequences.

---

## Part 1: Permissions

### Evaluation order is the whole model

Claude Code permissions have three lists, and one rule governs them:

> Rules are evaluated in order: **deny, then ask, then allow.** The first match determines the outcome, and rule specificity does not change the order.

That ordering is worth internalising because it is not what most people assume. A broad `deny` like `Bash(aws *)` blocks every matching call *including* one that also matches a narrow allow like `Bash(aws s3 ls)`. Deny rules cannot carry allowlist exceptions. The same holds between ask and allow: a matching ask rule prompts even when a more specific allow rule also matches.

There is also a distinction in how deny rules are written. A bare tool name like `Bash` removes the tool from Claude's context entirely, so it never sees the tool exists. A scoped rule like `Bash(rm *)` leaves the tool available and blocks matching calls when Claude attempts them. The second is usually what you want; the first is for tools you have no use for at all.

### `allow` is the list that grants privilege

Every entry in `allow` is a standing grant to act without checking with you. That is the list to be stingy with, and the reason is structural: `deny` is a backstop for the irreversible, while `allow` is the thing that actually widens what runs unattended.

The practical build order follows from that. Start with `allow` nearly empty and let things prompt. When you approve a command with "Yes, and don't ask again", Claude Code writes the rule to `.claude/settings.local.json` at the **git repository root**, so it applies to future sessions anywhere in that repo. After a week of real work your local file *is* your evidence log: it contains exactly the commands you approved repeatedly and safely. Promote the durable ones to the shared file. You are now building policy from evidence rather than prediction, and the result will be a third the size of the list you would have written up front.

From there it is tempting to conclude that `ask` entries are redundant, since anything unmatched prompts anyway. Two things make that wrong, and both matter more on a cluster than on a laptop.

### The built-in read-only set never prompts

Claude Code recognises a built-in set of Bash commands as read-only and **runs them without a permission prompt in every mode**. The set includes `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, and read-only forms of `git`.

It is not configurable. Quoting the documentation directly:

> The set is not configurable; to require a prompt for one of these commands, add an `ask` or `deny` rule for it.

So for these commands the logic inverts. Leaving `find` out of your allow list achieves nothing, because it was never going to prompt. If you want a prompt, an **explicit `ask` rule is the only mechanism.** This is the single most consequential thing to get right on shared storage, and I come back to it in Part 4.

Two related behaviours are worth knowing. Exec wrappers such as `watch`, `setsid`, `ionice`, and `flock` cannot be auto-approved by a prefix rule like `Bash(watch *)`, so they always prompt in Manual mode. The same applies to `find` with `-exec` or `-delete`: a `Bash(find *)` rule does not cover those forms.

### Your session probably does not start in Manual mode

On Pro, Max, and Team plans the built-in starting mode is **auto mode**, where a classifier model reviews actions instead of you. There are six modes now:

| Mode | Behaviour |
|---|---|
| `default` (Manual) | prompts on first use of each tool |
| `acceptEdits` | auto-accepts file edits and common filesystem commands |
| `plan` | reads and explores, does not edit source |
| `auto` | classifier approves tool calls with background safety checks |
| `dontAsk` | auto-**denies** unless pre-approved by an allow rule |
| `bypassPermissions` | skips prompts entirely |

`dontAsk` is the interesting one for the argument above: there, `allow` is load-bearing in the opposite direction, because anything not allowed is refused rather than queued for you. So "keep `allow` short" is good default advice, not a universal law. Know which mode you are actually in.

Auto mode is worth understanding in a little more detail, because it enforces its own version of the short-allow-list discipline. Its decision order is: rules resolve first, then read-only actions and in-workspace edits are auto-approved, then everything else goes to the classifier. Two consequences follow. **The built-in read-only commands skip the classifier too**, so auto mode does not help with the `find` and `grep` problem below. And on entering auto mode, broad allow rules that grant arbitrary code execution are **dropped**: blanket `Bash(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over, and dropped rules are restored when you leave. If a permission you thought you had stops working, check your mode before you edit your config.

A small set of actions is never auto-approved in **any** mode, `bypassPermissions` included: anything matched by an explicit `ask` rule, tools requiring user interaction, and `rm`/`rmdir` targeting a critical path. That first item is the lever. An `ask` rule is the one thing that survives every mode.

### Three files, two different merge rules

| File | Scope | Travels? |
|---|---|---|
| `~/.claude/settings.json` | every project, this machine | ❌ lives in `$HOME` |
| `.claude/settings.json` | this project, shared | ✅ if tracked |
| `.claude/settings.local.json` | this project, this machine | ❌ conventionally gitignored |

Ordinary settings (model, effort level) follow **narrowest-wins** precedence: managed, then command line arguments, then local, then project, then user.

**Permission rules do not.** They **merge across scopes**, and within that merged set the deny-then-ask-then-allow order applies globally:

> If a tool is denied at any level, no other level can allow it. [...] if user settings allow a permission and project settings deny it, the deny rule blocks it. The reverse is also true: a user-level deny blocks a project-level allow.

That symmetry has a design consequence most people discover backwards:

> **Denies compose upward. Put the loosest acceptable rule in the shared file, and let each machine tighten locally.**

Write a strict rule into the shared file and you are stuck with it everywhere, because no local file can loosen it. Write the permissive version and each machine hardens as needed. If you want a command merely prompting on the laptop but hard-denied on the cluster, the *shared* file must carry the prompt and the *cluster's local file* must carry the deny. Getting this backwards is the most common structural mistake I see.

### Keep the local file to genuine deltas

Two settings files cannot usefully disagree. One silently wins and the other misleads whoever reads it next.

I audited a config where the local file had 42 permission rules. Twenty-nine were byte-identical to the shared file. Six were subsumed by broader shared rules. Two were actively wrong: the local file listed `rm` under `ask` while the shared file **denied** it. Deny wins, so those lines did nothing, but anyone reading the local file would reasonably conclude `rm` was available with approval.

Slimming it to seven real deltas made both files honest. **If it matches the baseline, it does not belong in the local file.**

### There is a real sandbox now, and you probably cannot use it on the cluster

A lot of writing on this topic, including advice I gave earlier, tells you to stop trying to build a sandbox out of permission rules because no sandbox exists. That is now out of date. Claude Code ships an OS-enforced Bash sandbox that isolates filesystem and network access, on macOS, Linux, and WSL2. Run `/sandbox` to see its state.

On a research cluster, though, look closely before you count on it. On Linux it depends on two packages:

* `bubblewrap`, which enforces filesystem isolation through unprivileged user namespaces
* `socat`, which relays network traffic through the sandbox proxy

The documented install path is `sudo apt-get install bubblewrap socat`, and you do not have `sudo` on a shared cluster. Worse, many HPC sites disable unprivileged user namespaces at the kernel level as a matter of policy, which is exactly the primitive bubblewrap needs. There is an `enableWeakerNestedSandbox` escape hatch for hosts in that state, and the documentation is blunt that it "considerably weakens security and should only be used when additional isolation is otherwise enforced."

Check with `/sandbox` on your login node. If the panel shows only a Dependencies tab, you are not getting a sandbox, and note the default failure mode:

> By default, if the sandbox cannot start because dependencies are missing or the platform is unsupported, Claude Code shows a warning and runs commands without sandboxing.

It degrades quietly. Set `sandbox.failIfUnavailable` to `true` if you would rather it stop than proceed unsandboxed.

So on the laptop, use the sandbox. On the cluster, assume you have permission rules and nothing else, which makes the rest of this section load-bearing rather than academic.

### Permission rules are a guardrail, not a sandbox

Rules match **command text**. None of these trip a `Bash(rm *)` deny:

```
python -c "import shutil; shutil.rmtree(path)"
FOO="rm -rf /path"; $FOO
bash cleanup.sh
ssh host 'rm -rf /path'
```

You cannot close the hole by restricting `python`, because on any real project running Python *is* the work.

The matcher is smarter than it first appears in one respect worth crediting. It understands shell operators, so `Bash(safe-cmd *)` does not authorise `safe-cmd && other-cmd`. The recognised separators are `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines, and a rule must match each subcommand independently. But the four lines above are still wide open, so design the layering deliberately:

1. **`deny`** for the few actions that are irreversible or hit shared resources
2. **Model judgment** for the long tail
3. **You**, as approver, for anything consequential

Layer 2 is genuinely strong but probabilistic, which is precisely why layers 1 and 3 exist. Chasing every permutation through text matching has sharply diminishing returns and produces a config nobody can read.

One thing worth doing: **state the intent in your context file too.** Something like *"do not reach for a Python equivalent to get the same effect."* The mechanism cannot enforce that, and the documentation says so plainly ("Permission rules are enforced by Claude Code, not by the model. Instructions in your prompt or `CLAUDE.md` shape what Claude tries to do, but they don't change what Claude Code allows"). But the instruction is read every session, and layer 2 responds to it. In auto mode this cuts further than you might expect: the classifier is given your `CLAUDE.md` content along with the tool call, so a clearly stated constraint shapes the automated reviewer as well as the acting model. Tool results are stripped from what the classifier sees, so a hostile file cannot talk back to it.

For anything that must be enforced rather than encouraged, use a `PreToolUse` hook. A hook that exits with code 2 stops the call before permission rules are even evaluated, so it overrides allow rules. Hooks cannot loosen anything: deny and ask rules still apply regardless of what a hook returns.

### `.claude/` is already protected

A common recommendation is to put `.claude/**` in `ask` so the agent cannot widen its own `allow` list, which it will otherwise do from time to time while helpfully trying to reduce friction for you. If the file is tracked, that change then rides along in a commit unnoticed. The concern is real, but the mechanism is now built in. `.claude/` and `.git/` are **protected paths**, and writes to them are never auto-approved except in `bypassPermissions`:

| Mode | Protected-path writes |
|---|---|
| `default`, `acceptEdits` | prompted |
| `auto` | routed to the classifier |
| `dontAsk` | denied |
| `bypassPermissions` | allowed |

Note also that allow rules cannot pre-approve these writes at all. The safety check runs *before* allow rules are evaluated, so an `Edit(.claude/**)` entry in your settings does not change the table above.

An explicit `ask` rule on `.claude/**` is still defensible as belt-and-braces, but do not expect it to buy you a human prompt in auto mode: protected-path writes route to the classifier there *even when a rule matches*. Content-matching ask rules on Bash commands, such as `Bash(git push *)`, do fall back to a real prompt in auto mode. Path-scoped ask rules on protected paths are the case where the built-in behaviour wins. If you want a person in that loop specifically, change the mode rather than the rules.

### Test that your guardrails actually fire

A guardrail nobody has tested is a guess. Run one denied command and confirm you get a **permission error**, not "command not found":

```
Permission to use Bash with command sbatch --version has been denied.
```

Then note what that proves, which is less than it looks. Deny is evaluated first in every mode, so a passing deny test tells you nothing about `allow`, `ask`, or which mode you are in. Test an `ask` rule too, since that is the layer whose behaviour actually varies.

Watch the matching semantics while you are there. A trailing `*` **with a space before it** enforces a word boundary: the prefix must be followed by a space **or end-of-string**. So `Bash(ls *)` matches both `ls` and `ls -la`, but not `lsof`. Without the space, `Bash(ls*)` matches `lsof` too. The `:*` suffix is equivalent to a trailing ` *`, and is only recognised at the end of a pattern.

---

## Part 2: Context

`CLAUDE.md` is loaded into every session. Claude Code reads `CLAUDE.md`, not `AGENTS.md`, so if your repo already uses `AGENTS.md` for other agents, the documented bridge is a one-line import:

```markdown
@AGENTS.md

## Claude Code
Use plan mode for changes under `src/pipeline/`.
```

A symlink works too, if you have nothing Claude-specific to add. Note that imports are expanded at launch and count against your context, and that an import resolving *outside* the working directory triggers a one-time approval dialog the first time Claude Code sees it.

**Track these files.** This is the mechanism by which project understanding reaches the cluster. It rides the same `git push` your code does, which is the entire reason the workflow holds together. If your context files are gitignored, a very common default since they feel like personal scratch, then every session on the cluster starts blind, and you will not notice, because the agent will confidently do something reasonable and wrong.

### They concatenate; they do not override

It is natural to assume the nearest `CLAUDE.md` wins, the way settings do. It does not:

> All discovered files are concatenated into context rather than overriding each other.

Claude Code walks up the directory tree from your working directory and loads every `CLAUDE.md` and `CLAUDE.local.md` it finds, ordered root-first so the file closest to where you launched is read last. Files in *sub*directories load on demand, when Claude reads a file in that directory.

The practical consequence: a subfolder file cannot retract something the root file said. It can only add. If you need genuinely different behaviour in a subtree, phrase the root rule so the override is legal, or use a path-scoped rule instead.

### Use `.claude/rules/` for anything conditional

Rules are markdown files under `.claude/rules/`, and with a `paths` frontmatter field they load only when Claude touches matching files:

```markdown
---
paths:
  - "src/pipeline/**/*.py"
---
Chunk with Dask before any operation that would materialise a full array.
```

This is the right home for instructions that only matter in part of the tree, and it keeps your root file under the ~200 line target where adherence is best. Rules without a `paths` field load unconditionally, at the same priority as `.claude/CLAUDE.md`.

One caveat if you rely on this: after `/compact`, the project-root `CLAUDE.md` is re-read from disk and re-injected, but nested files and path-scoped rules are **not**. They reload the next time Claude reads a matching file. An instruction that seems to evaporate mid-session is usually this.

### If the repo is public, sanitize before committing

Tracked means published. Before committing a context file, confirm it carries no hostname, username, account, or SSH detail. Git history is permanent, and deleting the line later does not unpublish it.

The distinction worth internalising: **paths already present in tracked code are not a new disclosure. The authentication chain is.** A directory name is usually fine. `user@host.institution.edu` is not.

### Write pointers, not snapshots

This is the failure mode I see most often in agent context files, and the one that quietly poisons everything downstream.

| Instead of | Write |
|---|---|
| "both branches sit at `a1b2c3d`" | "check `git log --oneline main dev`" |
| "active work: none" | *(omit, it is derivable)* |
| "verified as of {date}" | what was checked, and what it does **not** cover |

Anything derivable from git, a changelog, or the code should be pointed at, not copied. A copy is a second source of truth that starts decaying immediately. In an agent-assisted workflow "currently at commit X" can be false within the hour, and then your agent is reasoning from a confident, wrong premise.

Reserve narration for things with no live source: domain knowledge, hard constraints, incident write-ups, the reasoning behind a decision.

---

## Part 3: Auto memory

Auto memory is per-project markdown under `~/.claude/projects/<project>/memory/`, with a `MEMORY.md` index loaded at the start of every session. The `<project>` path derives from the git repository, so all worktrees and subdirectories of one repo share a memory directory.

Only the **first 200 lines or 25KB** of `MEMORY.md` load. Anything past that is silently dropped, which is why the index should stay an index, with detail pushed into topic files that Claude reads on demand.

On travel, the documentation is unambiguous:

> Auto memory is machine-local. [...] Files are not shared across machines or cloud environments.

There is one asterisk on "never". An `autoMemoryDirectory` setting can relocate the directory, and pointing it somewhere synced would technically make memory travel. I would not: you would be syncing a store that is deliberately unsanitized, and the reason it holds useful things is precisely that it is private. But "never" is a default, not a law.

Its properties are the **exact inverse** of a tracked context file, and that inversion is the decision rule:

| | Tracked `CLAUDE.md` | Auto memory |
|---|---|---|
| Reaches the cluster | ✅ | ❌ |
| Public | ✅ | ❌ |
| Visible to colleagues | ✅ | ❌ |
| Survives a fresh clone | ✅ | ❌ |
| Needs sanitizing | ✅ | ❌ |

| The fact is… | Put it in |
|---|---|
| Needed by a session on the cluster | **context file**, the only thing that travels |
| Durable and safe to publish | **context file** |
| About a person, or not for the internet | **memory** |
| A quirk of one machine | **memory** |
| A working preference not worth publishing | **memory** |
| True only this week | **neither**, use a scratch folder |

### Never write the same fact in both places

Your context file is auto-loaded every session. A memory restating it therefore adds **zero recall value and pure drift risk**.

This creeps up on you. In one project I reviewed, six of fourteen memories had quietly become duplicates, not because anyone wrote them carelessly, but because the tracked guide had matured past them. One duplicate asserted a commit hash that had already moved on, so the memory was simply wrong, and it loaded into every session as background truth.

The model to copy: **keep the rule public and the reason private.** "No AI attribution in commit messages" belongs in the tracked guide. *Why*, a specific colleague's preference about AI-generated work, belongs only in memory. Publishing the reason would be indiscreet. Losing it would make the rule look arbitrary and invite someone to "fix" it.

---

## Part 4: The cluster end of the loop

Everything above applies to any two machines. This part is specific to the second one being shared.

### First, find out where the agent can run at all

The agent needs outbound network access to reach the API, and on many clusters compute nodes have no route to the internet. That is the common case. Where it holds, **the login node is your only option**, and login-node discipline is the whole story.

Some sites do permit outbound traffic from compute nodes. Check yours; it is a five-minute test and it decides the shape of your workflow. If you are on one of them, you get a second mode worth using:

| Where you start the agent | Good for |
|---|---|
| **Login node** | reading files, checking git, queue status, log triage |
| **Inside an interactive allocation** | test runs, and anything touching real data at scale |

Allocate first, then start the agent inside the allocation. Its commands now run on hardware reserved for you rather than the node everyone shares, and you stop having to ration what the agent may touch.

> ⚠️ **The session dies when the allocation ends.** A four-hour allocation caps your conversation at four hours, mid-thought or not. Size the wall time for the conversation, not just the job.

**If your compute nodes are firewalled, you are not stuck**, and this is where most readers will land. The agent stays on the login node doing what login nodes are for: reading logs, inspecting outputs, reasoning about what went wrong. That is the diagnosis half of our loop, and it is the half where the agent is most valuable anyway. The heavy work still happens on compute nodes; the agent hands you the command to launch it.

### The `find` and `grep` problem, correctly

Treat the login node as shared, because it is. Every command the agent runs lands there alongside everyone else's work.

| Fine on a login node | Allocate first |
|---|---|
| reading files, `git log` | recursive `find` or `grep` over project storage |
| queue status | anything touching real data at scale |
| tailing a log | comparisons, conversions, analysis runs |

Moving to a compute node removes the **CPU** contention, not the **I/O**. A recursive scan of shared project storage loads that filesystem for everyone regardless of which node issued it.

This is where the read-only set from Part 1 bites hardest. The intuitive move is to leave `find` and `grep` out of your allow list so they prompt and you can see the scope before they run. **That does nothing.** Both are built-in read-only commands: they run without prompting in every mode, they skip the classifier in auto mode, and your allow list is not consulted either way.

To actually get a prompt, write explicit `ask` rules in the cluster's local settings file:

```json
{
  "permissions": {
    "ask": [
      "Bash(find *)",
      "Bash(grep *)",
      "Bash(du *)"
    ]
  }
}
```

Local file, not shared, because on the laptop there is no shared filesystem and these should stay frictionless. Same repository, different posture per machine. That is exactly what the shared/local split is for.

Note that `find` with `-exec` or `-delete` is not covered by a `Bash(find *)` rule in the first place, and always prompts in Manual mode. That is a helpful default rather than something to work around.

### Lock out the modes you do not want on shared hardware

Both permissive modes can be disabled from any settings scope, including your own:

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "disableAutoMode": "disable"
  }
}
```

`disableBypassPermissionsMode` is the easy call: put it in the cluster's local settings. It is normally an admin control, but the documentation notes a user can set it in their own settings to lock themselves out of bypass mode, which is exactly the right instinct on hardware you share.

`disableAutoMode` is a genuine tradeoff, not an obvious win, and I would not reach for it first. Auto mode drops your broad allow rules on entry and routes protected-path writes to a reviewer, so it is not simply "less safe" than Manual; what you give up is a human in the loop, and what you gain is not being prompted forty times an hour. Since content-matching `ask` rules still produce real prompts in auto mode, the `ask` rules above already buy you the specific protection that matters on shared storage. Disable auto mode when you want to watch everything the agent does on the cluster, not as a default.

If your centre administers Claude Code centrally, both belong in managed settings at `/etc/claude-code/`, alongside a managed `CLAUDE.md` if the site wants standing instructions that no project file can exclude.

### The copy/paste handoff

For privileged operations, job submission, deletion, writes to shared storage, the pattern that works is:

1. **Deny the command** so it cannot execute.
2. **Write a line in your context file** telling the agent to propose these as single-line commands for you to run.

Both halves are load-bearing. Without the deny, the instruction is a suggestion. Without the instruction, the agent repeatedly tries the command, hits a wall, and you have built friction instead of a workflow.

Keep proposed commands to **one line each**, no backslash continuations, which break when pasted into a terminal.

---

## Setting up a new machine

1. Install and authenticate. **Never copy credentials between machines.**
2. `git pull`. This brings context files and the shared settings file.
3. Set machine-local preferences (`model`, effort level) in `~/.claude/settings.json`.
4. Add a local settings file **only** for genuine deltas from the shared baseline.
5. Run `/sandbox` and find out whether you have one.
6. Run `/context` and confirm your `CLAUDE.md` actually loaded, under **Memory files**.
7. Test one `deny` rule and one `ask` rule. Confirm permission errors, not "command not found".
8. Consciously note what did *not* arrive: auto memory, local settings, anything gitignored.

Step 8 is the one people skip. A session on the new machine genuinely knows less than the one you just left, and that is correct behaviour, not something to work around by copying `$HOME`.

---

## Traps, collected

| Trap | Why it bites |
|---|---|
| Omitting `find`/`grep` from `allow` to make them prompt | they are built-in read-only commands and never prompt; only an `ask` rule changes that |
| Assuming your session is in Manual mode | Pro/Max/Team start in auto mode, where a classifier approves instead of you |
| An allow rule that silently stopped working | auto mode drops broad rules like `Bash(python*)` on entry and restores them on exit |
| Assuming the nearest `CLAUDE.md` wins | they concatenate; a subfolder file can add but never retract |
| A passing `deny` test | deny is evaluated first in every mode, so it proves nothing about `ask` or `allow` |
| Expecting the sandbox to be there | on Linux it needs bubblewrap and user namespaces, and it degrades to unsandboxed with only a warning |
| `!` exceptions inside an ignored directory | files look untracked but are not; a later cleanup deletes them from every checkout |
| Duplicated rules across settings files | they cannot disagree usefully; one silently wins, the other misleads readers |
| Commit hashes written into context files | stale within hours; the agent then reasons from a confident wrong premise |
| Memory restating a tracked guide | no recall benefit, guaranteed drift |
| `MEMORY.md` over 200 lines | everything past the limit is silently dropped at load |
| Permissions in `~/.claude/settings.json` | applies to every project, travels to none |
| Gitignored context files | agent context silently never arrives on the second machine |

On that first ignore-pattern row: if you need to track one file inside an ignored directory, do not reach for a negation pattern. Ignore the specific personal file instead.

```gitignore
# Avoid
.claude/*
!.claude/settings.json

# Prefer
.claude/settings.local.json
```

Same outcome, no exception, and no chance of the silent-deletion failure that negation patterns inside ignored directories are famous for.

---

## The short version

Track your context files and your shared settings file so understanding and guardrails reach the cluster on the same `git push` as your code; keep a local settings file for per-machine deltas only. Make the shared file the **loosest acceptable** policy, because denies compose upward and can never be loosened locally. Keep `allow` short and promote to it from evidence, but know that for the built-in read-only commands an **`ask` rule is the only thing that produces a prompt**, and that your session probably starts in auto mode rather than Manual. Use the sandbox on your laptop and verify whether you have one on the cluster, because it fails open. Deny the irreversible, let model judgment cover the long tail, approve anything consequential yourself, and reach for a `PreToolUse` hook when something must be enforced rather than encouraged. On shared hardware, run the agent on the login node but have it *propose* privileged commands rather than run them. Put durable, publishable facts in the tracked guides and private or machine-specific ones in memory, and never in both.

The underlying discipline is smaller than all of that: **know which of your three systems each fact belongs to, and write it down exactly once.**
