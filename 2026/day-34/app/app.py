from flask import Flask
import psycopg2
import time

app = Flask(__name__)

def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                host="db",
                database="postgres",
                user="postgres",
                password="password"
            )
            return conn
        except Exception as e:
            print("Database not ready, retrying...")
            time.sleep(2)

@app.route("/")
def home():
    conn = connect_db()
    return "Flask + PostgreSQL Connected 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
