import psycopg2
import time
import uuid

from typing import Dict, Any, List, Tuple
from devvio_util.exceptions import DBError

SQL_ATTEMPTS = 5


class PsqlMixin:
    def __init__(self, *args, **kwargs):
        """
        :param logger: Logging object
        :param db_secrets: Dict passing DB credentials (db_host, db_user, db_pass, db_name, db_port)
        :param sql_attempts: Number of attempts the query must try before throwing a timeout exception
        """
        # try:
        #     super().__init__(*args, **kwargs)  # forwards all unused arguments
        # except Exception as e:
        #     kwargs["logger"].debug("super().__init__() failed: {}".format(e))
        self._logger = kwargs["logger"]
        self._conn_string = None
        self._conn = None
        self._db_secrets = kwargs["db_secrets"]
        self._sql_attempts = kwargs.get("sql_attempts", SQL_ATTEMPTS)

    def connect(self, autocommit: bool = True):
        """
        Connect to the database and set session options
        :return:
        :rtype:
        """
        # self._logger.info("Connecting to database: %s", self._conn_string)
        self._conn = psycopg2.connect(self._conn_string)
        self._logger.info("Database connected.")
        self._conn.set_session(autocommit=autocommit)

    def dbquery(self, *args, **kwargs):
        """
        Query the connected database. Attempt to reconnect upon Operational or Interface error
        :param args:
        :param kwargs:
        :return:
        """
        attempts = self._sql_attempts
        while attempts > 0:
            attempts = attempts - 1
            try:
                n = len(self._conn.notices)
                cursor = self._conn.cursor()
                self._logger.debug(f"{args}")
                cursor.execute(*args, **kwargs)
                for notice in self._conn.notices[n:]:
                    self._logger.info(f"{notice}.")
                return cursor
            except psycopg2.OperationalError as e:
                self._logger.exception(e)
                self._logger.notice("psycopg2.OperationalError: {}".format(e))
                time.sleep(0.2)
                self.connect()
            except psycopg2.InterfaceError as e:
                self._logger.exception(e)
                self._logger.notice("psycopg2.InterfaceError: {}".format(e))
                time.sleep(0.2)
                self.connect()
            except psycopg2.Error as e:
                self._logger.exception(e)
                raise

        raise TimeoutError("Reached maximum number of DB connection retries.")

    def commit(self):
        """
        Commit DB updates.
        :return:
        """
        self._conn.commit()

    def rollback(self):
        """
        Rollback uncommitted updates.
        :return:
        """
        self._conn.rollback()

    def create_record(
        self, relation: str, record_props: Dict[str, Any]
    ) -> bool or None:
        stmt = "insert into {} (".format(relation)
        counter = 0
        if not record_props:
            raise DBError("Missing record_props argument in PsqlMixin.create_record()")
        for k in record_props:
            if counter > 0:
                stmt += ", "
            counter += 1
            stmt += k
        stmt += ", created, modified) (select "
        counter = 0
        # Don't modify the incoming properties
        new_record_props = dict(record_props)
        for k in record_props:
            if counter > 0:
                stmt += ", "
            counter += 1
            stmt += "%({})s".format(k)
        stmt += ", %(created)s, %(modified)s)"
        new_record_props["created"] = record_props.get("created") or self.get_devvtime()
        new_record_props["modified"] = self.get_devvtime()
        self._logger.debug(
            "Create record query: {}; values: {}".format(stmt, new_record_props)
        )
        try:
            self.dbquery(stmt, new_record_props)
            return True
        except psycopg2.InternalError as i:
            self._logger.exception(
                "PSQL error in CreateRecord, attempt rollback: {}".format(i)
            )
            self.dbquery("rollback")
            return None
        except Exception as e:
            return self.handle_psql_exception(e)

    def update_record(
        self, relation: str, update_props: Dict[str, Any], constraints: Dict[str, Any]
    ) -> int | None:
        stmt = "update {} set ".format(relation)
        counter = 0
        if not update_props:
            raise DBError("Missing record_props argument in PsqlMixin.update_record()")
        for k in update_props:
            if counter > 0:
                stmt += ", "
            counter += 1
            stmt += "{} = %({})s".format(k, k)
        stmt += ", modified = {}".format(self.get_devvtime())
        stmt += " where "
        counter = 0
        if not constraints:
            raise DBError("Missing constraint argument in PsqlMixin.update_record()")
        for k in constraints:
            if counter > 0:
                stmt += " and "
            stmt += "{} = %({})s".format(k, k)
            counter += 1
        update_props.update(constraints)
        self._logger.debug("Update record query: {}".format(stmt))
        try:
            self.dbquery(stmt, update_props)
            return True
        except psycopg2.InternalError as i:
            self._logger.debug(f"PSQL error in UpdateRecord, attempt rollback: {i}")
            self.dbquery("rollback")
            return None
        except Exception as e:
            return self.handle_psql_exception(e)

    def delete_record(self, relation: str, constraints: Dict[str, Any]):
        stmt = "delete from {} where ".format(relation)
        counter = 0
        if not constraints:
            raise DBError("Missing constraint argument in PsqlMixin.delete_record()")
        for k in constraints:
            if counter > 0:
                stmt += " and "
            counter += 1
            stmt += "{} = %({})s".format(k, k)
        self._logger.debug("Delete record query: {}".format(stmt))
        try:
            self.dbquery(stmt, constraints)
            return True
        except psycopg2.InternalError as i:
            self._logger.debug(f"PSQL error in DeleteRecord, attempt rollback: {i}")
            self.dbquery("rollback")
            return None
        except Exception as e:
            return self.handle_psql_exception(e)

    def set_record(
        self, relation: str, record_props: Dict[str, Any], constraints: Dict[str, Any]
    ) -> int or None:
        try:
            stmt = "select count(*) from {} where ".format(relation)
            num_records = 0
            counter = 0
            if not constraints:
                raise DBError("Missing constraint argument in PsqlMixin.set_record()")
            for k in constraints:
                if counter > 0:
                    stmt += " and "
                stmt += "{} = %({})s".format(k, k)
                counter += 1
            try:
                res = self.dbquery(stmt, constraints).fetchone()
                num_records = res[0]
            except psycopg2.InternalError as i:
                self._logger.debug(
                    f"PSQL error in select portion of SetRecord, attempt create: {i}"
                )
            if num_records < 1:
                return self.create_record(relation, record_props)
            else:
                self.update_record(relation, record_props, constraints)
            return num_records
        except psycopg2.InternalError as i:
            self._logger.debug(f"PSQL error in SetRecord, attempt rollback: {i}")
            self.dbquery("rollback")
            return None
        except Exception as e:
            return self.handle_psql_exception(e)

    def select_single_record(
        self,
        relation: str,
        select_props: List[str],  # noqa: C901
        constraints: Dict[str, Any],
    ) -> dict or None:
        stmt = "select "
        counter = 0
        if not select_props:
            raise DBError(
                "Missing select_props argument in PsqlMixin.select_single_record()"
            )
        for k in select_props:
            if counter > 0:
                stmt += ", "
            counter += 1
            stmt += "{}".format(k)
        stmt += " from {} ".format(relation)
        if constraints:
            stmt += " where "
            counter = 0
            for k in constraints:
                if counter > 0:
                    stmt += " and "
                counter += 1
                stmt += "{} = %({})s".format(k, k)
        else:
            constraints = {}
        stmt += " limit 1"
        self._logger.debug("Select record query: {}".format(stmt))
        try:
            out = dict()
            res = self.dbquery(stmt, constraints).fetchone()
            if not res:
                return None
            counter = 0
            for k in select_props:
                out[k] = res[counter]
                counter += 1
            return out
        except psycopg2.InternalError as i:
            self._logger.debug(f"PSQL error in SelectSingleRecord: {i}")
            return None
        except Exception as e:
            return self.handle_psql_exception(e)

    def select_all_records(
        self,
        relation: str,
        select_props: List[str],  # noqa: C901
        constraints: Dict[str, Any],
    ) -> List[Dict[str, Any]] or None:
        stmt = "select "
        counter = 0
        if not select_props:
            raise DBError(
                "Missing select_props argument in PsqlMixin.select_all_record()"
            )
        for k in select_props:
            if counter > 0:
                stmt += ", "
            counter += 1
            stmt += "{}".format(k)
        stmt += " from {} ".format(relation)
        if constraints:
            stmt += " where "
            counter = 0
            for k in constraints:
                if counter > 0:
                    stmt += " and "
                counter += 1
                stmt += "{} = %({})s".format(k, k)
        else:
            constraints = {}
        self._logger.debug("Select record query: {}".format(stmt))
        try:
            out = []
            res = self.dbquery(stmt, constraints).fetchall()
            if not res:
                return None
            for x in res:
                inner_out = {}
                counter = 0
                for k in select_props:
                    inner_out[k] = x[counter]
                    counter += 1
                out.append(inner_out)
            return out
        except psycopg2.InternalError as i:
            self._logger.debug(f"PSQL error in SelectAllRecords: {i}")
            return None
        except Exception as e:
            return self.handle_psql_exception(e)

    def paged_query(
        self,
        select_props: List[str],
        constraint_filters: str,
        args: Dict[str, Any],  # noqa: C901
        page: int,
        per_page: int,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Select one page of record(s) of size per_page from the constraint_filters query as a list
        including page metadata

        :param select_props: the fields to return
        :type select_props: List of columns or aggregate functions as strs
        :param constraint_filters: sql to filter and constrain this query including relations and the where clause
        :type constraint_filters: sql string
        :param args: arguments to inject into the query constraint_filters
        :type args: Dict of arg labels that exit in constraint_filters and their values
        :param page: the page of results to return (1st page is 1, there is no zero page)
        :type page: int
        :param per_page: the number of results to include in a page
        :type per_page: positive int
        :return: a list of dictionaries the current page results and a dictionary of paging metadata
        :rtype: List[Dict[str, Any]], Dict[str, Any]
        """
        stmt = "select "
        page = int(page)
        per_page = int(per_page)
        counter = 0
        if not select_props:
            raise DBError("Missing select_props argument in cache.paged_query()")
        if not constraint_filters:
            raise DBError("Missing constraint_filters argument in cache.paged_query()")
        if per_page < 1:
            raise DBError("Invalid per_page argument in cache.paged_query()")
        if page < 1:
            raise DBError("Invalid page argument in cache.paged_query()")
        for k in select_props:
            if counter > 0:
                stmt += ", "
            counter += 1
            stmt += "{}".format(k)
        stmt += ", count(*) over() as total_count "
        stmt += constraint_filters
        stmt += " offset " + str((page - 1) * per_page)
        stmt += " limit " + str(per_page)
        self._logger.debug("Select record query: {}".format(stmt))
        try:
            out = []
            res = self.dbquery(stmt, args).fetchall()
            page_stats = {"_total_count": 0, "_page": page, "_per_page": per_page}
            if res:
                for x in res:
                    inner_out = {}
                    counter = 0
                    for k in select_props:
                        inner_out[k] = x[counter]
                        counter += 1
                    if page_stats["_total_count"] == 0:
                        page_stats["_total_count"] = x[counter]
                    out.append(inner_out)
            return out, page_stats
        except psycopg2.InternalError as i:
            self._logger.debug(f"PSQL error in paged_query: {i}")
            return [], {"_total_count": 0, "_page": page, "_per_page": per_page}
        except Exception as e:
            return self.handle_psql_exception(e)

    def set_conn_string(self):
        """
        Set the database connection string
        :return:
        :rtype:
        """
        db_host, db_user, db_pass, db_name, db_port = self.get_db_cred()
        self._conn_string = "host=" + db_host
        self._conn_string += " dbname=" + db_name
        self._conn_string += " user=" + db_user
        self._conn_string += " password=" + db_pass
        self._conn_string += " port=" + db_port

    def get_db_cred(self):
        db_host = self._db_secrets.get("DEVV_DB_HOST")
        db_user = self._db_secrets.get("DEVV_DB_USER")
        db_pass = self._db_secrets.get("DEVV_DB_PASS")
        db_name = self._db_secrets.get("DEVV_DB_NAME")
        db_port = self._db_secrets.get("DEVV_DB_PORT")
        return db_host, db_user, db_pass, db_name, db_port

    def get_cache_cred(self):
        db_host = self._db_secrets.get("DEVV_CACHE_HOST")
        db_user = self._db_secrets.get("DEVV_CACHE_USER")
        db_pass = self._db_secrets.get("DEVV_CACHE_PASS")
        db_name = self._db_secrets.get("DEVV_CACHE_NAME")
        db_port = self._db_secrets.get("DEVV_CACHE_PORT")
        return db_host, db_user, db_pass, db_name, db_port

    def get_vault_cred(self):
        try:
            vault_host = self._db_secrets.get("DEVV_VAULT_HOST")
            if not vault_host:
                raise Exception("DEVV_VAULT_HOST is not defined")
            vault_user = self._db_secrets.get("DEVV_VAULT_USER")
            if not vault_user:
                raise Exception("DEVV_VAULT_USER is not defined")
            vault_pass = self._db_secrets.get("DEVV_VAULT_PASS")
            if not vault_pass:
                raise Exception("DEVV_VAULT_PASS is not defined")
            vault_name = self._db_secrets.get("DEVV_VAULT_NAME")
            if not vault_name:
                raise Exception("DEVV_VAULT_NAME is not defined")
            vault_port = self._db_secrets.get("DEVV_VAULT_PORT")
            if not vault_port:
                raise Exception("DEVV_VAULT_PORT is not defined")
        except Exception as e:
            self._logger.exception("Vault params not set, defaulting to cache DB.", e)
            vault_host = self._db_secrets.get("DEVV_DB_HOST")
            vault_user = self._db_secrets.get("DEVV_DB_USER")
            vault_pass = self._db_secrets.get("DEVV_DB_PASS")
            vault_name = self._db_secrets.get("DEVV_DB_NAME")
            vault_port = self._db_secrets.get("DEVV_DB_PORT")
        return vault_host, vault_user, vault_pass, vault_name, vault_port

    def set_cache_conn_string(self):
        """
        Set the database connection string
        :return:
        :rtype:
        """
        db_host, db_user, db_pass, db_name, db_port = self.get_cache_cred()
        self._conn_string = "host=" + db_host
        self._conn_string += " dbname=" + db_name
        self._conn_string += " user=" + db_user
        self._conn_string += " password=" + db_pass
        self._conn_string += " port=" + db_port

    def set_vault_conn_string(self):
        """
        Set the vault database connection string
        :return:
        :rtype:
        """
        vault_host, vault_user, vault_pass, vault_name, vault_port = (
            self.get_vault_cred()
        )
        self._conn_string = "host=" + vault_host
        self._conn_string += " dbname=" + vault_name
        self._conn_string += " user=" + vault_user
        self._conn_string += " password=" + vault_pass
        self._conn_string += " port=" + vault_port

    def get_devvtime(self) -> int:
        try:
            res = self.dbquery("SELECT devv_timestamp()").fetchone()
            devvtime = None
            if res:
                devvtime = res[0]
            return devvtime
        except psycopg2.InternalError as i:
            self._logger.exception("Could not create devvtime: {}".format(i))
            raise
        except Exception as e:
            self.handle_psql_exception(e)
            raise

    def get_uuid(self) -> uuid.UUID:
        try:
            return uuid.uuid4()
        except Exception as err:
            self._logger.exception("Unknown error: {}".format(err))
            raise DBError("Unknown error encountered while creating UUID")

    def handle_psql_exception(self, e):
        self._logger.exception("Error: {}".format(e))
        if hasattr(e, "pgerror"):
            self._logger.exception("pgerror: {} pgcode: {}".format(e.pgerror, e.pgcode))
        raise e
