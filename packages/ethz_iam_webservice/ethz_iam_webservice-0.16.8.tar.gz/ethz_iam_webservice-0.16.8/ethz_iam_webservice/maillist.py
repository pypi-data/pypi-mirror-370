from dataclasses import dataclass, field
from datetime import date

from .conn import IAMApi
from .verbose import VERBOSE
from .group import RecertificationPeriod
from .utils import to_date

@dataclass
class Maillist:
    name: str = ""
    admingroup: str = ""
    certificationDate: date = field(default_factory=date.today)
    certificationPeriod: RecertificationPeriod = RecertificationPeriod.BIENNIAL
    certificationNote: str = ""
    groupManager: str = ""
    description: str = ""
    displayName: str = ""
    dn: str = ""
    gidNumber: str = ""
    hideFromAddressLists: bool = False
    isSecurityGroup: bool = False
    mail: str = ""
    mailNickname: str = ""
    memberOf: list[str] = field(default_factory=list)
    members: list[str] = field(default_factory=list)
    proxyAddresses: list[str] = field(default_factory=list) 

class MaillistService(IAMApi):

    def new_from_dict(self, data: dict):
        """Create a new Maillist object from a dictionary"""
        try:
            data["certificationPeriod"] = RecertificationPeriod(data.get("certificationPeriod"))
            if "certificationDate" in data:
                data["certificationDate"] = to_date(data["certificationDate"]) 
            data["name"] = data.pop("listName", "")
        except Exception as exc:
            print(exc)
            print(data)
        
        try:
            return Maillist(**data)
        except Exception as exc:
            print(exc)
            raise ValueError(f"Could not create Maillist from data: {data}") from exc

    def get(self, identifier: str | None = None):
        """Get a mailling list by its group name"""
        endpoint = f"/mailinglists/{identifier}"
        data = self.get_request(endpoint=endpoint)
        if not data:
            raise ValueError(f"Maillist {identifier} not found")
        return self.new_from_dict(data[0])

    def add_members(self, name, users, groups):
        """Add members to a mailling list: users and/or subgroups"""
        endpoint = f"/mailinglists/{name}/members/add"
        payload = {"users": users, "groups": groups}
        self.put_request(endpoint, payload)
        return self.get(name)

    def remove_members(self, name, users, groups):
        """Remove the members of a mailling list: users and/or subgroups"""
        endpoint = f"/mailinglists/{name}/members/remove"
        payload = {"users": users, "groups": groups}
        self.put_request(endpoint, payload)
        return self.get(name)

    def set_members(self, name, users, subgroups):
        """Set the members of a mailling list, replace all the previous ones."""
        endpoint = f"/mailinglists/{name}/members"
        payload = {"users": users, "subgroups": subgroups}
        self.post_request(endpoint, payload)
        return self.get(name)

    def delete(self, name: str):
        """Delete a mailling list by its name"""
        endpoint = f"/mailinglists/{name}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"Maillist {name} was successfully deleted")
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        else:
            data = resp.json()
            raise ValueError(data["msg"])

    def get_maillists_for_admingroup(self, admingroup):
        """
        Get all groups for a given admingroup.
        :param admingroup: The name of the admingroup.
        :return: A list of Group objects.
        """
        endpoint = f"/mailinglists/admGroup/{admingroup}"
        data = self.get_request(endpoint)
        groups = []
        for data_entry in data:
            group = self.get(data_entry["listName"])
            groups.append(group)
        return groups

    def get_maillist_names_for_admingroup(self, admingroup):
        """
        :return: A list of maillist names.
        """
        endpoint = f"/mailinglists/admGroup/{admingroup}"
        data = self.get_request(endpoint)
        maillist_names = []
        for data_entry in data:
            maillist_names.append(data_entry["listName"])
        return maillist_names

    def get_maillists_for_mail(self, mail: str):
        """
        Get a mailling list by its email address.
        :param email: The email address of the mailling list.
        :return: A Maillist object.
        """
        endpoint = f"/mailinglists?mail={mail}"
        data = self.get_request(endpoint)
        if not data:
            raise ValueError(f"Maillist with email {mail} not found")
        return self.new_from_dict(data[0])
