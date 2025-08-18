import os
# install the snowflake connector
import snowflake.connector
import pandas as pd
from important.location import CONF_DIR
from typing import Optional
from yaml import safe_load
import logging


def read_sql(sql):
    conn = snowflake.connector.connect(
        user="READ_ONLY_USER",
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account="firework_prod",
        warehouse="COMPUTE_WH",
        database="FIREWORK",
        schema="PUBLIC"
    )
    cur = conn.cursor()
    cur.execute(sql)
    df = cur.fetch_pandas_all()
    conn.close()
    return df


class SnowFlake:
    """
    Snowflake query
    Set SNOFLAKE_PASSWORD in your environment
    Then run SnowFlake.from_config()
    """

    def __init__(self,
                 user: str,
                 account: str,
                 warehouse: str,
                 database: str,
                 schema: str,
                 password: str,
                 ):
        self.user = user
        self.account = account
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.password = password

    def __repr__(self):
        return f"SnowFlake(user={self.user}, account={self.account}, " +\
            f"warehouse={self.warehouse}, schema={self.schema})"

    def __call__(self, sql: str) -> pd.DataFrame:
        conn = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema)
        cur = conn.cursor()
        cur.execute(sql)
        df = cur.fetch_pandas_all()
        conn.close()
        return df

    @classmethod
    def from_config(
        cls,
        env: str = "prod",
        config_path: Optional[str] = None,
    ) -> "SnowFlake":
        if 'SNOWFLAKE_PASSWORD' not in os.environ:
            raise KeyError(
                "🔑 SNOWFLAKE_PASSWORD not in environment variables")

        if config_path is None:
            config_path = CONF_DIR / "snowflake.yaml"

        with open(config_path, "r") as f:
            conf_data = safe_load(f)

        if env not in conf_data:
            raise KeyError(f"🤔 {env} not in {config_path}")

        conf = conf_data[env]

        return cls(
            password=os.environ['SNOWFLAKE_PASSWORD'],
            **conf)


class SnowFlakeDatabricks(SnowFlake):
    """
    Using with clause in the Snowflake connector
    This will run better on the databricks cluster
    """

    def __call__(self, sql: str) -> pd.DataFrame:
        logging.debug(f"Running SQL: {sql}")
        with snowflake.connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema) as conn:
            df = pd.read_sql(sql, con=conn)
        logging.debug(
            f"SnowFlake Result:\t{len(df)} lines of data")
        return df
