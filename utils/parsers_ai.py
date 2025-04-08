from typing import Dict, List, Optional
from pydantic.v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser


class LyricsSection(BaseModel):
    lines: List[str] = Field(..., description="Lignes bilingues pour cette section.")

class LyricsStructure(BaseModel):
    introduction: LyricsSection
    refrain_1: LyricsSection
    couplet: LyricsSection
    refrain_2: LyricsSection
    mini_dialogue: Optional[LyricsSection] = None
    outro: Optional[LyricsSection] = None

class PedagogicalSheet(BaseModel):
    language: str
    cecrl_level: str
    theme: str
    context: str
    objective: str
    target_vocabulary: List[str]
    grammar_structures: List[str]
    skills: List[str]

class MusicLyrics(BaseModel):
    title: str
    style: str
    auto_style: str
    lyrics: LyricsStructure
    pedagogy: PedagogicalSheet

    def to_dict(self):
        return {
            "title": self.title,
            "style": self.style,
            "auto_style": self.auto_style,
            "lyrics": self.lyrics.dict(),
            "pedagogy": self.pedagogy.dict()
        }

# Le parser principal
music_lyrics_parser = PydanticOutputParser(pydantic_object=MusicLyrics)


# from typing import List, Dict
# from langchain.output_parsers import PydanticOutputParser
# from pydantic.v1 import BaseModel, Field


# class MusicLyrics(BaseModel):
#     title: str = Field(..., description="Titre suggéré automatiquement basé sur le contenu du texte")
#     style: str = Field(..., description="Style de la musique")
#     auto_style: str = Field(..., description="courte phrase suggérant la mélodie  automatiquement et se basant au contenu du texte")
#     lyrics: dict[str,str] = Field(..., description="Paroles de la musique, organisées par sections comme Couplet, Refrain, et Pont")

#     def to_dict(self):
#         return {"title": self.title, "style": self.style, "auto_style": self.auto_style, "lyrics": self.lyrics}

# class Lyrics(BaseModel):
#     lyrics_without_formule: dict[str,str]= Field(..., description="Paroles de la musique,organisées par sections comme Couplet, Refrain, et Pont,  ")
#     other:str=Field(...,description="Tout ce qui reste")
#     def to_dict(self):
#         return { "lyrics_without_formule": self.lyrics_without_formule}
# # Créer le parser Pydantic pour les paroles de la musique
# music_lyrics_parser = PydanticOutputParser(pydantic_object=MusicLyrics)
# lyrics_parser = PydanticOutputParser(pydantic_object=Lyrics)
