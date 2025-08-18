from zut import __version__, gpg
from zut.commands import create_command_parser, exec_command, add_command
from zut.config import configure_logging


def main():
    parser = create_command_parser('zut', version=__version__, doc="Zut command-line utilities.")
    parser.add_argument('-i', '--info', action='store_true', help="Display an informational message before first decryption of a password using GPG/pass.")

    configure_logging()

    subparsers = parser.add_subparsers(title='commands')
    add_command(subparsers, gpg, name='pass')
    
    args = vars(parser.parse_args())

    info = args.pop('info')
    configure_logging('INFO' if info else 'WARNING')

    exec_command(args)


if __name__ == '__main__':
    main()
