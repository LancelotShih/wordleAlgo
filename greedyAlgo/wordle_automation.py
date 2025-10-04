import sys
sys.path.append('.')  # Ensure current directory is in path
from wordleai import filter_words, score_word, WORDS

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

    greens = {}
    yellows = {}
    grays = {}
    candidates = WORDS[:]

    for turn in range(6):
        # pick best guess
        if candidates:
            guess = max(candidates, key=score_word)
        else:
            print("No candidates left. Stopping.")
            break
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
        for pos, (letter, state) in enumerate(feedback_row):
            if state == 'correct':
                feedback += 'g'
            elif state == 'present':
                feedback += 'y'
            elif state == 'absent':
                feedback += '.'
            else:
                feedback += '.'

        # update known info
        for pos, (letter, mark) in enumerate(zip(guess, feedback)):
            if mark == "g":  # green
                greens[pos] = letter
            elif mark == "y":  # yellow
                if pos not in yellows:
                    yellows[pos] = []
                yellows[pos].append(letter)
            else:  # gray
                required_count = (
                    list(greens.values()).count(letter) +
                    sum(letter in lst for lst in yellows.values())
                )
                grays[letter] = required_count

        candidates = filter_words(greens, yellows, grays)

        # check for win
        if feedback == 'ggggg':
            print(f"\nSolved! The answer is: {guess}")
            break

    # driver.quit()  # Uncomment to close browser when done

if __name__ == "__main__":
    main()
