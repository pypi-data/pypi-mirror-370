from pydantic import BaseModel

class PatraXAIAnalysis(BaseModel):
    """Represents explainable AI (XAI) analysis results for a PATRA AI model.

    This class stores the results of explainability analysis performed on an AI model,
    providing insights into model decision-making processes.

    Attributes:
        external_id (str): Unique identifier for the XAI analysis.
        name (str): Name or description of the XAI analysis performed.

    Example:
        >>> xai_analysis = PatraXAIAnalysis(
        ...     external_id="XAI123",
        ...     name="LIME Analysis Results"
        ... )
    """

    external_id: str
    name: str