import json

import boto3
from botocore.exceptions import ClientError


class SecretManager:

    def __init__(self, access_key=None, secret_key=None, region_name=None):
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__region_name = region_name

    def get_secrets_manager_client(self):
        try:
            session = boto3.session.Session(aws_access_key_id=self.__access_key,
                                            aws_secret_access_key=self.__secret_key)
            return session.client(service_name="secretsmanager", region_name=self.__region_name)
        except Exception as e:
            print(f'Exception while creating secrets_manager_client: {e}')
            raise e

    # Retrieves the secret value for the given secret name from AWS Secrets Manager.
    def get_secret_key_value(self, secret_name, verbose=False):
        if verbose:
            print(f"INFO: In get_secret_key_value for: {secret_name}")
        client = self.get_secrets_manager_client()
        try:
            get_secret_key_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            print(f"An error occurred while retrieving the secret for {secret_name}: {e}")
            raise e

        return json.loads(get_secret_key_value_response['SecretString'])
