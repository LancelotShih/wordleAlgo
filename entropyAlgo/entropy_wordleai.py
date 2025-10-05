# Entropy-based Wordle AI (Knuth-style minimax)
# Uses entropy to select guesses that maximize information gain

from collections import Counter, defaultdict
import math

with open("wordle_targets.txt", "r") as f:
    WORDS = [w.strip().lower() for w in f.readlines() if len(w.strip()) == 5]

# Generate Wordle feedback for a guess against the answer
def get_feedback(guess, answer):
    feedback = ['.'] * 5
    answer_chars = list(answer)
    guess_chars = list(guess)
    # First pass: greens
    for i in range(5):
        if guess_chars[i] == answer_chars[i]:
            feedback[i] = 'g'
            answer_chars[i] = None
            guess_chars[i] = None
    # Second pass: yellows
    for i in range(5):
        if guess_chars[i] is not None and guess_chars[i] in answer_chars:
            feedback[i] = 'y'
            answer_index = answer_chars.index(guess_chars[i])
            answer_chars[answer_index] = None
    return ''.join(feedback)

# Calculate entropy for a guess given current candidates
def entropy_for_guess(guess, candidates):
    pattern_counts = defaultdict(int)
    for answer in candidates:
        pattern = get_feedback(guess, answer)
        pattern_counts[pattern] += 1
    total = len(candidates)
    entropy = 0.0
    for count in pattern_counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

# Select the guess with maximum expected entropy
def select_best_guess(candidates):
    best_guess = None
    best_entropy = -1
    # Always use full WORDS list for guesses (Knuth-style)
    for guess in WORDS:
        ent = entropy_for_guess(guess, candidates)
        if ent > best_entropy:
            best_entropy = ent
            best_guess = guess
    return best_guess

# Filter candidates based on feedback
def filter_words(candidates, guess, feedback):
    filtered = []
    for word in candidates:
        if get_feedback(guess, word) == feedback:
            filtered.append(word)
    return filtered

# Interactive main for entropy-based guessing
def main():
    candidates = WORDS[:]
    print("Entropy-based Wordle Assistant")
    print("Enter your guess and feedback each round.")
    print("Feedback format: g = green, y = yellow, . = gray: .g.gy for green in pos 2 and 4 and yellow in pos 5")
    print("Example: guess = crane, feedback = g..y. (c=green, a=yellow, rest gray)\n")
    while True:
        print(f"\nRemaining candidates: {len(candidates)}")
        if len(candidates) <= 50:
            print(candidates)
        if candidates:
            ranked = sorted(candidates, key=lambda w: entropy_for_guess(w, candidates), reverse=True)
            print("\nTop recommended guesses (by entropy):")
            for w in ranked[:5]:
                print(f"  {w} (entropy: {entropy_for_guess(w, candidates):.4f})")
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
        candidates = filter_words(candidates, guess, feedback)
        if len(candidates) == 1:
            print(f"\nThe answer must be: {candidates[0]}")
            break
        elif not candidates:
            print("\nNo candidates left. Check your input.")
            break

if __name__ == "__main__":
    main()