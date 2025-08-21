class Teams(object):
    def __init__(self, client):
        self._client = client

    def get_all_teams(self, params=None, **kwargs):
        url = "legacyTeams"
        return self._client._get(self._client.BASE_URL + url, params=params, **kwargs)
