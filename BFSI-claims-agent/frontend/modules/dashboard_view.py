from datetime import date

import streamlit as st

from modules.api_client import ApiError, list_my_claims, list_my_policies, send_chat_message, submit_claim
from modules.theme import INK_NAVY, SLATE, STATUS_COLORS, accent_bar, recommendation_block

def _render_policies_tab(policies):
    if not policies:
        st.info("No policies found for your account.")
        return

    columns = st.columns(2)
    for i, policy in enumerate(policies):
        with columns[i % 2]:
            with st.container(border=True):
                st.markdown(accent_bar(INK_NAVY), unsafe_allow_html=True)
                st.markdown(f"**{policy['policy_id']}**")
                st.caption(policy["sub_type"])
                st.write(f"{policy['policy_type']} · {policy['status']}")
                st.write(f"Coverage: {policy['start_date']} to {policy['end_date']}")
                st.write(f"Premium: {policy['premium']}")


def _render_submit_claim_tab(policies):
    if not policies:
        st.info("No policies found for your account -- nothing to file a claim against.")
        return

    policy_options = {f"{p['policy_id']} -- {p['sub_type']}": p["policy_id"] for p in policies}

    with st.form("submit_claim_form"):
        left, right = st.columns(2)
        with left:
            policy_label = st.selectbox("Policy", options=list(policy_options.keys()))
            claim_type = st.text_input("Claim type", placeholder="e.g. Accident - Own Damage")
            incident_date = st.date_input("Incident date", max_value=date.today())
        with right:
            incident_description = st.text_area(
                "What happened?",
                height=140,
                placeholder="Describe the incident in detail -- a very short description can't be assessed.",
            )
            claim_amount = st.number_input("Claimed amount (optional)", min_value=0.0, step=1000.0, value=0.0)

        submitted = st.form_submit_button("Submit claim")

    if submitted:
        with st.spinner("Processing your claim -- this runs the full coverage, history, and fraud checks, and can take up to a minute."):
            try:
                claim = submit_claim(
                    policy_id=policy_options[policy_label],
                    claim_type=claim_type,
                    incident_description=incident_description,
                    incident_date=incident_date.isoformat(),
                    claim_amount=claim_amount if claim_amount > 0 else None,
                )
            except ApiError as exc:
                st.error(exc.detail)
                return

        st.session_state["last_submitted_claim"] = claim
        st.rerun()

    last_claim = st.session_state.get("last_submitted_claim")
    if last_claim:
        st.success(f"Claim {last_claim['claim_id']} submitted -- status: {last_claim['status']}")
        st.markdown(recommendation_block(last_claim["ai_recommendation"], last_claim["ai_rationale"]), unsafe_allow_html=True)


def _render_claim_chat(claim):
    history_key = f"chat_history_{claim['claim_id']}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    with st.expander("Ask about this claim"):
        for turn in st.session_state[history_key]:
            avatar = "🧑" if turn["role"] == "user" else "🛡️"
            with st.chat_message(turn["role"], avatar=avatar):
                st.write(turn["content"])

        if not st.session_state[history_key]:
            st.caption("Ask why this claim got its recommendation, or what it means for you.")

        with st.form(f"chat_form_{claim['claim_id']}", clear_on_submit=True, border=False):
            left, right = st.columns([5, 1])
            with left:
                question = st.text_input(
                    "Your question",
                    label_visibility="collapsed",
                    placeholder="e.g. Why was this claim flagged?",
                )
            with right:
                asked = st.form_submit_button("Send", use_container_width=True)

        if asked and question.strip():
            st.session_state[history_key].append({"role": "user", "content": question})
            try:
                with st.spinner("Thinking..."):
                    reply = send_chat_message(claim["claim_id"], question)
                st.session_state[history_key].append({"role": "assistant", "content": reply})
            except ApiError as exc:
                st.session_state[history_key].append(
                    {"role": "assistant", "content": f"Sorry, I couldn't answer that: {exc.detail}"}
                )
            st.rerun()


def _render_claim_history_tab(claims):
    if not claims:
        st.info("You haven't filed any claims yet.")
        return

    claims_sorted = sorted(claims, key=lambda c: c["intimation_date"], reverse=True)

    for claim in claims_sorted:
        color = STATUS_COLORS.get(claim["ai_recommendation"], SLATE)
        with st.container(border=True):
            st.markdown(accent_bar(color), unsafe_allow_html=True)

            header_col, badge_col = st.columns([4, 1])
            with header_col:
                st.markdown(f"**{claim['claim_id']}** &nbsp;·&nbsp; {claim['claim_type']}")
            with badge_col:
                if claim["fraud_flag"]:
                    st.markdown(f"<span style='color:{color};font-size:0.85rem;'>⚠ fraud risk</span>", unsafe_allow_html=True)

            detail_col, verdict_col = st.columns([3, 2])
            with detail_col:
                st.caption(f"Policy {claim['policy_id']} · status: {claim['status']}")
                st.write(f"**Incident date:** {claim['incident_date']}")
                st.write(claim["incident_description"])
                if claim["claim_amount"]:
                    st.write(f"**Claimed amount:** {claim['claim_amount']}")
            with verdict_col:
                st.markdown(recommendation_block(claim["ai_recommendation"], claim["ai_rationale"]), unsafe_allow_html=True)

            if claim["ai_recommendation"] is not None:
                _render_claim_chat(claim)


def _render_status_strip(policies, claims):
    """
    The dashboard's opening moment -- an at-a-glance queue overview.
    Fraud-flagged deliberately isn't a 7th/6th metric here -- it's
    already shown per-card in Claim History (the fraud-risk badge), so
    repeating it at the strip level was redundant clutter, not extra
    signal.
    """
    approved = sum(1 for c in claims if c["ai_recommendation"] == "approve")
    denied = sum(1 for c in claims if c["ai_recommendation"] == "deny")
    needs_review = sum(1 for c in claims if c["ai_recommendation"] == "needs_more_info")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Policies", len(policies))
    col2.metric("Claims filed", len(claims))
    col3.metric("Approved", approved)
    col4.metric("Needs review", needs_review)
    col5.metric("Denied", denied)


def _render_account_bar():
    """
    Top-right account row (username + log out), above the status strip
    -- more conventional placement than burying it in the sidebar, and
    more robust in Streamlit than trying to CSS-pin something to the
    sidebar's bottom edge.
    """
    spacer, account = st.columns([4, 1])
    with account:
        st.markdown(
            f"<div style='text-align:right;color:{SLATE};font-size:0.9rem;'>Logged in as <strong>{st.session_state.get('username', '')}</strong></div>",
            unsafe_allow_html=True,
        )
        if st.button("Log out", use_container_width=True):
            st.session_state.pop("access_token", None)
            st.session_state.pop("username", None)
            st.session_state.pop("last_submitted_claim", None)
            st.rerun()


def _count_text(count, singular, plural):
    """Small helper so the sidebar says "1 policy" but "2 policies"."""
    word = singular if count == 1 else plural
    return f"**{count}** {word}"


def _render_sidebar(policies, claims):
    """
    Left sidebar: the brand, a short summary of this customer's account,
    how the claim process works, and a few tips for filing a good claim.
    """
    awaiting = sum(1 for c in claims if c["status"] in ("Under Review", "Pending"))

    with st.sidebar:
        st.markdown(
            "<div style='font-family:Fraunces,serif;font-size:1.3rem;'>Meridian Shield</div>",
            unsafe_allow_html=True,
        )
        st.caption("Customer claims portal")
        st.divider()

        st.caption("Your account")
        st.markdown(_count_text(len(policies), "policy", "policies"))
        st.markdown(_count_text(len(claims), "claim filed", "claims filed"))
        st.markdown(f"**{awaiting}** awaiting a decision")
        st.divider()

        st.caption("How it works")
        st.markdown(
            "1. Choose a policy and tell us what happened\n"
            "2. Our AI assistant checks your cover, your claim history and the details you give\n"
            "3. It recommends approve, deny or needs more info\n"
            "4. Our claims team reviews it and makes the final decision"
        )
        st.divider()

        st.caption("Tips for a smooth claim")
        st.markdown(
            "- Describe the incident in detail: what, where and when\n"
            "- Report it as soon as you can -- late reports need extra checks\n"
            "- Add the claimed amount if you know it"
        )


def render_dashboard_view():
    _render_account_bar()
    st.title("Claims Processing Agent")

    try:
        policies = list_my_policies()
        claims = list_my_claims()
    except ApiError as exc:
        st.error(exc.detail)
        return

    _render_sidebar(policies, claims)

    _render_status_strip(policies, claims)
    st.divider()

    policies_tab, submit_tab, history_tab = st.tabs(["My Policies", "Submit a Claim", "Claim History"])
    with policies_tab:
        _render_policies_tab(policies)
    with submit_tab:
        _render_submit_claim_tab(policies)
    with history_tab:
        _render_claim_history_tab(claims)