from connection import Connection
from credentials import Credentials


def get_connection(client_email, private_key_path):
  credentials = Credentials.get_for_service_account(
      client_email, private_key_path)
  return Connection(credentials=credentials)

def get_dataset(dataset_id, client_email, private_key_path):
  connection = get_connection(client_email, private_key_path)
  return connection.dataset(dataset_id)
