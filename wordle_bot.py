import requests
import sys
from collections import Counter
from typing import List, Tuple, Union


def sort_words_split(words_split: List[List[str]]) -> List[List[str]]:
    positions = tuple(map(list, zip(*words_split)))

    position_counters = []
    for pos in positions:
        counter = Counter(pos)
        total = sum(counter.values(), 0.0)
        for key in counter:
            counter[key] /= total
        position_counters.append(counter)

    def weigh_by_pos(word: List[str], weights: List[Counter]) -> int:
        result = 1
        for index, letter in enumerate(word):
            result = result * weights[index][letter]
        return result

    lengths = [len(set(word)) for word in words_split]
    length_counter = Counter(lengths)
    for key in length_counter:
        length_counter[key] /= len(lengths)

    words_weighted = [weigh_by_pos(word, position_counters) * length_counter[len(set(word))] for word in words_split]
    sorted_words_split = [item[0] for item in sorted(list(zip(words_split, words_weighted)), key=lambda x: x[1], reverse=True)]
    return sorted_words_split


def filter_words(words_split: List[List[str]], converted_result_code: List[Tuple[str, Union[str, int]]]) -> List[List[str]]:
    words_split_copy = words_split
    for letter in converted_result_code:
        if isinstance(letter[1], int) and letter[1] > 0:
            words_split_copy = [word for word in words_split_copy if letter[0] == word[letter[1] - 1]]
    for letter in converted_result_code:
        if isinstance(letter[1], int) and letter[1] < 0:
            words_split_copy = [word for word in words_split_copy if letter[0] != word[-1 * letter[1] - 1] and letter[0] in word]
        elif letter[1] == "n":
            occurences = [l[0] for l in converted_result_code if isinstance(l[1], int) and l[0] == letter[0]]
            if letter[0] in occurences:
                words_split_copy = [
                    word for word in words_split_copy if letter[0] in word and word.count(letter[0]) == len(occurences)
                ]
            else:
                words_split_copy = [word for word in words_split_copy if letter[0] not in word]
    words_split_copy = sort_words_split(words_split_copy)
    return words_split_copy


def guess_word(words_split_filtered) -> List[str]:
    return words_split_filtered[0]


def convert_result_code(word: str, result_code: str) -> List[Tuple[str, Union[str, int]]]:
    converted = []
    for count, letter in enumerate(word):
        if result_code[count] == "y":
            converted.append((letter, count + 1))
        elif result_code[count] == "e":
            converted.append((letter, -1 * (count + 1)))
        elif result_code[count] == "n":
            converted.append((letter, "n"))
    return converted


def play_automated_round(word: str, guess: str) -> str:
    return_string = [""] * 5
    further_matches = {letter: 0 for letter in set(guess)}
    for ct, letter in enumerate(guess):
        if word[ct] == letter:
            return_string[ct] = "y"
    for ct, letter in enumerate(guess):
        occurences = word.count(letter)
        exact_matches = sum([a == b for a, b in list(zip(word, guess)) if b == letter])
        if letter not in word:
            return_string[ct] = "n"
        if letter in word and word[ct] != letter:
            if occurences - exact_matches - further_matches.get(letter, 0) > 0:
                return_string[ct] = "e"
                further_matches[letter] += 1
            else:
                return_string[ct] = "n"
    return "".join(return_string)


def load_and_prepare_data() -> Tuple[List[str], List[List[str]]]:
    c = requests.get("https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt").content.decode("utf-8")
    words = c.split("\n")
    words_split = [list(word) for word in words if len(word) == 5]
    sorted_words_split = sort_words_split(words_split)
    return words, sorted_words_split


def main():
    words, sorted_words_split = load_and_prepare_data()
    if len(sys.argv) == 2:
        goal = sys.argv[1]
        assert goal in words, "Dude, pls, use an existing 5-character word"

    rounds = 1
    while True:
        print("----")
        if rounds > 6:
            print("Only 6 rounds permitted, sorry!")
            break

        print("Round number ", rounds)
        current_guess = guess_word(sorted_words_split)
        print("Current guess is: ", current_guess)
        print("Number of words left: ", len(sorted_words_split))
        if len(sys.argv) == 2:
            result_code = play_automated_round(goal, current_guess)
        else:
            result_code = input("Enter result code (green=y(es), grey=n(o), yellow=e(xists), example: eeenn): ")
            while len(result_code) != 5 or not set(result_code).issubset({"y", "n", "e"}):
                result_code = input("Result code must have 5 letters and must consist of y, n, e: ")
        if result_code == "yyyyy":
            print("You got it, congratulations!")
            print("Rounds played: ", rounds)
            break
        else:
            converted_result_code = convert_result_code(current_guess, result_code)
        sorted_words_split = filter_words(sorted_words_split, converted_result_code)
        rounds += 1


if __name__ == "__main__":
    main()
