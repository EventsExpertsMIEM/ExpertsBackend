from argparse import ArgumentParser
import logging
from evproj import db, full, rest
import urllib3
from passlib.hash import sha256_crypt


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = ArgumentParser(description='Backend service of Events project')

    parser.add_argument('role', metavar='role', type=str,
                        help='A role of application variant: full backend (full) or RESTful backend (rest)')
    parser.add_argument('--create-tables', type=str, dest='password',
                        help='Creates data base tables before launch.')

    args = parser.parse_args()

    if args.password:
        db.create_tables(sha256_crypt.encrypt(args.password))

    if args.role == 'full':
        logging.info('Starting full backend server')
        full.run()
    elif args.role == 'rest':
        logging.info('Starting restful api backend server')
        rest.run()
    else:
        logging.critical('Unknown role, exit...')


if __name__ == '__main__':
    main()
