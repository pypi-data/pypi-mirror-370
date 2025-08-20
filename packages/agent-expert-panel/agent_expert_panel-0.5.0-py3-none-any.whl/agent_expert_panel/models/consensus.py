from pydantic import BaseModel


class Consensus(BaseModel):
    """
    Consensus is a Pydantic model that contains information about the consensus of the discussion.
    """

    consensus_reached: bool
    summary: str
    participants: list[str]

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "consensus_reached": True,
                    "summary": "The participants reached a consensus.",
                    "participants": ["John", "Jane"],
                }
            ]
        },
    }
