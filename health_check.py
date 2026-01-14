from config import Settings
import psycopg2
import redis
import sys


# Loads .env automatically
settings = Settings()  

def check_postgres_connection():
    try:
        # Uses the postgres url from .env file
        conn = psycopg2.connect(settings.database_url)
        print(f"PostgreSQL connected: {settings.database_url}")
        conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL failed: {e}")
        return False

def check_redis_connection():
    try:
        # Uses the REDIS_URL from .env file 
        r = redis.from_url(settings.redis_url)
        r.ping()
        print(f"Redis connected: {settings.redis_url}")
        return True
    except Exception as e:
        print(f"Redis failed: {e}")
        return False


if __name__ == "__main__":

    print('Running System check for external services connection')


    try:
        if check_postgres_connection() and check_redis_connection():
        
            print('Run complete')
            sys.exit(0)

        else:
            sys.exit(1)

    except Exception as e:
        print(e)

