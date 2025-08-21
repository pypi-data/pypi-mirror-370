import json
import datetime
import dateutil
import dateutil.parser
import dateutil.utils
from .verbose import VERBOSE
from .conn import IAMApi


class Mailinglist:
    def __init__(self, iam, data=None):
        self._iam: IAMApi = iam
        self.name: str = ""
        self.mail: str = ""
        self.mailNickname: str = ""
        self.displayName: str = ""
        self.admingroup: str = ""
        self.certificationDate: datetime.datetime = ""
        self.certificationPeriod: str = ""
        self.description: str = ""
        self.dn: str = ""
        self.gidNumber: int = ""
        self.hideFromAddressLists: bool = None
        self.proxyAddresses: list[str] = []
        self.members: list[str] = []
        self.memberOf: list[str] = []

        if data:
            self._new_from_data(data)

    def _new_from_data(self, data):
        self._data = data
        for key, val in data.items():
            setattr(self, key, val)

        if "certificationDate" in data:
            try:
                self.certificationDate = dateutil.parser.parse(
                    data["certificationDate"]
                )
            except dateutil.parser.ParserError:
                self.certificationDate = None
        if "gidNumber" in data:
            try:
                self.gidNumber = int(data["gidNumber"])
            except ValueError:
                self.gidNumber = None
        if "listName" in data:
            self.name = data["listName"]

    def _get_body_for_members(self, members):
        if isinstance(members, tuple):
            members = list(members)
        if not isinstance(members, list):
            members = [members]

        users = []
        emails = []

        for member in members:
            if "@" in member:
                emails.append(member)
            else:
                users.append(member)
        body = {"users": users, "emails": emails}
        return body

    def reload_maillist(self):
        data = self._iam.get_request(f"/mailinglists/{self.name}")
        self._new_from_data(data[0])

    def add_members(self, *members):
        body = self._get_body_for_members(members)

        self._iam.put_request(
            endpoint=f"/mailinglists/{self.name}/members/add",
            body=body,
            ignore_errors=True,
        )
        self.reload_maillist()

    def del_members(self, *members):
        body = self._get_body_for_members(members)

        self._iam.put_request(
            endpoint=f"/mailinglists/{self.name}/members/remove",
            body=body,
            ignore_errors=True,
        )
        self.reload_maillist()

    def recertify(self):
        self._iam.put_request(endpoint=f"/mailinglists/{self.name}/recertify")
        self.reload_maillist()

    def _to_from_group(self, members, action="add", mess="{}"):
        endpoint = "/mailinglists/{}/members/{}".format(self.name, action)
        resp = self._iam.put_request(endpoint, members)
        if resp.ok:
            if VERBOSE:
                print(mess.format(self.name))
            return json.loads(resp.content.decode())

        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])

    def delete(self):
        endpoint = "/mailinglists/{}".format(self.name)
        resp = self._iam.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print("Mailinglist {} deleted.".format(self.name))
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])
