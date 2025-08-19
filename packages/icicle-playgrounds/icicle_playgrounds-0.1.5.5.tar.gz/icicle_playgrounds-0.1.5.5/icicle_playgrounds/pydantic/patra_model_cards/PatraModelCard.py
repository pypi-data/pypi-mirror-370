from pydantic import BaseModel
from .PatraAIModel import PatraAIModel
from .PatraBiasAnalysis import PatraBiasAnalysis
from .PatraXAIAnalysis import PatraXAIAnalysis

class PatraModelCard(BaseModel):
    """A model card containing metadata and analysis information for a PATRA AI model.

    This class represents a comprehensive model card that includes information about the AI model,
    its creator, descriptions, and optional analysis results.

    Attributes:
        ai_model (PatraAIModel): The AI model details and metrics.
        author (str): Name of the model card author.
        bias_analysis (PatraBiasAnalysis | None): Optional bias analysis results.
        categories (str): Model categories or domains.
        external_id (str): Unique external identifier for the model card.
        full_description (str): Detailed description of the model.
        input_data (str): Description of expected input data format.
        input_type (str): Type of input the model accepts.
        keywords (str): Relevant keywords for model search.
        name (str): Name of the model card.
        output_data (str): Description of model output format.
        short_description (str): Brief summary of the model.
        version (str): Version identifier of the model card.
        xai_analysis (PatraXAIAnalysis | None): Optional explainable AI analysis results.

    Example:
        >>> model_card = PatraModelCard(
        ...     ai_model=ai_model,
        ...     author="John Doe",
        ...     categories="Computer Vision",
        ...     external_id="MC123",
        ...     name="Image Classification Model",
        ...     version="1.0.0",
        ...     # ... other fields ...
        ... )
    """

    ai_model: PatraAIModel
    author: str
    bias_analysis: PatraBiasAnalysis | None = None
    categories: str
    external_id: str
    full_description: str
    input_data: str
    input_type: str
    keywords: str
    name: str
    output_data: str
    short_description: str
    version: str
    xai_analysis: PatraXAIAnalysis | None = None