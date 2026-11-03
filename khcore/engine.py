import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
import re
import os
import subprocess
import time
from datetime import datetime
from khcore.config import (R, R2, R3, G, G2, B, W, W2, Y, Y2, O, C, C2, M, D, D2, N, BOLD,
                            LOOT, CLONE_DIR, UA, PATTERNS, SCAN_EXTS, SKIP_DIRS, SKIP_FILES,
                            MAX_FILE_SIZE)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def http_get(url, headers=None, timeout=15):
    hdrs = {"User-Agent": UA, "Accept": "application/vnd.github.v3+json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=CTX)
        body = resp.read().decode("utf-8", errors="replace")
        rh = {k.lower(): v for k, v in resp.getheaders()}
        return {"ok": True, "status": resp.status, "headers": rh, "body": body,
                "json": json.loads(body) if body.startswith(("{", "[")) else None}
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except:
            body = ""
        return {"ok": False, "status": e.code, "headers": {}, "body": body, "json": None}
    except Exception as e:
        return {"ok": False, "status": 0, "headers": {}, "body": str(e), "json": None}

def scan_text(text, source="unknown", line_offset=0):
    findings = []
    if not text or len(text) > MAX_FILE_SIZE:
        return findings
    lines = text.split("\n")
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 8:
            continue
        for name, meta in PATTERNS.items():
            try:
                for m in re.finditer(meta["regex"], line):
                    matched = m.group(0)
                    if len(matched) < 8:
                        continue
                    if _is_fp(matched):
                        continue
                    findings.append({
                        "type": name, "severity": meta["severity"],
                        "secret": _mask(matched), "raw": matched[:80],
                        "line": line_num + line_offset,
                        "context": line[:120], "source": source,
                    })
            except re.error:
                pass
    return findings

def _mask(s):
    if len(s) <= 8:
        return s[:2] + "***"
    return s[:6] + "***" + s[-4:]

def _is_fp(m):
    low = m.lower()
    for fp in ["example","test","dummy","fake","xxxx","yyyy","zzzz",
               "placeholder","changeme","your_","todo","fixme"]:
        if fp in low:
            return True
    if low.count("a") > len(low) * 0.6:
        return True
    return False

def scan_file(filepath):
    findings = []
    try:
        fname = os.path.basename(filepath)
        if fname in SKIP_FILES:
            return findings
        ext = os.path.splitext(fname)[1].lower()
        if ext and ext not in SCAN_EXTS and fname not in (".env",".netrc",".htpasswd"):
            return findings
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE or size == 0:
            return findings
        with open(filepath, "r", errors="replace") as f:
            text = f.read(MAX_FILE_SIZE)
        findings = scan_text(text, source=filepath)
    except Exception:
        pass
    return findings

def scan_directory(dirpath):
    findings = []
    count = [0]
    for root, dirs, files in os.walk(dirpath):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = os.path.join(root, fname)
            count[0] += 1
            if count[0] % 100 == 0:
                print(f"\r  {C}[+]{N} {W2}Scanned {count[0]} files...{N}", end="", flush=True)
            f = scan_file(fpath)
            findings.extend(f)
    print()
    return findings

def git_clone(repo_url, depth=50):
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = os.path.join(CLONE_DIR, f"{repo_name}_{int(time.time())}")
    if os.path.exists(clone_path):
        import shutil
        shutil.rmtree(clone_path)
    info(f"Cloning {repo_url} (depth={depth})...")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", str(depth), "--quiet", repo_url, clone_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            info(f"Cloned to {clone_path}")
            return clone_path
        else:
            err(f"Clone failed: {result.stderr[:200]}")
            return None
    except FileNotFoundError:
        err("git not installed! Run: pkg install git")
        return None
    except subprocess.TimeoutExpired:
        err("Clone timed out (120s)")
        return None
    except Exception as e:
        err(f"Clone error: {e}")
        return None

def git_log_commits(repo_path, max_commits=50):
    commits = []
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={max_commits}", "--format=%H|%an|%ae|%s|%ai", "--all"],
            capture_output=True, text=True, cwd=repo_path, timeout=30
        )
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commits.append({"hash": parts[0], "author": parts[1],
                                    "email": parts[2], "message": parts[3], "date": parts[4]})
    except Exception:
        pass
    return commits

def git_show_commit(repo_path, commit_hash):
    try:
        result = subprocess.run(
            ["git", "show", "--format=", commit_hash],
            capture_output=True, text=True, cwd=repo_path, timeout=30
        )
        return result.stdout
    except Exception:
        return ""

def gh_get_user_repos(username, max_repos=30, token=None):
    repos = []
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    for page in range(1, (max_repos // 30) + 2):
        url = f"https://api.github.com/users/{username}/repos?per_page=30&page={page}&sort=updated"
        r = http_get(url, headers=headers)
        if not r["ok"] or not r["json"]:
            break
        for repo in r["json"]:
            repos.append({
                "name": repo.get("full_name", ""), "url": repo.get("html_url", ""),
                "clone": repo.get("clone_url", ""), "desc": repo.get("description", "") or "",
                "stars": repo.get("stargazers_count", 0), "lang": repo.get("language", "") or "",
            })
            if len(repos) >= max_repos:
                break
        if len(repos) >= max_repos:
            break
        time.sleep(0.5)
    return repos

def gh_get_org_repos(org, max_repos=30, token=None):
    repos = []
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    url = f"https://api.github.com/orgs/{org}/repos?per_page={min(max_repos, 100)}&sort=updated"
    r = http_get(url, headers=headers)
    if r["ok"] and r["json"]:
        for repo in r["json"][:max_repos]:
            repos.append({
                "name": repo.get("full_name", ""), "url": repo.get("html_url", ""),
                "clone": repo.get("clone_url", ""), "desc": repo.get("description", "") or "",
                "stars": repo.get("stargazers_count", 0), "lang": repo.get("language", "") or "",
            })
    return repos

def found_secret(finding):
    sev = finding["severity"]
    colors = {"CRITICAL": R3, "HIGH": R, "MEDIUM": O, "LOW": Y}
    c = colors.get(sev, R)
    print(f"\n  {c}{'━'*55}{N}")
    print(f"  {c}{BOLD}[{sev}] {finding['type']}{N}")
    print(f"  {W2}File: {C}{finding['source']}{N}")
    print(f"  {W2}Line: {Y}{finding['line']}{N}")
    print(f"  {W2}Secret: {R}{finding['secret']}{N}")
    print(f"  {D}Context: {W2}{finding['context'][:100]}{N}")
    print(f"  {c}{'━'*55}{N}")

def info(msg):
    print(f"  {C}[+]{N} {W2}{msg}{N}")

def warn(msg):
    print(f"  {Y}[!]{N} {Y}{msg}{N}")

def safe(msg):
    print(f"  {G}[✓]{N} {G2}{msg}{N}")

def err(msg):
    print(f"  {R}[-]{N} {R2}{msg}{N}")

def section(msg):
    print(f"\n  {R3}{BOLD}[MODULE]{N} {W}{BOLD}{msg}{N}")
    print(f"  {D}{'─'*50}{N}")

def save_report(target, module, findings):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = os.path.join(LOOT, f"keys_{module}_{ts}.json")
    data = {
        "target": target, "module": module, "time": ts,
        "total_secrets": len(findings),
        "by_severity": {
            "CRITICAL": sum(1 for f in findings if f["severity"] == "CRITICAL"),
            "HIGH": sum(1 for f in findings if f["severity"] == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f["severity"] == "MEDIUM"),
        },
        "findings": findings,
    }
    with open(fn, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n  {G}[+]{N} {W2}Loot saved: {R}{fn}{N}")
    return fn
