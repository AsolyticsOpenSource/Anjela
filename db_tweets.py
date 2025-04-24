import sqlite3

class Tweets_DataBase:
    

    def __init__(self):
        self.conn = sqlite3.connect("tweets.db")
        self.create_table()

    def create_table(self):
        
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_url TEXT UNIQUE,
                    content TEXT,
                    answer TEXT
                )
            ''')
        pass

    def insert_tweet(self, tweet_url: str, content: str, answer: str):
        with self.conn:
            self.conn.execute('''
                INSERT OR IGNORE INTO tweets (tweet_url, content, answer) VALUES (?, ?, ?)
            ''', (tweet_url, content, answer))
        pass

    def contains_tweet(self, tweet_url: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM tweets WHERE tweet_url = ?
        ''', (tweet_url,))
        count = cursor.fetchone()[0]
        return count > 0