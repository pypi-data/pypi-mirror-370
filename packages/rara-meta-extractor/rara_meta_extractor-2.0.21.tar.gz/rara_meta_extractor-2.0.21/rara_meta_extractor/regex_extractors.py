import regex as re
from typing import List


class ISBNRegexExtractor:
    """ Regex-based ISBN extractor.
    """
    def __init__(self):
        self.pattern = re.compile(r"(?<=\D|^)(\d-?\s*){13}(?=\D|[^-]|$)")

    def _clean(self, isbn: str) -> str:
        """ Cleans extracted ISBNs from "-" and from whitespaces.

        Parameters
        -----------
        isbn: str
            Extracted raw ISBN number which might contain additional
            punctuation characters.

        Returns
        -----------
        str:
            Cleaned ISBN number.
        """
        isbn = re.sub("-", "", isbn)
        isbn = isbn.strip()
        return isbn

    def extract(self, text: str) -> List[str]:
        """ Extracts ISBN numbers from the input textself.

        Parameters
        -----------
        text: str
            Text from where to extract the numbers.

        Returns
        ----------
        List[str]:
            Extracted and cleaned ISBN numbers.
        """
        isbn_matches = re.finditer(self.pattern, text)
        isbns = [self._clean(match.group()) for match in isbn_matches]
        return isbns
