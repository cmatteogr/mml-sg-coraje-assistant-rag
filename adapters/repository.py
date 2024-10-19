"""
* Author: Cesar M. Gonzalez R

Repository layer.
DB Repository
"""
import abc

from models.discord_models import QADiscord, UserDiscord
from models.gradio_models import QAGradio
from utils.constants import TABLE_NAME_QA_USERS_GRADIO, SCHEMA_NANE, TABLE_NAME_QA_USERS_DISCORD, \
    TABLE_NAME_DISCORD_USERS


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def insert_qa_users_gradio(self, qa_user_gradio: QAGradio):
        raise NotImplementedError

    @abc.abstractmethod
    def insert_qa_users_discord(self, qa_user_discord: QADiscord):
        raise NotImplementedError

    @abc.abstractmethod
    def insert_users_discord(self, user_discord: UserDiscord):
        raise NotImplementedError

    @abc.abstractmethod
    def query_users_discord(self, name: str) -> UserDiscord:
        raise NotImplementedError


class SQLServerRepository(AbstractRepository):

    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def insert_qa_users_gradio(self, qa_user_gradio: QAGradio):
        # Define the sql insert statement
        query = f"INSERT INTO {SCHEMA_NANE}.{TABLE_NAME_QA_USERS_GRADIO} (question, answer, history, exe_datetime) VALUES (?, ?, ?, ?)"
        # Define the data to be inserted
        data = (qa_user_gradio.question, qa_user_gradio.answer, qa_user_gradio.history, qa_user_gradio.exe_datetime)
        # Execute the query
        self.cursor.execute(query, data)
        # Commit the transaction
        self.conn.commit()

    def insert_qa_users_discord(self, qa_user_discord: QADiscord):
        # Define the sql insert statement
        query = f"INSERT INTO {SCHEMA_NANE}.{TABLE_NAME_QA_USERS_DISCORD} (user_id, question, answer, history, exe_datetime) VALUES (?, ?, ?, ?, ?)"
        # Define the data to be inserted
        data = (qa_user_discord.user_id, qa_user_discord.question, qa_user_discord.answer, qa_user_discord.history,
                qa_user_discord.exe_datetime)
        # Execute the query
        self.cursor.execute(query, data)
        # Commit the transaction
        self.conn.commit()

    def insert_users_discord(self, user_discord: UserDiscord):
        # Define the sql insert statement
        query = f"INSERT INTO {SCHEMA_NANE}.{TABLE_NAME_DISCORD_USERS} (id, name) VALUES (?, ?)"
        # Define the data to be inserted
        data = (user_discord.id_discord, user_discord.name)
        # Execute the query
        self.cursor.execute(query, data)
        # Commit the transaction
        self.conn.commit()

    def query_users_discord(self, name: str) -> UserDiscord:
        # Define the sql select statement
        query = f"SELECT * FROM {SCHEMA_NANE}.{TABLE_NAME_DISCORD_USERS} WHERE name = ?"
        # Define the query params
        param = (name)
        # Execute the query
        self.cursor.execute(query, param)
        # Fetch all results from the executed query
        results = self.conn.cursor.fetchall()
        # Create a UserDiscord object from the fetched results
        user_discord = UserDiscord(*results[0])
        # Return the UserDiscord object
        return user_discord