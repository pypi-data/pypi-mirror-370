from typing import List
from nestful import API
from sentence_transformers import SentenceTransformer, util

import string
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def split_camel_case(text: str) -> List[str]:
    words: List[str] = []
    current_word = ""

    for i, char in enumerate(text):
        if char.isupper() and i != 0:
            words.append(current_word)
            current_word = char
        else:
            current_word += char

    words.append(current_word)
    return words


def split_variable_name(name: str) -> List[str]:
    name_without_whitespace = name.replace(" ", "")
    name_split_with_underscore = name_without_whitespace.split("_")

    new_split: List[str] = []
    for item in name_split_with_underscore:
        de_camel_words = split_camel_case(item)
        new_split.extend(de_camel_words)

    return new_split


class Cosim:
    def __init__(self) -> None:
        print("Loading Sentence Transformer")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Loading NLTK")
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        import nltk

        nltk.download("stopwords")
        nltk.download("punkt_tab")

        self.word_tokenize = word_tokenize
        self.stop_words = set(stopwords.words("english"))

    def process_text(self, text: str) -> str:
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))

        text_tokens = self.word_tokenize(text)
        filtered_tokens = [w for w in text_tokens if w not in self.stop_words]

        return " ".join(filtered_tokens)

    def construct_description(
        self, var: str, description: str, api: API
    ) -> str:
        return self.process_text(
            f"{var} {description} {api.name} {api.description}"
        )

    def cosine_similarity(
        self, t1: str, t2: str, preprocess_text: bool = False
    ) -> float:
        if preprocess_text is True:
            t1 = " ".join(split_variable_name(t1))
            t1 = self.process_text(t1)

            t2 = " ".join(split_variable_name(t2))
            t2 = self.process_text(t2)

        t1 = self.model.encode(t1)
        t2 = self.model.encode(t2)

        try:
            cos_sim: float = round(
                util.dot_score(t1, t2)[0].cpu().tolist()[0], 2
            )
            return (1 + cos_sim) / 2.0

        except Exception as e:
            print(e)
            return 0.0
