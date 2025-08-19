from copyreg import constructor
import json
import logging
from os import getenv
import re
import psycopg
from datetime import date, datetime
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

HTTP_200_OK = 200
HTTP_204_NO_CONTENT = 204


class FdsnNetExtender:
    """
    Toolbox to manage the correspondance between a short network code
    and an extended network code.
    Correspondance is made using the metadata
    """

    def __init__(
        self,
        base_url="postgres://resifinv_ro@resif-pgprod.u-ga.fr:5432/resifInv-Prod",
    ):
        """
        param: base_url is the base url for getting metadata. Default is resifInv prod database.
        """
        # we can guess that a network is temporary from this regex:
        logging.basicConfig()
        self.logger = logging.getLogger("fdsnnetextender")
        self.tempo_network_re = "^[0-9XYZ][0-9A-Z]$"
        self.base_url = base_url.replace("PASS", getenv("PGPASS", default=""))
        self.date_format = "%Y-%m-%d"

    def extend(self, net, date_string):
        """
        Param date_string can be a year or a date string like 2022-01-01
        """
        found = False
        extnet = net
        # Only extend temporary networks
        if re.match(self.tempo_network_re, net):
            # Normalize the start year from date_string
            try:
                # Can I cast it to an integer ? ie. is date_string just the year ?
                dateparam = date(year=int(date_string), month=1, day=1)
            except ValueError:
                self.logger.debug(
                    "Parameter %s is not a year. "
                    "Trying to guess the date in iso format",
                    date_string,
                )
                try:
                    dateparam = datetime.strptime(date_string, self.date_format).date()
                except ValueError as err:
                    msg = (
                        "date argument is not in format YYYY-MM-DD."
                        "Expected like 2022-01-01."
                    )
                    raise ValueError(msg) from err
            # Now that we have a start date :
            print("Trying to extend %s for %s", net, dateparam)
            # In order to make effective use of cache,
            # we always consider the first day of the year.
            # This should work except if a network code has been reused
            # in the same year. Is this possible ?
            extnet = self._get_fdsn_network(net, dateparam.year)
            if extnet is None:
                raise ValueError("No network at %s, %s", net, dateparam.year)
        return extnet

    @lru_cache(maxsize=1000)
    def _get_fdsn_network(self, net, year):
        """
        This function gets all networks metadata from database
        Returns the extended network code
        all the networks matching the short code.
        params:
        net : the short network code

        """
        net_result = [None]
        try:
            with psycopg.connect(self.base_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        select network||start_year from networks
                        where network=%s
                        and start_year <= %s
                        order by start_year desc
                        """,
                        (
                            net,
                            year,
                        ),
                    )
                    net_result = cur.fetchone()
        except:
            self.logger.exception("ERROR connecting to database")
        if isinstance(net_result, tuple):
            return net_result[0]
        else:
            return None
