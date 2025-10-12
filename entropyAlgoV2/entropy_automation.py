import sys
import os
sys.path.append(os.path.dirname(__file__))
from entropy_wordleai import select_best_guess, filter_words, entropy_for_guess, WORDS

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
import time

# Path to your msedgedriver.exe (update if needed)
EDGE_DRIVER_PATH = r"msedgedriver.exe"
WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html"

def launch_wordle():
    service = EdgeService(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service)
    driver.get(WORDLE_URL)
    time.sleep(5)  # Wait for page to load
    return driver

def close_popups(driver):
    # Try to close intro modal, tutorial, and click Play button
    time.sleep(2)
    # Close the help modal if present
    try:
        close_btn = driver.find_element(By.XPATH, "//button[@data-testid='icon-close']")
        close_btn.click()
        time.sleep(1)
    except Exception:
        pass
    # Click the Play button if present
    try:
        play_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Play')]" )
        play_btn.click()
        time.sleep(1)
    except Exception:
        pass
    # Close the tutorial modal if present (usually another close button)
    try:
        tutorial_close = driver.find_element(By.XPATH, "//button[@aria-label='Close']")
        tutorial_close.click()
        time.sleep(1)
    except Exception:
        pass

def get_board_state(driver):
    # Get the current board state (letters and colors)
    board = []
    rows = driver.find_elements(By.CSS_SELECTOR, "div.Row-module_row__pwpBq")
    for row in rows:
        tiles = row.find_elements(By.CSS_SELECTOR, "div.Tile-module_tile__UWEHN")
        word = []
        for tile in tiles:
            letter = tile.get_attribute("data-letter")
            color = tile.get_attribute("data-state")  # can either be 'correct', 'present', 'absent', or ''
            word.append((letter, color))
        if word:
            board.append(word)
    return board

def main():
    driver = launch_wordle()
    close_popups(driver)
    print("Wordle loaded. Board state:")
    board = get_board_state(driver)
    for row in board:
        print(row)

    candidates = WORDS[:]
    for turn in range(6):
        print("First 50 candidates:", candidates[:20])
        if len(candidates) == 1:
            guess = candidates[0]
            print(f"\nTurn {turn+1}: Only one candidate left, guessing: {guess}")
        elif not candidates:
            print("No candidates left. Stopping.")
            break
        else:
            # Print top 5 guesses by entropy
            ranked = sorted(candidates, key=lambda w: entropy_for_guess(w, candidates), reverse=True)
            print(f"\nTop recommended guesses (by entropy):")
            for w in ranked[:5]:
                print(f"  {w} (entropy: {entropy_for_guess(w, candidates):.4f})")
            guess = select_best_guess(candidates)
            print(f"\nTurn {turn+1}: Entering guess: {guess}")
        for letter in guess:
            driver.find_element(By.TAG_NAME, 'body').send_keys(letter)
            time.sleep(0.1)
        driver.find_element(By.TAG_NAME, 'body').send_keys("\ue007")
        time.sleep(3)

        board = get_board_state(driver)
        print(f"\nBoard state after guess {guess}:")
        for row in board:
            print(row)

        # get feedback from the latest row
        feedback_row = board[turn]
        feedback = ''
        for letter, state in feedback_row:
            if state == 'correct':
                feedback += 'g'
            elif state == 'present':
                feedback += 'y'
            elif state == 'absent':
                feedback += '.'
            else:
                feedback += '.'

        candidates = filter_words(candidates, guess, feedback)

        if feedback == 'ggggg':
            print(f"\nSolved! The answer is: {guess}")
            break

    # driver.quit()  # Uncomment to close browser when done

if __name__ == "__main__":
    main()
