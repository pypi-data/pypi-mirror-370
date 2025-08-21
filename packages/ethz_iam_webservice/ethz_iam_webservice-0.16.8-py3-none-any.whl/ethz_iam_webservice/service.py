from .utils import to_date

servicename_map = {
    "LDAP": "LDAP",
    "LDAPS": "LDAP",
    "MAILBOX": "Mailbox",
    "AD": "Active Directory",
    "VPN": "WLAN_VPN",
    "WLAN_VPN": "WLAN_VPN",
    "OPEN-DIRECTORY": "OpenDirectory",
    "OPENDIRECTORY": "OpenDirectory",
    "OD": "OpenDirectory",
    "ITETAUTH": "ItetAuth",
    "HESTAUTH": "HestAuth",
    "LDAPS-PROXY": "LDAPS-Proxy",
    "PHYSIK-MAIL": "Physik-Mail",
    "PHYSIKMAIL": "Physik-Mail",
}

class Service:
    def __init__(self, conn, username, service_name, data):
        self.__dict__["username"] = username
        self.__dict__["service_name"] = service_name
        self.__dict__["conn"] = conn
        # self.__dict__['data'] = data
        if data:
            for key in data:
                if key in ["delete_after", "login_until"]:
                    d = to_date(data[key])
                    data[key] = d.strftime("%Y-%m-%d")
                setattr(self, key, data[key])
        self.__dict__["updated_attrs"] = {}


class Mailbox(Service):
    def __dir__(self):
        return [
            "sn",
            "givenName",
            "displayName",
            "description",
            "mail",
            "isHidden",
            "noMailReceive",
            "quota",
            "homeDrive",
            "homeDirectory",
            "profilePath",
            "unixHomeDirectory",
            "loginShell",
            "primaryGroup",
            "unifiedMessagingTask",
            "telephoneNumber",
            "forward_address",
            "proxyAddresses",
        ]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        self.__dict__["updated_attrs"][name] = value

    def __getattr__(self, name):
        return self.__dict__[name]
