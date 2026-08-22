from app.data_tools import lookup_data, proactive_issue_detection

def test_northstar_order_is_scoped():
    r = lookup_data("ORD-1001", account_id="ACCT-001", role="customer")
    assert any(x["sheet"] == "orders" for x in r["results"])

def test_customer_cannot_get_other_account_order():
    r = lookup_data("ORD-2001", account_id="ACCT-001", role="customer")
    assert not any("ORD-2001" in str(x) for x in r["results"])

def test_proactive_detects_p1():
    r = proactive_issue_detection()
    assert any(x["ticket_id"] == "TKT-501" and x["severity"] == "P1" for x in r["findings"])
    assert any(x["ticket_id"] == "TKT-505" and x["severity"] == "P1" for x in r["findings"])
