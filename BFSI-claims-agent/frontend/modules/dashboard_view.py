from datetime import date

import streamlit as st

from modules.api_client import (
    ApiError,
    get_chat_history,
    get_policies_chat_history,
    list_my_claims,
    list_my_policies,
    send_chat_message,
    send_policies_chat_message,
    submit_claim,
)
from modules.theme import INK_NAVY, SLATE, STATUS_COLORS, accent_bar, recommendation_block

def _render_policies_tab(policies):
    if not policies:
        st.info("No policies found for your account.")
        return

    cards_area, chat_area = st.columns([3, 2], gap="large")

    with cards_area:
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

    with chat_area:
        _render_policies_chat()


def _render_submit_claim_tab(policies):
    if not policies:
        st.info("No policies found for your account -- nothing to file a claim against.")
        return

    policy_options = {f"{p['policy_id']} -- {p['sub_type']}": p["policy_id"] for p in policies}

    with st.form("submit_claim_form"):
        left, right = st.columns(2)
        with left:
            policy_label = st.selectbox("Policy", options=list(policy_options.keys()))
            claim_type = st.text_input("Claim type", max_chars=50, placeholder="e.g. Accident - Own Damage")
            incident_date = st.date_input("Incident date", max_value=date.today())
        with right:
            incident_description = st.text_area(
                "What happened?",
                height=140,
                max_chars=3000,
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
        if last_claim.get("privacy_notice"):
            st.info(last_claim["privacy_notice"])
        st.markdown(recommendation_block(last_claim["ai_recommendation"], last_claim["ai_rationale"]), unsafe_allow_html=True)


def _render_chat_box(key, send_fn, load_fn, empty_hint, placeholder, expander_title=None, height=None):
    """
    The one chat box both chats use. The question stays visible while the
    answer loads, because the user's turn is saved and shown first and the
    reply is fetched on the next rerun.

    key: unique per chat (used for session state and the form).
    send_fn: takes the question text, returns the reply text.
    load_fn: returns earlier messages from the backend, so the conversation
        reappears after logging out and back in.
    expander_title: wrap the box in an expander with this title; None = plain box.
    height: fixed height in pixels for a scrollable message area; None = grows with the conversation.
    """
    history_key = f"chat_history_{key}"
    if history_key not in st.session_state:
        try:
            st.session_state[history_key] = load_fn()
        except ApiError:
            st.session_state[history_key] = []

    container = st.expander(expander_title) if expander_title else st.container()
    with container:
        history = st.session_state[history_key]
        # A fixed-height scroll box only once there is a conversation; before that, nothing takes up space.
        messages_area = st.container(height=height) if (height and history) else st.container()

        with messages_area:
            for turn in history:
                avatar = "🧑" if turn["role"] == "user" else "🛡️"
                with st.chat_message(turn["role"], avatar=avatar):
                    st.write(turn["content"])

            if not history and empty_hint:
                st.caption(empty_hint)

            if history and history[-1]["role"] == "user":
                with st.chat_message("assistant", avatar="🛡️"):
                    with st.spinner("Thinking..."):
                        try:
                            reply = send_fn(history[-1]["content"])
                        except ApiError as exc:
                            reply = f"Sorry, I couldn't answer that: {exc.detail}"
                        except Exception as exc:
                            reply = f"Sorry, something went wrong: {exc}"
                    st.write(reply)
                st.session_state[history_key].append({"role": "assistant", "content": reply})

        # Hide Streamlit's "Press Enter to submit form" hint, which overlaps the placeholder in small boxes.
        st.markdown(
            "<style>[data-testid='InputInstructions'] { display: none; }</style>",
            unsafe_allow_html=True,
        )
        with st.form(f"chat_form_{key}", clear_on_submit=True, border=False):
            left, right = st.columns([3, 1])
            with left:
                question = st.text_input(
                    "Your question", label_visibility="collapsed", placeholder=placeholder, max_chars=1000
                )
            with right:
                asked = st.form_submit_button("Send", use_container_width=True)

        if asked and question.strip():
            st.session_state[history_key].append({"role": "user", "content": question})
            st.rerun()


def _render_claim_chat(claim):
    _render_chat_box(
        key=claim["claim_id"],
        send_fn=lambda question: send_chat_message(claim["claim_id"], question),
        load_fn=lambda: get_chat_history(claim["claim_id"]),
        empty_hint="Ask why this claim got its recommendation, or what it means for you.",
        placeholder="e.g. Why was this claim flagged?",
        expander_title="Ask about this claim",
    )


def _render_policies_chat():
    with st.container(border=True):
        st.markdown(accent_bar(INK_NAVY), unsafe_allow_html=True)
        st.markdown("**💬 Ask about your policies**")
        st.caption("Ask what's covered, exclusions, waiting periods, dates or premium -- for any of your policies.")
        _render_chat_box(
            key="policies",
            send_fn=send_policies_chat_message,
            load_fn=get_policies_chat_history,
            empty_hint=None,
            placeholder="Ask anything...",
            height=350,
        )


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
            for key in [k for k in st.session_state if k.startswith("chat_history_")]:
                del st.session_state[key]
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
            "- Add the claimed amount if you know it\n"
            "- Never type ID, card, bank or password details -- we hide them anyway"
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