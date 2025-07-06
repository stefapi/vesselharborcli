import sys
import argparse

from os.path import basename

from .service import svc_store
from .core.arg_params import arg_parser
from .core.config import create_config
from .version import __software__, __description__, __version__
from .orgs.main import orgs_services
from .environments.main import environments_services
from .users.main import users_services
from .auth_commands import auth_services
from .interactive_service import interactive_services


__SOFTWARE__ = __software__.upper()

# default configuration attribute stored in configuration file (useful for command line program)
# internal items are not stored but are used internally
# you may use <> to define repetitive items
default_config = {
    'application': {
        'verbose': False,
        'ip_address': '127.0.0.1',
        'port': 8010,
        'socket':'',
        'user': 'example@example.com',
        'password': 'changeme',
        'api_key': 'changeme',
    },
    'internal': {
        'development': False,
        'debug': False,
    },
}

# each long name option has to be defined into basic_options
params_link = { # configuration attribute  [ long name option, Environment attribute , .env attribute]
    'internal.debug': ['debug_do_not_use', __SOFTWARE__ + '_DEBUG', 'DEBUG'],
    'internal.simulate': ['simulate_do_not_use', __SOFTWARE__ + '_SIMULATE', 'SIMULATE'],
    'internal.development': ['development_do_not_use', __SOFTWARE__ + '_DEVEL', 'DEVELOPMENT'],
    'internal.noauth': ['noauth_do_not_use', __SOFTWARE__ + '_DEVEL', 'NOAUTH'],
    'internal.demo': ['demo', __SOFTWARE__ + '_DEMO', 'DEMO'],
    'application.verbose': ['verbose', __SOFTWARE__ + '_VERBOSE', 'VERBOSE'],
    'application.ip_address': ['ip_address[0]', __SOFTWARE__ + '_IP_ADDRESS', 'IP_ADDRESS'],
    'application.port': ['port[0]', __SOFTWARE__ + '_PORT', 'PORT'],
    'application.socket': ['socket[0]', __SOFTWARE__ + '_SOCKET', 'SOCKET'],
}

params_link_app = None
default_config_app = None
args = None

def basic_options(parser):
    parser.add_argument('-v', '--version', help='Print version and exit', action='store_true')
    parser.add_argument('-C', '--conf', help='Name of configuration file to read', nargs=1)
    parser.add_argument('-w', '--write', help='write local config to file ./vesselharbor.toml', action='store_true')
    parser.add_argument('-W', '--write-conf', help='Name of configuration file to write', nargs=1)
    parser.add_argument('-V', '--verbose', help='Name of configuration file', action='store_true')

    parser.add_argument('-A', '--ip-address', help='IP address to bind for the server', nargs=1)
    parser.add_argument('-p', '--port', help='port to bind for the server', nargs=1)
    parser.add_argument('-S', '--socket', help='socket file to bind for the server', nargs=1)

    parser.add_argument('--debug_do_not_use', help=argparse.SUPPRESS, action='store_true')
    parser.add_argument('--development_do_not_use', help=argparse.SUPPRESS, action='store_true')


def main():
    """
    Main function of the application.

    This function serves as the entry point for the application. It initializes the service store, detects the appropriate application based on the program name prefix, and sets up argument parsing. Depending on the parsed arguments, it either writes a configuration file or runs the detected application with the provided configuration.

    :param Params: Command-line arguments.
    :type Params: list of str

    :raises SystemExit: If the version flag is set to True or if an unknown mode is specified.

    :return: The result of running the detected application.
    :rtype: int
    """

    Params = sys.argv
    # Create the store with organizations, environments, users, authentication and interactive services
    apps_store = svc_store([orgs_services(), environments_services(), users_services(), auth_services(), interactive_services()])
    app_name = basename(Params[0])

    # Detect the application based on the program name
    selected_app = apps_store.selected_app(app_name)
    params_link_app = apps_store.update_params_link(params_link)
    default_config_app = apps_store.update_default_config(default_config)

    # Prepare the services list for the parser
    if selected_app is None:
        services_list = apps_store.svcs  # All services
        generic = True
    else:
        services_list = [selected_app]   # Specific detected service
        generic = False

    # Create the main parser
    parser = arg_parser(
        __software__,
        __version__,
        __description__,
        basic_options,
        {
            'title': 'Command Group',
            'description': 'Select Command Group then Subgroup',
            'help': 'get help with --help',
            'dest': 'mode'
        },
        services_list,  # Pass the services list
        generic
    )

    # Parse the arguments
    args = parser.parse_args(Params)

    config = create_config(args.conf, args, params_link_app, default_config_app, args.debug_do_not_use)

    if args.version == True:
        parser.print_version()
        exit(0)

    # Dispatch to the appropriate service
    run_app = None
    for service in apps_store.svcs:
        if service.cmd_name(args.mode):
            run_app= service
            break
    # if no service match, raise an error
    if run_app is None:
        print(f"Error: Unknown commands group '{args.mode}'", file=sys.stderr)
        parser.print_help()
        return 1

    if args.write == True:
        config.writeto("./myeasyserver.toml", False)
        print("Configuration file is written to ./myeasyserver.toml. Exiting.")
        exit(0)
    if args.write_conf is not None:
        config.writeto(args.write_conf[0], False)
        print("Configuration file is written to %s. Exiting." % args.write_conf[0])
        exit(0)

    return run_app.run()

if __name__ == "__main__":
    ret = main()
    exit(ret)
