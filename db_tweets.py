import sqlite3

class Tweets_DataBase:
    

    def __init__(self):
        self.conn = sqlite3.connect("tweets.db")
        self.create_table()
        self.create_user_posts_table()

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

    def create_user_posts_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publication_date TEXT,
                    login TEXT,
                    publication_text TEXT
                )
            ''')

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
    
    def insert_user_post(self, login: str, publication_text: str):
        from datetime import datetime
        publication_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            self.conn.execute('''
                INSERT INTO user_posts (publication_date, login, publication_text)
                VALUES (?, ?, ?)
            ''', (publication_date, login, publication_text))

    def get_only_posts(self, login: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT publication_text
            FROM user_posts
            WHERE login = ?
            ORDER BY publication_date DESC
            LIMIT 14
        ''', (login,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    
    def is_last_post_older_than(self, login: str, hours: float) -> bool:
        from datetime import datetime, timedelta
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MAX(publication_date)
            FROM user_posts
            WHERE login = ?
        ''', (login,))
        row = cursor.fetchone()
        # Якщо немає попередніх постів - повертаємо True
        if row[0] is None:
            return True
        try:
            last_post_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return True
        return (datetime.now() - last_post_date) > timedelta(hours=hours)