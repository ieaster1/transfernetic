import re
import requests


class MWClient():

    def __init__(self, url, user=None, password=None):
        self.url = url
        self.user = user
        self.password = password
        self.session = requests.Session()

    def token(self):
        token_params = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }

        response = self.session.get(url=self.url, params=token_params)
        return response
    
    def login(self, token):
        login_data = {
            "action": "login",
            "lgname": self.user,
            "lgpassword": self.password,
            "lgtoken": token,
            "format": "json"
        }

        response = self.session.post(self.url, data=login_data)
        return response

    def siteinfo(self):
        siteinfo_params = {
            "action": "query",
            "meta": "siteinfo",
            "formatversion": "2",
            "format": "json"
        }

        response = self.session.get(url=self.url, params=siteinfo_params)
        return response

    def mwversion(self, format="full"):
        siteinfo = self.siteinfo().json()
        generator = siteinfo["query"]["general"]["generator"]
        if format.lower() == "full":
            return generator
        elif format.lower() == "short":
            version = re.search(r'\s*([\d.]+)', generator).group(1)
            return version
        else:
            print(f"{format} is an invalid option. Valid options are 'full' or 'short'.")

    def apcontinue(self, result):
        """TODO: tossing ideas on how to handle 'continue' data"""
        pass

    def allpages(self, apnamespace=0, apcontinue=None):

        allpages_params = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apnamespace": apnamespace,
            "aplimit": "500",
            "apcontinue": apcontinue
        }

        response = self.session.get(url=self.url, params=allpages_params)
        return response

    def page_contents(self, pageid=None, page_title=None):
        pc_params = {
            "action": "parse",
            "format": "json",
            "pageid": pageid,
            "page": page_title,
            "prop": "wikitext"
        }

        response = self.session.get(url=self.url, params=pc_params)
        return response