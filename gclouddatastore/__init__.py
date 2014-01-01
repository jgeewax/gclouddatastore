from connection import Connection
from credentials import Credentials


def get_connection(dataset_id, client_email=None, private_key_path=None):
  credentials = Credentials.get_for_service_account(
      client_email, private_key_path)
  return Connection(dataset_id, credentials=credentials)
