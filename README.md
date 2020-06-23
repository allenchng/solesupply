![Logo](SoleSupply-Black.png)

A tool to give a sneak peek into the future. Check it out [here!](https://solesupply.herokuapp.com/).

## Background and Problem Statement

StockX is the world's largest marketplace for sneaker reselling and was recently valued at 1 billion dollars. StockX is unique from other marketplaces in that it hand authenticates each and every pair of shoes sold on its platform. This process is essential in an industry of counterfeits and fake goods, but adds additional time to each transaction. To maintain customer satisfaction, StockX must ensure its authentication pipeline minimizes delays and runs as efficiently as possible. One way to increase efficiency is to effectively forecast sales projections.

Disclaimer: this is meant as a toy problem.

This project was built during a session at [Insight Data Science](https://insightdatascience.com/). I scraped over 2 million sneaker transactions from StockX's website, which contained detailed information on over 700 different shoes. From this raw data, I [engineered features](https://github.com/allenchng/solesupply/blob/master/model-development/engineer_features.py) capturing date information, rolling metrics on the previous week of sales, and domain specific information about sneaker releases. To predict the future, I used [Bayesian linear regression](https://github.com/allenchng/solesupply/blob/master/model-development/bayes_linear_module.py). I validated my model against a persistence model (in which the day's current volume is used to predict the future) and a random forest regression.

This repo contains functions used during model development as well as code for the dockerized flask app.

Logo graciously provided by [Bang Tran](https://www.bangctran.com/about)