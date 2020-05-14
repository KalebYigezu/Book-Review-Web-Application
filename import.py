import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# app = Flask(__name__)


# Check for environment variable
if not os.getenv("MYDATAONHEROKU"):
    raise RuntimeError("DATABASE_URL is not set")


# Set up database
engine = create_engine(os.getenv("MYDATAONHEROKU"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open('books.csv')
    reader = csv.reader(f)
    for isbn, title, author, yearr in reader:
        db.execute("insert into books (isbn, title, author, yearr) values (:isbn, :title, :author, :yearr)",
                    {"isbn":isbn, "title":title, "author":author, "yearr":yearr})
        print(f"Added book Title = {title}")
        db.commit()


if __name__ == "__main__":
    main()
