import csv
import os
import mysql.connector
import bcrypt


def get_database_config():
    required = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

    return {
        "host": os.environ["MYSQL_HOST"],
        "user": os.environ["MYSQL_USER"],
        "password": os.environ["MYSQL_PASSWORD"],
        "database": os.environ["MYSQL_DB"],
    }


# Read CSV dataset into MySQL database.
def read_csv(file_path):
    database_config = get_database_config()
    mydb = mysql.connector.connect(**database_config)
    cursor = mydb.cursor()
    data = []

    imported_account_password = os.environ.get("IMPORTED_ACCOUNT_PASSWORD")
    if not imported_account_password:
        raise RuntimeError("Missing required environment variable: IMPORTED_ACCOUNT_PASSWORD")

    with open(file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            thumbnail_url = row.get("logo_url").strip()
            company_name = row.get("company_name").strip()
            task = row.get("primary_task").strip()
            task1 = row.get("applicable_tasks").strip()
            description = row.get("full_description").strip()
            price = row.get("pricing").strip()
            url = row.get("visit_website_url").strip()
            hashed_password = bcrypt.hashpw(
                imported_account_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                "SELECT idAccount FROM Company WHERE company_name = %s",
                (company_name,),
            )
            idCompany = cursor.fetchone()
            if idCompany:
                idCompany = idCompany[0]
            else:
                cursor.execute("INSERT INTO User(name) VALUES (%s)", (company_name,))
                mydb.commit()
                idUser = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO Account (idUser, email, hashed_password, username, Account_Type) VALUES (%s,%s,%s,%s,%s)",
                    (idUser, company_name, hashed_password, company_name, "Company"),
                )
                mydb.commit()
                idAccount = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO Company (idAccount, company_name, website) VALUES (%s,%s,%s)",
                    (idAccount, company_name, url),
                )
                mydb.commit()
                cursor.execute(
                    "SELECT idAccount FROM Company WHERE company_name = %s",
                    (company_name,),
                )
                idCompany = cursor.fetchone()[0]

            cursor.execute("SELECT idTool FROM Tools WHERE name = %s", (company_name,))
            idTool = cursor.fetchone()
            if idTool:
                idTool = idTool[0]
            else:
                cursor.execute(
                    "INSERT INTO Tools (name, description, url, thumbnail_url, company, pricing) VALUES (%s,%s,%s,%s,%s,%s)",
                    (company_name, description, url, thumbnail_url, idCompany, price),
                )
                mydb.commit()
                idTool = cursor.lastrowid

                cursor.execute("SELECT idCategory FROM Category WHERE name = %s", (task,))
                idCategory = cursor.fetchone()[0]

                cursor.execute("SELECT idIndex FROM SearchIndex WHERE idTool = %s", (idTool,))
                idIndex = cursor.fetchone()
                if idIndex:
                    idIndex = idIndex[0]
                else:
                    cursor.execute(
                        "INSERT INTO SearchIndex (idTool, idCategory) VALUES (%s,%s)",
                        (idTool, idCategory),
                    )
                    mydb.commit()
                    idIndex = cursor.lastrowid

                platform = 4
                cursor.execute(
                    "INSERT IGNORE INTO IndexPlatform (idIndex, idPlatform) VALUES (%s,%s)",
                    (idIndex, platform),
                )
                mydb.commit()

                keywords = task1.split(",")
                for keyword in keywords:
                    keyword = keyword.strip()
                    cursor.execute(
                        "SELECT idKeywords FROM Keywords WHERE name = %s", (keyword,)
                    )
                    idKeyword = cursor.fetchone()
                    if idKeyword:
                        idKeyword = idKeyword[0]
                    else:
                        cursor.execute("INSERT INTO Keywords (name) VALUES (%s)", (keyword,))
                        mydb.commit()
                        idKeyword = cursor.lastrowid

                    cursor.execute(
                        "INSERT IGNORE INTO Keywords_Indexes (IndexID, keywordID) VALUES (%s,%s)",
                        (idIndex, idKeyword),
                    )
                    mydb.commit()

    cursor.close()
    mydb.close()
    return data


if __name__ == "__main__":
    read_csv("application/static/dataset/tools.csv")
