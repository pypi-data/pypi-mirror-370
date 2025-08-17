import csv
import datetime
import logging

from krxfetch import fetch

from . import calendar


def _trading_date(dt: datetime.datetime = None, base_hour: int = 0) -> str:
    """Return trading date

    Return the previous date if it is the closing date or before base_hour.
    """
    if dt is None:
        dt = calendar.now()

    # Before the base hour
    if dt.hour < base_hour:
        dt = dt - datetime.timedelta(days=1)

    # When it is the closing date
    while calendar.is_closing_day(dt):
        dt = dt - datetime.timedelta(days=1)

    date = dt.strftime('%Y%m%d')

    return date


class KrxBase:
    """Base Class for Stock, Index, Bond, etc.

    :param date: 조회일자
    :param start: 조회기간 start
    :param end: 조회기간 end
    :param base_hour: 날짜 계산의 기준 시간
    :param start_days: 조회기간 start 의 default 값
    """

    def __init__(
            self,
            date: str | None = None,
            start: str | None = None,
            end: str | None = None,
            base_hour: int = 9,
            start_days: int = 8
    ):
        self._date = date
        self._start = start
        self._end = end

        now_date = _trading_date(dt=None, base_hour=base_hour)

        if self._date is None:
            self._date = now_date

        if self._end is None:
            self._end = now_date

        if self._start is None:
            dt = datetime.datetime.strptime(self._end, '%Y%m%d')
            dt = dt - datetime.timedelta(days=start_days)
            self._start = _trading_date(dt=dt, base_hour=0)

        self._locale = 'ko_KR'
        self._csvxls_is_no = 'false'

    def fetch_json(self, bld: str, params: dict) -> list[dict]:
        payload = {
            'bld': bld,
            'locale': self._locale
        }
        payload.update(params)
        payload.update({
            'csvxls_isNo': self._csvxls_is_no
        })
        logging.info(payload)

        data = fetch.get_json_data(payload)

        return data

    def fetch_csv(self, bld: str, params: dict) -> list[dict]:
        payload = {
            'locale': self._locale
        }
        payload.update(params)
        payload.update({
            'csvxls_isNo': self._csvxls_is_no,
            'name': 'fileDown',
            'url': bld
        })
        logging.info(payload)

        csv_str = fetch.download_csv(payload)

        reader = csv.DictReader(csv_str.splitlines())
        data = list(reader)

        return data

    def fetch_data(self, bld: str, params: dict) -> list[dict]:
        return self.fetch_json(bld, params)

    def search_item(self, bld: str, params: dict) -> tuple:
        payload = {
            'locale': self._locale
        }
        payload.update(params)
        payload.update({
            'bld': bld
        })
        logging.info(payload)

        dic_lst = fetch.get_json_data(payload)
        first_item = dic_lst[0]

        return (
            first_item['codeName'],
            first_item['short_code'],
            first_item['full_code']
        )
