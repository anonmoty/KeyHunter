import shutil
from khcore.config import R, R2, R3, G, G2, C, W, W2, Y, O, D, D2, N, BOLD
from khcore.engine import (git_clone, git_log_commits, git_show_commit,
                            scan_text, found_secret, section,
                            info, warn, safe, err, save_report)

def run(repo_url, max_commits=50, token=None):
    section("Commit History Scanner")
    findings = []
    if not repo_url.startswith("http"):
        repo_url = f"https://github.com/{repo_url}"
    if not repo_url.endswith(".git"):
        repo_url += ".git"
    info(f"Repo: {C}{repo_url}{N} | Max commits: {Y}{max_commits}{N}")
    clone_path = git_clone(repo_url, depth=max_commits)
    if not clone_path:
        err("Clone failed"); return findings
    commits = git_log_commits(clone_path, max_commits)
    info(f"Found {Y}{len(commits)}{W2} commits")
    if not commits:
        safe("No commits"); return findings
    for i, commit in enumerate(commits):
        short = commit["hash"][:8]
        info(f"[{i+1}/{len(commits)}] {Y}{short}{N} {W2}{commit['message'][:50]}{N}")
        diff = git_show_commit(clone_path, commit["hash"])
        if not diff:
            continue
        added = "\n".join(l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++"))
        if added:
            cf = scan_text(added, source=f"commit:{short}")
            for f in cf:
                f["commit"] = commit["hash"]
                f["author"] = commit["author"]
                f["date"] = commit["date"]
                found_secret(f)
                findings.append(f)
    if findings:
        info(f"Secrets in history: {R3}{len(findings)}{N}")
        save_report(repo_url, "commits", findings)
    else:
        safe("No secrets in commit history")
    try:
        shutil.rmtree(clone_path)
    except:
        pass
    return findings
