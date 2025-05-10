from flask import Blueprint, current_app
import MySQLdb.cursors
from dotenv import dotenv_values
from google import genai

# take environment variables
GEMINI_KEY = dotenv_values("credentials/.env")["GEMINI_KEY"]

chat_bp = Blueprint("chat", __name__)


def get_data():
    conn = current_app.config["MYSQL"].connection
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    sql = """
        select
            t.name as "AI Tool Name",
            t.description,
            c.name as category,
            group_concat(k.name) as keywords
        from SearchIndex si
        join Tools t on si.idTool = t.idTool
        left join Category c on si.idCategory = c.idCategory
        left join Keywords_Indexes ki on si.idIndex = ki.IndexId
        join Keywords k on ki.keywordID = k.idKeywords
        group by t.name, t.description, c.name;
    """
    cursor.execute(sql)
    results = cursor.fetchall()

    column_names = [x[0] for x in cursor.description]
    csv = ",".join(column_names) + "\n"
    for row in results:
        csv += ",".join([f'"{value}"' for value in row.values()]) + "\n"

    return csv


@chat_bp.route("/chat/<question>", methods=["GET"])
def chat(question):
    data = get_data()

    prompt = f"""You are a customer support chatbot for "Gaitor Gate", a search engine for AI tools. Answer the user's questions based ONLY on the following CSV data:

--- CSV DATA START ---
{data}
--- CSV DATA END ---

If the answer cannot be found in the CSV data, respond with "I do not have that information in the provided data." Do not use any external knowledge.

User question: {question}
Chatbot answer:
"""

    # print(prompt)

    client = genai.Client(api_key=GEMINI_KEY)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)

    return f"response: {response.text}"
