import os
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), '.env'))


class SQLCredentials:
    def __init__(self, db_name, server_type=None, azure=None):
        if db_name is None:
            raise ValueError("Please provide a value for db_name")
        self.db_name = db_name
        self.server_type = server_type
        self.azure = azure

    def simple_creds(self):
        if self.server_type is None:
            raise ValueError("Please provide a value for server_type")

        try:
            if self.azure is not None:
                if self.azure:
                    server_name = os.environ.get(f"SQL_AZURE_{self.server_type.upper()}")
                else:
                    server_name = os.environ.get(f"SQL_ONPREM_{self.server_type.upper()}")
            else:
                server_name = os.environ.get("SQL_" + self.db_name.upper() + '_' + self.server_type.upper())

            if os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper()) is not None:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper())
            else:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME')

            user_name = os.environ.get("SQL_" + self.db_name.upper() + '_USER_NAME')
            password = os.environ.get("SQL_" + self.db_name.upper() + '_PASSWORD')

            return {'server_name': re.sub(r'(\\)\1*', r'\1', server_name),
                    'db_name': db_name,
                    'user_name': user_name,
                    'password': password}
        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))

    def all_creds(self):
        try:
            prod_ = os.environ.get("SQL_" + self.db_name.upper() + '_PROD')
            test_ = os.environ.get("SQL_" + self.db_name.upper() + '_TEST')
            try:
                dev_ = os.environ.get("SQL_" + self.db_name.upper() + '_DEV')
            except Exception as e:
                print(e)
                dev_ = None
            if os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper()) is not None:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper())
            else:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME')
            user_name = os.environ.get("SQL_" + self.db_name.upper() + '_USER_NAME')
            password = os.environ.get("SQL_" + self.db_name.upper() + '_PASSWORD')

            creds = {'prod': prod_,
                     'test': re.sub(r'(\\)\1*', r'\1', test_),
                     'db_name': db_name,
                     'user_name': user_name,
                     'password': password}

            if dev_ is not None:
                creds.update({'dev': dev_})
            return creds

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class BCCredentials:
    def __init__(self, db_name=None, auth=False):
        self.db_name = db_name
        self.auth = auth

    def simple_creds(self):
        try:
            if self.auth:
                scope = os.environ.get("BC_AUTH_SCOPE")
                client_id = os.environ.get("BC_AUTH_CLIENT_ID")
                client_secret = os.environ.get("BC_AUTH_CLIENT_SECRET")

                return {'scope': scope,
                        'client_id': client_id,
                        'client_secret': client_secret}
            elif self.db_name is not None:
                server_type = os.environ.get(f"BC_ENV_SERVER_{self.db_name.upper()}")

                return {'server_type': server_type}
            else:
                raise ValueError("Please provide a valid input")

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class CDSCredentials:
    def __init__(self, env_name, webhook=False, auth=False):
        self.env_name = env_name
        self.webhook = webhook
        self.auth = auth

    def simple_creds(self):
        try:
            if self.auth:
                scope = os.environ.get("CDS_AUTH_SCOPE")
                client_id = os.environ.get("CDS_AUTH_CLIENT_ID")
                client_secret = os.environ.get("CDS_AUTH_CLIENT_SECRET")

                return {'scope': scope,
                        'client_id': client_id,
                        'client_secret': client_secret}
            else:
                server = os.environ.get(f"CDS_ENV_SERVER_{self.env_name.upper()}")
                organisation_id = os.environ.get(f"CDS_ENV_ORG_{self.env_name.upper()}")
                environment_prefix = os.environ.get(f"CDS_ENV_PREFIX_{self.env_name.upper()}")
                environment_url = os.environ.get(f"CDS_ENV_URL_{self.env_name.upper()}")
                if self.webhook:
                    environment_name = os.environ.get(f"CDS_ENV_NAME_{self.env_name.upper()}")
                else:
                    environment_name = self.env_name

                return {'server': server,
                        'environment_name': environment_name,
                        'organisation_id': organisation_id,
                        'environment_prefix': environment_prefix,
                        'environment_url': environment_url}

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class SharePointCredentials:
    def __init__(self, site=None):
        self.site = site

    def simple_creds(self):
        try:
            if self.site is None:
                raise ValueError("Please provide a value for site")

            client_id = os.environ.get(f"SHAREPOINT_CLIENT_ID_{self.site.upper()}")
            scopes = os.environ.get(f"SHAREPOINT_SCOPES_{self.site.upper()}")
            organisation_id = os.environ.get(f"SHAREPOINT_ORG_{self.site.upper()}")
            username = os.environ.get(f"SHAREPOINT_USER_{self.site.upper()}")
            password = os.environ.get(f"SHAREPOINT_PASSWORD_{self.site.upper()}")
            site_id = os.environ.get(f"SHAREPOINT_SITE_ID_{self.site.upper()}")
            site_name = os.environ.get(f"SHAREPOINT_SITE_NAME_{self.site.upper()}")
            api_version = os.environ.get(f"SHAREPOINT_API_VERSION_{self.site.upper()}")

            return {'client_id': client_id,
                    'scopes': scopes,
                    'organisation_id': organisation_id,
                    'username': username,
                    'password': password,
                    'site_id': site_id,
                    'site_name': site_name,
                    'api_version': api_version}

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class WebServiceCredentials:
    def __init__(self, service=None):
        self.service = service

    def simple_creds(self):
        try:
            if self.service is None:
                raise ValueError("Please provide a value for site")

            try:
                user_name = os.environ.get(f"WEBSERVICE_USER_{self.service.upper()}")
            except Exception as e:
                print(e)
                user_name = ''
            try:
                password = os.environ.get(f"WEBSERVICE_PASSWORD_{self.service.upper()}")
            except Exception as e:
                print(e)
                password = ''
            try:
                access_token = os.environ.get(f"WEBSERVICE_ACCESS_TOKEN_{self.service.upper()}")
            except Exception as e:
                print(e)
                access_token = ''

            return {'user_name': user_name,
                    'password': password,
                    'access_token': access_token}

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class MicrosoftTeamsCredentials:
    def __init__(self, organisation_id=None):
        self.organisation_id = organisation_id

    def simple_creds(self):
        try:
            if self.organisation_id is None:
                self.organisation_id = os.environ.get("POUPART_ORGANISATION_ID")

            client_id = os.environ.get("MICROSOFT_TEAMS_APP_CLIENT_ID")
            client_secret = os.environ.get("MICROSOFT_TEAMS_APP_CLIENT_SECRET")
            username = os.environ.get("MICROSOFT_TEAMS_USERNAME")
            password = os.environ.get("MICROSOFT_TEAMS_PASSWORD")

            return {'organisation_id': self.organisation_id,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'username': username,
                    'password': password}

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class SnowflakeCredentials:
    def __init__(self, db_name):
        if db_name is None:
            raise ValueError("Please provide a value for db_name")
        self.db_name = db_name

    def simple_creds(self):
        try:
            account = os.environ.get("SNOWFLAKE_" + self.db_name.upper() + '_ACCOUNT')
            user_name = os.environ.get("SNOWFLAKE_" + self.db_name.upper() + '_USERNAME')
            password = os.environ.get("SNOWFLAKE_" + self.db_name.upper() + '_PASSWORD')

            return {
                'account': account,
                'user_name': user_name,
                'password': password}
        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))
