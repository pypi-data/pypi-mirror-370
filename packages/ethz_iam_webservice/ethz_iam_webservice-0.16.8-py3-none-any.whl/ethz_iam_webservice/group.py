import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum

from .conn import IAMApi, IAMApiAlternative
from .verbose import VERBOSE


class RecertificationPeriod(Enum):
    ANNUAL = "Annual"
    QUARTERLY = "Quarterly"
    BIENNIAL = "Biennial"
    NONE = "No recertification"
    INVALID = "Not set or invalid value"


class GroupType(Enum):
    CUSTOM = "custom"
    LZ = "lz"
    GROUPS = "groups"
    DOMAIN = "domain"
    PERSKAT = "perskat"
    PRIVATE = "private"
    REALM = "realm"
    BUILDING = "building"


class Targets(Enum):
    AD = "AD"
    LDAP = "LDAP"


@dataclass
class GroupAlternative:
    cn: str = ""
    description: str = ""
    type: GroupType = GroupType.CUSTOM
    members: list[str] = field(default_factory=list)
    gidNumber: int = -1


class GroupAlternativeService(IAMApiAlternative):

    def new_from_data(self, data):
        return GroupAlternative(
            **{k: data[k] for k in data if k in GroupAlternative.__dataclass_fields__}
        )

    def search_groups(
        self,
        group_name,
        member,
        gidnumber,
        group_type,
        email,
        firstname,
        lastname,
        member_details: bool = False,
        no_members: bool = False,
    ):
        endpoint = "/groupmgr/groups?"
        query = {}
        if group_name:
            query["cn"] = group_name
        if member:
            query["member"] = member
        if gidnumber:
            query["gidNumber"] = gidnumber
        if group_type:
            query["type"] = group_type
        if email:
            query["mail"] = email
        if firstname:
            query["firstname"] = firstname
        if lastname:
            query["lastname"] = lastname
        if member_details:
            query["member_details"] = "true"
        if no_members:
            query["no_members"] = "true"

        querystring = "&".join(f"{k}={v}" for k, v in query.items())
        full_endpoint = endpoint + querystring
        data = self.get_request(full_endpoint)
        groups = []
        for d in data:
            groups.append(self.new_from_data(d))
        return groups


@dataclass
class Group:
    name: str = ""
    description: str = ""
    admingroup: str = ""
    group_ad_ou: str = ""
    cre_date: str = ""
    mod_date: str = ""
    grid: int = -1
    gidNumber: int = -1
    category: str = ""
    state: str = ""
    certification_date: str = ""
    certification_period: str = RecertificationPeriod.NONE.value
    certification_note: str = ""
    members: list[str] = field(default_factory=list)
    subgroups: list[str] = field(default_factory=list)
    managers: list[str] = field(default_factory=list)
    targets: list[Targets] = field(default_factory=list)


class GroupService(IAMApi):
    """
    A class to manage groups in the ETHZ IAM web service.
    It allows creating, updating, deleting groups, and managing their members and targets.
    """

    @classmethod
    def new_from_data(cls, data):
        new_group = {}
        new_group["certification_date"] = (
            datetime.strptime(data.get("certificationDate"), "%d.%m.%Y").isoformat(
                timespec="seconds"
            )
            if data.get("certificationDate")
            else ""
        )
        new_group["cre_date"] = datetime.fromisoformat(
            data["createTimestamp"][:-1]
        ).isoformat(timespec="seconds")
        new_group["mod_date"] = datetime.fromisoformat(
            data["modifyTimestamp"][:-1]
        ).isoformat(timespec="seconds")
        new_group["name"] = data["groupName"]
        new_group["category"] = data["groupRoleCategory"]
        new_group["admingroup"] = data.get("respAdminGroup", "(system)")
        new_group["members"] = data.get("users", [])
        new_group["subgroups"] = data.get("subgroups", [])
        new_group["managers"] = data.get("groupManager", [])
        new_group["targets"] = []
        for target in data.get("targetSystems", []):
            new_group["targets"].append(
                "AD" if target == "Active Directory" else "LDAP"
            )

        new_group["group_ad_ou"] = data.get("groupADOU", "")
        new_group["certification_period"] = data.get("certificationPeriod")
        new_group["certification_note"] = data.get("certificationNote", "")

        for key in (
            "description",
            "grid",
            "gidNumber",
            "state",
        ):
            new_group[key] = data.get(key, "")
        group = Group(
            **{k: new_group[k] for k in new_group if k in Group.__dataclass_fields__}
        )
        return group

    def create(
        self,
        name: str,
        admingroup: str,
        description: str,
        targets: list[Targets] | None = None,
        group_ad_ou: str | None = None,
        certification_period: RecertificationPeriod = RecertificationPeriod.NONE,
        certification_note: str | None = None,
        managers: list[str] | None = None,
    ):
        if targets is None:
            targets = []
        map_targets = {
            "AD": "Active Directory",
            "ACTIVE DIRECTORY": "Active Directory",
            "LDAP": "LDAPS",
            "LDAPS": "LDAPS",
        }
        body = {
            "name": name,
            "description": description,
            "admingroup": admingroup,
            "targets": [map_targets[target.upper()] for target in targets],
            "groupADOU": group_ad_ou,
            "certificationPeriod": certification_period,
            "certificationNote": (
                certification_note or "no recertification needed"
                if certification_period == RecertificationPeriod.NONE.value
                else ""
            ),
            "groupManager": managers,
        }

        endpoint = "/groups"
        data = self.post_request(endpoint, body)
        if VERBOSE:
            print("new group {} was successfully created".format(name))
        new_group = self.new_from_data(data)
        return new_group

    def update(
        self,
        current_name: str,
        new_name: str | None = None,
        description: str | None = None,
        group_ad_ou: str | None = None,
        certification_period: RecertificationPeriod | None = None,
        certification_note: str | None = None,
        managers: list[str] | None = None,
    ):
        payload = {}
        if new_name and new_name != current_name:
            payload["newName"] = new_name
        if description:
            payload["newDescription"] = description
        if managers:
            payload["newGroupManager"] = managers
        if group_ad_ou:
            payload["newGroupADOU"] = group_ad_ou
        if certification_period:
            payload["newCertPeriod"] = certification_period
            if certification_period == RecertificationPeriod.NONE.value:
                payload["newCertNote"] = (
                    certification_note or "no recertification needed"
                )
        if certification_note:
            payload["newCertNote"] = certification_note
            payload["newCertPeriod"] = RecertificationPeriod.NONE.value
        if not payload:
            return self

        endpoint = f"/groups/{current_name}"
        data = self.put_request(endpoint, payload)
        if VERBOSE:
            print(f"group {current_name} has been successfully updated")
        group = self.new_from_data(data)
        return group

    @property
    def data(self):
        return asdict(self)

    def get_group(self, identifier=None):
        """Get a group by its group name or by gidNumber"""
        if re.search(r"^\d+$", str(identifier)):
            # we search using a gidNumber
            endpoint = f"/groups?gidNumber={identifier}"
            data = self.get_request(endpoint=endpoint)
            if len(data) == 1:
                data = data[0]
            elif len(data) > 1:
                raise ValueError(
                    f"More than one group found with gidNumber={identifier}"
                )
            else:
                raise ValueError(f"No group found with gidNumber={identifier}")
        else:
            endpoint = f"/groups/{identifier}"
            data = self.get_request(endpoint=endpoint)
        group = self.new_from_data(data)
        return group

    def add_members(self, name, users, subgroups):
        """Add members to a group: users and/or subgroups"""
        endpoint = f"/groups/{name}/members/add"
        payload = {"users": users, "subgroups": subgroups}
        data = self.put_request(endpoint, payload)
        return self.new_from_data(data)

    def remove_members(self, name, users, subgroups):
        """Remove the members of a group: users and/or subgroups"""
        endpoint = f"/groups/{name}/members/remove"
        payload = {"users": users, "subgroups": subgroups}
        data = self.put_request(endpoint, payload)
        return self.new_from_data(data)

    def set_members(self, name, users=None, subgroups=None):
        """Set the members of a group, replace all the previous ones."""
        endpoint = f"/groups/{name}/members"
        payload = {}
        if users:
            payload["users"] = users
        if subgroups:
            payload["subgroups"] = subgroups
        data = self.post_request(endpoint, payload)
        return self.new_from_data(data)

    def set_targets(self, name, targets):
        """Put the group in AD and/or LDAP"""
        map_targets = {
            "AD": "AD",
            "ACTIVE DIRECTORY": "AD",
            "LDAP": "LDAP",
            "LDAPS": "LDAP",
        }
        targets = [map_targets[target.upper()] for target in targets]
        if "AD" in targets and "LDAP" in targets:
            target_string = "ALL"
        else:
            target_string = targets[0].upper()
        endpoint = f"/groups/{name}/targetsystems/{target_string}"
        self.put_request(endpoint, {})

    def remove_targets(self, name, targets):
        """Remove the group from AD and/or LDAP."""
        map_targets = {
            "AD": "AD",
            "ACTIVE DIRECTORY": "AD",
            "LDAP": "LDAP",
            "LDAPS": "LDAP",
        }
        for target in [map_targets[target.upper()] for target in targets]:
            endpoint = f"/groups/{name}/targetsystems/{target.upper()}"
            self.delete_request(endpoint)

    def delete(self, name: str):
        """Delete a group and remove it from all its target systems."""
        endpoint = f"/groups/{name}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"group {name} was successfully deleted")
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )
        else:
            data = resp.json()
            raise ValueError(data["msg"])

    def recertify(self, name: str):
        """Recertify and adjust the end date of a group"""
        endpoint = f"/groups/{name}/recertify"
        data = self.put_request(endpoint, "")
        group = self.new_from_data(data)
        return group

    def get_groups_for_admingroup(self, admingroup):
        """
        Get all groups for a given admingroup.
        :param admingroup: The name of the admingroup.
        :return: A list of Group objects.
        """
        endpoint = f"/groups/admGroup/{admingroup}"
        data = self.get_request(endpoint)
        groups = []
        for data_entry in data:
            groups.append(self.new_from_data(data=data_entry))
        return groups
