from .base import KrxBase


class ETF(KrxBase):
    """통계 > 기본 통계 > 증권상품 > ETF

    :param date: 조회일자
    :param start: 조회기간 start
    :param end: 조회기간 end
    """

    def __init__(
            self,
            date: str | None = None,
            start: str | None = None,
            end: str | None = None
    ):
        super().__init__(date, start, end)

        # '1': 좌
        # '2': 천좌
        # '3': 백만좌
        self._share = '1'
        # '1': 원
        # '2': 천원
        # '3': 백만원
        # '4': 십억원
        self._money = '1'

    def search_issue(self, issue_code: str) -> tuple:
        """ETF 종목 검색"""

        bld = 'dbms/comm/finder/finder_secuprodisu'
        params = {
            'mktsel': 'ETF',
            'searchText': issue_code
        }

        return self.search_item(bld, params)

    def etf_price(self) -> list[dict]:
        """[13101] 통계 > 기본 통계 > 증권상품 > ETF > 전종목 시세"""

        bld = 'dbms/MDC/STAT/standard/MDCSTAT04301'
        params = {
            'trdDd': self._date,
            'share': self._share,
            'money': self._money
        }

        return self.fetch_data(bld, params)

    def etf_price_rate(self) -> list[dict]:
        """[13102] 통계 > 기본 통계 > 증권상품 > ETF > 전종목 등락률"""

        bld = 'dbms/MDC/STAT/standard/MDCSTAT04401'
        params = {
            'strtDd': self._start,
            'endDd': self._end,
            'share': self._share,
            'money': self._money
        }

        return self.fetch_data(bld, params)

    def price_by_issue(self, issue_code: str) -> list[dict]:
        """[13103] 통계 > 기본 통계 > 증권상품 > ETF > 개별종목 시세 추이"""

        (item_name, item_code, full_code) = self.search_issue(issue_code)

        bld = 'dbms/MDC/STAT/standard/MDCSTAT04501'
        params = {
            'tboxisuCd_finder_secuprodisu1_0': item_code + '/' + item_name,
            'isuCd': full_code,
            'isuCd2': 'KR7152100004',
            'codeNmisuCd_finder_secuprodisu1_0': item_name,
            'param1isuCd_finder_secuprodisu1_0': '',
            'strtDd': self._start,
            'endDd': self._end,
            'share': self._share,
            'money': self._money
        }

        return self.fetch_data(bld, params)

    def all_etf_issues(self) -> list[dict]:
        """[13104] 통계 > 기본 통계 > 증권상품 > ETF > 전종목 기본정보"""

        bld = 'dbms/MDC/STAT/standard/MDCSTAT04601'
        params = {
            'share': self._share
        }

        return self.fetch_data(bld, params)

    def portfolio_deposit_file(self, issue_code: str) -> list[dict]:
        """[13108] 통계 > 기본 통계 > 증권상품 > ETF > PDF(Portfolio Deposit File)"""

        (item_name, item_code, full_code) = self.search_issue(issue_code)

        bld = 'dbms/MDC/STAT/standard/MDCSTAT05001'
        params = {
            'tboxisuCd_finder_secuprodisu1_0': item_code + '/' + item_name,
            'isuCd': full_code,
            'isuCd2': 'KR7152100004',
            'codeNmisuCd_finder_secuprodisu1_0': item_name,
            'param1isuCd_finder_secuprodisu1_0': '',
            'trdDd': self._date,
            'share': self._share,
            'money': self._money
        }

        return self.fetch_data(bld, params)
