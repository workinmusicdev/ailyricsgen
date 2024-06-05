from pydantic import BaseModel, Field


class GenerateMusicRequest(BaseModel):
    lyrics: str = Field(..., description="Les paroles de la chanson à générer")
    title: str = Field(..., description="Le titre de la chanson")
    style: str = Field(..., description="Le style musical de la chanson")
