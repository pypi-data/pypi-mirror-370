from pydantic import BaseModel, Field, ConfigDict

class PatraAIModel(BaseModel):
    """Represents an AI model in the PATRA system with its metadata and metrics.

    This class contains detailed information about an AI model, including its architecture,
    training parameters, performance metrics, and deployment details.

    Attributes:
        backbone (str | None): Neural network backbone architecture. Defaults to None.
        batch_size (int | None): Training batch size. Defaults to None.
        epochs (int | None): Number of training epochs. Defaults to None.
        input_shape (str | None): Expected input tensor shape. Defaults to None.
        learning_rate (float | None): Training learning rate. Defaults to None.
        optimizer (str | None): Optimization algorithm used. Defaults to None.
        precision (float | None): Model precision metric. Defaults to None.
        recall (float | None): Model recall metric. Defaults to None.
        description (str): Detailed description of the model.
        foundational_model (str | None): Base model used, if any. Defaults to None.
        framework (str): ML framework used (e.g., PyTorch, TensorFlow).
        inference_labels (str): Labels or classes for inference.
        license (str): Model license information.
        location (str): Model storage or deployment location.
        model_id (str): Unique identifier for the model.
        model_type (str): Type or category of the model.
        name (str): Model name.
        owner (str): Model owner or organization.
        test_accuracy (float): Accuracy on test dataset.
        version (str): Model version identifier.

    Example:
        >>> model = PatraAIModel(
        ...     name="ResNet50 Classifier",
        ...     model_id="M123",
        ...     framework="PyTorch",
        ...     backbone="ResNet50",
        ...     test_accuracy=0.95,
        ...     # ... other fields ...
        ... )
    """

    model_config = ConfigDict(populate_by_name=True)

    backbone: str | None = Field(default=None, alias="Backbone")
    batch_size: int | None = Field(default=None, alias="Batch_Size")
    epochs: int | None = Field(default=None, alias="Epochs")
    input_shape: str | None = Field(default=None, alias="Input_Shape")
    learning_rate: float | None = Field(default=None, alias="Learning_Rate")
    optimizer: str | None = Field(default=None, alias="Optimizer")
    precision: float | None = Field(default=None, alias="Precision")
    recall: float | None = Field(default=None, alias="Recall")
    description: str
    foundational_model: str | None = None
    framework: str
    inference_labels: str
    license: str
    location: str
    model_id: str
    model_type: str
    name: str
    owner: str
    test_accuracy: float
    version: str