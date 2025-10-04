# Wordle Assistant
# Usage: python wordle_helper.py

# Load word list (adjust file path if needed)
with open("wordle_targets.txt", "r") as f:
    WORDS = [w.strip().lower() for w in f.readlines() if len(w.strip()) == 5]

# Calculate letter frequencies in WORDS
from collections import Counter
letter_counts = Counter()
for word in WORDS:
    letter_counts.update(set(word))  # count each letter once per word

# Score a word by summing its unique letter frequencies
def score_word(word):
    return sum(letter_counts[c] for c in set(word))


def filter_words(greens: dict, yellows: dict, grays: dict):
    candidates = []
    for word in WORDS:
        valid = True

        # Green checks
        for pos, letter in greens.items():
            if word[pos] != letter:
                valid = False
                break

        if not valid:
            continue

        # Yellow checks
        for pos, letters in yellows.items():
            for letter in letters:
                if letter not in word or word[pos] == letter:
                    valid = False
                    break
            if not valid:
                break

        if not valid:
            continue

        # Gray checks
        for letter, max_allowed in grays.items():
            if word.count(letter) > max_allowed:
                valid = False
                break

        if valid:
            candidates.append(word)

    return candidates


def main():
    greens = {}          # {pos: letter}
    yellows = {}         # {pos: [letters]}
    grays = {}           # {letter: max_allowed}

    candidates = WORDS[:]

    print("Wordle (i'm Ass)istant")
    print("Enter your guess and feedback each round.")
    print("Feedback format: g = green, y = yellow, . = gray: .g.gy for green in pos 2 and 4 and yellow in pos 5")
    print("Example: guess = crane, feedback = g..y. (c=green, a=yellow, rest gray)\n")

    while True:
        print(f"\nRemaining candidates: {len(candidates)}")
        if len(candidates) <= 50:
            print(candidates)

            # Recommend best guesses based on letter frequency
            if candidates:
                ranked = sorted(candidates, key=score_word, reverse=True)
                print("\nTop recommended guesses:")
                for w in ranked[:5]:
                    print(f"  {w} (score: {score_word(w)})")
        elif len(candidates) > 50:
            print("Candidates are too many to display. Need more information, try one of the following:")

        guess = input("\nEnter your guess (or 'quit'): ").strip().lower()
        if guess == "quit":
            break
        if len(guess) != 5 or guess not in WORDS:
            print("Invalid guess. Must be a 5-letter word from the list.")
            continue

        feedback = input("Enter feedback (g/y/.): ").strip().lower()
        if len(feedback) != 5 or not all(c in "gy." for c in feedback):
            print("Invalid feedback. Must be 5 chars using g/y/.")
            continue

        # Update knowledge
        for pos, (letter, mark) in enumerate(zip(guess, feedback)):
            if mark == "g":  # green
                greens[pos] = letter
            elif mark == "y":  # yellow
                if pos not in yellows:
                    yellows[pos] = []
                yellows[pos].append(letter)
            else:  # gray
                # Count how many times this letter is "needed" elsewhere
                required_count = (
                    list(greens.values()).count(letter) +
                    sum(letter in lst for lst in yellows.values())
                )
                # Store max allowed occurrences
                grays[letter] = required_count

        # Re-filter candidates
        candidates = filter_words(greens, yellows, grays)

        if len(candidates) == 1:
            print(f"\n The answer must be: {candidates[0]}")
            break
        elif not candidates:
            print("\n No candidates left. Check your input.")
            break


if __name__ == "__main__":
    main()
