import os
import platform
import requests


OS_SYSTEM: str = platform.system()


def clean_terminal():
    match OS_SYSTEM:
        case "Windows":
            os.system("cls")
        case _:
            os.system("clear")


def download_pt_br_words() -> list:
    """
    Downloads a list of Brazilian Portuguese words from a given URL and returns them as a list.

    Returns:
        list: A list containing Brazilian Portuguese words.

    Raises:
        requests.exceptions.RequestException: If there is an error while making the HTTP request.

    Example:
        >>> words_list = download_pt_br_words()
        >>> print(words_list[:10])  # Print the first 10 words in the list
        ['abacate', 'abacateiro', 'abacaxi', 'abade', 'abadessa', 'abadia', 'abaixo']
    """

    link: str = "https://www.ime.usp.br/~pf/dicios/br-utf8.txt"
    response: requests.Response = None
    words_list: list[str] = None

    try:
        print("Downloading pt-br words ...")
        response = requests.get(link)
        response.raise_for_status()
        print("All pt-br words downloaded")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        return []

    words_list = response.text.splitlines()
    return words_list


def remove_repetitive_ngrams(ngrams: list[str]) -> list[str]:
    """
    Removes repetitive n-grams from a list of n-grams.

    Parameters:
        ngrams (list[str]): A list of n-grams, where each n-gram is represented as a string.

    Returns:
        list[str]: A new list containing the n-grams with duplicates removed.

    Example:
        ngrams = ["ba", "an", "na", "an", "na"]
        result = remove_repetitive_ngrams(ngrams)
        print(result)  # Output: ["ba"]
    """
    unique_ngrams = []
    seen_ngrams = set()

    for ngram in ngrams:
        if ngrams.count(ngram) == 1 and ngram not in seen_ngrams:
            unique_ngrams.append(ngram)
            seen_ngrams.add(ngram)

    return unique_ngrams


def ngrams_generator(string: str, n: int = 2) -> list[str]:
    """
    Generates n-grams from a given string.

    Parameters:
        string (str): The input string from which n-grams will be generated.
        n (int, optional): The size of the n-grams to be generated (default is 2).

    Returns:
        list[str]: A list containing the n-grams generated from the input string.

    Example:
        string = "banana"
        ngrams = ngrams_generator(string, 2)
        print(ngrams)  # Output: ["ba", "an", "na", "an", "na"]

        ngrams = ngrams_generator(string, 3)
        print(ngrams)  # Output: ["ban", "ana", "nan", "ana"]
    """
    ngrams = [string[i : i + n] for i in range(len(string) - n + 1)]
    return ngrams


class SyntaxSimilarity:
    @property
    def n(self) -> int:
        return self._n

    @n.setter
    def n(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("")
        self._n = value

    @property
    def words(self) -> dict:
        return self._words

    def _routine(self, word):
        ngrams = ngrams_generator(string=word, n=self.n)
        ngrams_without_repetitive_elements = remove_repetitive_ngrams(ngrams=ngrams)

        return {
            "ngrams": ngrams,
            "without_repetitive_ngrams": ngrams_without_repetitive_elements,
            "ngrams_size": len(ngrams),
            "B": len(ngrams_without_repetitive_elements),
        }

    def __init__(self, words: list[str], n: int = 2) -> None:
        self._n: int = None
        self._words: list[str] = None
        self._A = None

        if not isinstance(words, list):
            raise ValueError("")

        for word in words:
            if not isinstance(word, str):
                raise ValueError("")

        if not isinstance(n, int):
            raise ValueError("")

        self.n = n

        print("Running word routine ...")
        self._words = {word: self._routine(word=word) for word in words}
        print("Finish word routine")

        print("Ready to start")

    def edit_distance(self, A: int, B: int, C: int) -> float:
        return 2 * C / (A + B)

    def pt_br_spell_checker(self, input_word: str) -> tuple[str, float]:
        result: dict[str, float] = None
        B: int = None
        C: int = None
        ngrams_input_word: list[str] = None
        ngrams_input_word_without_repetitive_elements: list[str] = None
        result: dict[str, float] = {}

        ngrams_input_word = ngrams_generator(string=input_word)
        ngrams_input_word_without_repetitive_elements = remove_repetitive_ngrams(
            ngrams=ngrams_input_word
        )

        A = len(ngrams_input_word_without_repetitive_elements)

        for word in self.words.keys():
            B = self.words[word]["B"]
            C = len(
                set(ngrams_input_word_without_repetitive_elements)
                & set(self.words[word]["without_repetitive_ngrams"])
            )
            edit_distance = self.edit_distance(A, B, C)
            result[word] = edit_distance

        key_best_value = max(result, key=result.get)
        best_value = result[key_best_value]

        return key_best_value, best_value


if __name__ == "__main__":
    word: str = None
    words: list[str] = None
    syntax_similarity: SyntaxSimilarity = None

    clean_terminal()

    words = download_pt_br_words()
    if not words:
        print("Failed")

    syntax_similarity = SyntaxSimilarity(words=words)
    clean_terminal()

    try:
        while True:
            input_word = input("Write pt-br word: ")
            correct_word, probability = syntax_similarity.pt_br_spell_checker(
                input_word=input_word
            )
            if not probability == 1:
                print(f"\nCorrect Word: {correct_word}")
                print(f"Edit Distance: {round(probability, 2)}\n")
    except KeyboardInterrupt:
        # Handle Ctrl + C here (code execution will reach here when Ctrl + C is pressed)
        print("\nExiting the program due to user interruption (Ctrl + C).")
