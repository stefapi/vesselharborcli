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
from ..core.requests import APIError
from ..service import svc_class
from ..version import __software__


from .environments import get_APIenvironment, EnvironmentCreate, EnvironmentUpdate
import sys

__SOFTWARE__ = __software__.upper()
commands = {
    "list": ["list_environments", [], {}, 'Lists Environments'],
    "get": ["get_environment", ['environment_id'], {}, 'Gets Environment'],
    "create": ["create_environment", ['name', 'description?'], {}, 'Creates Environment'],
    "update": ["update_environment", ['environment_id', 'name?', 'description?'], {}, 'Updates Environment'],
    "delete": ["delete_environment", ['environment_id'], {}, 'Deletes Environment'],
}


class environments_services(svc_class):
    default_config = {
    }

    params_link = {
    }

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        return ("environment", f"Manage {__software__} environments")

    @staticmethod
    def params(parser):
        subparsers = parser.add_subparsers(dest='command', title='Subcommands', required=True)

        # list
        list_parser = subparsers.add_parser('list', help='List environments')
        list_parser.set_defaults(func='list_environments')

        # get
        get_parser = subparsers.add_parser('get', help='Get environment details')
        get_parser.add_argument('environment_id', type=int, help='Environment ID')
        get_parser.set_defaults(func='get_environment')

        # create
        create_parser = subparsers.add_parser('create', help='Create new environment')
        create_parser.add_argument('--name', required=True, help='Environment name')
        create_parser.add_argument('--description', help='Environment description')
        create_parser.set_defaults(func='create_environment')

        # update
        update_parser = subparsers.add_parser('update', help='Update environment')
        update_parser.add_argument('environment_id', type=int, help='Environment ID')
        update_parser.add_argument('--name', help='New environment name')
        update_parser.add_argument('--description', help='New environment description')
        update_parser.set_defaults(func='update_environment')

        # delete
        delete_parser = subparsers.add_parser('delete', help='Delete environment')
        delete_parser.add_argument('environment_id', type=int, help='Environment ID')
        delete_parser.set_defaults(func='delete_environment')

    @staticmethod
    def test_name(name):
        return name == __software__ + 'environment'

    @staticmethod
    def cmd_name(name):
        return name == 'environment'

    def run(self):
        config = get_config()
        args = config.args

        # Création du client API avec configuration complète
        api = get_APIenvironment(config)

        try:
            if args.command == 'list':
                environments = api.list_environments()
                print(f"Environments ({len(environments)}):")
                for environment in environments:
                    print(f"  {environment.id}: {environment.name}")

            elif args.command == 'get':
                environment = api.get_environment(args.environment_id)
                print(f"Environment details:")
                print(f"  ID: {environment.id}")
                print(f"  Name: {environment.name}")
                if environment.description:
                    print(f"  Description: {environment.description}")

            elif args.command == 'create':
                new_environment = api.create_environment(EnvironmentCreate(
                    name=args.name,
                    description=args.description
                ))
                print(f"Environment created successfully:")
                print(f"  ID: {new_environment.id}")
                print(f"  Name: {new_environment.name}")

            elif args.command == 'update':
                updated_environment = api.update_environment(
                    args.environment_id,
                    EnvironmentUpdate(
                        name=args.name,
                        description=args.description
                    )
                )
                print(f"Environment updated successfully:")
                print(f"  ID: {updated_environment.id}")
                print(f"  New name: {updated_environment.name}")

            elif args.command == 'delete':
                api.delete_environment(args.environment_id)
                print(f"Environment {args.environment_id} deleted successfully")

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
        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr)
            return 3
