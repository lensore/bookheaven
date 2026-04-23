import argparse
from services.user_service import UserService


def list_users(db_path: str) -> None:
    service = UserService(db_path=db_path)
    users = service.get_all_users()
    if not users:
        print('No users found.')
        return

    print('Registered users:')
    for username, data in users.items():
        print(f'- {username}: {data}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BookHaven CLI для просмотра пользователей',
    )
    parser.add_argument(
        '--db', '-d',
        default='users.db',
        help='Путь до файла shelve с пользователями',
    )
    parser.add_argument(
        'command',
        nargs='?',
        choices=['list'],
        default='list',
        help='Команда CLI',
    )
    args = parser.parse_args()

    if args.command == 'list':
        list_users(args.db)
