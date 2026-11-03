import json
import http.server
import socketserver
from khcore.config import R, R2, R3, G, G2, C, W, W2, Y, O, D, D2, N, BOLD
from khcore.engine import scan_text, found_secret, section, info, warn, safe, err, save_report

class WH(http.server.BaseHTTPRequestHandler):
    findings_list = []
    target_name = "webhook"
    def do_POST(self):
        cl = int(self.headers.get("Content-Length", 0))
        if cl == 0:
            self.send_response(200); self.end_headers(); return
        body = self.rfile.read(cl).decode("utf-8", errors="replace")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
        try:
            data = json.loads(body)
        except:
            data = {}
        event = self.headers.get("X-GitHub-Event", "push")
        info(f"Received {Y}{event}{W2} event")
        for commit in data.get("commits", []):
            ch = commit.get("id", "")[:8]
            author = commit.get("author", {}).get("name", "?")
            info(f"Commit {Y}{ch}{N} by {W}{author}{N}")
            text = json.dumps(commit, indent=2)
            for f in scan_text(text, source=f"webhook:{ch}"):
                f["commit"] = ch; f["author"] = author; f["event"] = event
                found_secret(f)
                WH.findings_list.append(f)
        if WH.findings_list:
            save_report(WH.target_name, "webhook", WH.findings_list)
    def log_message(self, fmt, *args):
        pass

def run(port=9090, target="github-webhook"):
    section("Webhook Listener")
    info(f"Server on port {Y}{port}{N}")
    info(f"Add to GitHub: {G}http://YOUR_IP:{port}/{N}")
    info("Listening... (Ctrl+C to stop)")
    WH.target_name = target
    WH.findings_list = []
    try:
        srv = socketserver.TCPServer(("0.0.0.0", port), WH)
        srv.serve_forever()
    except KeyboardInterrupt:
        print(f"\n  {Y}[+]{N} {W2}Stopped{N}")
        if WH.findings_list:
            save_report(target, "webhook", WH.findings_list)
    except OSError as e:
        err(str(e))
    return WH.findings_list
