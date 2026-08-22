# Architecture Note

## Agent
The LLM interprets requests and selects tools. It is not trusted to enforce authorization or mutate state.

## Tools
1. `search_documents`
2. `lookup_structured_data`
3. `detect_proactive_issues`
4. `prepare_escalation`
5. `confirm_escalation`

The last two deliberately separate proposal from execution so explicit confirmation is enforceable in application code.

## Source precedence
1. Active signed customer agreement
2. Current support policy
3. Current SOP/product documentation
4. Historical context

Deprecated policy v2 is retained for traceability but excluded from current retrieval.

## Access control
Customer mode passes the authenticated account ID into the structured-data tool, where filtering happens before results are returned. This prevents the model from being the only security boundary.

## Reliability
The agent should acknowledge conflicts, avoid promising credits when facts are unknown, surface SLA breaches, and recommend escalation for P1 or unresolved uncertainty.

## Trade-offs
A lightweight local retriever keeps the take-home simple to run. The supplied PDF/Excel pack is represented in text/JSON in the repository so browser deployment can run without binary-file preprocessing. The same tool contracts can later use a vector database and native spreadsheet storage.
