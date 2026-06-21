"""所有扫描器的统一数据模型 + 归一化。"""

from dataclasses import dataclass, asdict

# 严重度排序。INFO 折算为 LOW（我们报告所有 >= LOW 的级别）。
SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "INFO": 1}
VALID_SEVERITIES = ("HIGH", "MEDIUM", "LOW")


def normalize_severity(raw, tool):
    """把工具特有的严重度/优先级映射为 HIGH/MEDIUM/LOW 之一。"""
    raw = str(raw).upper().strip()

    if tool in ("gosec", "bandit"):
        return raw if raw in VALID_SEVERITIES else "LOW"

    if tool == "semgrep":
        return {"INFO": "LOW", "LOW": "LOW", "MEDIUM": "MEDIUM",
                "HIGH": "HIGH", "ERROR": "HIGH", "WARNING": "MEDIUM"}.get(raw, "LOW")

    if tool == "ruff":
        return {"ERROR": "MEDIUM", "WARNING": "LOW", "FATAL": "HIGH"}.get(raw, "LOW")

    if tool == "spotbugs":
        return {"1": "HIGH", "2": "MEDIUM", "3": "LOW"}.get(raw, "LOW")

    if tool == "pmd":
        try:
            p = int(raw)
        except ValueError:
            return "LOW"
        return "HIGH" if p <= 2 else ("MEDIUM" if p == 3 else "LOW")

    if tool == "checkstyle":
        return {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}.get(raw, "LOW")

    if tool == "golangci-lint":
        return {"ERROR": "MEDIUM", "WARNING": "LOW", "INFO": "LOW"}.get(raw, "MEDIUM")

    return "LOW"


# golangci-lint 内各 linter 按类别分组。
GOLANGCI_SECURITY = {"gosec"}
GOLANGCI_STYLE = {"gofmt", "goimports", "gocritic", "whitespace", "nlreturn"}

# findsecbugs（SpotBugs 安全插件）检测器的已知类型前缀。
# 标准 SpotBugs 正确性缺陷（NP_*、MS_*、EI_* 等）虽以字母开头但不在此列 → quality。
SPOTBUGS_SECURITY_PREFIXES = (
    "SQL_", "XSS_", "DESERIALIZATION", "OBJECT_DESERIALIZATION",
    "PASSWORD_", "CUSTOM_MESSAGE_DIGEST", "ECB_MODE", "UNCRYPTED_",
    "WEAK_", "SSL_CONTEXT", "BROKEN_", "DEFAULT_", "REDOS",
    "REQUEST_FORGERY", "BLIND_REQUEST_FORGERY", "URLCONNECTION_SSRF", "SSRF",
    "XXE_", "XML_", "STRUTS", "XSLT_", "HTTP_", "MALICIOUS_", "HARDCODE_",
    "PREDICTABLE_", "IMPROPER_", "OVERLY_PERMISSIVE_", "BLOWFISH_",
    "RSA_", "TDES_", "PADDING_ORACLE", "TRUST_MANAGER",
)


def categorize(tool, rule_id):
    """判定一个问题是 security / quality / style。"""
    rule_id = (rule_id or "").lower()

    if tool in ("gosec", "bandit"):
        return "security"
    if tool == "semgrep":
        # 我们跑 OWASP/安全规则集；默认 security（除非路径另有说明）。
        return "security"
    if tool == "spotbugs":
        # findsecbugs 安全检测器有已知类型前缀；其余（NP_* 等）按 quality。
        rid = rule_id.upper()
        return "security" if any(rid.startswith(p) for p in SPOTBUGS_SECURITY_PREFIXES) else "quality"
    if tool == "pmd":
        return "quality"
    if tool == "checkstyle":
        return "style"
    if tool == "ruff":
        # E/W/F = pycodestyle（style）；其余（B, C, SIM, PLC...）= quality。
        return "style" if rule_id[:1] in ("e", "w", "f") else "quality"
    if tool == "golangci-lint":
        if rule_id in GOLANGCI_SECURITY:
            return "security"
        if rule_id in GOLANGCI_STYLE:
            return "style"
        return "quality"
    return "quality"


@dataclass
class Issue:
    id: str
    file: str
    line: int
    end_line: int
    language: str
    tool: str
    rule_id: str
    severity: str
    category: str
    message: str
    code_snippet: str
    fixable: bool = True

    def to_dict(self):
        return asdict(self)
