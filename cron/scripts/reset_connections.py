import psycopg2
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    host = os.getenv("POSTGRES_HOST", "postgres")
    user = os.getenv("POSTGRES_USER")
    port = os.getenv("POSTGRES_PORT", 5432)
    passwd = os.getenv("POSTGRES_PASS")
    dbname = os.getenv("POSTGRES_DB", "postgres")
    conn = psycopg2.connect(
        user=user, password=passwd, host=host, port=port, database=dbname
    )

    try:
        cr = conn.cursor()
        cr.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND now() - state_change > interval '10 minutes';")
        result = cr.fetchall()
        conn.commit()
        print("terminated %s connections" % len(result))
    except Exception as e:
        print("Failed to reset the connections, message: %s" % e)
    finally:
        conn.close()
