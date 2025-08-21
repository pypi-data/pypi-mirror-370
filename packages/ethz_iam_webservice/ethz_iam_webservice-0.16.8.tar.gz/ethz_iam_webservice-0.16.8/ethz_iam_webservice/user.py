import json
from dataclasses import dataclass, field
from typing import List
from datetime import date

from .conn import IAMApi, IAMApiAlternative
from .service import servicename_map
from .utils import to_date
from .verbose import VERBOSE


map_iamfields2internal = {
    "username": "username",
    "firstname": "firstname",
    "lastname": "lastname",
    "displayName": "displayname",
    "description": "description",
    "gender": "gender",
    "salutation": "salutation",
    "preferredLanguage": "preferred_language",
    "mail": "mail",
    "department": "department",
    "nuid": "nuid",
    "npid": "npid",
    "persid": "persid",
    "uidNumber": "uidNumber",
    "gidnumber": "gidNumber",
    "orcID": "orcid",
    "startDate": "start_date",
    "createTimestamp": "cre_date",
    "endDate": "valid_until",
    "modifyTimestamp": "mod_date",
    "services": "services",
    "userState": "status",
    "persCat": "persCat",
    "persCatText": "persCatText",
    "officePlace": "office_place",
    "officeAddressLine1": "office_address_line1",
}


@dataclass
class UserAlternative:
    uid: str = ""
    mail: str = ""
    firstname: str = ""
    lastname: str = ""
    manager_uid: str = ""
    company: str = ""
    title: str = ""
    npid: str = ""
    uidNumber: str = ""
    orcid: str = ""
    swissEduIDUniqueID: str = ""


class UserAlternativeService(IAMApiAlternative):
    def new_from_data(self, data):
        return UserAlternative(
            **{k: data.get(k, "") for k in UserAlternative.__dataclass_fields__.keys()}
        )

    def search_users(
        self,
        username=None,
        mail=None,
        firstname=None,
        lastname=None,
        uidNumber=None,
    ):
        endpoint = "/usermgr/persons?"
        query = {}
        if username:
            query["uid"] = username
        if mail:
            query["mail"] = mail
        if firstname:
            query["firstname"] = firstname
        if lastname:
            query["lastname"] = lastname
        if uidNumber:
            query["uidNumber"] = uidNumber
        if not query:
            raise ValueError(
                "please provide at least one query item: username, mail, firstname or lastname."
            )

        querystring = "&".join(f"{k}={v}" for k, v in query.items())
        full_endpoint = endpoint + querystring
        data = self.get_request(full_endpoint)
        users = []
        for d in data:
            users.append(self.new_from_data(d))
        return users


@dataclass
class UserRelation:
    """Represents a relation of a user in the IAM system.
    Relations are used to manage the employment or affiliation of a user with ETH Zurich.
    """

    beschaeftigungsgrad: str = ""
    beziehung: str = ""
    description: str = ""
    dienstverhaeltnis: str = ""  # Employment relationship
    dienstverhaeltnisCode: str = ""
    effectiveEndDate: str = ""  # "9999-12-31T00:00:00.000Z"
    endDate: str = ""  # "9999-12-31T00:00:00.000Z"
    hauptbeziehung: str = ""  # "TRUE"
    leitzahl: str = ""  # "06006"
    orgeinheit: str = ""  # "Scientific Software and Data Mgmt."
    persCat: list[str] = field(default_factory=list)  # ["P00"]
    persid: str = ""  # "55327"
    pnr: str = ""  # "00033018"
    startDate: str = ""  # "2019-01-01T00:00:00.000Z"


@dataclass
class Persona:
    """
    Represents a persona in the IAM system.
    Personas are used to manage different roles or identities for a user.
    """

    npid: str = ""
    nuid: str = ""
    username: str = ""
    cre_date: date = field(default_factory=date.today)
    start_date: date = field(default_factory=date.today)
    mod_date: date = field(default_factory=date.today)
    description: str = ""
    createTimestamp: str = ""
    state: str = ""
    uidNumber: str = ""


@dataclass
class Service:
    """
    Represents a service in the IAM system.
    Services are used to manage access to various resources and functionalities.
    """

    name: str = ""
    assignedBy: str = ""


@dataclass
class User:
    username: str = ""
    lastname: str = ""
    firstname: str = ""
    displayname: str = ""
    salutation: str = ""
    preferred_language: str = ""
    mail: list[str] = field(default_factory=list)
    persCat: list[str] = field(default_factory=list)
    persCatText: list[str] = field(default_factory=list)
    office_place: str = ""
    office_address_line1: str = ""
    persid: int = -1
    npid: int = 1
    nuid: int = -1
    uidNumber: int = -1
    gidNumber: int = -1
    cre_date: str = ""
    start_date: date = field(default_factory=date.today)
    mod_date: date = field(default_factory=date.today)
    valid_until: str = ""
    description: str = ""
    department: str = ""
    gender: str = ""
    manager_uid: str = ""  # Username of the manager, if the user is a persona
    status: str = ""
    orcid: str = ""
    relations: list[UserRelation] = field(default_factory=list)
    personas: list[Persona] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)


class UserService(IAMApi):

    def delete(self, username):
        # Deletes a persona from the IAM system.
        owner = self.get_owner_of_persona(username)
        endpoint = f"users/{owner.username}/personas/{username}"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"User {username} deleted.")
        else:
            data = json.loads(resp.content.decode())
            raise ValueError(data["message"])

    def new_from_data(self, data):
        new_user = {}
        for data_field in data:
            if data_field in (
                "createTimestamp",
                "modifyTimestamp",
                "startDate",
                "endDate",
            ):
                data[data_field] = to_date(data[data_field]).strftime("%Y-%m-%d")
            if data_field in map_iamfields2internal:
                new_user[map_iamfields2internal[data_field]] = data[data_field]
            else:
                pass

        for service in new_user.get("services", []):
            service["login_until"] = to_date(service["login_until"]).strftime(
                "%Y-%m-%d"
            )
            service["delete_after"] = to_date(service["delete_after"]).strftime(
                "%Y-%m-%d"
            )

        user = User(**new_user)
        return user

    def get_user(self, username):
        endpoint = f"users/{username}"
        user_info = self.get_request(endpoint)
        return self.new_from_data(user_info)

    def search_users(
        self,
        firstname=None,
        lastname=None,
        persid=None,
        npid=None,
        uidNumber=None,
        matrikelNr=None,
        pnr=None,
        leitzahl=None,
        email=None,
    ):
        """
        Get the data of the user/s with the attribute specified in the query parameters.
        The only allowed query parameters are (at the moment): matrikelNr,PNR,leitzahl,firstname,lastname,npid,persid,email,uidNumber.
        """
        endpoint = "/users?"
        query = {}
        if firstname:
            query["firstname"] = firstname
        if lastname:
            query["lastname"] = lastname
        if persid:  # persid is the ETHZ person ID
            query["persid"] = persid
        if npid:  # npid is the nethz person ID
            query["npid"] = npid
        if uidNumber:
            query["uidNumber"] = uidNumber
        if matrikelNr:
            query["matrikelNr"] = matrikelNr
        if pnr:  # pnr is the ETHZ personalnummer
            query["pnr"] = pnr
        if leitzahl:  # leitzahl is the ETHZ organizational unit number
            query["leitzahl"] = leitzahl
        if email:
            query["email"] = email
        if not query:
            raise ValueError(
                "Please provide at least one query item: email, firstname, lastname, persid, npid, uidNumber, matrikelNr, pnr or leitzahl"
            )
        querystring = "&".join(f"{k}={v}" for k, v in query.items())
        full_endpoint = endpoint + querystring
        data = self.get_request(full_endpoint)
        users = []
        for d in data:
            users.append(self.new_from_data(d))
        return users

    def _to_from_group(self, username, group_name, action="add", mess="{} {}"):
        endpoint = f"/groups/{group_name}/members/{action}"
        body = [username]
        self.put_request(endpoint, body)
        if VERBOSE:
            print(mess.format(username, group_name))

    def add_to_group(self, username, group_name):
        self._to_from_group(
            username,
            group_name,
            action="add_forgiving",
            mess="Added user {} to group {}",
        )

    def remove_from_group(self, username, group_name):
        self._to_from_group(
            username, group_name, "del", mess="Removed user {} from group {}"
        )

    def get_relations(self, username) -> List[UserRelation]:
        """Get all relations of a user."""
        endpoint = f"/users/{username}/relations"
        relations = self.get_request(endpoint=endpoint)
        user_relations = []
        for relation in relations:
            relation["startDate"] = to_date(relation.pop("startDate", ""))
            relation["endDate"] = to_date(relation.pop("endDate", ""))
            relation["effectiveEndDate"] = to_date(relation.pop("effectiveEndDate", ""))
            relation["leitzahl"] = relation.pop("leitzahl", "")
            relation["persCat"] = relation.pop("persCat", [])
            user_relations.append(
                UserRelation(
                    **{
                        k: relation[k]
                        for k in UserRelation.__dataclass_fields__.keys()
                        if k in relation
                    }
                )
            )
        return user_relations

    def get_services(self, username):
        endpoint = f"/users/{username}/services"
        services = self.get_request(endpoint=endpoint)
        user_services = []
        for service in services:
            user_services.append(Service(**service))
        return user_services

    def get_personas(self, username):
        """Get all personas of a user."""
        endpoint = f"/users/{username}/personas"
        personas = self.get_request(endpoint=endpoint)
        user_personas = []
        for persona in personas:
            persona["cre_date"] = to_date(persona.pop("createTimestamp", ""))
            persona["start_date"] = to_date(persona.pop("startDate", ""))
            persona["mod_date"] = to_date(persona.pop("modifyTimestamp", ""))
            persona["npid"] = persona.pop("NPID", "")
            persona["nuid"] = persona.pop("NUID", "")
            persona["username"] = persona.pop("cn", "")
            user_personas.append(Persona(**persona))
        return user_personas

    def get_owner_of_persona(self, username):
        user_alt = UserAlternativeService()
        users = user_alt.search_users(username=username)
        if not users:
            raise ValueError(f"No persona found with username: {username}")
        if len(users) > 1:
            raise ValueError(
                f"Multiple personas found with username: {username}. Please specify a unique username."
            )
        user = users[0]
        if not user.manager_uid:
            raise ValueError(f"User {username} is not a persona.")

        owner = self.get_user(user.manager_uid)
        return owner

    def update_persona(
        self, host_username, username, description="", displayname="", owner_username=""
    ):
        if not description and not displayname and not owner_username:
            raise ValueError(
                "Please provide at least one of the following: description, displayname, or owner_username."
            )
        endpoint = f"/users/{host_username}/personas/{username}"
        body = {}
        if description:
            body["description"] = description
        if displayname:
            body["displayName"] = displayname
        if owner_username:
            body["owner"] = owner_username
        return self.put_request(endpoint=endpoint, body=body)

    def grant_service(self, username, service_name):
        if service_name.upper() in servicename_map:
            service_name = servicename_map[service_name.upper()]
        endpoint = f"users/{username}/services/{service_name}"
        try:
            self.post_request(endpoint, {})
        except ValueError as exc:
            if "already" in str(exc):
                pass
            else:
                raise ValueError(exc) from exc

    def revoke_service(self, username, service_name):
        if service_name.upper() in servicename_map:
            service_name = servicename_map[service_name.upper()]
        endpoint = f"users/{username}/services/{service_name}"
        try:
            self.delete_request(endpoint)
        except ValueError as exc:
            if "not granted" in str(exc):
                pass
            else:
                raise ValueError(exc) from exc

    def revoke_all_services(self, username):
        endpoint = f"users/{username}/services"
        resp = self.delete_request(endpoint)
        if resp.ok:
            if VERBOSE:
                print(f"All services revoked from {username}")
        elif resp.status_code == 401:
            raise ValueError(
                "Provided admin-username/password is incorrect or you are not allowed to do this operation"
            )

    def get_service(self, username, service_name):
        clean_service_name = servicename_map.get(service_name.upper())
        if not clean_service_name:
            raise ValueError(f"No such service: {service_name}")
        service_name = clean_service_name
        endpoint = f"users/{username}/services/{service_name}"
        data = self.get_request(endpoint)
        return data

    def set_password(self, username, password, service_name="LDAPS"):
        """Sets a password for a given service"""

        if service_name.upper() not in servicename_map:
            raise ValueError(f"Cannot set password for service: {service_name}. Sorry!")

        endpoint = (
            f"users/{username}/service/{servicename_map[service_name.upper()]}/password"
        )
        body = {"password": password}
        self.put_request(endpoint, body)
