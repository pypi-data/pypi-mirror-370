# typegpt_moderation/models.py

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class ModerationResultItem(BaseModel):
    """
    Represents the moderation result for a single request.
    """
    flagged: bool = Field(..., description="True if the content was flagged as unsafe, False otherwise.")
    moderation_type: str = Field(..., description="Indicates which modalities were moderated (e.g., 'text_and_image').")
    categories: Dict[str, bool] = Field(..., description="A dictionary of moderation categories and whether they were violated.")
    category_scores: Dict[str, float] = Field(..., description="A dictionary of scores for each moderation category.")
    reason: Optional[str] = Field(None, description="A brief, factual reason for the moderation decision if flagged.")
    transcribed_text: Optional[str] = Field(None, description="The text transcribed from the audio, if provided.")

class ModerationResponse(BaseModel):
    """
    Represents the full response from the moderation API endpoint.
    """
    id: str
    model: str
    results: List[ModerationResultItem]