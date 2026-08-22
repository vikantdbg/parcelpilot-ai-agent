# ParcelPilot AI Support Agent

AI support and operations agent for the CalQuity AI Engineer take-home assessment.

## Included
- Natural-language AI support chatbot
- Current-policy document retrieval
- Structured account/order/ticket lookup
- Customer account-level access control
- Confirmation-gated escalation action
- Proactive P1/P2 issue detection
- Architecture, product, and AI-tool usage notes
- Assessment test cases

The supplied PDF content is stored as searchable text and the supplied structured workbook is represented as JSON so the demo can run easily in browser hosting.

## Run locally
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add `OPENAI_API_KEY`.
3. Run `streamlit run app/main.py`.

## Streamlit deployment
Deploy this repository from Streamlit Community Cloud with main file `app/main.py`. Add `OPENAI_API_KEY` and `OPENAI_MODEL` in the app Secrets.

## Demo prompts
- Can Northstar cancel ORD-1001 without a cancellation fee? Explain why.
- Why does my SwiftShip order still show BOOKED?
- What is the current CSV upload limit and why can 4,200 rows fail?
- Find all P1 tickets.
- Escalate TKT-501 to the support team.

The last prompt should require explicit confirmation before execution.
