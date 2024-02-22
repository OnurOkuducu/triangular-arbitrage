Code for detecting triangular arbitrage opportunities in the Binance cryptocurrency exchange.

The algorithm begins by retrieving the bid and ask prices for each currency pair. If a price change is detected from the previous records, the algorithm proceeds to search for potential arbitrage opportunities using the formula P(ask)AB * P(ask)BC / P(ask)AC < 1 or P(bid)AB * P(bid)BC / P(bid)AC > 1. 

The code stores the detected arbitrage opportunities as an array of dictionaries and, upon completion, saves the data in an Excel file.
