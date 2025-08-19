from pydantic import BaseModel

class PatraBiasAnalysis(BaseModel):
    """Represents bias analysis results for a PATRA AI model.

    This class stores the results of bias analysis performed on an AI model,
    helping identify and document potential biases in model behavior.

    Attributes:
        external_id (str): Unique identifier for the bias analysis.
        name (str): Name or description of the bias analysis performed.

    Example:
        >>> bias_analysis = PatraBiasAnalysis(
        ...     external_id="BA123",
        ...     name="Gender Bias Analysis"
        ... )
    """

    external_id: str
    name: str