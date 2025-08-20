from .BiginLoginSession import SelfBasedBiginLoginSessionInteractive
import PythonAPIClientBase
import json
from .Wrappers import layoutWrapperFactory

class BiginClient(PythonAPIClientBase.APIClientBase):




    def getSelfBasedBiginLoginSessionInteractive(
        self,
        client_id,
        client_secret,
        endpoint,
        token_file,
        inquirer
    ):
        return SelfBasedBiginLoginSessionInteractive(
            client_id=client_id,
            client_secret=client_secret,
            endpoint=endpoint,
            token_file=token_file,
            inquirer=inquirer
        )

    def __init__(self, mock=None, verboseLogging=PythonAPIClientBase.VerboseLoggingNullLogClass()):
        super().__init__(baseURL="", mock=mock, forceOneRequestAtATime=True, verboseLogging=verboseLogging)

    def sendRequest(self, reqFn, url, loginSession, data, origin, injectHeadersFn, postRefreshCall=False, skipLockCheck=False, params=None):
        if not loginSession.isLoggedIn():
            raise Exception("Must be logged in")
        return super().sendRequest(
            reqFn=reqFn,
            url=loginSession._get_api_url(url),
            loginSession=loginSession,
            data=data,
            origin=origin,
            injectHeadersFn=injectHeadersFn,
            postRefreshCall=postRefreshCall,
            skipLockCheck=skipLockCheck,
            params=params
        )

    def getModules(self, loginSession):
        result = self.sendGetRequest(
            url="/settings/modules",
            loginSession=loginSession,
            injectHeadersFn=None
        )
        if result.status_code != 200:
            self.raiseResponseException(result)

        print("OK TODO")
        response = json.loads(result.text)
        modules = []
        for module in response["modules"]:
            modules.append(module)
        return modules

    #https://www.bigin.com/developer/docs/apis/v2/get-team-pipeline-records.html

    def getLayouts(self, loginSession, module):
        params = {
            "module": module.value
        }
        result = self.sendGetRequest(
            url="/settings/layouts",
            loginSession=loginSession,
            injectHeadersFn=None,
            params=params
        )
        if result.status_code != 200:
            self.raiseResponseException(result)

        response = json.loads(result.text)

        return layoutWrapperFactory(client=self, loginSession=loginSession, dict=response, layout_module=module)

