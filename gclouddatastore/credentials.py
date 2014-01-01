from oauth2client import client


class Credentials(object):

  SCOPE = ('https://www.googleapis.com/auth/datastore '
           'https://www.googleapis.com/auth/userinfo.email')

  @classmethod
  def get_for_service_account(cls, client_email, private_key_path):
    return client.SignedJwtAssertionCredentials(
        service_account_name=client_email,
        private_key=open(private_key_path).read(),
        scope=cls.SCOPE)
