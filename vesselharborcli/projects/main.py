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
from ..auth import AuthenticationError
from ..core.config import get_config
from ..service import svc_class
from ..version import __software__


from .projects import get_APIproject, ProjectCreate, ProjectUpdate, APIError
import sys

__SOFTWARE__ = __software__.upper()
commands = {
    "list": ["list_projects", [], {}, 'Lists Projects'],
    "get": ["get_project", ['project_id'], {}, 'Gets Project'],
    "create": ["create_project", ['name', 'description?'], {}, 'Creates Project'],
    "update": ["update_project", ['project_id', 'name?', 'description?'], {}, 'Updates Project'],
    "delete": ["delete_project", ['project_id'], {}, 'Deletes Project'],
}


class projects_services(svc_class):
    default_config = {
    }

    params_link = {
    }

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        return ("project", f"Manage {__software__} projects")

    @staticmethod
    def params(parser):
        subparsers = parser.add_subparsers(dest='command', title='Subcommands', required=True)

        # list
        list_parser = subparsers.add_parser('list', help='List projects')
        list_parser.set_defaults(func='list_projects')

        # get
        get_parser = subparsers.add_parser('get', help='Get project details')
        get_parser.add_argument('project_id', type=int, help='Project ID')
        get_parser.set_defaults(func='get_project')

        # create
        create_parser = subparsers.add_parser('create', help='Create new project')
        create_parser.add_argument('--name', required=True, help='Project name')
        create_parser.add_argument('--description', help='Project description')
        create_parser.set_defaults(func='create_project')

        # update
        update_parser = subparsers.add_parser('update', help='Update project')
        update_parser.add_argument('project_id', type=int, help='Project ID')
        update_parser.add_argument('--name', help='New project name')
        update_parser.add_argument('--description', help='New project description')
        update_parser.set_defaults(func='update_project')

        # delete
        delete_parser = subparsers.add_parser('delete', help='Delete project')
        delete_parser.add_argument('project_id', type=int, help='Project ID')
        delete_parser.set_defaults(func='delete_project')

    @staticmethod
    def test_name(name):
        return name == __software__ + 'project'

    @staticmethod
    def cmd_name(name):
        return name == 'project'

    def run(self):
        config = get_config()
        args = config.args

        # Création du client API avec configuration complète
        api = get_APIproject(config)

        try:
            if args.command == 'list':
                projects = api.list_projects()
                print(f"Projects ({len(projects)}):")
                for project in projects:
                    print(f"  {project.id}: {project.name}")

            elif args.command == 'get':
                project = api.get_project(args.project_id)
                print(f"Project details:")
                print(f"  ID: {project.id}")
                print(f"  Name: {project.name}")
                if project.description:
                    print(f"  Description: {project.description}")

            elif args.command == 'create':
                new_project = api.create_project(ProjectCreate(
                    name=args.name,
                    description=args.description
                ))
                print(f"Project created successfully:")
                print(f"  ID: {new_project.id}")
                print(f"  Name: {new_project.name}")

            elif args.command == 'update':
                updated_project = api.update_project(
                    args.project_id,
                    ProjectUpdate(
                        name=args.name,
                        description=args.description
                    )
                )
                print(f"Project updated successfully:")
                print(f"  ID: {updated_project.id}")
                print(f"  New name: {updated_project.name}")

            elif args.command == 'delete':
                api.delete_project(args.project_id)
                print(f"Project {args.project_id} deleted successfully")

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
