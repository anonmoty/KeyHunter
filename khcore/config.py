import os

R   = "\033[91m"
R2  = "\033[31m"
R3  = "\033[38;5;196m"
G   = "\033[92m"
G2  = "\033[32m"
B   = "\033[94m"
B2  = "\033[34m"
W   = "\033[97m"
W2  = "\033[37m"
Y   = "\033[93m"
Y2  = "\033[33m"
O   = "\033[38;5;208m"
C   = "\033[96m"
C2  = "\033[36m"
M   = "\033[95m"
P   = "\033[35m"
D   = "\033[90m"
D2  = "\033[38;5;240m"
BOLD = "\033[1m"
N   = "\033[0m"
E   = N

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOT = os.path.join(BASE, "loot")
os.makedirs(LOOT, exist_ok=True)
CLONE_DIR = os.path.join(BASE, "loot", "_clones")
os.makedirs(CLONE_DIR, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0"

PATTERNS = {
    "AWS Access Key": {
        "regex": r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
        "severity": "CRITICAL", "example": "AKIAIOSFODNN7EXAMPLE",
    },
    "AWS Secret Key": {
        "regex": r'(?i)aws[_\-]?secret[_\-]?access[_\-]?key[\s]*[=:]\s*["\']?([A-Za-z0-9/+=]{40})["\']?',
        "severity": "CRITICAL", "example": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    },
    "GitHub Token": {
        "regex": r'\b(ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghu_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|ghr_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59})\b',
        "severity": "CRITICAL", "example": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "GitLab Token": {
        "regex": r'\b(glpat-[A-Za-z0-9\-]{20}|glptt-[A-Za-z0-9]{40})\b',
        "severity": "CRITICAL", "example": "glpat-xxxxxxxxxxxxxxxxxxxx",
    },
    "Slack Token": {
        "regex": r'\bxox[baprs]-[A-Za-z0-9\-]{10,48}\b',
        "severity": "CRITICAL", "example": "xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx",
    },
    "Slack Webhook": {
        "regex": r'https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24}',
        "severity": "HIGH", "example": "https://hooks.slack.com/services/T.../B.../...",
    },
    "Stripe Secret": {
        "regex": r'\bsk_live_[A-Za-z0-9]{24,99}\b',
        "severity": "CRITICAL", "example": "sk_live_xxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Stripe Publishable": {
        "regex": r'\bpk_live_[A-Za-z0-9]{24,99}\b',
        "severity": "HIGH", "example": "pk_live_xxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Google API Key": {
        "regex": r'\bAIza[A-Za-z0-9\-_]{35}\b',
        "severity": "HIGH", "example": "AIzaSyA1234567890abcdefghijklmnopqrstu",
    },
    "Google OAuth": {
        "regex": r'\b[0-9]+-[A-Za-z0-9_]{32}\.apps\.googleusercontent\.com\b',
        "severity": "HIGH", "example": "123-xxxx.apps.googleusercontent.com",
    },
    "Firebase URL": {
        "regex": r'https://[a-z0-9\-]+\.firebaseio\.com',
        "severity": "MEDIUM", "example": "https://myapp.firebaseio.com",
    },
    "RSA Private Key": {
        "regex": r'-----BEGIN RSA PRIVATE KEY-----',
        "severity": "CRITICAL", "example": "-----BEGIN RSA PRIVATE KEY-----",
    },
    "DSA Private Key": {
        "regex": r'-----BEGIN DSA PRIVATE KEY-----',
        "severity": "CRITICAL", "example": "-----BEGIN DSA PRIVATE KEY-----",
    },
    "EC Private Key": {
        "regex": r'-----BEGIN EC PRIVATE KEY-----',
        "severity": "CRITICAL", "example": "-----BEGIN EC PRIVATE KEY-----",
    },
    "PGP Private Key": {
        "regex": r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        "severity": "CRITICAL", "example": "-----BEGIN PGP PRIVATE KEY BLOCK-----",
    },
    "Generic Private Key": {
        "regex": r'-----BEGIN PRIVATE KEY-----',
        "severity": "CRITICAL", "example": "-----BEGIN PRIVATE KEY-----",
    },
    "JWT Token": {
        "regex": r'\beyJ[A-Za-z0-9\-_]{10,}\.eyJ[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\b',
        "severity": "HIGH", "example": "eyJhbGciOi.eyJzdWIiOi.xxx",
    },
    "SendGrid API": {
        "regex": r'\bSG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}\b',
        "severity": "HIGH", "example": "SG.xxxxxx.xxxxxx",
    },
    "Twilio API Key": {
        "regex": r'\bSK[A-Za-z0-9]{32}\b',
        "severity": "HIGH", "example": "SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Twilio SID": {
        "regex": r'\bAC[A-Za-z0-9]{32}\b',
        "severity": "MEDIUM", "example": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Mailgun Key": {
        "regex": r'\bkey-[A-Za-z0-9]{32}\b',
        "severity": "HIGH", "example": "key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Heroku API Key": {
        "regex": r'(?i)heroku[_\-]?api[_\-]?key[\s]*[=:]\s*["\']?([A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12})["\']?',
        "severity": "HIGH", "example": "heroku_api_key=xxxx-xxxx-xxxx-xxxx-xxxx",
    },
    "Square Token": {
        "regex": r'\bsq0atp-[A-Za-z0-9\-_]{22}\b',
        "severity": "HIGH", "example": "sq0atp-xxxxxxxxxxxxxxxxxxxxxx",
    },
    "Shopify Token": {
        "regex": r'\bshpat_[A-Za-z0-9]{32}\b',
        "severity": "HIGH", "example": "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Telegram Bot": {
        "regex": r'\b[0-9]{8,10}:[A-Za-z0-9\-_]{35}\b',
        "severity": "HIGH", "example": "123456789:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Discord Webhook": {
        "regex": r'https://discord(?:app)?\.com/api/webhooks/[0-9]{17,19}/[A-Za-z0-9\-_]{60,68}',
        "severity": "HIGH", "example": "https://discord.com/api/webhooks/...",
    },
    "NPM Token": {
        "regex": r'\bnpm_[A-Za-z0-9]{36}\b',
        "severity": "HIGH", "example": "npm_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "PyPI Token": {
        "regex": r'\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9\-_]{50,}\b',
        "severity": "HIGH", "example": "pypi-AgEIcHlwaS5vcmc...",
    },
    "Docker Hub Token": {
        "regex": r'\bdckr_pat_[A-Za-z0-9\-_]{27,}\b',
        "severity": "HIGH", "example": "dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    "Azure Storage": {
        "regex": r'(?i)(?:AccountKey|DefaultEndpointsProtocol).*?Key=([A-Za-z0-9+/=]{86,88})',
        "severity": "CRITICAL", "example": "AccountKey=xxxx...",
    },
    "Generic API Key": {
        "regex": r'(?i)(?:api[_\-]?key|apikey|api[_\-]?secret)[\s]*[=:]\s*["\']?([A-Za-z0-9\-_]{16,64})["\']?',
        "severity": "MEDIUM", "example": "api_key=xxxxxxxxxxxxxxxx",
    },
    "Generic Secret": {
        "regex": r'(?i)(?:secret|password|passwd|pwd)[\s]*[=:]\s*["\']([^\s"\']{8,64})["\']',
        "severity": "MEDIUM", "example": 'password="mysecret"',
    },
    "Generic Token": {
        "regex": r'(?i)(?:access[_\-]?token|auth[_\-]?token|bearer)[\s]*[=:]\s*["\']?([A-Za-z0-9\-_.]{20,128})["\']?',
        "severity": "MEDIUM", "example": "access_token=xxxxxxxxxxxxxxxxxxxx",
    },
    "DB Connection": {
        "regex": r'(?i)(?:mysql|postgres|postgresql|mongodb|redis|mssql)://[^\s"\']{10,120}',
        "severity": "CRITICAL", "example": "postgres://user:pass@host:5432/db",
    },
    "Bearer Token": {
        "regex": r'(?i)bearer\s+[A-Za-z0-9\-_.]{20,256}',
        "severity": "HIGH", "example": "Bearer eyJhbGciOi...",
    },
}

SCAN_EXTS = {
    ".py",".js",".ts",".jsx",".tsx",".java",".go",".rb",".php",
    ".c",".cpp",".h",".cs",".swift",".kt",".rs",".sh",".bash",
    ".ps1",".bat",".json",".yaml",".yml",".toml",".ini",".cfg",
    ".conf",".properties",".env",".xml",".html",".vue",".sql",
    ".graphql",".tf",".md",".txt",".log",".pem",".key",".crt",
}

SKIP_DIRS = {
    ".git","node_modules","__pycache__",".venv","venv","env",
    "dist","build",".next","vendor","target",".idea",".vscode","bin",
}

SKIP_FILES = {
    "package-lock.json","yarn.lock","poetry.lock","Pipfile.lock",
    "Cargo.lock","go.sum","composer.lock","Gemfile.lock",
}

MAX_FILE_SIZE = 5 * 1024 * 1024
