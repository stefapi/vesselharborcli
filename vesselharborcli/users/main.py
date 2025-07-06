#  Copyright (c) 2024-2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#
#
#
#      ______                 _____
#     / ____/___ ________  __/ ___/___  ______   _____  _____
#    / __/ / __ `/ ___/ / / /\__ \/ _ \/ ___/ | / / _ \/ ___/
#   / /___/ /_/ (__  ) /_/ /___/ /  __/ /   | |/ /  __/ /
#  /_____/\__,_/____/\__, //____/\___/_/    |___/\___/_/
#                   /____/
#
#  Apache License
#  ================
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from ..core.auth import AuthenticationError
from ..core.config import get_config
from ..service import svc_class
from ..version import __software__


from .users import get_APIuser, UserCreate, UserUpdate, ChangePassword, APIError
import sys

__SOFTWARE__ = __software__.upper()
commands = {
    "list": ["list_users", [], {}, 'Lists Users'],
    "get": ["get_user", ['user_id'], {}, 'Gets User'],
    "create": ["create_user", ['username', 'first_name', 'last_name', 'email', 'password', 'organization_id?'], {}, 'Creates User'],
    "update": ["update_user", ['user_id', 'username?', 'first_name?', 'last_name?', 'email?'], {}, 'Updates User'],
    "delete": ["delete_user", ['user_id'], {}, 'Deletes User'],
    "change-password": ["change_password", ['user_id', 'new_password', 'current_password?'], {}, 'Changes User Password'],
}


class users_services(svc_class):
    default_config = {
    }

    params_link = {
    }

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        return ("user", f"Manage {__software__} users")

    @staticmethod
    def params(parser):
        subparsers = parser.add_subparsers(dest='command', title='Subcommands', required=True)

        # list
        list_parser = subparsers.add_parser('list', help='List users')
        list_parser.add_argument('--email', help='Filter by email')
        list_parser.add_argument('--skip', type=int, default=0, help='Number of users to skip')
        list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of users to return')
        list_parser.set_defaults(func='list_users')

        # get
        get_parser = subparsers.add_parser('get', help='Get user details')
        get_parser.add_argument('user_id', type=int, help='User ID')
        get_parser.set_defaults(func='get_user')

        # create
        create_parser = subparsers.add_parser('create', help='Create new user')
        create_parser.add_argument('--username', help='Username', required=True)
        create_parser.add_argument('--first-name', help='First name', required=True)
        create_parser.add_argument('--last-name', help='Last name', required=True)
        create_parser.add_argument('--email', help='Email address', required=True)
        create_parser.add_argument('--password', help='Password', required=True)
        create_parser.add_argument('--organization-id', type=int, help='Organization ID to attach user to')
        create_parser.set_defaults(func='create_user')

        # update
        update_parser = subparsers.add_parser('update', help='Update user')
        update_parser.add_argument('user_id', type=int, help='User ID')
        update_parser.add_argument('--username', help='New username')
        update_parser.add_argument('--first-name', help='New first name')
        update_parser.add_argument('--last-name', help='New last name')
        update_parser.add_argument('--email', help='New email address')
        update_parser.set_defaults(func='update_user')

        # delete
        delete_parser = subparsers.add_parser('delete', help='Delete user')
        delete_parser.add_argument('user_id', type=int, help='User ID')
        delete_parser.set_defaults(func='delete_user')

        # change-password
        password_parser = subparsers.add_parser('change-password', help='Change user password')
        password_parser.add_argument('user_id', type=int, help='User ID')
        password_parser.add_argument('--new-password', help='New password', required=True)
        password_parser.add_argument('--current-password', help='Current password (required for own password)')
        password_parser.set_defaults(func='change_password')

    @staticmethod
    def test_name(name):
        return name == __software__ + 'user'

    @staticmethod
    def cmd_name(name):
        return name == 'user'

    def run(self):
        config = get_config()
        args = config.args

        # Create API client with complete configuration
        api = get_APIuser(config)

        try:
            if args.command == 'list':
                users = api.list_users(
                    skip=args.skip,
                    limit=args.limit,
                    email=getattr(args, 'email', None)
                )
                print(f"Users ({len(users)}):")
                for user in users:
                    status = " (superadmin)" if user.is_superadmin else ""
                    print(f"  {user.id}: {user.username} ({user.first_name} {user.last_name}) - {user.email}{status}")

            elif args.command == 'get':
                user = api.get_user(args.user_id)
                print(f"User details:")
                print(f"  ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Name: {user.first_name} {user.last_name}")
                print(f"  Email: {user.email}")
                print(f"  Superadmin: {user.is_superadmin}")
                if user.tags:
                    print(f"  Tags: {', '.join([tag.get('value', '') for tag in user.tags])}")

                # Get and display user organizations
                organizations = api.get_user_organizations(args.user_id)
                if organizations:
                    org_names = []
                    for org in organizations:
                        if isinstance(org, dict):
                            org_names.append(f"{org.get('name', 'Unknown')} (ID: {org.get('id', 'N/A')})")
                        else:
                            org_names.append(str(org))
                    print(f"  Organizations: {', '.join(org_names)}")
                else:
                    print(f"  Organizations: None")

            elif args.command == 'create':
                new_user = api.create_user(
                    UserCreate(
                        username=args.username,
                        first_name=getattr(args, 'first_name'),
                        last_name=getattr(args, 'last_name'),
                        email=args.email,
                        password=args.password
                    ),
                    organization_id=getattr(args, 'organization_id', None)
                )
                print(f"User created successfully:")
                print(f"  ID: {new_user.id}")
                print(f"  Username: {new_user.username}")
                print(f"  Name: {new_user.first_name} {new_user.last_name}")
                print(f"  Email: {new_user.email}")

            elif args.command == 'update':
                # Only include fields that were provided
                update_data = {}
                if args.username:
                    update_data['username'] = args.username
                if getattr(args, 'first_name', None):
                    update_data['first_name'] = getattr(args, 'first_name')
                if getattr(args, 'last_name', None):
                    update_data['last_name'] = getattr(args, 'last_name')
                if args.email:
                    update_data['email'] = args.email

                if not update_data:
                    print("No update fields provided", file=sys.stderr)
                    return 1

                # Set defaults for required fields if not provided
                current_user = api.get_user(args.user_id)
                update_data.setdefault('username', current_user.username)
                update_data.setdefault('first_name', current_user.first_name)
                update_data.setdefault('last_name', current_user.last_name)
                update_data.setdefault('email', current_user.email)

                updated_user = api.update_user(
                    args.user_id,
                    UserUpdate(**update_data)
                )
                print(f"User updated successfully:")
                print(f"  ID: {updated_user.id}")
                print(f"  Username: {updated_user.username}")
                print(f"  Name: {updated_user.first_name} {updated_user.last_name}")
                print(f"  Email: {updated_user.email}")

            elif args.command == 'delete':
                api.delete_user(args.user_id)
                print(f"User {args.user_id} deleted successfully")

            elif args.command == 'change-password':
                api.change_password(
                    args.user_id,
                    ChangePassword(
                        new_password=getattr(args, 'new_password'),
                        current_password=getattr(args, 'current_password', None)
                    )
                )
                print(f"Password changed successfully for user {args.user_id}")

            return 0
        except APIError as e:
            if e.status_code in [403, 404]:
                print(f"{str(e)}")
            else:
                print(f"API Error ({e.status_code or 'No status'}): {str(e)}", file=sys.stderr)
            return 1
        except AuthenticationError as e:
            print(f"Authentication Error: {str(e)}", file=sys.stderr)
            return 2
        # TODO to reactivate!
        #except Exception as e:
        #    print(f"Unexpected error: {str(e)}", file=sys.stderr)
        #    return 3
