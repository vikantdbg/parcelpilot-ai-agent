import streamlit as st
from dotenv import load_dotenv
from .agent import run_agent
from .data_tools import proactive_issue_detection

load_dotenv()
st.set_page_config(page_title="ParcelPilot AI Support", page_icon="📦", layout="wide")
st.title("📦 ParcelPilot AI Support Agent")
st.caption("Support + operations assistant with retrieval, structured data, access control and confirmed actions.")

with st.sidebar:
    st.header("Demo Context")
    user = st.selectbox("User", ["Internal Support", "Northstar Customer", "LumenWorks Customer"])
    if user == "Internal Support": role, account_id = "internal", None
    elif user == "Northstar Customer": role, account_id = "customer", "ACCT-001"
    else: role, account_id = "customer", "ACCT-002"
    st.divider(); st.write("📚 Document search"); st.write("🗃️ Structured-data lookup"); st.write("⚠️ Prepare escalation"); st.write("✅ Confirm escalation")
    st.info("State-changing actions require explicit confirmation.")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

prompt = st.chat_input("Ask about an order, ticket, policy, cancellation, SLA or known issue...")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Checking ParcelPilot sources..."):
            answer = run_agent(st.session_state.messages, role=role, account_id=account_id)
        st.markdown(answer)
    st.session_state.messages.append({"role":"assistant","content":answer})

st.divider(); st.subheader("Proactive Issue Detection")
finding = proactive_issue_detection()
if "findings" in finding: st.dataframe(finding["findings"], use_container_width=True, hide_index=True)
else: st.warning(finding.get("error", "Unable to analyze tickets."))
