import json
import os
import sys
import signal
import time
import re
from dataclasses import asdict
from datetime import datetime

import click
import yaml
from click.exceptions import ClickException

from requests import ConnectionError as ConnError

from .user import UserService, UserAlternativeService
from .group import RecertificationPeriod, GroupAlternativeService, GroupService
from .guest import GuestService
from .realm import RealmService
from .maillist import MaillistService
from .netsupport import NetsupportService
from .service import servicename_map

recertification_period_map = {
    "A": "Annual",
    "Y": "Annual",
    "Q": "Quarterly",
    "B": "Biennial",
    "N": "No recertification",
}


class Credentials(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password


def handle_second_sigint(*_):
    click.echo("Script aborted.")
    sys.exit()


def handle_sigint(*_):
    click.echo(
        "Cannot abort operation, since the request was already sent to the IAM webservice. Hit CTRL-C during next 5 sec to abort the script anyway."
    )
    signal.signal(signal.SIGINT, handler=handle_second_sigint)
    time.sleep(5)
    click.echo("Resuming script...")
    signal.signal(signal.SIGINT, handler=handle_sigint)


pass_iam_credentials = click.make_pass_decorator(Credentials)


def _load_configuration(paths, filename=".ethz_iam_webservice"):
    if paths is None:
        paths = [os.path.expanduser("~")]

    # look in all config file paths
    # for configuration files and load them
    admin_accounts = []
    for path in paths:
        abs_filename = os.path.join(path, filename)
        if os.path.isfile(abs_filename):
            with open(abs_filename, "r", encoding="utf-8") as stream:
                try:
                    config = yaml.safe_load(stream)
                    for admin_account in config["admin_accounts"]:
                        admin_accounts.append(admin_account)
                except yaml.YAMLError as exc:
                    raise ClickException(str(exc)) from exc

    return admin_accounts
                        
@click.group()
@click.option(
    "-u",
    "--username",
    envvar="IAM_USERNAME",
    help="username of ETHZ IAM admin account. Can be set via IAM_USERNAME environment variable. If not set, you will be prompted for the username.",
)
@click.option(
    "--password",
    envvar="IAM_PASSWORD",
    help="password of ETHZ IAM admin account. Can be set via IAM_PASSWORD environment variable. If not set, you will be prompted for the password.",
)
@click.option(
    "--timeout",
    envvar="IAM_TIMEOUT",
    help="Timeout in seconds when querying the IAM API. Can be set via IAM_TIMEOUT environment variable. Default: 240 seconds.",
)
@click.version_option(prog_name="IAM command line tool")
@click.pass_context
def cli(ctx, username, password=None, timeout=240):
    """ETHZ IAM command-line tool."""
    ctx.help_option_names = ["-h", "--help"]
    ctx.obj = Credentials(username, password)
    if timeout:
        os.environ["IAM_TIMEOUT"] = str(timeout)


@cli.command("users", help="search for users at ETH Zurich")
@click.option("-u", "--username", help="username")
@click.option("-m", "--mail", help="email address of a user")
@click.option("-f", "--firstname", help="firstname of a user")
@click.option("-l", "--lastname", help="lastname of a user")
@click.option("-n", "--uidnumber", help="uidNumber of a user")
def get_users(
    username,
    mail,
    firstname,
    lastname,
    uidnumber,
):
    if not (username or mail or firstname or lastname or uidnumber):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
    user_alt = UserAlternativeService()
    users = user_alt.search_users(
        username=username,
        mail=mail,
        firstname=firstname,
        lastname=lastname,
        uidNumber=uidnumber,
    )
    click.echo(
        json.dumps(
            [asdict(person) for person in users],
            indent=4,
            sort_keys=True,
            ensure_ascii=False,
        )
    )

@cli.command("groups", help="search for groups at ETH Zurich. If indicated, only search in LDAP groups.")
@click.option("-u", "--username", help="Username that is member of a group (LDAP)")
@click.option("-n", "--group-name", help="Name of the group. Supports wildcards * (LDAP)")
@click.option("-g", "--gidnumber", help="gidNumber of the group")
@click.option(
    "-t", "--type", "type_", help="type of the group, e.g. custom, lz, realm, "
)
@click.option("-m", "--mail", help="email of a member of the group (LDAP)")
@click.option("-f", "--firstname", help="firstname of a member of the group (LDAP)")
@click.option("-l", "--lastname", help="lastname of a member of the group (LDAP)")
@click.option("-a", "--admingroup", help="name of the admingroup that manages this group")
@click.option(
    "--member-details",
    is_flag=True,
    help="Show some details of every member in the groups",
)
@click.option(
    "-p",
    "--prop",
    multiple=True,
    help="define properties you want to display, e.g. -p cn -p members",
)
@click.option(
    "--no-members", is_flag=True, help="Only show the group infos, no group users"
)
def get_groups(
    username,
    group_name,
    gidnumber,
    type_,
    mail,
    firstname,
    lastname,
    admingroup,
    member_details,
    prop,
    no_members,
):
    if not (
        username
        or group_name
        or gidnumber
        or type_
        or mail
        or firstname
        or lastname
        or member_details
        or admingroup
    ):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
    if prop:
        if "members" not in prop:
            no_members = True
        for p in prop:
            valid_props = ("cn", "description", "gidNumber", "members", "type")
            if p not in valid_props:
                raise click.ClickException(
                    f"{p} is not a valid property. Valid properties are: {', '.join(valid_props)}"
                )
    if admingroup:
        ctx = click.get_current_context()
        groupservice = GroupService(ctx.obj.username, ctx.obj.password)
        groups = groupservice.get_groups_for_admingroup(admingroup=admingroup)
        click.echo(
            json.dumps(
                [asdict(group) for group in groups],
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return

    groupaltservice = GroupAlternativeService()
    groups = groupaltservice.search_groups(
        group_name=group_name,
        member=username,
        gidnumber=gidnumber,
        group_type=type_,
        email=mail,
        firstname=firstname,
        lastname=lastname,
        member_details=member_details,
        no_members=no_members,
    )
    if prop:
        click.echo(
            json.dumps(
                [{p: getattr(group, p) for p in prop} for group in groups],
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
    else:
        click.echo(
            json.dumps(
                [asdict(group) for group in groups],
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )


@cli.command("group", help="manage groups")
@click.argument("groupname")   
@click.option(
    "--new-name",
    help="New name for this group (only used when renaming an existing group)",
)
@click.option(
    "-d",
    "--description",
    help="Description about this group.",
)
@click.option(
    "--agroup",
    "--ag",
    help="Admingroup for this group, mandatory for new a group",
)
@click.option(
    "-t",
    "--target",
    help="Add target system for this group. Can be used multiple times: -t AD -t LDAP",
    multiple=True,
)
@click.option(
    "--remove-target",
    "--rt",
    help="Remove target system for this group. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--organizational-unit",
    "--ou",
    help="OU (organizational unit) for this group, e.g. AGRL, USYS, INFK etc. where this group should be stored. If not specified, this group will appear in OU=Custom,OU=ETHLists",
)
@click.option(
    "--certification-period",
    "--cp",
    help="Define a certification period, whithin this group needs to be verified. [A]nnually, [B]iennial, [Q]uarterly, [N]one (default)",
)
@click.option(
    "--certification-note",
    "--cn",
    help="Reason (certification note) in case you don't want to periodically certify this group",
)
@click.option(
    "-m",
    "--manager",
    help="Username of the group manager for this group. Can appear multiple times. -m '' to remove all managers",
    multiple=True,
)
@click.option(
    "-a",
    "--add",
    help="Add username as member to group. Can be used multiple times: -a user1 -a user2",
    multiple=True,
)
@click.option(
    "-s",
    "--set",
    help="Set username as member to group and replaces existing ones. Can be used multiple times: -s user1 -s user2",
    multiple=True,
)
@click.option(
    "-r",
    "--remove",
    help="Remove username as member to group. Can be used multiple times: -r user1 -r user2",
    multiple=True,
)
@click.option(
    "--add-subgroup",
    "--as",
    help="Add subgroup as member to group. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--set-subgroup",
    "--ss",
    help="Set subgroup as member to group and replaces existing subgroups. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--remove-subgroup",
    "--rs",
    help="Remove subgroup as member from group. Can be used multiple times.",
    multiple=True,
)
@click.option("--new", "-n", is_flag=True, help="Create a group")
@click.option("--update", is_flag=True, help="Update a group")
@click.option("--recertify", is_flag=True, help="Recertify a group")
@click.option("--delete", is_flag=True, help="Delete a group")
@pass_iam_credentials
def manage_group(
    credentials,
    groupname,
    new_name=None,
    description=None,
    agroup=None,
    target=None,
    remove_target=None,
    organizational_unit=None,
    certification_period=None,
    certification_note="No recertification needed",
    manager=None,
    add=None,
    set=None,
    remove=None,
    add_subgroup=None,
    set_subgroup=None,
    remove_subgroup=None,
    new=False,
    update=False,
    recertify=False,
    delete=False,
):
    """manage groups
    Name of the group must start with the admingroup's nickname,
    followed by a dash, e.g. agrl-xxxx
    """
    groupservice = GroupService(credentials.username, credentials.password)
    group = None

    if re.search(r"^\d+$", str(groupname)):
        # if groupname is a number, assume it's a gidNumber
        group = groupservice.get_group(groupname)
        groupname = group.name

    if certification_period:
        if certification_period.upper() not in recertification_period_map:
            raise ClickException(
                "Please specify [A]nnual, [B]iennial, [Q]uarterly or [N]o recertification period."
            )
        certification_period = recertification_period_map[certification_period.upper()]
    

    signal.signal(signal.SIGINT, handler=handle_sigint)
    if new:
        if certification_period is None:
            certification_period = RecertificationPeriod.NONE.value
        if not agroup:
            raise ClickException("Please provide an admingroup with --agroup")
        if not description:
            raise ClickException(
                "Description of the group is missing. Use -d 'some description'"
            )
        try:
            group = groupservice.create(
                name=groupname,
                description=description,
                admingroup=agroup,
                targets=[t.upper() for t in target] if target else None,
                group_ad_ou=organizational_unit,
                certification_period=certification_period,
                certification_note=certification_note,
                managers=manager,
            )
        except ValueError as exc:
            raise ClickException(f"Could not create group {groupname}: {str(exc)}") from exc
        except ConnError as exc:
            raise ClickException(
                f"Cannot connect to IAM webservice at {exc.request.url}"
            ) from exc
    elif delete:
        try:
            groupservice.delete(groupname)
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
        click.echo(f"Successfully deleted group {groupname}")
        return
    elif recertify:
        groupservice.recertify(groupname)
        click.echo(f"Group {groupname} successfully recertified.")
    elif update:
        try:
            new_group = groupservice.update(
                current_name=groupname,
                new_name=new_name,
                description=description,
                group_ad_ou=organizational_unit,
                certification_period=certification_period,
                certification_note=certification_note,
                managers=list(manager),
            )
            group = new_group if new_group else group
        except ValueError as exc:
            raise ClickException(f"Could not update group {groupname}: {str(exc)}") from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    if add or add_subgroup:
        group = groupservice.add_members(name=groupname, users=add, subgroups=add_subgroup)
    if set or set_subgroup:
        if set and set_subgroup:
            pass
        else:
            # if only members or subgroups are set, we need to make sure
            # members or subgroups are not accidentally removed
            group = groupservice.get_group(groupname)
            if not set:
                set = group.members
            if not set_subgroup:
                set_subgroup = group.subgroups

        try:
            group = groupservice.set_members(name=groupname, users=set, subgroups=set_subgroup)
        except ValueError as exc:
            raise ClickException(f"Could not set members for group {groupname}: {str(exc)}") from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
    if remove or remove_subgroup:
        group = groupservice.remove_members(name=groupname, users=remove, subgroups=remove_subgroup)
    if target and not new:
        targets = [t.upper() for t in target]
        try:
            groupservice.set_targets(groupname, targets)
        except ValueError as exc:
            if "already present" in str(exc):
                pass
            else:
                raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
        group = groupservice.get_group(groupname)
    if remove_target:
        targets = [t.upper() for t in remove_target]
        try:
            groupservice.remove_targets(groupname, targets)
        except ValueError as exc:
            if "already not present" in str(exc):
                pass
            else:
                raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
        group = groupservice.get_group(groupname)
    if not group:
        try:
            group = groupservice.get_group(groupname)
        except ValueError as exc:
            raise ClickException(f"No such group: {groupname}") from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    click.echo(json.dumps(asdict(group), indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("guests", help="search for guests")
@click.option("-l", "--leitzahl", help="Leitzahl of the host organization")
@click.option("-h", "--host", help="username of the guest host")
@click.option("-a", "--admingroup", help="responsible admin group of the guest")
@click.option("--ends-in-days", help="search for guests that end in this many days or less", type=int)
@click.option("-c", "--contact", help="email address of the technical contact")
@pass_iam_credentials
def search_guests(credentials, leitzahl, host, admingroup, ends_in_days, contact):
    """Search for guests at ETH Zurich.
    """

    guestservice = GuestService(credentials.username, credentials.password)
    if not (leitzahl or host or admingroup):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    try:
        guests = guestservice.search_guests(host_leitzahl=leitzahl, host_username=host, host_admingroup=admingroup)
    except ValueError:
        guests = []
    if ends_in_days:
        guests = [guest for guest in guests if guest.end_date and (guest.end_date - datetime.today().date()).days <= ends_in_days]
    if contact:
        guests = [guest for guest in guests if guest.technical_contact and contact.lower() == guest.technical_contact.lower()]

    click.echo(
        json.dumps(
            [asdict(guest) for guest in guests],
            # convert datetime objects to string
            default=str,
            indent=4,
            sort_keys=True,
            ensure_ascii=False
        )
    )

@cli.group("guest", help="manage guests")
def guest_group():
    pass

@guest_group.command("get", help="get an existing guest")
@click.argument("username")
@pass_iam_credentials
def get_guest(credentials, username):
    guestservice = GuestService(credentials.username, credentials.password)
    try:
        guest = guestservice.get_guest(username)
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request.url}"
        ) from exc
    except ValueError as exc:
        raise ClickException(f"No such guest: {username}") from exc
    except PermissionError as exc:
            raise ClickException(exc) from exc
    click.echo(json.dumps(asdict(guest), default=str, indent=4, sort_keys=True, ensure_ascii=False))


@guest_group.command(
    "extend", help="extend validation of an existing guest. Default is today+1 year."
)
@click.option(
    "-e", "--end-date", help="specify end date of guest (YYYY-MM-DD or DD.MM.YYYY)."
)
@click.option(
    "-m", "--months", help="extend validation of an existing guest by this many months."
)
@click.argument("username")
@pass_iam_credentials
def extend_guest(credentials, end_date, months, username):
    guestservice = GuestService(credentials.username, credentials.password)
    try:
        guest = guestservice.extend(username=username, end_date=end_date, months=months)
        click.echo(json.dumps(guest, default=str, indent=4, sort_keys=True, ensure_ascii=False))
    except ValueError as exc:
        raise ClickException(str(exc)) from exc
    except PermissionError as exc:
        raise ClickException(exc) from exc


@click.option("-d", "--description", help="")
@click.option("-m", "--mail", required=True, help="email address")
@click.option("-h", "--host-username", help="ETHZ Username of host")
@click.option(
    "-a",
    "--host-admingroup",
    help="Name of the admin group this guest should be connected to. Default: same as the technical user which is creating this guest.",
)
@click.option(
    "-o",
    "--host-leitzahl",
    help="Leitzahl of host organization, see http://www.org.ethz.ch. Default: Leitzahl of the host.",
)
@click.option(
    "-c",
    "--technical-contact",
    help="email address of technical contact. Default: email of the host of this guest.",
)
@click.option(
    "-n",
    "--notification",
    help="g=guest, h=host, t=technical contact. Use any combination of the 3 chars. Defaults to «gh»",
)
@click.option(
    "-e", "--end-date", help="End date of guest (YYYY-MM-DD). Default: today+1 year"
)
@click.option(
    "--deactivation-start-date",
    help='Deactivation start date of guest (YYYY-DD-MM). Set it to "" to remove',
)
@click.option(
    "--deactivation-end-date",
    help='Deactivation end date of guest (YYYY-MM-DD). Set it to "" to remove',
)
@guest_group.command("update", help="update an existing guest")
@click.argument("username")
@pass_iam_credentials
def update_guest(
    credentials,
    description,
    mail,
    host_leitzahl,
    host_username,
    technical_contact,
    host_admingroup,
    notification,
    end_date,
    username,
    deactivation_start_date,
    deactivation_end_date,
):
    guestservice = GuestService(credentials.username, credentials.password)
    try:
        signal.signal(signal.SIGINT, handler=handle_sigint)
        guest = guestservice.update(
            username=username,
            mail=mail,
            host_username=host_username,
            host_admingroup=host_admingroup,
            description=description,
            technical_contact=technical_contact,
            notification=notification,
            host_leitzahl=host_leitzahl,
            end_date=end_date,
            deactivation_start_date=deactivation_start_date,
            deactivation_end_date=deactivation_end_date,
        )
        click.echo(json.dumps(asdict(guest), default=str, indent=4, sort_keys=True, ensure_ascii=False))
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request}"
        ) from exc


@guest_group.command("delete", help="delete an existing guest")
@click.argument("username")
@pass_iam_credentials
def delete_guest(
    credentials,
    username,
):
    guestservice = GuestService(credentials.username, credentials.password)
    try:
        signal.signal(signal.SIGINT, handler=handle_sigint)
        guestservice.delete(username)
        click.echo(f"Guest {username} successfully deleted.")
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice at {exc.request.url}"
        ) from exc


@guest_group.command("new", help="create a new guest")
@click.option("-f", "--firstname", required=True, help="given name")
@click.option("-l", "--lastname", required=True, help="surname")
@click.option("-m", "--mail", required=True, help="email address")
@click.option("-d", "--description", required=True, help="")
@click.option("-h", "--host-username", required=True, help="ETHZ Username of host")
@click.option(
    "-a",
    "--host-admingroup",
    required=True,
    help="Name of the administrative group that hosts this guest.",
)
@click.option(
    "-o",
    "--host-leitzahl",
    help="Leitzahl of host organization, see http://www.org.ethz.ch. If not provided, the leitzahl of the host will be used.",
)
@click.option(
    "-c",
    "--technical-contact",
    help="email address of technical contact. If not provided, the email address of the host will be used.",
)
@click.option(
    "-b",
    "--birth-date",
    help="birthdate in YYYY-MM-DD format. Default: Today's date + year 2000",
)
@click.option(
    "-n",
    "--notification",
    default="gh",
    help="g=guest, h=host, t=technical contact. Use any combination of the 3 chars. ",
)
@click.option(
    "-s", "--start-date", help="Start date of guest (YYYY-DD-MM). Default: today"
)
@click.option(
    "-e", "--end-date", help="End date of guest (YYYY-MM-DD). Default: today+1 year"
)
@click.option(
    "--init-password",
    is_flag=True,
    help="Set initial password and return it in cleartext",
)
@click.option(
    "--ignore-existing-email",
    is_flag=True,
    help="Ignore the few cases where users with the same email address already exists (usually Empa users)",
)
@pass_iam_credentials
def new_guest(
    credentials,
    firstname,
    lastname,
    mail,
    description,
    birth_date,
    host_leitzahl,
    host_username,
    technical_contact,
    host_admingroup,
    notification,
    start_date,
    end_date,
    init_password,
    ignore_existing_email,
):

    guestservice = GuestService(credentials.username, credentials.password)
    userservice = UserService(credentials.username, credentials.password)
    useralternativeservice = UserAlternativeService()
    try:
        if not ignore_existing_email:
            persons = useralternativeservice.search_users(mail=mail)
            if persons:
                raise ClickException(
                    f"Account(s) with same email address already exists: {','.join([person['uid'] for person in persons])}"
                )
            if not host_leitzahl:
                # if no host leitzahl is given, use the leitzahl of the host
                relations = userservice.get_relations(host_username)
                for relation in relations:
                    if relation.beziehung == "Mitarbeiter":
                        host_leitzahl = relation.leitzahl
                        break
                if not host_leitzahl:
                    raise ClickException(
                        f"Host {host_username} has no Leitzahl set. Please provide a Leitzahl with -o"
                    )
                
        signal.signal(signal.SIGINT, handler=handle_sigint)
        guest = guestservice.create(
            firstname=firstname,
            lastname=lastname,
            mail=mail,
            birth_date=birth_date,
            host_username=host_username,
            host_admingroup=host_admingroup,
            description=description,
            technical_contact=technical_contact,
            notification=notification,
            host_leitzahl=host_leitzahl,
            start_date=start_date,
            end_date=end_date,
        )
    except ConnError as exc:
        raise ClickException(
            f"Cannot connect to IAM webservice: {str(exc)}"
        ) from exc
    except ValueError as exc:
        raise ClickException(str(exc)) from exc
    except PermissionError as exc:
        raise ClickException(exc) from exc
    


    click.echo(json.dumps(asdict(guest), default=str, indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("user", help="manage IAM users")
@click.argument("username")
@click.option("-r", "--show-relations", is_flag=True, help="show relations of this user")
@click.option("-p", "--show-personas", is_flag=True, help="show personas of this user")
@click.option("-s", "--show-services", is_flag=True, help="show services of this user")
@click.option("-d", "--delete", is_flag=True, help="delete this user")
@pass_iam_credentials
def get_user(
    credentials,
    show_relations,
    show_personas,
    show_services,
    username,
    delete,
):

    userservice = UserService(credentials.username, credentials.password)
    if "@" in username:
        users = userservice.search_users(email=username)
        if not users:
            raise ClickException(f"No user found with email {username}.")
        user = users[0]
    elif re.match(r"^\d+$", username):
        # if username is a number, assume it's a uidNumber
        users = userservice.search_users(uidNumber=username)
        if not users:
            users = userservice.search_users(npid=username)
        user = users[0] 
    else:
        try:
            user = userservice.get_user(username)
        except ValueError as exc:
            raise ClickException(f"No such user: {username}.") from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
    
    if show_personas:
        personas = userservice.get_personas(username)
        user.personas = personas

    if show_relations:
        relations = userservice.get_relations(username)
        user.relations = relations 

    if show_services:
        services = userservice.get_services(username)
        user.services = services

    if delete:
        click.confirm("Do you really want to delete this user?", abort=True)
        try:
            userservice.delete(username)
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    print(json.dumps(asdict(user), default=str, indent=4, sort_keys=True, ensure_ascii=False))

@cli.command("netsupport", help="manage netsupport-groups")
@click.argument("netsupport-group")
@click.option(
    "-a",
    "--add",
    help="Add username as member to netsupport-group. Can be used multiple times: -a user1 -a user2",
    multiple=True,
)
@click.option(
    "-r",
    "--remove",
    help="Remove username as member to netsupport-group. Can be used multiple times: -r user1 -r user2",
    multiple=True,
)
@click.option(
    "--add-subgroup",
    "--as",
    help="Add subgroup as member to netsupport-group. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--remove-subgroup",
    "--rs",
    help="Remove subgroup as member from netsupport-group. Can be used multiple times.",
    multiple=True,
)
@pass_iam_credentials
def manage_netsupport(
    credentials,
    netsupport_group,
    add=None,
    remove=None,
    add_subgroup=None,
    remove_subgroup=None,
):
    netsupportservice = NetsupportService(credentials.username, credentials.password)
    if add or add_subgroup:
        try:
            realm = netsupportservice.add_members(
                name=netsupport_group, users=add, subgroups=add_subgroup
            )
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
    elif remove or remove_subgroup:
        try:
            realm = netsupportservice.remove_members(
                name=netsupport_group, users=remove, subgroups=remove_subgroup
            )
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    try:
        realm = netsupportservice.get(netsupport_group)
    except ValueError as exc:
        raise ClickException(f"No such netsupport group: {netsupport_group}.") from exc
    except PermissionError as exc:
            raise ClickException(exc) from exc

    print(json.dumps(asdict(realm), default=str, indent=4, sort_keys=True, ensure_ascii=False))
    
    
@cli.command("maillist", help="manage mailing lists. Maillistname can be either the name of the mailing list or the email address of the mailing list.")
@click.argument("maillistname")
@click.option(
    "-a",
    "--add",
    help="Add username as member to a mailing lists. Can be used multiple times: -a user1 -a user2",
    multiple=True,
)
@click.option(
    "-r",
    "--remove",
    help="Remove username as member to a mailing list. Can be used multiple times: -r user1 -r user2",
    multiple=True,
)
@click.option(
    "--add-subgroup",
    "--as",
    help="Add subgroup as member to a mailing list. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--remove-subgroup",
    "--rs",
    help="Remove subgroup as member from a mailing list. Can be used multiple times.",
    multiple=True,
)
@pass_iam_credentials
def manage_maillist(
    credentials,
    maillistname,
    add=None,
    remove=None,
    add_subgroup=None,
    remove_subgroup=None,
):
    maillistservice = MaillistService(credentials.username, credentials.password)
    if "@" in maillistname:
        # Identify maillist by email address
        maillist = maillistservice.get_maillists_for_mail(maillistname)
        maillistname = maillist.name

    if add or add_subgroup:
        try:
            maillist = maillistservice.add_members(
                name=maillistname, users=add, groups=add_subgroup
            )
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
    elif remove or remove_subgroup:
        try:
            maillist = maillistservice.remove_members(
                name=maillistname, users=remove, groups=remove_subgroup
            )
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    try:
        maillist = maillistservice.get(maillistname)
    except ValueError as exc:
        raise ClickException(f"No such mailing list: {maillistname}.") from exc
    except PermissionError as exc:
            raise ClickException(exc) from exc

    print(json.dumps(asdict(maillist), default=str, indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("maillists", help="search for mailinglists")
@click.option("-m", "--manager", help="manager of mailing list")
@click.option("-a", "--admingroup", help="name of the admingroup that manages this group")
@click.option("-n", "--name-only", help="only show the names of the mailing lists", is_flag=True)
def get_mailinglists(
    manager,
    admingroup,
    name_only=False,
):
    if not (
        manager
        or admingroup
    ):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if admingroup:
        ctx = click.get_current_context()
        groupservice = MaillistService(ctx.obj.username, ctx.obj.password)
        if name_only:
            mailinglists = groupservice.get_maillist_names_for_admingroup(admingroup)
            click.echo(
                json.dumps(
                    mailinglists,
                    indent=4,
                    sort_keys=True,
                    ensure_ascii=False,
                )
            )
            return
        mailinglists = groupservice.get_maillists_for_admingroup(admingroup)
        click.echo(
            json.dumps(
                [asdict(group) for group in mailinglists],
                default=str,
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        return
    

@cli.command("realm", help="manage realms")
@click.argument("realmname")
@click.option(
    "-a",
    "--add",
    help="Add username as member to group. Can be used multiple times: -a user1 -a user2",
    multiple=True,
)
@click.option(
    "-r",
    "--remove",
    help="Remove username as member to group. Can be used multiple times: -r user1 -r user2",
    multiple=True,
)
@click.option(
    "--add-subgroup",
    "--as",
    help="Add subgroup as member to group. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "--remove-subgroup",
    "--rs",
    help="Remove subgroup as member from group. Can be used multiple times.",
    multiple=True,
)
@pass_iam_credentials
def manage_realm(
    credentials,
    realmname,
    add=None,
    remove=None,
    add_subgroup=None,
    remove_subgroup=None,
):
    realmservice = RealmService(credentials.username, credentials.password)
    if add or add_subgroup:
        try:
            realm = realmservice.add_members(
                name=realmname, users=add, subgroups=add_subgroup
            )
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc
    elif remove or remove_subgroup:
        try:
            realm = realmservice.remove_members(
                name=realmname, users=remove, subgroups=remove_subgroup
            )
        except ValueError as exc:
            raise ClickException(str(exc)) from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    try:
        realm = realmservice.get(realmname)
    except ValueError as exc:
        raise ClickException(f"No such realm: {realmname}.") from exc
    except PermissionError as exc:
            raise ClickException(exc) from exc

    print(json.dumps(asdict(realm), default=str, indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("service", help="manage services of IAM users")
@click.argument("username")
@click.option(
    "-g",
    "--grant",
    multiple=True,
    help="grant a service to this user, e.g. LDAP, Mailbox, WLAN_VPN. Use this option for every service you want to grant",
)
@click.option(
    "-r",
    "--revoke",
    multiple=True,
    help="revoke a service from this user, e.g. LDAP, Mailbox, WLAN_VPN. Use this option for every service you want to revoke",
)
@click.option(
    "--revoke-all",
    is_flag=True,
    help="revoke all services from this user.",
)
@pass_iam_credentials
def manage_service(
    credentials,
    username,
    grant=None,
    revoke=None,
    revoke_all=None,
):
    userservice = UserService(credentials.username, credentials.password)
    if grant:
        for service_name in grant:
            if service_name.upper() not in servicename_map:
                raise click.ClickException(
                    f"Service {service_name} is not a valid service name. Valid service names are: {', '.join(servicename_map.keys())}"
                )
            try:
                userservice.grant_service(username, servicename_map[service_name.upper()])
            except ValueError as exc:
                raise click.ClickException(str(exc))
            except PermissionError as exc:
                raise ClickException(exc) from exc

    elif revoke:
        for service_name in revoke:
            if service_name.upper() not in servicename_map:
                raise click.ClickException(
                    f"Service {service_name} is not a valid service name. Valid service names are: {', '.join(servicename_map.keys())}"
                )
            try:
                userservice.revoke_service(username, service_name=servicename_map[service_name.upper()])
            except ValueError as exc:
                raise click.ClickException(str(exc))
            except PermissionError as exc:
                raise ClickException(exc) from exc
    elif revoke_all:
        if not click.confirm(
            f"Do you really want to revoke all services from user {username}?"
        ):
            click.echo("Aborted.")
            return
        try:
            userservice.revoke_all_services(username)
        except ValueError as exc:
            raise click.ClickException(str(exc))
        except PermissionError as exc:
            raise ClickException(exc) from exc
        click.echo(f"All services for user {username} successfully revoked.")
    
    if not revoke_all:
        # display all services of this user after granting or revoking
        services = userservice.get_services(username)
        click.echo(json.dumps([asdict(service) for service in services], default=str, indent=4, sort_keys=True, ensure_ascii=False))


@cli.command("persona", help="manage personas of IAM users")
@click.argument("username")
@click.option(
    "-d",
    "--set-description",
    help="set a description for the persona. Use this option to set a description for the persona.",
)
@click.option(
    "-n",
    "--set-display-name",
    help="set a display name for the persona. Use this option to set a display name for the persona.",
)
@click.option(
    "-o",
    "--set-owner",
    help="set a owner for the persona. Use this option to set a owner for the persona.",
)
@pass_iam_credentials
def manage_persona(
    credentials,
    username,
    set_description=None,
    set_display_name=None,
    set_owner=None,
):
    """Manage personas of IAM users."""
    userservice = UserService(credentials.username, credentials.password)

    try:
        persona_owner = userservice.get_owner_of_persona(username)
    except ValueError as exc:
        raise ClickException(f"No such persona: {username}.") from exc
    except PermissionError as exc:
            raise ClickException(exc) from exc

    changes = {}
    if set_description:
        changes["description"] = set_description
    if set_display_name:
        changes["display_name"] = set_display_name
    if set_owner:
        changes["owner"] = set_owner

    if changes:
        try:
            userservice.update_persona(host_username=persona_owner.username, username=username, **changes)
        except ValueError as exc:
            raise ClickException(f"Failed to update persona {username}: {exc}") from exc
        except PermissionError as exc:
            raise ClickException(exc) from exc

    personas = userservice.get_personas(persona_owner.username)

    # Return the owner of that persona with only
    # the current persona
    persona_owner.personas = [persona for persona in personas if persona.username == username]
    
    click.echo(json.dumps(asdict(persona_owner), default=str, indent=4, sort_keys=True, ensure_ascii=False))

cli = click.help_option("-h", "--help")(cli)


if __name__ == "__main__":
    cli()
