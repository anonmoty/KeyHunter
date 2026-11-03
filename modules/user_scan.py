import shutil
from khcore.config import R, R2, R3, G, G2, C, W, W2, Y, O, D, D2, N, BOLD
from khcore.engine import (gh_get_user_repos, git_clone, scan_directory,
                            found_secret, section, info, warn, safe, err, save_report)

def run(username, max_repos=10, token=None):
    section(f"User Scanner — @{username}")
    all_findings = []
    repos = gh_get_user_repos(username, max_repos=max_repos, token=token)
    if not repos:
        err(f"No repos for @{username}"); return all_findings
    info(f"Found {Y}{len(repos)}{W2} repos")
    for i, repo in enumerate(repos):
        name = repo["name"]
        print(f"\n  {Y}[{i+1}/{len(repos)}]{N} {W}{name}{N} {D2}★{repo['stars']} {repo['lang']}{N}")
        clone_path = git_clone(repo["clone"], depth=20)
        if not clone_path:
            warn(f"Skipped {name}"); continue
        findings = scan_directory(clone_path)
        if findings:
            for f in findings:
                f["repo"] = name
                found_secret(f)
            all_findings.extend(findings)
            info(f"{R}{len(findings)}{W2} secrets in {name}")
        else:
            safe(f"Clean: {name}")
        try:
            shutil.rmtree(clone_path)
        except:
            pass
    if all_findings:
        info(f"Total: {R3}{len(all_findings)}{N}")
        save_report(username, "user", all_findings)
    else:
        safe("No secrets found")
    return all_findings
