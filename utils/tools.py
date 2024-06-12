def format_lyrics(lyrics_dict):
    # Initialize an empty string to store the formatted lyrics
    formatted_lyrics = ""

    # Extract the refrain lyrics to append after each section
    refrain_lyrics = lyrics_dict.get("Refrain", "")

    # Get the keys of the dictionary as a list
    keys = list(lyrics_dict.keys())

    # Iterate through the dictionary items
    for i, section in enumerate(keys):
        # Add the section title
        formatted_lyrics += section + "\n"

        # Split the lyrics into individual lines
        lines = lyrics_dict[section].split('\n')

        # Add each line to the formatted lyrics
        for line in lines:
            formatted_lyrics += line + "\n"

        # Add a newline for separation between sections
        formatted_lyrics += "\n"

        # Add the Refrain lyrics after each section except the Refrain itself
        if section != "Refrain" and (i == len(keys) - 1 or keys[i + 1] != "Refrain"):
            formatted_lyrics += "Refrain\n"
            formatted_lyrics += refrain_lyrics + "\n\n"

    return formatted_lyrics.strip()


def format_lyrics_single_refrain(lyrics_dict):
    # Initialize an empty string to store the formatted lyrics
    formatted_lyrics = ""

    # Extract the refrain lyrics to append at the end
    refrain_lyrics = lyrics_dict.get("Refrain", "")

    # Iterate through the dictionary items, excluding the refrain
    for section, lyrics in lyrics_dict.items():
        if section != "Refrain":
            # Add the section title
            formatted_lyrics += section + "\n"

            # Split the lyrics into individual lines
            lines = lyrics.split('\n')

            # Add each line to the formatted lyrics
            for line in lines:
                formatted_lyrics += line + "\n"

            # Add a newline for separation between sections
            formatted_lyrics += "\n"

    # Add the refrain once at the end
    if refrain_lyrics:
        formatted_lyrics += "Refrain\n"
        formatted_lyrics += refrain_lyrics + "\n"

    return formatted_lyrics.strip()

