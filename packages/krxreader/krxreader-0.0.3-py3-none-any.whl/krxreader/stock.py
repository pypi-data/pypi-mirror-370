from .base import KrxBase


class Stock(KrxBase):
    """통계 > 기본 통계 > 주식

    :param date: 조회일자
    :param start: 조회기간 start
    :param end: 조회기간 end
    :param market: 'ALL': 전체, 'STK': KOSPI, 'KSQ': KOSDAQ, 'KNX': KONEX
    :param adjusted_price: 수정주가 적용
    """

    def __init__(
            self,
            date: str | None = None,
            start: str | None = None,
            end: str | None = None,
            market: str = 'ALL',
            adjusted_price: bool = True
    ):
        super().__init__(date, start, end)

        self._market = market
        self._adjusted_price = adjusted_price
        # '1': 주
        # '2': 천주
        # '3': 백만주
        self._share = '1'
        # '1': 원
        # '2': 천원
        # '3': 백만원
        # '4': 십억원
        self._money = '1'

    def search_issue(self, issue_code: str) -> tuple:
        """주식 종목 검색"""

        bld = 'dbms/comm/finder/finder_stkisu'
        params = {
            'mktsel': 'ALL',
            'typeNo': '0',
            'searchText': issue_code
        }

        return self.search_item(bld, params)

    def stock_price(self) -> list[dict]:
        """[12001] 통계 > 기본 통계 > 주식 > 종목시세 > 전종목 시세"""

        bld = 'dbms/MDC/STAT/standard/MDCSTAT01501'
        params = {
            'mktId': self._market
        }

        if self._market == 'KSQ':
            params.update({
                'segTpCd': 'ALL'
            })

        params.update({
            'trdDd': self._date,
            'share': self._share,
            'money': self._money
        })

        return self.fetch_data(bld, params)

    def stock_price_change(self) -> list[dict]:
        """[12002] 통계 > 기본 통계 > 주식 > 종목시세 > 전종목 등락률"""

        bld = 'dbms/MDC/STAT/standard/MDCSTAT01602'
        params = {
            'mktId': self._market
        }

        if self._market == 'KSQ':
            params.update({
                'segTpCd': 'ALL'
            })

        params.update({
            'strtDd': self._start,
            'endDd': self._end
        })

        if self._adjusted_price is True:
            params.update({
                'adjStkPrc_check': 'Y',
                'adjStkPrc': '2'
            })
        else:
            params.update({
                'adjStkPrc': '1'
            })

        params.update({
            'share': self._share,
            'money': self._money
        })

        return self.fetch_data(bld, params)

    def price_by_issue(self, issue_code: str) -> list[dict]:
        """[12003] 통계 > 기본 통계 > 주식 > 종목시세 > 개별종목 시세 추이"""

        (item_name, item_code, full_code) = self.search_issue(issue_code)

        bld = 'dbms/MDC/STAT/standard/MDCSTAT01701'
        params = {
            'tboxisuCd_finder_stkisu0_0': item_code + '/' + item_name,
            'isuCd': full_code,
            'isuCd2': 'KR7005930003',
            'codeNmisuCd_finder_stkisu0_0': item_name,
            'param1isuCd_finder_stkisu0_0': 'ALL',
            'strtDd': self._start,
            'endDd': self._end
        }

        if self._adjusted_price is True:
            params.update({
                'adjStkPrc_check': 'Y',
                'adjStkPrc': '2'
            })
        else:
            params.update({
                'adjStkPrc': '1'
            })

        params.update({
            'share': self._share,
            'money': self._money
        })

        return self.fetch_data(bld, params)
