# test sqlite3 using direct connection without django get all transactions:

import sqlite3
def get_all_transactions():
    # Connect to the SQLite database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Execute a query to fetch all transactions
    cursor.execute("SELECT * FROM transaction_transaction")

    # Fetch all results
    transactions = cursor.fetchall()

    # Print the results
    for transaction in transactions:
        print(transaction)

    # Close the connection
    conn.close()



if __name__ == "__main__":
    get_all_transactions()