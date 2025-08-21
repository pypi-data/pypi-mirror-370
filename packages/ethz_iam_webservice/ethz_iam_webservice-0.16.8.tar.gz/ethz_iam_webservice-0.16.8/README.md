# ETHZ IAM Webservice

Manage users, groups and various services of the ETH Identity and Access Management system (IAM).

## Command Line Interface

When installing this module, the `iam` command is also installed. The **basic parameters which are always needed** – otherwise they will be asked interactivley – are:

```bash
$ iam -u admin-username --password MY-SECRET-PASSWORD
```

You can also set these environment variables instead:

```bash
$ export IAM_USERNAME=admin-username
$ export IAM_PASSWORD=MY-SECRET-PASSWORD
```

### Group

```bash
$ iam group --help                           # get extensive help text
# create new group
$ iam group --new id-test-test-01 --ag "ID SIS" -d 'some test description' -t AD -t LDAP ou=AGRL
$ iam group <group-name>                     # info about a group
$ iam group <group-name> -a user1 -a user2   # add new users
$ iam group <group-name> -r user3 -r user4   # remove users
```

### Mailing list

```bash
$ iam maillist --help                           # get extensive help text
$ iam maillist <group-name>                     # info about a group
$ iam maillist <group-name> -a user1 -a user2   # add new users
$ iam maillist <group-name> -r user3 -r user4   # remove users
```

### User

Get info about a person (identity). You might either provide a username, a NPID or a email address.

```bash
$ iam user --help
$ iam user username
$ iam user some.person@ethz.ch
$ iam user 123445
```

### Guest

**Create guests**. For the new guest a new username will automatically be generated. This user gets LDAP and VPN service granted. Because by policy the VPN password needs to differ from the other passwords, the result will present the two initial passwords that are set shortly after creating the guest.

**CLI**

```bash
$ iam guest get <username>
$ iam guest new --help
$ iam guest new -f firstname -l lastname -m first.last@unknown.org -d "my test guest" -h host_username -a "Admingroup Name"
{
    "firstName": "first",
    "lastName": "last",
    "mail ": "first.last@unknown.org",
    "host ": "host_username",
    "respAdminRole ": "Admingroup Name",
    "description": "my test guest",
    "dateOfBirth": "16.06.2000",
    "guestTechnicalContact": "somebody@ethz.ch",
    "notification": "To guest and host",
    "hostOrg": "06006",
    "startDate": "16.06.2021",
    "endDate": "16.06.2022",
    "username": "flast",
    "npid": "3210159",
    "init_ldap_password": "xxxxxxx",
}
```

**Default values:**

- `--technicalContact / -c` will default to the email address of the host
- `--notification / -n` will default to «gh», meaning **g**uest and **h**ost will be notified when a guest account expires.
- `--startDate / -s` is today.
- `--endDate / -e` is today + 1 year
- `--dateOfBirth / -b` is today's date in year 2000

**Extend guest**. After a year, you might want to extend the validity of your guest by another year or by a specific number of months

```bash
$ iam guest extend <username>               # will extend the guest by 1 year
$ iam guest extend <username> -m 6          # extend it by today+6 months
$ iam guest extend <username> -e 1.4.2022   # extend it until April 1st. 2022
$ iam guest extend <username> -e 2022-04-01 # same thing, different date format
```
