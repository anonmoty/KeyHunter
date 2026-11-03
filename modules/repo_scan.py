import shutil
from khcore.config import R, R2, R3, G, G2, C, W, W2, Y, O, D, D2, N, BOLD
from khcore.engine import (git_clone, scan_directory, found_secret, section,
                            info, warn, safe, err, save_report)

def run(repo_url, token=None):
    section("Repository Scanner — Clone & Scan")
    findings = []
    if not repo_url.startswith("http"):
        repo_url = f"https://github.com/{repo_url}"
    if not repo_url.endswith(".git"):
        repo_url += ".git"
    info(f"Repo: {C}{repo_url}{N}")
    clone_path = git_clone(repo_url, depth=100)
    if not clone_path:
        err("Clone failed."); return findings
    info("Scanning all files for secrets...")
    findings = scan_directory(clone_path)
    if findings:
        for f in findings:
            found_secret(f)
        info(f"Total secrets: {R3}{len(findings)}{N}")
        save_report(repo_url, "repo", findings)
    else:
        safe("No secrets found")
    try:
        shutil.rmtree(clone_path)
    except:
        pass
    return findings
