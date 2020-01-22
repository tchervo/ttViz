# ttViz
ttViz is a collection of python scripts for gathering data from Twitter, storing it, and visualizing it. This software allows for searches by query, user profile, or a "network" of users and 10 of their followers/people following them. This data can then be saved as a .csv file for easy import into statistical software such as R or Excel and can also be visualized. This software additionally supports the posting of these visualizations to Twitter. Current data that can be gathered using this software are nouns/adjectives that are used in tweets, the whole text of tweets, the number of interactions for a set of tweets, and temporal information about the tweets.

# Usage
ttViz currently supports 4 general modes: topic search, user search, network search, and proportion testing.

### Topic Search
Users can input any valid Twitter search query (Both simple and advanced) and a selected number of tweets (100 is the default) to be downloaded and stored as a .csv file with options for visualization of commonly used nouns/adjectives as a bar graph.

### User Search
A user can be identified through their profile ID or other unique identifier's such as their screen name and can have:
1. All of the tweets on their profile (Things they posted, liked tweets, retweets) analyzed
2. All the things on their profile that they posted themselves (i.e No retweets) analyzed
3. A linear model of the number of retweets their tweets get as a function of likes their tweets get.

This visualizaions can be displayed in a bar graph for categorical data and a scatter plot with optional linear model for quantitative data.

### Network Search
A "root user" is selected, then 100 of their followers/people following them are selected and have their tweets undergo the same analysis as option 2 of a User Search (No retweets). Results are visualized as a bar graph of frequently used nouns/adjectives.

### Proportion Testing
The number of retweets and likes two user's tweets (excluding retweets) are compared using Welch's T-test. The distribution of likes/retweets for each user's tweets is then visualized on a bar graph.

# Software Organization
This software is currently split into 4 different modules, each with a specific purpose:
1. tweetplot.py - Logistics of running the software such as logging in to Twitter, posting, user input, etc. This is the "main file" for this software.
2. datamanager.py - Processing of tweets and organization of data into dataframes.
3. plotmaker.py - Contains the PlotMaker class which creates the visualizations used in this software.
4. statsmanager.py - Performs statistical calculations for this software.

# Acknowledgements, License, and Warrenty Information
This software is provided under the GNU GPL v3 license and is distributed without any form of warrenty. A copy of the license is included with this software's source code. This software would not be possible without the following libraries:
- Pandas
- Scipy
- Matplotlib
- Natural Language Toolkit
- Tweepy

This software uses code from the Natural Language Toolkit (NLTK).
Bird, Steven, Edward Loper and Ewan Klein (2009), *Natural Language Processing with Python.* O’Reilly Media Inc
