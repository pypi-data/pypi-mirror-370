from dataclasses import dataclass, field
from datetime import datetime 

from .conn import IAMApi
from .verbose import VERBOSE

@dataclass
class Realm:
    createTimestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    gidNumber: str = ""
    grid: str = ""
    groupName: str = ""
    groupRoleCategory: str = ""
    modifyTimestamp: datetime = field(default_factory=datetime.now)
    respAdminGroup: str = ""
    state: str = ""
    subgroups: list[str] = field(default_factory=list)
    targetSystems: list[str] = field(default_factory=list)
    users: list[str] = field(default_factory=list)

class RealmService(IAMApi):

    def new_from_data(self, data: dict):
        return Realm(**{k: data[k] for k in data if k in Realm.__dataclass_fields__})

    def get(self, identifier: str | None = None):
        """Get a realm by its group name"""
        endpoint = f"/realms/{identifier}"
        data = self.get_request(endpoint=endpoint)
        realm = self.new_from_data(data)
        return realm

    def add_members(self, name, users, subgroups):
        """Add members to a group: users and/or subgroups"""
        endpoint = f"/realms/{name}/members/add"
        payload = {"users": users, "subgroups": subgroups}
        data = self.put_request(endpoint, payload)
        group = self.new_from_data(data)
        return group

    def remove_members(self, name, users, subgroups):
        """Remove the members of a group: users and/or subgroups"""
        endpoint = f"/realms/{name}/members/remove"
        payload = {"users": users, "subgroups": subgroups}
        data = self.put_request(endpoint, payload)
        group = self.new_from_data(data)
        return group

    def set_members(self, name, users, subgroups):
        """Set the members of a group, replace all the previous ones."""
        endpoint = f"/realms/{name}/members"
        payload = {"users": users, "subgroups": subgroups}
        data = self.post_request(endpoint, payload)
        return self.new_from_data(data)

    def delete(self, name: str):
        """Delete a realm by its name"""
        endpoint = f"/realms/{name}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"realm {name} was successfully deleted")
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        else:
            data = resp.json()
            raise ValueError(data["msg"])
