from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from dateutil.relativedelta import relativedelta

from .conn import IAMApi
from .user import UserAlternativeService, User
from .utils import (
    format_notification,
    to_date,
)


class Notification(Enum):
    GH = "To guest and host"
    GHT = "To guest, host and technical contact"
    HT = "To host and technical contact"
    G = "To guest only"
    GT = "To guest and technical contact"
    H = "To host"
    T = "To technical contact"


map_iamfields2internal = {
    "displayName": "displayname",
    "employeeType": "type",
    "firstname": "firstname",
    "lastname": "lastname",
    "gender": "gender",
    "salutation": "title",
    "mail": "mail",
    "department": "department",
    "dateofbirth": "birth_date",
    "startdate": "start_date",
    "endDate": "end_date",
    "createTimestamp": "cre_date",
    "modifyTimestamp": "mod_date",
    "npid": "npid",
    "nuid": "nuid",
    "persid": "persid",
    "uidNumber": "uidNumber",
    "gidnumber": "gidNumber",
    "orcid": "orcid",
    "userState": "state",
    "username": "username",
    "category": "category",
    "perscattext": "category",
    "guestTechnicalContact": "technical_contact",
    "host": "host_username",
    "hostOrg": "host_leitzahl",
    "notification": "notification",
    "description": "description",
    "respAdminRole": "host_admingroup",
}

map_internal2iamfields = {
    "host_username": "host",
    "host_leitzahl": "hostOrg",
    "host_admingroup": "respAdminRole",
}

guest_properties_required = [
    "firstname",
    "lastname",
    "mail",
    "description",
    "dateofbirth",
    "hostorg",
    "host",
    "technicalcontact",
    "admingroup",
    "notification",
    "startdate",
    "enddate",
]

guest_properties_optional = [
    "title",
    "salutation",
    "ahvNo",
    "addressLine1",
    "addressLine2",
    "addressLine3",
    "postCode",
    "place",
    "countryName",
]

guest_properties_update = [
    "description",
    "hostOrg",
    "host",
    "guestTechnicalContact",
    "endDate",
    "notification",
    "respAdminRole",
    "deactivationStartDate",
    "deactivationEndDate",
]


@dataclass
class Guest(User):
    host_username: int = -1
    host_leitzahl: int = -1
    host_admingroup: str = ""
    notification: Notification = Notification.GH
    technical_contact: str = ""
    type: str = ""
    category: str = ""
    end_date: date = field(default_factory=date.today)
    state: str = ""
    title: str = ""


class GuestService(IAMApi):

    def new_from_data(self, data):
        new_guest = {}
        for data_field in data:
            if data_field in map_iamfields2internal:
                new_guest[map_iamfields2internal[data_field]] = data[data_field]
            else:
                pass

        for date_field in ("start_date", "end_date", "cre_date", "mod_date"):
            if date_field not in new_guest or not new_guest[date_field]:
                continue
            new_guest[date_field] = to_date(new_guest[date_field])

        new_guest["mail"] = (
            new_guest["mail"][0] if len(new_guest.get("mail", [])) else None
        )

        guest = Guest(
            **{k: new_guest[k] for k in new_guest if k in Guest.__dataclass_fields__}
        )
        return guest

    def replace_field_values(self, new_obj):
        for key in new_obj.data.keys():
            setattr(self, key, getattr(new_obj, key))

    def get_guest(self, identifier):
        endpoint = f"/guests/{identifier}"
        data = self.get_request(endpoint=endpoint)
        return self.new_from_data(data)

    def search_guests(
        self,
        host_username: str | None = None,
        host_leitzahl: str | None = None,
        host_admingroup: str | None = None,
    ):
        """
        Search for guests by host_username, host_leitzahl or host_admingroup.
        returns a list of Guest objects.
        Example:
        {'createTimestamp': '2021-04-06T16:35:23', 'description': 'Authorized Leonhard Med guest', 'endDate': '04.03.2026', 'firstname': 'Daniel Jakob Silvester', 'gidnumber': '449484', 'lastname': 'Abler', 'mail': ['daniel.abler@hevs.ch'], 'modifyTimestamp': '2025-05-22T05:05:34', 'salutation': 'Herr', 'startDate': '06.04.2021', 'userState': 'ENABLED', 'username': 'dabler', 'guestTechnicalContact': 'leomed-support@id.ethz.ch', 'host': 'gpontrand', 'hostOrg': '06005', 'notification': 'To technical contact', 'respAdminRole': 'ID SIS'}
        """
        query = "&".join(
            [
                f"{map_internal2iamfields[k]}={v}"
                for k, v in locals().items()
                if v is not None and k != "self"
            ]
        )
        endpoint = f"/guests?{query}"
        guest_datas = self.get_request(endpoint=endpoint)
        guests = []
        for guest_data in guest_datas:
            guests.append(self.new_from_data(guest_data))
        return guests

    def extend(self, username: str, end_date=None, months=None):
        if end_date:
            end_date = to_date(end_date)
        elif months:
            today = date.today()
            end_date = today + relativedelta(months=int(months))
        else:
            today = date.today()
            end_date = today + relativedelta(months=12)
        body = {"endDate": end_date.strftime("%d.%m.%Y")}

        endpoint = f"/guests/{username}"
        data = self.put_request(endpoint=endpoint, body=body)
        guest = self.new_from_data(data)
        return guest

    def update(
        self,
        username,
        mail: str = "",
        description: str = "",
        host_username: str = "",
        host_admingroup: str = "",
        host_leitzahl: str = "",
        technical_contact: str = "",
        notification: Notification = Notification.GH,
        end_date: str = "",
        deactivation_start_date: str = "",
        deactivation_end_date: str = "",
    ):
        payload = {}
        if host_username:
            payload["host"] = host_username
        if mail:
            payload["mail"] = mail
        if host_admingroup:
            payload["respAdminRole"] = host_admingroup
        if description:
            payload["description"] = description
        if technical_contact:
            payload["guestTechnicalContact"] = technical_contact
        if notification:
            notification = format_notification(notification)
            payload["notification"] = notification
        if host_leitzahl:
            payload["hostOrg"] = host_leitzahl
        if end_date:
            payload["endDate"] = to_date(end_date).strftime("%Y-%m-%d")
        if deactivation_start_date is not None:
            payload["deactivationStartDate"] = to_date(
                deactivation_start_date
            ).strftime("%Y-%m-%d")
        if deactivation_end_date is not None:
            payload["deactivationEndDate"] = to_date(deactivation_end_date).strftime(
                "%Y-%m-%d"
            )

        endpoint = f"/guests/{username}"
        data = self.put_request(endpoint=endpoint, body=payload)
        guest = self.new_from_data(data)
        self.replace_field_values(guest)
        return self

    def create(
        self,
        firstname: str,
        lastname: str,
        mail: str,
        host_username: str,
        host_admingroup: str,
        host_leitzahl: str,
        description: str = "",
        birth_date: str = "",
        technical_contact: str = "",
        notification: str = "",
        start_date: str = "",
        end_date: str = "",
        salutation: str = "",
        ahvNo=None,
        address_line1: str = "",
        address_line2: str = "",
        address_line3: str = "",
        postcode: str = "",
        place: str = "",
        country: str = "",
    ):
        if birth_date is None:
            birth_date = date(2000, date.today().month, date.today().day)
        if start_date is None:
            start_date = date.today()
        else:
            start_date = to_date(start_date)
        if not end_date:
            end_date = start_date + relativedelta(days=365)
        elif (end_date - start_date).days > 365:
            raise ValueError(
                "Difference between endDate and startDate is more than 356 days."
            )

        host_users = UserAlternativeService().search_users(username=host_username)
        if not host_users:
            raise ValueError(f"no such host: {host_username}")

        host_user = host_users[0]

        if host_leitzahl is None:
            try:
                for perskat in host_user["perskats"]:
                    if perskat["perskat"] == "Mitarbeiter":
                        host_leitzahl = perskat["leitzahl"]
                        break
            except Exception:
                pass
        if host_leitzahl is None:
            raise ValueError("no host leitzahl for guest provided.")
        if technical_contact is None:
            try:
                technical_contact = host_user.mail
            except Exception:
                pass
            if not technical_contact:
                raise ValueError("no mail for guestTechnicalContact found.")
        if notification is None:
            notification = "gh"
        else:
            notification = format_notification(notification)

        body = {
            "firstName": firstname,
            "lastName": lastname,
            "mail": mail,
            "host": host_username,
            "respAdminRole": host_admingroup,
            "description": (
                f"guest of {host_username}" if description is None else description
            ),
            "dateOfBirth": birth_date.strftime("%d.%m.%Y"),
            "guestTechnicalContact": technical_contact,
            "notification": notification,
            "hostOrg": host_leitzahl,
            "startDate": start_date.strftime("%d.%m.%Y"),
            "endDate": end_date.strftime("%d.%m.%Y"),
            "salutation": salutation,
            "ahvNo": ahvNo,
            "addressLine1": address_line1,
            "addressLine2": address_line2,
            "addressLine3": address_line3,
            "postCode": postcode,
            "place": place,
            "countryName": country,
        }
        endpoint = "/guests"
        data = self.post_request(endpoint=endpoint, body=body)
        guest = self.new_from_data(data)
        return guest

    def delete(self, username):
        endpoint = f"/guests/{username}"
        self.delete_request(endpoint=endpoint)
