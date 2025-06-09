"""Authentication commands for the VesselHarbor CLI."""

#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#
#

import sys
import requests
from .auth import TokenManager, AuthenticationError
from .service import svc_class
from .version import __software__
from .core.config import get_config

__SOFTWARE__ = __software__.upper()

class auth_services(svc_class):
    default_config = {
    }

    params_link = {
    }

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        return ("auth", f"Manage {__software__} authentication")

    @staticmethod
    def params(parser):
        subparsers = parser.add_subparsers(dest='command', title='Subcommands', required=True)

        # test_basic_auth
        basic_auth_parser = subparsers.add_parser('test_basic_auth', help='Test basic authentication with username and password')
        basic_auth_parser.set_defaults(func='test_basic_auth')

        # test_token_auth
        token_auth_parser = subparsers.add_parser('test_token_auth', help='Test token authentication with API key')
        token_auth_parser.set_defaults(func='test_token_auth')

    @staticmethod
    def test_name(name):
        return name == __software__ + 'auth'

    @staticmethod
    def cmd_name(name):
        return name == 'auth'

    def run(self):

        config = get_config()
        args = config.args

        try:
            if args.command == 'test_basic_auth':
                # Test basic authentication with username and password
                token_manager = TokenManager()

                # Check if username and password are configured
                if not config['application.user'] or not config['application.password']:
                    print("Error: Username or password not configured.", file=sys.stderr)
                    print("Please set them in your configuration file or environment variables.", file=sys.stderr)
                    return 1

                try:
                    # Attempt to login with password
                    token_response = token_manager.login_with_password()
                    print("Basic authentication successful!")
                    print(f"Token type: {token_response.token_type}")
                    print(f"Access token: {token_response.access_token[:10]}... (truncated)")
                    if token_response.expires_in:
                        print(f"Expires in: {token_response.expires_in} seconds")
                    if token_response.refresh_token:
                        print(f"Refresh token: {token_response.refresh_token[:10]}... (truncated)")
                    return 0
                except AuthenticationError as e:
                    print(f"Basic authentication failed: {str(e)}", file=sys.stderr)
                    return 1

            elif args.command == 'test_token_auth':
                # Test token authentication with API key
                token_manager = TokenManager()

                # Check if API key is configured
                if not config.config.get('application', 'api_key'):
                    print("Error: API key not configured.", file=sys.stderr)
                    print("Please set it in your configuration file or environment variables.", file=sys.stderr)
                    return 1

                try:
                    # Attempt to login with API key
                    token_response = token_manager.login_with_api_key()
                    print("Token authentication successful!")
                    print(f"Token type: {token_response.token_type}")
                    print(f"Access token: {token_response.access_token[:10]}... (truncated)")
                    if token_response.expires_in:
                        print(f"Expires in: {token_response.expires_in} seconds")
                    if token_response.refresh_token:
                        print(f"Refresh token: {token_response.refresh_token[:10]}... (truncated)")
                    return 0
                except AuthenticationError as e:
                    print(f"Token authentication failed: {str(e)}", file=sys.stderr)
                    return 1

            return 0
        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr)
            return 3
