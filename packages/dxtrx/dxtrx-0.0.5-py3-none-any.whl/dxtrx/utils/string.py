import re
import unicodedata

def normalize_string(input_string: str) -> str:
    """
        Normalize the input string by converting it to lowercase, replacing spaces with underscores,
        and replacing any non-printable characters or accented vowels with their corresponding
        non-accented vowels.

        Parameters:
        ----------
        input_string : str
            The string to be normalized.

        Returns:
        -------
        str
            The normalized string in lowercase, snake_case format, with non-printable characters
            replaced by their corresponding non-accented vowels.

        Examples:
        --------
        >>> normalize_string("Hóla Múndó!")
        'hola_mundo'
        """

    normalized_string = (" ".join(input_string.split())
                         .lower()
                         .strip()
                         .replace("/", "")
                         .replace("(", "")
                         .replace(")", ""))

    # Remove diacritics (accents) by decomposing characters and filtering out accents
    normalized_string = ''.join(
        char for char in unicodedata.normalize('NFD', normalized_string)
        if unicodedata.category(char) != 'Mn'
    )

    # Replace non-printable characters with corresponding non-accented vowels
    # Define a mapping of non-accented vowels to replace any non-printable characters
    vowel_mapping = {
        'á': 'a',
        'é': 'e',
        'í': 'i',
        'ó': 'o',
        'ú': 'u',
        'à': 'a',
        'è': 'e',
        'ì': 'i',
        'ò': 'o',
        'ù': 'u',
        'ä': 'a',
        'ë': 'e',
        'ï': 'i',
        'ö': 'o',
        'ü': 'u',
        'â': 'a',
        'ê': 'e',
        'î': 'i',
        'ô': 'o',
        'û': 'u',
        'ã': 'a',
        'õ': 'o',
        'å': 'a',
        'æ': 'ae',
        'œ': 'oe',
        'ø': 'o'
    }

    # Replace non-printable characters with their corresponding non-accented vowels
    normalized_string = ''.join(
        vowel_mapping.get(char, char) if not char.isprintable() else char
        for char in normalized_string
    )

    # Remove any remaining non-printable characters (if any)
    normalized_string = re.sub(r'[^\x20-\x7E]', '', normalized_string)

    # Replace spaces with underscores to achieve snake_case
    normalized_string = normalized_string.replace(' ', '_')

    return normalized_string