from __future__ import annotations
import json
import random
import time
from typing import Optional, TypeVar
import urllib.parse
import re
from datetime import datetime, timezone

from relationalai.tools.constants import Generation
import requests

from relationalai.errors import RAIException

# replace the values of the URL parameters that start with X-Amz- with XXX
def scrub_url(url):
    parsed = urllib.parse.urlparse(url)
    parsed_qs = urllib.parse.parse_qs(parsed.query)
    for key in parsed_qs:
        if key.startswith("X-Amz-"):
            parsed_qs[key] = ["XXX"]
    new_qs = urllib.parse.urlencode(parsed_qs, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_qs))

def find_urls(string):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = re.findall(url_pattern, string)
    return urls

def scrub_urls(string, urls):
    for url in urls:
        # replace with scrubbed version
        string = string.replace(url, scrub_url(url))
    return string

E = TypeVar("E", bound=BaseException)

def scrub_exception(exception: E) -> E|RAIException:
    exception_str = str(exception)
    urls = find_urls(exception_str)
    if urls:
        return RAIException(scrub_urls(exception_str, urls))
    return exception

def wrap_with_request_id(error: requests.RequestException) -> RAIException:
    original_message = str(error)
    try:
        if error.response is not None:
            request_id = error.response.headers['x-amz-request-id']
            return RAIException(f"{original_message} s3 request id: {request_id}")
        return RAIException(original_message)
    except Exception:
        return RAIException(original_message)

def escape_for_f_string(code: str) -> str:
    return (
        code
        .replace("\\", "\\\\")
        .replace("{", "{{")
        .replace("}", "}}")
        .replace("\n", "\\n")
        .replace('"', '\\"')
        .replace("'", "\\'")
    )

def escape_for_sproc(code: str) -> str:
    return code.replace("$$", "\\$\\$")

# @NOTE: `overhead_rate` should fall between 0.05 and 0.5 depending on how time sensitive / expensive the operation in question is.
def poll_with_specified_overhead(
    f,
    overhead_rate: float, # This is the percentage of the time we've already waited before we'll poll again.
    start_time: float | None = None,
    timeout: int | None = None,
    max_tries: int | None = None,
    max_delay: float = 120,
    min_delay: float = 0.1
):
    if overhead_rate < 0:
        raise ValueError("overhead_rate must be non-negative")

    if start_time is None:
        start_time = time.time()

    tries = 0
    max_time = time.time() + timeout if timeout else None

    while True:
        if f():
            break

        current_time = time.time()

        if max_tries is not None and tries >= max_tries:
            raise Exception(f'max tries {max_tries} exhausted')

        if max_time is not None and current_time >= max_time:
            raise Exception(f'timed out after {timeout} seconds')

        duration = (current_time - start_time) * overhead_rate
        duration = max(min(duration, max_delay), min_delay, 0)

        time.sleep(duration)
        tries += 1

def get_with_retries(
    session: requests.Session,
    url: str,
    max_retries: int = 3,
    backoff_factor = 2,
    min_backoff_s = 2,
):
    attempt = 1
    jitter_s = random.uniform(0.5, 1.5)
    delay_s = min_backoff_s
    while True:
        res = session.get(url)
        attempt += 1
        if 500 <= res.status_code <= 504:
            if attempt > max_retries:
                res.raise_for_status()
            else:
                delay_s *= backoff_factor
                time.sleep(delay_s + jitter_s)
                continue
        return res

class ParseError(Exception):
    def __init__(self, identifier):
        super().__init__(f"\nCould not parse fully-qualified name; make sure the identifier is fully qualified and valid:\n{identifier}\n\n")

class IdentityParser:
    """
    Parse a fully-qualified name into its parts and normalize it.
    """
    SF_ID_REGEX = re.compile(r'^[A-Za-z_][A-Za-z0-9_$]*$')

    def __init__(self, identifier: str, require_all_parts: bool = False, force_upper_case: bool = True):
        """
        Args:
            identifier (str): The fully-qualified name to parse.
            require_all_parts (bool): If True, raise an error if any part of the identifier is missing.
            force_upper_case (bool): If True, force all non unique (not double quoted) parts of the identifier to be upper case as per SF standard.
        """
        self.identifier = identifier

        self.db_part = None
        self.schema_part = None
        self.entity_part = None
        self.identity = None
        self._is_complete = False
        self.has_double_quoted_identifier = False
        self.require_all_parts = require_all_parts
        self.force_upper_case = force_upper_case

        self._parse()

    @property
    def db(self):
        return self.db_part['part'] if self.db_part else None

    @property
    def schema(self):
        return self.schema_part['part'] if self.schema_part else None

    @property
    def entity(self):
        return self.entity_part['part'] if self.entity_part else None

    @property
    def is_complete(self):
        return self._is_complete

    def _parse(self):
        self.db_part = self._get_part(self.identifier)
        if self.db_part['next']:
            self.schema_part = self._get_part(self.db_part['next'])
            if self.schema_part['next']:
                self.entity_part = self._get_part(self.schema_part['next'])
                self._is_complete = True

        if self.require_all_parts and (not self.db or not self.schema or not self.entity):
            raise ParseError(self.identifier)

        normalized_parts = [self._normalize_id(x) for x in [self.db_part, self.schema_part, self.entity_part] if x]
        self.identity = '.'.join(part for part in normalized_parts if part is not None)

        # Set has_double_quoted_identifier to True if self.identity contains double quotes
        self.has_double_quoted_identifier = '"' in self.identity if self.identity else False

    def _get_part(self, string: str) -> dict:
        if len(string) == 0:
            return {'part': None, 'next': None}

        if string[0] == '"':
            return self._get_quoted_part(string)
        else:
            return self._get_normal_part(string)

    def _get_normal_part(self, string: str) -> dict:
        ret = ""
        i = 0
        for char in string:
            i += 1
            if char == '.':
                break
            ret += char

        if self.SF_ID_REGEX.match(ret) and self.force_upper_case:
            ret = ret.upper()
        return {'part': ret, 'quoted': False, 'next': string[i:]}

    def _get_quoted_part(self, string: str):
        ret = ""
        i = 1
        while i < len(string):
            char = string[i]
            next_char = string[i + 1] if i + 1 < len(string) else None
            if char == '"':
                if next_char == '.':
                    i += 2
                    break
                elif next_char == '"':
                    ret += '"'
                    i += 1
                elif next_char:
                    raise ParseError(string)
            else:
                ret += char
            i += 1
        return {'part': ret, 'quoted': True, 'next': string[i:]}

    def _normalize_id(self, dict: dict):
        if dict:
            if self.SF_ID_REGEX.match(dict['part']) and not dict['quoted']:
                return dict['part']
            else:
                return '"' + dict['part'].replace('"', '""') + '"'
        return None

    def to_list(self) -> list[str]:
        """
        Return a list of all the fully-qualified normalized name parts including the fqn.
        This list is essentially the same as the identity, but broken down into array of parts.
        """
        result = []
        for part in [self.db_part, self.schema_part, self.entity_part]:
            if part is not None:
                normalized = self._normalize_id(part)
                if normalized is not None:
                    result.append(normalized)
        # Add the identity if it exists last. It's the already normalized version of the fully-qualified name.
        if self.identity is not None:
            result.append(self.identity)
        return result

    @staticmethod
    def to_sql_value(str: str):
        """
        Remove quotes, escape single quotes, and add single quotes around the string.
        """
        _str = str
        if _str.startswith('"') and _str.endswith('"'):
            _str = _str[1:-1]
        return "'" + _str.replace("'", "''") + "'"

def safe_json_loads(s: str):
    return json.loads(s) if s.strip() else {}

def sanitize_module_name(raw_name: str) -> str:
    """
    Turn any Snowflake-normalized name into a valid Python module identifier:
      - lowercase
      - non-alphanumerics => underscore
      - no leading digit
      - collapse multiple underscores
      - strip leading/trailing underscores
      - fallback to 'module' if empty
    """
    name = raw_name.lower()
    # replace anything except a–z, 0–9, or _ with _
    name = re.sub(r"[^0-9a-z_]", "_", name)
    # ensure it doesn’t start with a digit
    if re.match(r"^\d", name):
        name = f"_{name}"
    return name

def ms_to_timestamp(ms):
    if not ms:
        return None
    dt = datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).astimezone()  # convert to local time
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + dt.strftime(' %z')

def get_pyrel_version(generation: Optional[Generation] = None):
    from relationalai import __version__
    if generation is None:
        return f"pyrel/{__version__}"
    else:
        return f"pyrel/{__version__}/{generation}"
