from __future__ import annotations
import random
import os
from typing import Optional

import snowflake.connector

import relationalai as rai
from relationalai import debugging
from relationalai.debugging import logger
from relationalai.clients import config as cfg
from relationalai.util.otel_handler import enable_otel_export
from relationalai.tools.constants import USE_PACKAGE_MANAGER
from relationalai.util.snowflake_handler import SnowflakeHandler
from relationalai.util.span_format_test import SpanCollectorHandler, assert_valid_span_structure
from relationalai.util.span_tracker import TRACE_ID, get_root_span_attrs

def graph_index_config_fixture():
    cloud_provider = os.getenv("RAI_CLOUD_PROVIDER")
    if cloud_provider:
        config = make_config()
    else:
        config = cfg.Config()

    config.set("use_graph_index", True)
    config.set("reuse_model", False)

    yield config
    return

def engine_config_fixture(size, use_direct_access=False, reset_session=False, generation=rai.Generation.V0):
    # Check for an externally provided engine name
    # It is used in GitHub Actions to run tests against a specific engine
    engine_name = os.getenv("ENGINE_NAME")
    if engine_name:
        # If engine name was provided, just yield the config
        config = make_config(engine_name, use_direct_access=use_direct_access)
        # Try to reset the session instead of using active session if reset_session is true
        rai.Resources(config=config, reset_session=reset_session)

        if os.getenv("DISABLE_PROFILE_POLLING"):
            print('disabling `debug` in config')
            config.set("debug", False)

        config.set("reuse_model", False)
        config.set("enable_otel_handler", True) 

        yield config
        return

    # If there's a local config file, use it, including
    # the engine specified there.
    config = cfg.Config()
    if config.file_path is not None:
        # Try to reset the session instead of using active session if reset_session is true
        rai.Resources(config=config, reset_session=reset_session, generation=generation)
        yield config
        return

    # Otherwise, create a new engine and delete it afterwards.
    random_number = random.randint(1000000000, 9999999999)
    engine_name = f"pyrel_test_{random_number}"
    create_engine(engine_name, size=size, use_direct_access=use_direct_access)

    yield make_config(engine_name, use_direct_access=use_direct_access)

    delete_engine(engine_name, use_direct_access=use_direct_access)

def create_engine(engine_name: str, size: str,  use_direct_access=False):
    print('create_engine: about to call make_config')
    config = make_config(engine_name, use_direct_access=use_direct_access)

    provider = rai.Resources(config=config)
    print(f"Creating engine {engine_name}")
    provider.create_engine(name=engine_name, size=size)
    print(f"Engine {engine_name} created")

def delete_engine(engine_name: str, use_direct_access=False):
    print(f"Deleting engine {engine_name}")
    config = make_config(engine_name, use_direct_access=use_direct_access)
    provider = rai.Resources(config=config)
    provider.delete_engine(engine_name)
    print(f"Engine {engine_name} deleted")

def make_config(engine_name: str | None = None, fetch_profile: bool = True, use_package_manager = USE_PACKAGE_MANAGER, use_direct_access = False, show_full_traces = True) -> cfg.Config:
    cloud_provider = os.getenv("RAI_CLOUD_PROVIDER")

    print('cloud provider:', cloud_provider)

    if cloud_provider is None:
        raise ValueError("RAI_CLOUD_PROVIDER must be set")
    elif cloud_provider == "azure":
        client_id = os.getenv("RAI_CLIENT_ID")
        client_secret = os.getenv("RAI_CLIENT_SECRET")
        if client_id is None or client_secret is None:
            raise ValueError(
                "RAI_CLIENT_ID, RAI_CLIENT_SECRET must be set if RAI_CLOUD_PROVIDER is set to 'azure'"
            )

        # Pull from env vars; Default to prod
        host = os.getenv("RAI_AZURE_HOST") or "azure.relationalai.com"
        creds_url = os.getenv("RAI_AZURE_CLIENT_CREDENTIALS_URL") or "https://login.relationalai.com/oauth/token"
        region = os.getenv("RAI_AZURE_REGION") or "us-east"

        return cfg.Config(

            {
                "platform": "azure",
                "host": host,
                "port": "443",
                "region": region,
                "scheme": "https",
                "client_credentials_url": creds_url,
                "client_id": client_id,
                "client_secret": client_secret,
                "engine": engine_name,
                "use_package_manager": use_package_manager,
                "show_full_traces": show_full_traces,
            }
        )

    elif cloud_provider == "snowflake":
        sf_username = os.getenv("SF_TEST_ACCOUNT_USERNAME")
        sf_password = os.getenv("SF_TEST_ACCOUNT_PASSWORD")
        sf_account = os.getenv("SF_TEST_ACCOUNT_NAME")
        sf_role = os.getenv("SF_TEST_ROLE_NAME", "RAI_USER")
        sf_warehouse = os.getenv("SF_TEST_WAREHOUSE_NAME")
        sf_app_name = os.getenv("SF_TEST_APP_NAME")
        if sf_username is None or sf_password is None:
            raise ValueError(
                "SF_TEST_ACCOUNT_USERNAME, SF_TEST_ACCOUNT_PASSWORD, SF_TEST_ACCOUNT_NAME must be set if RAI_CLOUD_PROVIDER is set to 'snowflake'"
            )

        current_config = {
            "platform": "snowflake",
            "user": sf_username,
            "password": sf_password,
            "account": sf_account,
            "role": sf_role,
            "warehouse": sf_warehouse,
            "rai_app_name": sf_app_name,
            "use_package_manager": use_package_manager,
            "use_direct_access": use_direct_access,
            "show_full_traces": show_full_traces,
        }
        if engine_name:
            current_config["engine"] = engine_name
        return cfg.Config(current_config, fetch=fetch_profile)

    else:
        raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

def snowflake_handler_fixture():
    if not os.getenv("SF_REPORTING_PASSWORD"):
        print('snowflake logger disabled since required config env vars not present')
        yield
        return

    conn = snowflake.connector.connect(
        user=os.getenv("SF_REPORTING_USER"),
        password=os.getenv("SF_REPORTING_PASSWORD"),
        account=os.getenv("SF_REPORTING_ACCOUNT"),
        role=os.getenv("SF_REPORTING_ROLE"),
        warehouse=os.getenv("SF_REPORTING_WAREHOUSE"),
        database=os.getenv("SF_REPORTING_DATABASE"),
        schema=os.getenv("SF_REPORTING_SCHEMA"),
    )
    snowflake_handler = SnowflakeHandler(TRACE_ID, conn)
    logger.addHandler(snowflake_handler)
    yield
    snowflake_handler.shut_down()

def span_structure_validator_fixture():
    handler = SpanCollectorHandler()
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)
    # We skip tests in certain environments, so there's no need to perform span checks when those tests aren't executed.
    if os.getenv("SkipSpanValidation") != str(True):
        assert_valid_span_structure(handler.nodes, handler.events)

def root_span_fixture(get_full_config=False, span_type: str = "test_session", extra_attrs: Optional[dict] = None):
    root_span_attrs = get_root_span_attrs(get_full_config)
    if extra_attrs:
        root_span_attrs.update(extra_attrs)
    with debugging.span(span_type, **root_span_attrs):
        yield

def otel_collector_fixture(generation):
    config = make_config()
    resources = rai.clients.snowflake.Resources(config=config, generation=generation)
    enable_otel_export(
        resources,
        config.get('rai_app_name', 'RELATIONALAI')
    )

    yield