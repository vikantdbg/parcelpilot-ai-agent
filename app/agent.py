import json
import os
from openai import OpenAI
from retrieval import search_documents
from data_tools import lookup_data, proactive_issue_detection, prepare_escalation, confirm_escalation

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

SYSTEM = """You are ParcelPilot Support Agent.

Use tools rather than guessing.

Source precedence:
1. Active signed customer agreement
2. Current support policy
3. Current SOP/product documentation
4. Historical context only

Deprecated documents must not be used as current policy.

Customer users can only receive data for their own account. The structured-data tool enforces account scoping.

For state-changing actions, prepare first, explain the proposed action, ask for explicit confirmation, and execute only after explicit confirmation.

Never promise a service credit when carrier fault, pickup timing, or customer fault is unknown.
If sources conflict, explain the conflict and request verification.
Mention the source names used in the answer when practical.
"""

TOOLS = [
    {"type":"function","function":{"name":"search_documents","description":"Search current ParcelPilot policies, agreements, SOPs and product documentation.","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"lookup_structured_data","description":"Look up account, order and ticket data from the supplied structured dataset.","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"detect_proactive_issues","description":"Analyze open support tickets for P1/P2 risk and recurring/urgent issues.","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"prepare_escalation","description":"Prepare a ticket escalation without executing it.","parameters":{"type":"object","properties":{"ticket_id":{"type":"string"},"reason":{"type":"string"},"priority":{"type":"string"}},"required":["ticket_id","reason"]}}},
    {"type":"function","function":{"name":"confirm_escalation","description":"Execute an escalation only after explicit user confirmation.","parameters":{"type":"object","properties":{"ticket_id":{"type":"string"},"reason":{"type":"string"},"priority":{"type":"string"}},"required":["ticket_id","reason"]}}}
]

def run_agent(messages, role="internal", account_id=None):
    user_context = f"\nUser context: role={role}, account_id={account_id or 'N/A'}"
    msgs = [{"role":"system","content":SYSTEM + user_context}] + messages
    for _ in range(8):
        response = client.chat.completions.create(model=MODEL, messages=msgs, tools=TOOLS, tool_choice="auto", temperature=0)
        msg = response.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        msgs.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            if call.function.name == "search_documents": result = search_documents(args["query"])
            elif call.function.name == "lookup_structured_data": result = lookup_data(args["query"], account_id=account_id, role=role)
            elif call.function.name == "detect_proactive_issues": result = proactive_issue_detection()
            elif call.function.name == "prepare_escalation": result = prepare_escalation(args["ticket_id"], args["reason"], args.get("priority","P2"))
            elif call.function.name == "confirm_escalation": result = confirm_escalation(args["ticket_id"], args["reason"], args.get("priority","P2"))
            else: result = {"error":"Unknown tool"}
            msgs.append({"role":"tool","tool_call_id":call.id,"content":json.dumps(result, default=str)})
    return "I could not complete the request safely within the available tool steps."
