from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ParcelPilot_Assessment_Data.json"
STATE = ROOT / "data" / "mock_actions.json"

def load_tables():
    if not DATA.exists(): return {}
    return json.loads(DATA.read_text(encoding="utf-8"))

def lookup_data(query, account_id=None, role="internal"):
    tables=load_tables()
    if not tables: return {"error":"Assessment dataset is missing."}
    terms=[t for t in query.lower().replace("?"," ").split() if len(t)>2]
    results=[]
    for sheet, rows in tables.items():
        work=rows
        if role=="customer":
            if not account_id: return {"error":"Customer account context is required."}
            work=[r for r in work if str(r.get("account_id", "")).upper()==str(account_id).upper()]
        if terms:
            work=[r for r in work if any(any(term in str(v).lower() for term in terms) for v in r.values())]
        if work: results.append({"sheet":sheet,"rows":work[:25]})
    return {"results":results}

def proactive_issue_detection():
    tables=load_tables()
    tickets=tables.get("tickets", [])
    findings=[]
    for t in tickets:
        if str(t.get("status", "")).lower() != "open":
            continue
        desc=(str(t.get("subject", ""))+" "+str(t.get("description", ""))).lower()
        severity="P2"
        reason="Open support issue"
        if "http 500" in desc or "all shipment" in desc or "every user" in desc or "api key" in desc or "exposed" in desc:
            severity="P1"; reason="High-impact outage or security risk"
        elif "fails" in desc or "cannot" in desc or "incident" in desc:
            severity="P2"; reason="Operational failure requiring support attention"
        findings.append({"ticket_id":t.get("ticket_id"),"account_id":t.get("account_id"),"severity":severity,"subject":t.get("subject"),"reason":reason})
    return {"findings":findings}

def prepare_escalation(ticket_id, reason, priority="P2"):
    return {"status":"AWAITING_CONFIRMATION","ticket_id":ticket_id,"priority":priority,"reason":reason,"message":"Escalation prepared. Explicit confirmation is required before execution."}

def confirm_escalation(ticket_id, reason, priority="P2"):
    actions=json.loads(STATE.read_text()) if STATE.exists() else []
    action={"action":"escalate_ticket","ticket_id":ticket_id,"priority":priority,"reason":reason,"created_at":datetime.utcnow().isoformat()+"Z"}
    actions.append(action); STATE.write_text(json.dumps(actions,indent=2))
    return {"status":"EXECUTED","action":action}
