import random
from entropy_wordleai import WORDS, get_feedback, select_best_guess, filter_words

STATS_FILE = "entropyAlgo/wordle_stats.txt"
FAILED_FILE = "entropyAlgo/failed_words_entropy.txt"

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

def save_stats(tally):
    with open(STATS_FILE, "w") as f:
        f.write("# Wordle Data Collection Stats\n")
        f.write("# Format:\n")
        f.write("# guesses: count\n")
        f.write("# failed: count\n")
        for i in range(1, 7):
            f.write(f"{i}: {tally[str(i)]}\n")
        f.write(f"failed: {tally['failed']}\n")

def save_failed_words(failed_words):
    with open(FAILED_FILE, "w") as f:
        for word in sorted(failed_words):
            f.write(word + "\n")

def play_one_game(answer):
    candidates = WORDS[:]
    for turn in range(6):
        if not candidates:
            print(f"No candidates left on turn {turn+1} for answer {answer}")
            return None
        # First turn: use entropy over all WORDS, then restrict to candidates
        if turn == 0:
            guess = select_best_guess(WORDS)
        else:
            guess = select_best_guess(candidates)
        print(f"Turn {turn+1}: Guess = {guess}, Candidates left = {len(candidates)}")
        feedback = get_feedback(guess, answer)
        print(f"Feedback: {feedback}")
        candidates = filter_words(candidates, guess, feedback)
        print(f"Candidates after filtering: {len(candidates)}")
        print(f"Candidates: {candidates}")
        if answer in candidates:
            print(f"Answer {answer} is still in candidate list.")
        else:
            print(f"Answer {answer} has been filtered out!")
        if len(candidates) == 1:
            final_guess = candidates[0]
            print(f"Candidate list shrunk to 1: {final_guess}")
            final_feedback = get_feedback(final_guess, answer)
            print(f"Final guess: {final_guess}, Answer: {answer}, Feedback: {final_feedback}")
            if final_feedback == "ggggg":
                print(f"Solved {answer} in {turn+2} guesses!")
                return turn + 2
            else:
                print(f"Failed to solve {answer}. Final guess {final_guess} did not match.")
                return None
        if feedback == "ggggg":
            print(f"Solved {answer} in {turn+1} guesses!")
            return turn + 1
    print(f"Failed to solve {answer} in 6 guesses.")
    return None

def main():
    tally = load_stats()
    num_games = 900  # Change as needed
    failed_words = set()
    for i in range(num_games):
        answer = random.choice(WORDS)
        guesses = play_one_game(answer)
        if guesses is not None and 1 <= guesses <= 6:
            tally[str(guesses)] += 1
        elif guesses is None:
            tally["failed"] += 1
            failed_words.add(answer)
    save_stats(tally)
    save_failed_words(failed_words)
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
