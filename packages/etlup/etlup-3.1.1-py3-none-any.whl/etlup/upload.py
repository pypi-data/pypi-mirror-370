from .construction.adapters import ConstrModel, ConstrArrModel
from datetime import datetime
from pydantic import BaseModel
from typing import Iterable, Optional, Any, Union
import json
import pytz
import os
import warnings
import requests
from urllib.parse import urljoin
from pathlib import Path
API_TOKEN_ENV = "ETL_API_TOKEN"

class Config:
    """Configuration class for ETL session settings."""
    
    def __init__(self):
        self.api_token: Optional[str] = None

    def load_from_env(self, dotenv_path: Union[None, str]):
        """Load configuration from environment variables and .env file."""
        try:
            from dotenv import load_dotenv, find_dotenv
            if dotenv_path is None:
                dotenv_path = find_dotenv(usecwd=True)

            if not Path(dotenv_path).is_file():
                raise FileNotFoundError(f"Your .env file at {dotenv_path} does not exist.")
            
            env_loaded = load_dotenv(dotenv_path, override=True)
            print(f"loaded env: {env_loaded}")
        except ImportError:
            pass
        
        self.api_token = os.getenv(API_TOKEN_ENV)
        return self
    
    def validate_api_token(self) -> str:
        """Validate and return the API token, raising error if not found."""
        if self.api_token and self.api_token.strip():
            return self.api_token.strip()
        raise ValueError(
            f"API token not found. Set {API_TOKEN_ENV}=<token> in your environment "
            f"or .env file."
        )

def user_default_tz():
    """
    !NOT IMPLEMENTED! It would be nice to auto catch user timezone from their computer maybe
    """
    user_tz = datetime.now().astimezone().tzinfo
    warnings.warn(f"Explicit timezone information was not provided using your system default: {user_tz}")
    return user_tz

def localize_datetime(dt: datetime, tz: str = "auto") -> datetime:
    """
    Localize or convert a datetime to the specified timezone.

    - tz='auto': use the computer's local timezone.
    - If dt is naive: assign the timezone (pytz.localize when available).
    - If dt is aware: convert to the target timezone.
    """
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime.datetime")

    if tz == "auto":
        target_tz = datetime.now().astimezone().tzinfo  # local system tz
    else:
        if tz not in pytz.all_timezones:
            raise ValueError(
                f"Timezone '{tz}' is not valid. See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            )
        target_tz = pytz.timezone(tz)

    if dt.tzinfo is None:
        # naive -> assign timezone
        localizer = getattr(target_tz, "localize", None)
        return localizer(dt) if callable(localizer) else dt.replace(tzinfo=target_tz)

    # aware -> convert
    return dt.astimezone(target_tz)

def now_utc() -> datetime:
    """
    Return the current time as a timezone-aware UTC datetime.
    """
    return datetime.now(tz=pytz.UTC)

def get_model(version: str, constr_type: str):
    try:
        return ConstrModel.core_schema['schema']['choices'][version]['choices'][constr_type]["cls"]
    except KeyError:  # this only for the case for no versions, pydantic simplies the map
        return ConstrModel.core_schema['schema']['choices'][constr_type]["cls"]

class Session:
    """
    A lightweight API for committing ETL assemblies and tests.

    Options:
    prod: bool, If true it will be uploaded to the production instance
    domain: str, Overwrites prod and will attempt to upload to this domain, exmaples: http://127.0.0.1/ or https://prod-etl.app.cern.ch/
    for_assembly: bool, If true it uploads it as an assembly, otherwise a test, default is False
    dotenv_path: str, :Lets you  overwrite the default location of .env path (same directory as the python file you are running the script from) to a different location
    
    Usage:
    from etlup import now_utc, localize_datetime, Session, tests
    import numpy as np

    bl = tests.tamalero.BaselineNoisewidthV0(
        module = "PBU003",
        location = "BU",
        user_created = "hswanson",
        type = "noisewidth",
        version = "0.0",
        measurement_date = now_utc(),
        data = {
            "U1": np.zeros((16,16)),
            "U2": np.ones((16,16)),
            "U3": np.zeros((16,16)),
            "U4": np.ones((16,16))
        }
    )
    with Session(domain="http://127.0.0.1/") as sesh:    
        sesh.add(bl)
        sesh.to_file()
        sesh.upload()
    """

    def __init__(self, prod=False, domain=None, for_assembly=False, dotenv_path=None):
        self._constrs: list[BaseModel] = []  # only Pydantic models
        self.config = Config().load_from_env(dotenv_path)

        if domain is not None:
            self.api_domain = domain
        elif prod == True:
            self.api_domain = "https://prod-etl.app.cern.ch/"
        else:
            self.api_domain = "https://staging-etl.app.cern.ch/"
        
        endpoint = f"api/upload/{'assembly' if for_assembly else 'test'}"
        base = self.api_domain.rstrip('/') + '/'
        self.api_url = urljoin(base, endpoint.lstrip('/'))
        print(f"Using the API URL: {self.api_url}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # Always clear pending constructions on exit
        self.clear()
        # Propagate any exception
        return False

    def add(self, constr: BaseModel):
        """
        Add a single construction payload (Pydantic model only).
        """
        if not isinstance(constr, BaseModel):
            raise TypeError("Only Pydantic BaseModel instances can be added. Dicts are not supported.")
        self._constrs.append(constr)
        return self

    def add_all(self, items: Iterable[BaseModel]):
        for item in items:
            self.add(item)
        return self

    def clear(self):
        """
        Removes all the loaded assemblies or tests
        """
        self._constrs.clear()

    def _build_payload(self) -> Any:
        """
        Build a JSON-serializable payload for the pending constructions.
        Uses the ConstrArrModel TypeAdapter to ensure schema correctness.
        """
        if not self._constrs:
            raise ValueError("Cannot commit when no assembly or tests were added")
        
        # dump_python(..., mode='json') returns JSON-ready Python data
        return ConstrArrModel.dump_python(self._constrs, mode="json")

    def to_file(self, filepath: str = "") -> str:
        """
        Serialize the pending constructions to a JSON file (no network).
        """
        if not filepath:
            filepath = os.path.join(os.getcwd(), 'construction_upload.json')

        payload = self._build_payload()
        with open(filepath, 'w') as json_file:
            json.dump(payload, json_file, indent=4)
        return filepath

    def upload(
        self,
        timeout: float = 30.0,
        dry_run: bool = False,
    ) -> dict:
        """
        Commit pending constructions to the API.

        - base_url: overrides ETL_API_URL
        - dry_run: if True, do not POST; return the payload instead
        """
        payload = self._build_payload()

        if dry_run:
            return {"dry_run": True, 
                    "payload": payload, 
                    "count": len(self._constrs)}

        auth_token = self.config.validate_api_token()
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        
        resp = requests.post(self.api_url, 
                                json=payload, 
                                headers=headers, 
                                timeout=timeout)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            data = resp.text
            raise requests.HTTPError(
                f"{data}",
                response = resp,
                request = exc.request
            )
        try:
            return resp.json()
        except ValueError:
            raise RuntimeError("Upload succeeded but response body was not valid JSON")