from typing import List
import nltk
from nltk import sent_tokenize
from langchain_text_splitters.base import TextSplitter

nltk.download('punkt')

class SentenceSplitter(TextSplitter):
    def split_text(self, text: str) -> List[str]:
        return sent_tokenize(text)
