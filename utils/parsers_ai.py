from typing import List, Dict
from langchain.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel, Field

class MusicLyrics(BaseModel):
    title: str = Field(..., description="Titre suggéré automatiquement basé sur le contenu du texte")
    style: str = Field(..., description="Style de la musique")
    auto_style: str = Field(..., description="courte phrase suggérant la mélodie  automatiquement et se basant au contenu du texte")
    lyrics: Dict[str, str] = Field(..., description="Paroles de la musique, organisées par sections comme Couplet, Refrain, et Pont")

    def to_dict(self):
        return {"title": self.title, "style": self.style, "auto_style": self.auto_style, "lyrics": self.lyrics}

# Créer le parser Pydantic pour les paroles de la musique
music_lyrics_parser = PydanticOutputParser(pydantic_object=MusicLyrics)
