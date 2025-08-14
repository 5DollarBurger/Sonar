#
# Filename: app.py
#
# This script contains the core Python logic for a Slackbot that
# translates natural language questions into SQL queries using LangChain.
#
# Key Features:
# - Connects to Slack via Socket Mode for secure, firewall-friendly operation.
# - Uses the LangChain SQL Agent to understand database schema and generate SQL.
# - Integrates with a Google-provided LLM (Gemini) for language processing.
# - Executes the generated SQL against a read-only database connection.
# - Includes robust error handling and security best practices.
#

import logging
import os

from dotenv import find_dotenv, load_dotenv
# from langchain.agents import create_sql_agent
# from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from langchain.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# from sqlalchemy import create_engine

# -----------------------------------------------------------------------------
# 1. Configuration & Credential Setup
# -----------------------------------------------------------------------------


load_dotenv(find_dotenv())

# Use environment variables for secure credential management.
# This is a best practice for corporate environments.
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Set up the database connection string.
# IMPORTANT: Use a read-only user for security.
# This example uses a PostgreSQL connection string. Replace with your database.
# E.g., for MySQL: "mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>"
# DATABASE_URL = os.environ.get("DATABASE_URL")

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 2. Slack App Initialization
# -----------------------------------------------------------------------------

# Initializes the Slack app with the bot token.
app = App(token=SLACK_BOT_TOKEN)

# -----------------------------------------------------------------------------
# 3. LangChain SQL Agent Setup
# -----------------------------------------------------------------------------

# First, initialize the LLM.
# We're using a Google-provided model here.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-preview-05-20",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1
)

# Set up the database connection using SQLAlchemy.
# This will be used by the LangChain toolkit to introspect the database.
# db_engine = create_engine(DATABASE_URL)
# db = SQLDatabase(db_engine)

# Create the SQL Database Toolkit.
# This toolkit automatically provides the LLM with tools to list tables,
# inspect schemas, and execute queries.
# toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create the SQL agent. This is the core of our application.
# The agent will use the LLM to decide which tools to use and in what order.
# sql_agent = create_sql_agent(
#     llm=llm,
#     toolkit=toolkit,
#     verbose=True,  # Set to True for detailed logging of the agent's thought process.
#     handle_parsing_errors=True,
#     # Customize the system prompt to add specific instructions and guardrails.
#     # This is crucial for controlling the bot's behavior.
#     agent_executor_kwargs={
#         "agent_executor": {
#             "prompt": (
#                 "You are an expert SQL analyst for a data-payement team. "
#                 "Your task is to generate and run a SQL query from a user's question to solve their ad-hoc problems. "
#                 "Use the database schema provided by your tools. "
#                 "Always respond with the final answer based on the query results. "
#                 "You MUST NOT respond with the SQL code itself, only the answer. "
#                 "Be polite and helpful. Do NOT make any changes to the database (no INSERT, UPDATE, DELETE, etc. statements)."
#             )
#         }
#     }
# )


# -----------------------------------------------------------------------------
# 4. Slack Event Listener
# -----------------------------------------------------------------------------

# This decorator listens for any message that mentions the bot in a channel.
@app.event("app_mention")
def handle_app_mention(say, body):
    try:
        # Extract the user's question from the Slack message.
        # The bot mention is at the start, so we remove it.
        text_without_mention = body['event']['text'].split(' ', 1)[1]
        user_id = body['event']['user']
        
        logger.info(f"Received query from user {user_id}: {text_without_mention}")
        
        # Post an initial message to the channel to indicate the bot is working.
        say(f"Hey <@{user_id}>, I'm on it! Let me check the data for you...")

        # Invoke the LangChain agent with the user's question.
        # The agent will think, generate SQL, run it, and formulate a final answer.
        # response = sql_agent.invoke({"input": text_without_mention})
        response = {"input": text_without_mention, "output": "Hello World!"}
        
        logger.info(f"Agent's response: {response}")

        # Post the final, formatted answer back to Slack.
        say(f"Here is what I found:\n\n{response['output']}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        say(f"Oops! I ran into an issue. Could you please rephrase your request? The error was: {e}")


# -----------------------------------------------------------------------------
# 5. Run the Application
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Start the Slack bot in Socket Mode.
    # This is ideal for development and secure corporate deployment.
    # It requires the SLACK_APP_TOKEN to be set.
    SocketModeHandler(app, SLACK_APP_TOKEN).start()