from app.database import create_db_and_tables


def main():
    create_db_and_tables()
    print("Database and tables created successfully.")


if __name__ == "__main__":
    main()