#  Copyright (c) 2024.  stef.
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
from ..auth import AuthenticationError
from ..core.config import get_config
from ..service import svc_class
from ..version import __software__


from .organizations import get_APIorg, OrganizationCreate, OrganizationUpdate, APIError
import sys

__SOFTWARE__ = __software__.upper()
commands = {
    "list": ["list_organizations", [], {}, 'Lists Organizations'],
    "get": ["get_organization", ['org_id'], {}, 'Gets Organization'],
    "create": ["create_organization", ['name', 'description?'], {}, 'Creates Organization'],
    "update": ["update_organization", ['org_id', 'name?', 'description?'], {}, 'Updates Organization'],
    "delete": ["delete_organization", ['org_id'], {}, 'Deletes Organization'],
}


class orgs_services(svc_class):
    default_config = {
    }

    params_link = {
    }

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        return ("org", f"Manage {__software__} organizations")

    @staticmethod
    def params(parser):
        subparsers = parser.add_subparsers(dest='command', title='Subcommands', required=True)

        # list
        list_parser = subparsers.add_parser('list', help='List organizations')
        list_parser.set_defaults(func='list_organizations')

        # get
        get_parser = subparsers.add_parser('get', help='Get organization details')
        get_parser.add_argument('org_id', type=int, help='Organization ID')
        get_parser.set_defaults(func='get_organization')

        # create
        create_parser = subparsers.add_parser('create', help='Create new organization')
        create_parser.add_argument('--name', required=True, help='Organization name')
        create_parser.add_argument('--description', help='Organization description')
        create_parser.set_defaults(func='create_organization')

        # update
        update_parser = subparsers.add_parser('update', help='Update organization')
        update_parser.add_argument('org_id', type=int, help='Organization ID')
        update_parser.add_argument('--name', help='New organization name')
        update_parser.add_argument('--description', help='New organization description')
        update_parser.set_defaults(func='update_organization')

        # delete
        delete_parser = subparsers.add_parser('delete', help='Delete organization')
        delete_parser.add_argument('org_id', type=int, help='Organization ID')
        delete_parser.set_defaults(func='delete_organization')

    @staticmethod
    def test_name(name):
        return name == __software__ + 'org'

    @staticmethod
    def cmd_name(name):
        return name == 'org'

    def run(self):
        config = get_config()
        args = config.args

        # Création du client API avec configuration complète
        api = get_APIorg(config)

        try:
            if args.command == 'list':
                orgs = api.list_organizations()
                print(f"Organizations ({len(orgs)}):")
                for org in orgs:
                    print(f"  {org.id}: {org.name}")

            elif args.command == 'get':
                org = api.get_organization(args.org_id)
                print(f"Organization details:")
                print(f"  ID: {org.id}")
                print(f"  Name: {org.name}")
                if org.description:
                    print(f"  Description: {org.description}")

            elif args.command == 'create':
                new_org = api.create_organization(OrganizationCreate(
                    name=args.name,
                    description=args.description
                ))
                print(f"Organization created successfully:")
                print(f"  ID: {new_org.id}")
                print(f"  Name: {new_org.name}")

            elif args.command == 'update':
                updated_org = api.update_organization(
                    args.org_id,
                    OrganizationUpdate(
                        name=args.name,
                        description=args.description
                    )
                )
                print(f"Organization updated successfully:")
                print(f"  ID: {updated_org.id}")
                print(f"  New name: {updated_org.name}")

            elif args.command == 'delete':
                api.delete_organization(args.org_id)
                print(f"Organization {args.org_id} deleted successfully")

            return 0
        except APIError as e:
            print(f"API Error ({e.status_code or 'No status'}): {str(e)}", file=sys.stderr)
            return 1
        except AuthenticationError as e:
            print(f"Authentication Error: {str(e)}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr)
            return 3
