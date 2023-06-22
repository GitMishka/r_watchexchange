


import praw
from tabulate import tabulate
from datetime import datetime
from twilio.rest import Client
import psycopg2
import time
import config
while True:
  try:
# Connect to Postgres database
    conn = psycopg2.connect(
    host=config.pg_host,
    database=config.pg_database,
    user=config.pg_user,
    password=config.pg_password
)
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.execute("CREATE TABLE IF NOT EXISTS watch_exchange_posts (id TEXT PRIMARY KEY, title TEXT, post_time TIMESTAMP, url TEXT, price FLOAT, brand TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS texted_watch_exchange_posts (id TEXT PRIMARY KEY, title TEXT, post_time TIMESTAMP, url TEXT, price FLOAT, brand TEXT)")

    # Set up Twilio
    account_sid = config.twilio_account_sid
    auth_token = config.twilio_auth_token
    
    client = Client(account_sid, auth_token)

    # Set up Reddit
    user_agent = "Searchbot_01"
    reddit = praw.Reddit(username=config.reddit_username,
                        password =config.reddit_password,
                        client_id=config.reddit_client_id,
                        client_secret=config.reddit_client_secret,
                        user_agent=user_agent,
                        check_for_async=False)
    subreddit = reddit.subreddit('watchexchange')
    posts = subreddit.new(limit=10)

    # Define search terms and brand list
    # Define search terms and brand list
    global search_terms
    search_terms = ['omega', 'sinn', 'rolex', 'seiko']

    brand_list = ['A. Lange & Sohne', 'Alpina', 'Armani Exchange', 'Audemars Piguet', 
                    'Ball', 'Baume et Mercier', 'Bell & Ross', 'Blancpain', 'Breguet', 'Breitling', 
                    'Bremont', 'Bulova', 'Bvlgari', 'Cartier', 'Certina', 'Chanel', 'Chopard', 'Citizen', 
                    'Corum', 'Daniel Wellington', 'De Bethune', 'Doxa', 'Ebel', 'Eberhard & Co.', 
                    'F.P. Journe', 'Fossil', 'Frederique Constant', 'Girard-Perregaux', 'Glashütte Original', 
                    'G-Shock', 'Hamilton', 'Harry Winston', 'Hermes', 'Hublot', 'IWC', 'Jaeger-LeCoultre', 'Junghans', 
                    'Laco', 'Longines', 'Maurice Lacroix', 'MeisterSinger', 'Montblanc', 'Movado', 'Nomos Glashütte', 'Omega', 
                    'Oris', 'Panerai', 'Parmigiani Fleurier', 'Patek Philippe', 'Piaget', 'Rado', 'Raymond Weil', 'Richard Mille', 
                    'Rolex', 'Seiko', 'Shinola', 'Sinn', 'Tag Heuer', 'Tissot', 'Tudor', 'Ulysse Nardin', 'Vacheron Constantin', 
                    'Victorinox Swiss Army', 'Zenith']

    # Iterate through posts
    for post in posts:
        post_id = post.id
        post_name = post.title.lower()
        post_time = datetime.utcfromtimestamp(post.created_utc)
        url = post.url
        price_str = post_name.split("$")[-1].split()[0]
        try:
            price = float(price_str.replace("k", "000").replace("K", "000").replace(".", ""))
        except ValueError:
            price = None
        brand = None
        for brand_name in brand_list:
            if brand_name.lower() in post_name:
                brand = brand_name
                break
        
        # Check if post ID already exists in database
        cur.execute("SELECT id FROM watch_exchange_posts WHERE id=%s", (post_id,))
        existing_post = cur.fetchone()
        if existing_post:
            continue
        
        # Insert new row into database
        cur.execute("INSERT INTO watch_exchange_posts (id, title, post_time, url, price, brand) VALUES (%s, %s, %s, %s, %s, %s)",
                    (post_id, post_name, post_time, url, price, brand))
        conn.commit()
        
        if any(term in post_name for term in search_terms):
            # Check if post ID already exists in texted_watch_exchange_posts
            cur.execute("SELECT id FROM texted_watch_exchange_posts WHERE id=%s", (post_id,))
            texted_post = cur.fetchone()
            
            if not texted_post:
                message_body = f"Brand: {brand}\nTime: {post_time}\nLink: {url}"
                message = client.messages.create(
                    to='14232814382',
                    from_='18334633894',
                    body=message_body
                )
                print(f"Message sent with ID: {message.sid}")
                
                # Insert new row into texted_watch_exchange_posts
                cur.execute("INSERT INTO texted_watch_exchange_posts (id, title, post_time, url, price, brand) VALUES (%s, %s, %s, %s, %s, %s)",
                            (post_id, post_name, post_time, url, price, brand))
                conn.commit()
            
  except Exception as e:
        # handle any exceptions that may be raised
      print(f"An error occurred: {e}")
  #print(message_body) 
  time.sleep(10) # sleep for 10 seconds before running the loop again

