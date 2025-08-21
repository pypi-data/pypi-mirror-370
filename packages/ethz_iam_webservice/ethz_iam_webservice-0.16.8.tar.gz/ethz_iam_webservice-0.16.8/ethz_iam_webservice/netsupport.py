from dataclasses import dataclass, field
from datetime import datetime

from .conn import IAMApi
from .verbose import VERBOSE

"""
{
    "admins": [
        "lbre4iam",
        "aaneeser",
        "adm-asteven",
        "mas4iam",
        "rwi4iam",
        "asteven",
        "eric",
        "lop4iam",
        "aped4iam",
        "mbel4iam",
        "bca4iam",
        "ele4ea",
        "cbo4iam"
    ],
    "description": "ISG für SIS",
    "gidNumber": "83020",
    "grid": "4914626",
    "groupName": "id-sis-netsup",
    "groupRoleCategory": "Netsup",
    "members": [
        "gpontrand",
        "brge4ea",
        "apedziwilk",
        "adm-urbanb",
        "vadmin",
        "adm-nkowenski",
        "adm-cbollige",
        "bcasano",
        "richardw",
        "twuest",
        "mbelluco",
        "nkowenski",
        "hpc-netcenter-monkey",
        "lbrechbuehl",
        "cbovino"
    ],
    "state": "PROCESSED"
}

"""

@dataclass
class Netsupport:
    admins: list[str] = field(default_factory=list)
    description: str = ""
    gidNumber: str = ""
    grid: str = ""
    groupName: str = ""
    groupRoleCategory: str = "Netsup"
    members: list[str] = field(default_factory=list)
    state: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class NetsupportService(IAMApi):

    def new_from_data(self, data: dict):
        """Create a new Netsupport object from a dictionary"""
        return Netsupport(**{k: data[k] for k in data if k in Netsupport.__dataclass_fields__})

    def get(self, identifier: str | None = None):
        """Get a netsupport-group by its group name"""
        endpoint = f"/netsupport/{identifier}"
        data = self.get_request(endpoint=endpoint)
        return self.new_from_data(data)

    def add_members(self, name, users, subgroups):
        """Add members to a netsupport-group: users and/or subgroups"""
        endpoint = f"/netsupport/{name}/members/add"
        payload = {"users": users, "subgroups": subgroups}
        data = self.put_request(endpoint, payload)
        return self.new_from_data(data)

    def remove_members(self, name, users, subgroups):
        """Remove the members of a netsupport-group: users and/or subgroups"""
        endpoint = f"/netsupport/{name}/members/remove"
        payload = {"users": users, "subgroups": subgroups}
        data = self.put_request(endpoint, payload)
        return self.new_from_data(data)

    def set_members(self, name, users, subgroups):
        """Set the members of a netsupport-group, replace all the previous ones."""
        endpoint = f"/netsupport/{name}/members"
        payload = {"users": users, "subgroups": subgroups}
        data = self.post_request(endpoint, payload)
        return self.new_from_data(data)

    def delete(self, name: str):
        """Delete a netsupport-group by its name"""
        endpoint = f"/netsupport/{name}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"netsupport-group {name} was successfully deleted")
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        else:
            data = resp.json()
            raise ValueError(data["msg"])
