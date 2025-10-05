# WordleAlgo
An experimentation of Wordle algorithms that aim to solve Wordle in as few guesses as possible, as quickly as possible, as frequently as possible.

# Using the bot
If you just wanted to try each of the algorithms for yourself or do your own data collection, simply clone the repository with 
```
git clone https://github.com/LancelotShih/wordleAlgo.git
```
All greedy algorithm variants exist in: `wordleai/greedyAlgo`

All entropy algorithm variants exist in: `wordleai/entropyAlgo`

From here if you would like to use the bot as an assistant to when you play:
- Run `greedy_wordleai.py` for the greedy algorithm
- Run `entropy_wordleai.py` for the entropy algorithm

If you would like to autonomously open the daily NY Times wordle and complete it:
- Run `greedy_automation.py` for the greedy algorithm
- run `entropy_automation.py` for the entropy algorithm

If you would like to do data collection for yourself and run it a set number of times:
- Run `greedy_simulation.py` for the greedy algorithm
- Run `entropy_simulation.py` for the entropy algorithm
- Note to change the number of simulated games to run, change the `NUM_GAMES` variable at the top of each simulation python file.


# Greedy Algorithm

The greedy Wordle algorithm operates by taking the fixed list of Wordle targets from `wordle_targets.txt` and ranking them by how frequently each letter appears, giving each word a score indicating how "likely" it is to be the word.

Interestingly, contrary to what online sources suggest about best starting words like `"CRANE"`, the word with the most commonly used letters that will most likely yield a better second guess is `"IRATE"`.

The greedy algorithm here is an $O(n)$ solution, where $n$ is the number of possible target words, assuming the rankings of all words have been predetermined and stored. If not, it becomes $3O(n)$ (which is basically the same).

As a result, this algorithm runs incredibly fast and you can simulate thousands of Wordle games in a short period of time. The results are quite interesting.

### Wordle Data Collection Stats

| Attempt | Count | Percentage |
| ------- | ----- | ---------- |
| 1       | 7     | 0.05%      |
| 2       | 734   | 5.56%      |
| 3       | 4778  | 36.20%     |
| 4       | 4970  | 37.65%     |
| 5       | 1939  | 14.69%     |
| 6       | 543   | 4.11%      |
| failed  | 229   | 1.73%      |

Across 13,200 games, there is around a $2\%$ chance that the greedy algorithm fails entirely. However, the other $98\%$ of the time yields a correct answer, with almost $80\%$ of those answers being under $4$ guesses.

Because this algorithm is operating on a fixed dataset, it effectively runs an $O(n)$ decision tree. Because of this, the set of failed words will ALWAYS be the same. In other words, the $2\%$ of words missed are always going to be the same set of words. Here are most of them below found through my testing:

|  |  |  |  |
| ------------ | ------------ | ------------ | ------------ |
| baker        | boxer        | brave        | chill        |
| chock        | corer        | daddy        | eager        |
| fever        | fully        | gazer        | grave        |
| graze        | hatch        | jaunt        | jazzy        |
| joker        | jolly        | kitty        | lapel        |
| poker        | quack        | taste        | tatty        |
| tight        | waste        | waver        | wooly        |
| wound        |              |              |              |

# Entropy Algorithm
The entropy algorithm works by gravitating the guesses towards certainty (higher entropy) by utilizing a feedback loop to answer the question: 

<p align="center"><em>How much information do we expect to gain from guessing this word?</em></p>

The higher the entropy, the more new unique information you learn, the lower the entropy, the more candidate words show up that require you to gamble between.

The way this algorithm works is by taking each word in the word list and making a subsequent guess after it. 

For a candidate guess word, simulate the feedback against all remaining possible answers. Then you Group answers into “feedback buckets” (each unique feedback pattern is one bucket) where each bucket gets a size of how many words that fall into it. You can then convert these bucket sizes into probabilities (bucket size ÷ total candidates) and use them as scores by plugging them into the ***Shannon entropy formula***, which combines how many buckets exist + how balanced they are.

### Shannon Entropy Formula
$$
H = -\sum{p \log_2{p}} \ \ , \ \ p = \frac{\text{bucket size}}{\text{total candidates}}
$$

Because the feedback operates by scanning the words list for each word that is in the list, the algorithm operates in $O(n)^2$ time complexity which significantly increases the compute load required to play more games. As a result, the data collection was only feasibly able to play 1000 games, but the results should still speak for themselves given only 2309 words are in the wordle library. 

Interestingly, contrary to what the greedy solution suggests about the best starting word to be `"IRATE"`, the entropy algorithm uses `"RAISE"` as its starting word as it sees based on second order feedback the most favorable solution avenues. 

### Wordle Data Collection Stats
| Attempt | Count | Percentage |
| ------- | ----- | ---------- |
| 1       | 0     | 0.00%      |
| 2       | 11    | 1.10%      |
| 3       | 382   | 38.12%     |
| 4       | 538   | 53.69%     |
| 5       | 70    | 6.99%      |
| 6       | 1     | 0.10%      |
| failed  | 0     | 0.00%      |

Across $1000$ games, the entropy algorithm never fails to find the correct answer, with around $93\%$ of answers found under $4$ guesses. This results in a significantly more consistent performance compared to the greedy algorithm at the cost of larger compute time. 

# Conclusion and Considerations
Because the wordle target words will never change, there is an argument to be made that you can precompute the Entropy Algorithm once and run it as a lookup table instead. 

However, that introduces the triviality of the "wordle problem." If you can finitely create a lookup table for an algorithm that looks one step into the future, then you can also create a lookup table for an algorithm that looks 6 steps into the future to create a true entropic ranking. 

This brute force method would of course be $O(1)$ during runtime like all other lookup table solutions, but would defeat the purpose of the discussion of an algorithm to discover said lookup table. 
