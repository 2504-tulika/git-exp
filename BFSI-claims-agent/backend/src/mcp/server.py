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
    parsed_incident_date = date.fromisoformat(incident_date)
    parsed_intimation_date = date.fromisoformat(intimation_date)
    result = assess_fraud_risk(
        customer_id,
        policy_id,
        parsed_incident_date,
        parsed_intimation_date,
        claim_amount=claim_amount,
        exclude_claim_id=None,
    )
    return result


def warm_up():
    get_collection()
    logger.info("MCP server warm-up complete (embedding model + vector store loaded)")


if __name__ == "__main__":
    warm_up()
    mcp.run()
