import argparse
from typing import List

import pexpect
import psycopg2


def make_databases(args, option: str = 'all', range_min: int = -1, range_max: int = -1) -> List[str]:
    """

    @param args: Argparse arguments
    @param option: Which databases to select
                    all: Get all databases
                    clients: Get the clients databases only
                    global: Get the main database only
                    range:  Get a range of client databases.
                            If the range_min != -1: we get databases with number bigger or eq than it
                            If the range_max != -1: we get databases with number smaller or eq than it
    @param range_min: A min range to use when the option is `range`
    @param range_max: A max range to use when the option is `range`
    @return: List of databases to upgrade
    """
    if option == 'global':
        return [args.dbname]

    db = psycopg2.connect(user=args.user,
                          password=args.passwd,
                          host=args.host,
                          port=args.port,
                          database=args.dbname)
    cr = db.cursor()
    cr.execute("SELECT dbname FROM experio_cabinet "
               "WHERE has_system={} "
               "ORDER BY dbname DESC".format(True, ))
    dblist = sorted(list(set([str(name) for (name,) in cr.fetchall()])))
    clients = [dbname for dbname in dblist if args.client in dbname]
    if option == 'clients':
        return clients
    if option == 'range':
        if range_max != -1:
            clients = [dbname for dbname in clients if
                       dbname.startswith(args.client) and int(dbname.split('_')[-1]) <= range_max]
        if range_min != -1:
            clients = [dbname for dbname in clients if
                       dbname.startswith(args.client) and int(dbname.split('_')[-1]) >= range_min]
        return clients
    return dblist


def upgrade(args):
    dblist = args.databases or make_databases(args=args, option=args.option,
                                              range_min=args.range_min, range_max=args.range_max)
    modules = args.modules or ['all']
    for database in dblist:
        cmd = "odoo --database={} --update={} --i18n-overwrite --stop-after-init".format(database, ','.join(modules))
        print("UPDATE %s: %s" % (database, cmd))
        output = pexpect.spawn(cmd)
        try:
            output.expect('Modules loaded.', timeout=args.timeout)
        except pexpect.ExceptionPexpect as e:
            print(
                "Timeout reached while upgrading {}. Try manually upgrading the database with the command '{}'.".format(
                    database, cmd))
        output.kill(0)
        print("Upgraded database `{}` successfully.\n\n".format(database))


def install(args, module: str):
    dblist = args.databases or make_databases(args=args, option=args.option,
                                              range_min=args.range_min, range_max=args.range_max)
    for database in dblist:
        # if 'client' not in database and 'global' not in database and not database.startswith(args.client):
        #     continue
        # Wait for server to upgrade database, then kill it
        cmd = "odoo --database={} -i {} --stop-after-init".format(database, module)
        print("INSTALL %s: %s" % (database, cmd))
        output = pexpect.spawn(cmd)
        try:
            output.expect(['Initiating shutdown', 'Stopping gracefully'], timeout=args.timeout)
        except pexpect.ExceptionPexpect as e:
            print(
                "Timeout reached while installing {}. "
                "Try manually installing it in the database with the command '{}'.".format(database, cmd))
        output.kill(0)
        print("Installed `{}` inside `{}` successfully.\n\n".format(module, database))

def uninstall(args, module: str):
    dblist = args.databases or make_databases(args=args, option=args.option,
                                              range_min=args.range_min, range_max=args.range_max)
    for database in dblist:
        # if 'client' not in database and 'global' not in database and not database.startswith(args.client):
        #     continue
        # Wait for server to upgrade database, then kill it
        cmd = "odoo shell --database={}".format(database)
        print("Uninstall %s: %s" % (database, cmd))
        output = pexpect.spawn(cmd)
        try:
            output.expect('>>>', timeout=10)
            output.sendline("self.env['ir.module.module'].search([('name', '=', '{}')]).button_immediate_uninstall()".format(module))
            output.expect('>>>', timeout=args.timeout)
        except pexpect.ExceptionPexpect as e:
            print(
                "Timeout reached while uninstalling {}. "
                "Try manually uninstalling it in the database with the command '{}'.".format(database, cmd))
        output.kill(0)
        print("Uninstalled `{}` inside `{}` successfully.\n\n".format(module, database))


def quick_upgrade(args):
    dblist = args.databases or make_databases(args=args, option=args.option,
                                              range_min=args.range_min, range_max=args.range_max)
    for database in dblist:
        cmd = "odoo shell --database={}".format(database)
        print("Quick Update %s" % (database,))
        output = pexpect.spawn(cmd)
        try:
            output.expect('>>>', timeout=10)
            output.sendline("self.env['ir.module.module'].upgrade_changed_checksum()")
            output.expect('>>>', timeout=args.timeout)
        except pexpect.ExceptionPexpect as e:
            print(
                "Timeout reached while updating {}. Try manually updating it.".format(database))
        output.kill(0)
        print("Updated `{}` successfully.\n\n".format(database))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Commands from cmd')
    parser.add_argument('--host', nargs='?', const='postgres', type=str, help='Database hostname')
    parser.add_argument('--port', nargs='?', const=5432, type=int, help='Postgres port')
    parser.add_argument('--user', nargs='?', const='root', type=str, help='Database username')
    parser.add_argument('--passwd', nargs='?', const='root', type=str, help='Database password')
    parser.add_argument('--dbname', nargs='?', const='base_global', type=str, help='Global Database Name')
    parser.add_argument('--client', nargs='?', const='client', type=str, help='Client handeler Name')

    parser.add_argument('--option', nargs='?', const='all', choices=['all', 'clients', 'global', 'range'],
                        type=str, help='Run Database name')
    parser.add_argument('--range_max', nargs='?', const=-1, type=int, help='Postgres port')
    parser.add_argument('--range_min', nargs='?', const=-1, type=int, help='Postgres port')

    parser.add_argument('--timeout', nargs='?', const=120, type=int, help='Postgres port')

    parser.add_argument('--modules', nargs='*', default='all', type=str, help='Modules to upgrade')
    parser.add_argument('--databases', nargs='*', type=str, help='Modules to upgrade')

    parser.add_argument('--command', nargs='?', const='upgrade', choices=['upgrade', 'install', 'uninstall',
                                                                          'quick_upgrade'],
                        type=str, help='Command to run')

    arguments = parser.parse_args()

    if arguments.command == 'upgrade':
        upgrade(arguments)
    elif arguments.command == 'install':
        if len(arguments.modules) == 1 and arguments.modules[0] != 'all':
            install(arguments, arguments.modules[0])
        else:
            print("Can't install the modules: `{}`".format(arguments.modules))
    elif arguments.command == 'uninstall':
        if len(arguments.modules) == 1 and arguments.modules[0] != 'all':
            uninstall(arguments, arguments.modules[0])
        else:
            print("Can't uninstall the modules: `{}`".format(arguments.modules))
    elif arguments.command == 'quick_upgrade':
        quick_upgrade(arguments)

    # main(arguments)
