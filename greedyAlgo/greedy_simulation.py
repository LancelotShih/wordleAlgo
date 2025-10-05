import random
from greedyAlgo.greedy_wordleai import filter_words, score_word, WORDS

STATS_FILE = "greedyAlgo/wordle_stats.txt"
NUM_GAMES = 1  # Change as needed

# Generate Wordle feedback for a guess against the answer
def get_feedback(guess, answer):
    feedback = ['.'] * 5
    answer_chars = list(answer)
    # First pass: greens
    for i in range(5):
        if guess[i] == answer[i]:
            feedback[i] = 'g'
            answer_chars[i] = None  # Mark as used
    # Second pass: yellows
    for i in range(5):
        if feedback[i] == '.':
            if guess[i] in answer_chars:
                feedback[i] = 'y'
                answer_chars[answer_chars.index(guess[i])] = None
    return ''.join(feedback)

# Load stats from file
def load_stats():
    tally = {str(i): 0 for i in range(1, 7)}
    tally["failed"] = 0
    try:
        with open(STATS_FILE, "r") as f:
            for line in f:
                if ':' in line:
                    key, val = line.strip().split(':')
                    key = key.strip()
                    val = val.strip()
                    if key in tally:
                        tally[key] = int(val)
    except FileNotFoundError:
        pass
    return tally

# Save stats to file
def save_stats(tally):
    with open(STATS_FILE, "w") as f:
        f.write("# Wordle Data Collection Stats\n")
        f.write("# Format:\n")
        f.write("# guesses: count\n")
        f.write("# failed: count\n")
        for i in range(1, 7):
            f.write(f"{i}: {tally[str(i)]}\n")
        f.write(f"failed: {tally['failed']}\n")

# Simulate one game
def play_one_game(answer):
    greens = {}
    yellows = {}
    grays = {}
    candidates = WORDS[:]
    for turn in range(6):
        if not candidates:
            return None
        guess = max(candidates, key=score_word)
        feedback = get_feedback(guess, answer)
        # Update knowledge
        for pos, (letter, mark) in enumerate(zip(guess, feedback)):
            if mark == "g":
                greens[pos] = letter
            elif mark == "y":
                if pos not in yellows:
                    yellows[pos] = []
                yellows[pos].append(letter)
            else:
                required_count = (
                    list(greens.values()).count(letter) +
                    sum(letter in lst for lst in yellows.values())
                )
                grays[letter] = required_count
        candidates = filter_words(greens, yellows, grays)
        if feedback == "ggggg":
            return turn + 1
    return None

def main():
    tally = load_stats()
    num_games = NUM_GAMES
    failed_words = set()
    for i in range(num_games):
        answer = random.choice(WORDS)
        guesses = play_one_game(answer)
        if guesses is not None and 1 <= guesses <= 6:
            tally[str(guesses)] += 1
        elif guesses is None:
            tally["failed"] += 1
            failed_words.add(answer)
        # Discard runs that end before 6 guesses (already handled)
    save_stats(tally)
    print("\n--- Data Collection Results ---")
    for n in range(1, 7):
        print(f"Solved in {n} guesses: {tally[str(n)]} times | {tally[str(n)] / (sum(tally[str(n)] for n in range(1,7)) + tally['failed']) * 100:.2f}%")
    print(f"Failed: {tally['failed']} times | {tally['failed'] / (sum(tally[str(n)] for n in range(1,7)) + tally['failed']) * 100:.2f}%")
    print(f"Total games: {sum(tally[str(n)] for n in range(1,7)) + tally['failed']}")
    if failed_words:
        print("\nWords that failed in this run:")
        for word in sorted(failed_words):
            print(word)

if __name__ == "__main__":
    main()
