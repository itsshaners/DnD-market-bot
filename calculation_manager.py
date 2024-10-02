import database_manager

def calculate_statistics():
    items = database_manager.fetch_all_items()
    database_manager.create_item_data_table()
    for item_name, rarity in items:
        prices = database_manager.fetch_prices_for_item(item_name, rarity)
        if prices:
            avg_price = sum(prices) / len(prices)
            lowest_price = prices[0]
            price_gap = prices[1] - prices[0] if len(prices) > 1 else 0
            database_manager.save_item_data(item_name, rarity, avg_price, lowest_price, price_gap)

if __name__ == '__main__':
    calculate_statistics()