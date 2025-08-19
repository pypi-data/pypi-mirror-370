from faker import Faker
from nestful.hypothesis_generator.cosim import Cosim
from typing import Optional, List, Any, Callable


class FakerGenerator:
    forbidden_methods = [
        "add_provider",
        "seed",
        "binary",
        "get_providers",
        "cache_pattern",
        "set_arguments",
        "del_arguments",
        "xml",
        "enum",
        "factories",
        "format",
        "generator_attrs",
        "get_arguments",
        "set_formatter",
        "get_formatter",
        "image",
        "parse",
        "provider",
        "seed_locale",
    ]

    def __init__(self) -> None:
        self.faker = Faker()
        self.mapper = Cosim()

        all_faker_methods = [
            getattr(self.faker, item)
            for item in dir(self.faker)
            if not item.startswith("_") and item not in self.forbidden_methods
        ]

        self._methods = [item for item in all_faker_methods if callable(item)]

    @property
    def methods(self) -> List[Callable[..., Any]]:
        return self._methods

    def get_closest_method(
        self, name: str, threshold: float = 0.8
    ) -> Optional[Callable[..., Any]]:
        candidates = {func.__name__: func for func in self.methods}

        cosine_similarities = [
            (key, self.mapper.cosine_similarity(key, name))
            for key in candidates
        ]

        cosine_similarities.sort(key=lambda x: x[1], reverse=True)
        best_match = cosine_similarities[0]

        if best_match[1] >= threshold:
            return candidates[best_match[0]]

        return None
