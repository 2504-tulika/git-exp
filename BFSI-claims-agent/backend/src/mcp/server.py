"""
MCP server: exposes policy_coverage_tool, claim_history_tool, and
fraud_risk_tool to the agent over stdio, via the MCP Python SDK
(FastMCP).

Run standalone for local testing/inspection:
    python -m src.mcp.server
In the real app, claims_agent.py spawns this as a subprocess exactly
once, at FastAPI startup (see claims_agent.warm_up()), and keeps that one
session open for the app's whole lifetime -- not respawned per claim.

warm_up() below is what makes that startup worthwhile: it forces the
embedding model to load and the ChromaDB collection to open right now,
during server boot, instead of on whichever tool call happens to be
first (which would otherwise mean the very first claim submitted eats a
~30-40s delay -- the delay we're trying to move to app startup instead).
"""

from datetime import date
from typing import Optional

from mcp.server.fastmcp import FastMCP

from src.mcp.tools.claim_history_tool import get_claim_history
from src.mcp.tools.fraud_risk_tool import assess_fraud_risk
from src.mcp.tools.policy_coverage_tool import check_policy_coverage
from src.rag.vector_store import get_collection
from src.utils.logger import get_logger

logger = get_logger(__name__)

mcp = FastMCP("claims-processing")


@mcp.tool()
def check_coverage(
    policy_id: str,
    customer_id: str,
    claim_type: str,
    incident_description: str,
    incident_date: str,
) -> dict:
    """
    Check whether a claim is covered under a specific policy: confirms
    the customer actually holds the policy, whether the incident date
    falls inside the policy's active coverage window, and retrieves the
    specific policy clauses most relevant to this claim type and
    description.

    incident_date must be an ISO date string, e.g. "2026-03-15".
    """
    parsed_incident_date = date.fromisoformat(incident_date)
    result = check_policy_coverage(
        policy_id, customer_id, claim_type, incident_description, parsed_incident_date
    )
    return result


@mcp.tool()
def get_claims(customer_id: str, policy_id: Optional[str] = None) -> dict:
    """
    Look up a customer's claim history: every past claim across their
    policies, plus whether any were flagged as fraud risk before. Pass
    policy_id too to also get claims scoped to just that one policy.
    """
    result = get_claim_history(customer_id, policy_id=policy_id)
    return result


@mcp.tool()
def check_fraud_risk(
    customer_id: str,
    policy_id: str,
    incident_date: str,
    intimation_date: str,
    claim_amount: Optional[str] = None,
) -> dict:
    """
    Check this claim for fraud-risk signals: a prior fraud flag on this
    customer, an unusually high total claim count, other claims on this
    same policy clustered close in time to this one, late intimation
    (reported well after the incident), or a claim amount far above this
    customer's historical average. Returns signals as facts for you to
    weigh -- never a fraud verdict.

    incident_date and intimation_date must be ISO date strings, e.g.
    "2026-03-15". claim_amount is text, e.g. "Rs. 45,000" -- pass it if
    the claim states one, omit it if not yet known.
    """
    parsed_incident_date = date.fromisoformat(incident_date)
    parsed_intimation_date = date.fromisoformat(intimation_date)
    result = assess_fraud_risk(
        customer_id,
        policy_id,
        parsed_incident_date,
        parsed_intimation_date,
        claim_amount=claim_amount,
        # exclude_claim_id is intentionally not an agent-facing parameter:
        # it exists so an already-stored claim can exclude itself from
        # its own clustering check, which only matters for re-evaluating
        # an existing claim, not for a brand-new submission -- and the
        # agent should never be able to choose which claims get excluded
        # from its own fraud check.
        exclude_claim_id=None,
    )
    return result


def warm_up():
    """
    Force the one-time, expensive costs (embedding model load, ChromaDB
    collection open) to happen right now, during server startup, rather
    than on whichever tool call happens to be first. Doesn't touch
    MySQL -- each tool already opens its own short-lived DB session per
    call, which is fast; the embedding model load is the actual slow
    part worth moving to startup.
    """
    get_collection()
    logger.info("MCP server warm-up complete (embedding model + vector store loaded)")


if __name__ == "__main__":
    warm_up()
    mcp.run()
