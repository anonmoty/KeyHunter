import os
from khcore.config import R, R2, R3, G, G2, C, W, W2, Y, O, D, D2, N, BOLD
from khcore.engine import (scan_file, scan_directory, found_secret, section,
                            info, warn, safe, err, save_report)

def run(target_path):
    section("Local File/Folder Scanner")
    findings = []
    target_path = os.path.expanduser(target_path)
    if not os.path.exists(target_path):
        err(f"Not found: {target_path}"); return findings
    if os.path.isfile(target_path):
        info(f"File: {C}{target_path}{N}")
        findings = scan_file(target_path)
    elif os.path.isdir(target_path):
        info(f"Dir: {C}{target_path}{N}")
        findings = scan_directory(target_path)
    if findings:
        for f in findings:
            found_secret(f)
        info(f"Total: {R3}{len(findings)}{N}")
        save_report(target_path, "local", findings)
    else:
        safe("No secrets found")
    return findings
