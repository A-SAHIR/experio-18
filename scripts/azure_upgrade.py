import logging
import os
from typing import List

import pexpect
import psycopg2
from dotenv import load_dotenv

_logger = logging.getLogger(__name__)


def make_databases() -> List[str]:
    """
    param args: Argparse arguments
    param option: Which databases to select
                    all: Get all databases
                    clients: Get the clients databases only
                    global: Get the main database only
                    range:  Get a range of client databases.
                            If the range_min != -1: we get databases with number bigger or eq than it
                            If the range_max != -1: we get databases with number smaller or eq than it
    param range_min: A min range to use when the option is `range`
    param range_max: A max range to use when the option is `range`
    @return: List of databases to upgrade
    """
    option = os.getenv("OPTION", "all")
    range_min = os.getenv("RANGE_MIN", -1)
    range_max = os.getenv("RANGE_MAX", -1)
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    port = os.getenv("POSTGRES_PORT", 5432)
    passwd = os.getenv("POSTGRES_PASS")
    dbname = os.getenv("DBNAME", "cabinet_global")
    client_handle = os.getenv("CLIENT_HANDLE", "client")

    if option == "global":
        return [dbname]

    db = psycopg2.connect(
        user=user, password=passwd, host=host, port=port, database=dbname
    )
    cr = db.cursor()
    cr.execute(
        "SELECT dbname FROM experio_cabinet "
        "WHERE has_system={} "
        "ORDER BY dbname DESC".format(
            True,
        )
    )
    dblist = sorted(list({str(name) for (name,) in cr.fetchall()}))

    clients = [dbname for dbname in dblist if client_handle in dbname]
    if option == "clients":
        return clients
    if option == "range":
        if range_max != -1:
            clients = [
                dbname
                for dbname in clients
                if dbname.startswith(client_handle)
                and int(dbname.split("_")[-1]) <= range_max
            ]
        if range_min != -1:
            clients = [
                dbname
                for dbname in clients
                if dbname.startswith(client_handle)
                and int(dbname.split("_")[-1]) >= range_min
            ]
        return clients
    return dblist


def upgrade(modules, dblist, timeout):
    """
    Upgrade all the @modules inside the @dblist one by one
    @param modules:
    @param dblist:
    @param timeout:
    @return:
    """
    for database in dblist:
        cmd = (
            "odoo --database={} --update={} --i18n-overwrite --stop-after-init".format(
                database, ",".join(modules)
            )
        )
        _logger.warning("UPDATE %s: %s" % (database, cmd))
        output = pexpect.spawn(cmd)
        try:
            output.expect("Modules loaded.", timeout=timeout)
        except pexpect.ExceptionPexpect as e:
            _logger.error(
                "Timeout reached while upgrading {}. Try manually upgrading the database "
                "with the command '{}'.\nError: {}".format(database, cmd, e)
            )
        output.kill(0)
        _logger.warning("Upgraded database `{}` successfully.\n\n".format(database))


def install(dblist: List[str], module: str, timeout: int = 90):
    """
    Install one module inside all the databases listed in param
    @param dblist:
    @param module:
    @param timeout:
    @return:
    """
    for database in dblist:
        # if 'client' not in database and 'global' not in database and not database.startswith(args.client):
        #     continue
        # Wait for server to upgrade database, then kill it
        cmd = "odoo --database={} -i {} --stop-after-init".format(database, module)
        _logger.warning("INSTALL %s: %s" % (database, cmd))
        output = pexpect.spawn(cmd)
        try:
            output.expect(
                ["Initiating shutdown", "Stopping gracefully"], timeout=timeout
            )
        except pexpect.ExceptionPexpect as e:
            _logger.error(
                "Timeout reached while installing {}. "
                "Try manually installing it in the database with the command '{}'.\nError: {}".format(
                    database, cmd, e
                )
            )
        output.kill(0)
        _logger.warning(
            "Installed `{}` inside `{}` successfully.\n\n".format(module, database)
        )


def uninstall(dblist: List[str], module: str, timeout: int):
    """
    Uninstall one module inside all the databases listed in param
    @param dblist:
    @param module:
    @param timeout:
    @return:
    """
    for database in dblist:
        # if 'client' not in database and 'global' not in database and not database.startswith(args.client):
        #     continue
        # Wait for server to upgrade database, then kill it
        cmd = "odoo shell --database={}".format(database)
        _logger.warning("Uninstall %s: %s" % (database, cmd))
        output = pexpect.spawn(cmd)
        try:
            output.expect(">>>", timeout=10)
            output.sendline(
                "self.env['ir.module.module'].search([('name', '=', '{}')]).button_immediate_uninstall()".format(
                    module
                )
            )
            output.expect(">>>", timeout=timeout)
        except pexpect.ExceptionPexpect as e:
            _logger.error(
                "Timeout reached while uninstalling {}. "
                "Try manually uninstalling it in the database with the command '{}'.\nError: {}".format(
                    database, cmd, e
                )
            )
        output.kill(0)
        _logger.warning(
            "Uninstalled `{}` inside `{}` successfully.\n\n".format(module, database)
        )


def quick_upgrade(dblist: List[str], timeout: int = 90):
    """
    Run a quick upgrade on all the databases
    @param dblist:
    @param timeout:
    @return:
    """
    for database in dblist:
        cmd = "odoo shell --database={}".format(database)
        _logger.warning("Quick Update %s" % (database,))
        output = pexpect.spawn(cmd)
        try:
            output.expect(">>>", timeout=10)
            output.sendline("self.env['ir.module.module'].upgrade_changed_checksum()")
            output.expect(">>>", timeout=timeout)
        except pexpect.ExceptionPexpect as e:
            _logger.error(
                "Timeout reached while updating {}. Try manually updating it.\nError: {}".format(
                    database, e
                )
            )
        output.kill(0)
        _logger.warning("Updated `{}` successfully.\n\n".format(database))


if __name__ == "__main__":
    load_dotenv()

    modules_list = os.getenv("MODULES", "")
    modules_list = modules_list and modules_list.split(",") or ["all"]
    databases = os.getenv("DATABASES", "")
    databases = databases and databases.split(",") or make_databases()
    g_timeout = int(os.getenv("TIMEOUT", 90))

    command = os.getenv("COMMAND", "upgrade")
    if command == "upgrade":
        upgrade(modules=modules_list, dblist=databases, timeout=g_timeout)
    elif command == "install":
        if len(modules_list) == 1 and modules_list[0] != "all":
            install(dblist=databases, module=modules_list[0])
        else:
            _logger.error("Can't install the modules: `{}`".format(modules_list))
    elif command == "uninstall":
        if len(modules_list) == 1 and modules_list[0] != "all":
            uninstall(dblist=databases, module=modules_list[0], timeout=g_timeout)
        else:
            _logger.error("Can't uninstall the modules: `{}`".format(modules_list))
    elif command == "quick_upgrade":
        quick_upgrade(dblist=databases, timeout=g_timeout)
