import requests
import os


from dotenv import (
  load_dotenv,
  find_dotenv
)
from ..params import vars
from ..params.params import (
  Apikey,
  FileType,
)
from ..params.exceptions import (
  InvalidApikeyFormat,
  MissingApikey,
)
from typing import (
  Dict, Any
)
DOTENV = load_dotenv(find_dotenv())


class Fred:

  @classmethod
  def request(
    cls,
    endpoint: str,
    params: Dict[str, Any] = {},
  ) -> Dict:
    if not vars.APIKEY:
      if DOTENV:
        apikey = os.getenv('FRED_APIKEY')

        if apikey:
          vars.APIKEY = Apikey(apikey)
    
    if not vars.APIKEY:
      raise MissingApikey()

    if len(str(vars.APIKEY)) != 32:
      raise InvalidApikeyFormat()

    url = '/'.join([vars.BASEURL, endpoint])
    params['api_key'] = str(vars.APIKEY)
    params['file_type'] = str(FileType())
    response = requests.get(
      url,
      params=params)
    data = response.json()
    return data