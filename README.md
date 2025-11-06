# MTG Tournament Data Scraper

This project will scrape the tournament data from melee.gg for any tournament you want. The main goal was to create a way to get deck representation and deck win rates from a given tournament or list of tournaments.

# Project Proposal
The main question that this project is trying to answer is "What is the best strategy choice at the next tournament?". The best way to inform this descision is to look at winrates of each deck. This will be broken down into winrates by deck, and ,maybe sometime in the future, broken down further into winrates by deck by tournament.

# Data Source
All data is pulled from melee.gg. This site is the official tournament organizer for Wizards of the Coast (Owner of MTG). I specifically scrapped the data for each participant in the tournament. This includes their deck choice, name, and win/loss/draw. I also scrapped their complete decklist and all individual round data.

# Cleaning the Data
The biggest cleaning issue was with "Deck Name". It appears to me that each individual is able to label what their deck strategy is when they register for a tournament. This creates a ton of inconsitency in what each strategy actually means. Strategies in general are how a deck wants to use its cards to win a game. Each strategy has cards that define the specific strategy. I went through each of the major deck strategies and picked out 3 cards that categorized that deck. If a deck had all three of those cards in it, I renamed it to the most common title for that strategy. Spending more time on this could lead to a better consolidation of deck strategies.

# Visualizations
The first thing we need to look at is what strategies are available for us to choose from. The two main ways that I looked at this is through popularity (total number of a specific strategy) and winrate of a specific strategy.

## Popularity
![Strategy Popularity](https://via.placeholder.com/468x300?text=App+Screenshot+Here)
