# Two-step lookahead entropy (2-ply)
def select_best_guess_2ply(candidates):
    best_guess = None
    best_value = float('-inf')
    for guess in VALID_GUESSES:
        # Map feedback pattern to list of answers
        pattern_counts = defaultdict(list)
        for answer in candidates:
            pattern = get_feedback(guess, answer)
            pattern_counts[pattern].append(answer)
        total = len(candidates)
        expected_entropy = 0.0
        for pattern, answers_for_pattern in pattern_counts.items():
            prob = len(answers_for_pattern) / total
            # For this feedback, what is the best next guess's entropy?
            if len(answers_for_pattern) <= 1:
                entropy2 = 0.0
            else:
                # Find the best second guess for this reduced set
                entropy2 = max(entropy_for_guess(g2, answers_for_pattern) for g2 in VALID_GUESSES)
            expected_entropy += prob * entropy2
        if expected_entropy > best_value:
            best_value = expected_entropy
            best_guess = guess
    return best_guess
# Entropy-based Wordle AI (Knuth-style minimax)
# Uses entropy to select guesses that maximize information gain

from collections import Counter, defaultdict
import math


# Load all possible answer words
with open("wordle_targets.txt", "r") as f:
    ANSWERS = [w.strip().lower() for w in f.readlines() if len(w.strip()) == 5]
# Load all valid guess words (including answers)
with open("wordle_bank.txt", "r") as f:
    VALID_GUESSES = [w.strip().lower() for w in f.readlines() if len(w.strip()) == 5]

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
    # Use all valid guesses for entropy calculation
    for guess in VALID_GUESSES:
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
    candidates = ANSWERS[:]
    print("Entropy-based Wordle Assistant")
    print("Enter your guess and feedback each round.")
    print("Feedback format: g = green, y = yellow, . = gray: .g.gy for green in pos 2 and 4 and yellow in pos 5")
    print("Example: guess = crane, feedback = g..y. (c=green, a=yellow, rest gray)\n")
    while True:
        print(f"\nRemaining candidates: {len(candidates)}")
        if len(candidates) <= 50:
            print(candidates)
        if candidates:
            # Compute 2-ply expected entropy for all valid guesses
            guess_entropies = []
            total_guesses = len(VALID_GUESSES)
            for idx, w in enumerate(VALID_GUESSES):
                print(f"[Progress] Evaluating guess {idx+1}/{total_guesses}: {w}")
                pattern_counts = defaultdict(list)
                for answer in candidates:
                    pattern = get_feedback(w, answer)
                    pattern_counts[pattern].append(answer)
                total = len(candidates)
                expected_entropy = 0.0
                for pidx, (pattern, answers_for_pattern) in enumerate(pattern_counts.items()):
                    print(f"    [Subprogress] {w}: feedback {pidx+1}/{len(pattern_counts)} ({pattern})")
                    prob = len(answers_for_pattern) / total
                    if len(answers_for_pattern) <= 1:
                        entropy2 = 0.0
                    else:
                        entropy2 = max(entropy_for_guess(g2, answers_for_pattern) for g2 in VALID_GUESSES)
                    expected_entropy += prob * entropy2
                guess_entropies.append((w, expected_entropy))
            print("[Progress] 2-ply entropy calculation complete.")
            ranked = sorted(guess_entropies, key=lambda x: x[1], reverse=True)
            print("\nTop recommended guesses (by 2-ply expected entropy):")
            for w, ent in ranked[:5]:
                print(f"  {w} (2-ply expected entropy: {ent:.4f})")
        guess = input("\nEnter your guess (or 'quit'): ").strip().lower()
        if guess == "quit":
            break
        if len(guess) != 5 or guess not in VALID_GUESSES:
            print("Invalid guess. Must be a 5-letter word from the valid guess list.")
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