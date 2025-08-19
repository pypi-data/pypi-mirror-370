# PYTHON_ARGCOMPLETE_OK
from ara_cli.ara_command_parser import action_parser
from ara_cli.version import __version__
from ara_cli.ara_command_action import (
    create_action,
    delete_action,
    rename_action,
    list_action,
    list_tags_action,
    prompt_action,
    chat_action,
    template_action,
    fetch_templates_action,
    read_action,
    reconnect_action,
    read_status_action,
    read_user_action,
    set_status_action,
    set_user_action,
    classifier_directory_action,
    scan_action,
    autofix_action,
    extract_action
)
import argcomplete
import sys


def define_action_mapping():
    return {
        "create": create_action,
        "delete": delete_action,
        "rename": rename_action,
        "list": list_action,
        "list-tags": list_tags_action,
        "prompt": prompt_action,
        "chat": chat_action,
        "template": template_action,
        "fetch-templates": fetch_templates_action,
        "read": read_action,
        "reconnect": reconnect_action,
        "read-status": read_status_action,
        "read-user": read_user_action,
        "set-status": set_status_action,
        "set-user": set_user_action,
        "classifier-directory": classifier_directory_action,
        "scan": scan_action,
        "autofix": autofix_action,
        "extract": extract_action
    }


def handle_invalid_action(args):
    sys.exit("Invalid action provided. Type ara -h for help")


def cli():
    parser = action_parser()

    # Show examples when help is called
    if any(arg in sys.argv for arg in ["-h", "--help"]):
        parser.add_examples = True

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    action_mapping = define_action_mapping()

    argcomplete.autocomplete(parser)

    args = parser.parse_args()
    if not hasattr(args, "action") or not args.action:
        parser.print_help()
        return
    action = action_mapping.get(args.action, handle_invalid_action)
    action(args)


if __name__ == "__main__":
    cli()
