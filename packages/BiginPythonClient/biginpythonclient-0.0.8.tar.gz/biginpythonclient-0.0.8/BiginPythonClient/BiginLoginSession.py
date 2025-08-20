
from PythonAPIClientBase import LoginSession
import requests
import json
import os

#Scopes list: https://www.bigin.com/developer/docs/apis/v2/scopes.html

class BiginLoginSession(LoginSession):
    client_id = None
    client_secret = None

    loggedin = None
    endpoint = None
    access_token = None
    refresh_token = None
    scope = None
    api_domain = None
    token_type = None
    expires_in = None
    token_file = None

    def __init__(self, endpoint, token_file, client_id, client_secret):
        self.loggedin = False
        self.endpoint = endpoint
        self.token_file = token_file
        self.client_id = client_id
        self.client_secret = client_secret

        if token_file is not None:
            if (os.path.isfile(token_file)):
                token = None
                with open(token_file) as json_data:
                    token = json.load(json_data)
                self.loggedin = True
                self.access_token = token["access_token"]
                self.refresh_token = token["refresh_token"]
                self.scope = token["scope"]
                self.api_domain = token["api_domain"]
                self.token_type = token["token_type"]
                self.expires_in = token["expires_in"]

                if not self._check_existing_login():
                    if not self.refresh():
                        self.loggedin = False
                        return
                    if not self._check_existing_login():
                        self.loggedin = False

    def isLoggedIn(self):
        return self.loggedin

    def _check_existing_login(self):
        # check existing login works
        url = self._get_api_url("/settings/modules")
        headers = {}
        self.injectHeaders(headers)

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return False
            # print("Error response status", response.status_code)
            # #print("Error response text", response.text)
            # raise Exception("DDD")
        return True

    def injectHeaders(self, headers):
        headers["Authorization"] = "Zoho-oauthtoken " + self.access_token

    def register_auth_code(self, auth_code):
        raise Exception("Not overriddern")

    def _get_apilogin_url(self, path):
        return "https://accounts." + self.endpoint + path

    def _get_api_url(self, path):
        #return "https://www.zohoapis.com" + "/bigin/v1" + path
        return self.api_domain + "/bigin/v2" + path

    def _login(self, access_token, refresh_token, scope, api_domain, token_type, expires_in):
        self.loggedin = True
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.scope = scope
        self.api_domain = api_domain
        self.token_type = token_type
        self.expires_in = expires_in

        if self.token_file is not None:
            token_file_content = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "scope": scope,
                "api_domain": api_domain,
                "token_type": token_type,
                "expires_in": expires_in
            }
            with open(self.token_file, 'w') as f:
                json.dump(token_file_content, f)

    def refresh(self):
        url = self._get_apilogin_url("/oauth/v2/token")
        headers={
            "Accept": "application/json"
        }
        post_form_data = {
            "client_id": (None, self.client_id),
            "client_secret": (None, self.client_secret),
            "refresh_token": (None, self.refresh_token),
            "grant_type": (None, "refresh_token")
        }

        response = requests.post(url, headers=headers, files=post_form_data)
        if response.status_code != 200:
            print("Error")
            print("Got response status", response.status_code)
            print("Response text", response.text)
            raise Exception("Invalid Auth")
        responseDict = json.loads(response.text)
        if "error" in responseDict:
            print("Error -", responseDict["error"])
            print("Got response status", response.status_code)
            print("Response text", response.text)
            raise Exception(responseDict["error"])

        self._login(
            access_token=responseDict["access_token"],
            refresh_token=self.refresh_token,
            scope=responseDict["scope"],
            api_domain=responseDict["api_domain"],
            token_type=responseDict["token_type"],
            expires_in=responseDict["expires_in"]
        )
        return True


class ServerBasedBiginLoginSession(BiginLoginSession):
    redirect_url = None
    scopes = None
    def __init__(self, client_id, client_secret, endpoint, redirect_url, scopes):
        super().__init__(endpoint, token_file=None, client_id=client_id, client_secret=client_secret)
        self.redirect_url = redirect_url
        self.scopes = scopes


    def get_auth_url(self):
        offline_access = True
        access_type = "online"
        if offline_access:
            access_type = "offline"
        apipath = "/oauth/v2/auth?scope=" + self.scopes \
            + "&client_id=" + self.client_id \
            + "&response_type=code" \
            + "&access_type=" + access_type \
            + "&redirect_uri=" + self.redirect_url
        return self._get_apilogin_url(apipath)

    def register_auth_code(self, auth_code):
        ##"https://accounts.zoho.com/oauth/v2/token"
        url = self._get_apilogin_url("/oauth/v2/token")
        headers={
            "Accept": "application/json"
        }
        post_form_data = {
            "client_id": (None, self.client_id),
            "client_secret": (None, self.client_secret),
            "code": (None, auth_code),
            "redirect_uri": (None, self.redirect_url),
            "grant_type": (None, "authorization_code")
        }

        response = requests.post(url, headers=headers, files=post_form_data)
        if response.status_code != 200:
            print("Error")
            print("Got response status", response.status_code)
            print("Response text", response.text)
            raise Exception("Invalid Auth")
        responseDict = json.loads(response.text)
        if "error" in responseDict:
            print("Error -", responseDict["error"])
            print("Got response status", response.status_code)
            print("Response text", response.text)
            raise Exception("Invalid Auth")

        # print("Valid response")
        # print("Response text", response.text)

class SelfBasedBiginLoginSession(BiginLoginSession):
    endpoint = None
    def __init__(self, client_id, client_secret, endpoint, token_file=None):
        super().__init__(endpoint, token_file, client_id, client_secret)

    # https://api-console.zoho.eu/

    def register_auth_code(self, auth_code):
        ##"https://accounts.zoho.com/oauth/v2/token"
        url = self._get_apilogin_url("/oauth/v2/token")
        headers={
            "Accept": "application/json"
        }
        post_form_data = {
            "client_id": (None, self.client_id),
            "client_secret": (None, self.client_secret),
            "code": (None, auth_code),
            "grant_type": (None, "authorization_code")
        }

        print("register_auth_code url", url)
        raise Exception("DD")

        response = requests.post(url, headers=headers, files=post_form_data)
        if response.status_code != 200:
            print("Error")
            print("Got response status", response.status_code)
            print("Response text", response.text)
            raise Exception("Invalid Auth")
        responseDict = json.loads(response.text)
        if "error" in responseDict:
            print("Error -", responseDict["error"])
            print("Got response status", response.status_code)
            print("Response text", response.text)
            raise Exception("Invalid Auth")

        self._login(
            access_token = responseDict["access_token"],
            refresh_token = responseDict["refresh_token"],
            scope = responseDict["scope"],
            api_domain = responseDict["api_domain"],
            token_type = responseDict["token_type"],
            expires_in = responseDict["expires_in"]
        )

class SelfBasedBiginLoginSessionInteractive(SelfBasedBiginLoginSession):
    def __init__(self, client_id, client_secret, endpoint, token_file=None, inquirer=None):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            endpoint=endpoint,
            token_file=token_file
        )
        if not self.isLoggedIn():
            print("Need to relogin")

            print("Goto https://api-console.zoho.com/")
            print("Use scope:", "ZohoBigin.modules.ALL,ZohoBigin.settings.READ")

            auth_code = inquirer.text(message="Enter auth code returned:").execute()
            if auth_code == "":
                print("Exiting")
                exit(0)

            self.register_auth_code(auth_code=auth_code)

        print("Logged in!!")


