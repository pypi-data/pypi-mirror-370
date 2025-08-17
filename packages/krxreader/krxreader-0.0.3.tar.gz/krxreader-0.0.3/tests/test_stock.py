import pytest

from krxreader.stock import Stock


@pytest.mark.skipif(False, reason='requires http request')
def test_search_issue():
    stock = Stock()

    item = stock.search_issue('005930')
    assert item == ('삼성전자', '005930', 'KR7005930003')

    item = stock.search_issue('삼성전자')
    assert item == ('삼성전자', '005930', 'KR7005930003')

    item = stock.search_issue('035420')
    assert item == ('NAVER', '035420', 'KR7035420009')

    item = stock.search_issue('NAVER')
    assert item == ('NAVER', '035420', 'KR7035420009')


@pytest.mark.skipif(False, reason='requires http request')
def test_stock_price():
    stock = Stock('20250814', market='ALL')
    data = stock.stock_price()

    assert data[0]['ISU_SRT_CD'] == '060310'
    assert data[0]['ISU_ABBRV'] == '3S'
    assert data[0]['MKT_NM'] == 'KOSDAQ'
    assert data[0]['TDD_CLSPRC'] == '1,865'
    assert len(data[0]) == 17

    stock = Stock('20250814', market='STK')
    data = stock.stock_price()

    assert data[0]['ISU_SRT_CD'] == '095570'
    assert data[0]['ISU_ABBRV'] == 'AJ네트웍스'
    assert data[0]['MKT_NM'] == 'KOSPI'
    assert data[0]['TDD_CLSPRC'] == '4,225'
    assert len(data[0]) == 17

    stock = Stock('20250814', market='KSQ')
    data = stock.stock_price()

    assert data[0]['ISU_SRT_CD'] == '060310'
    assert data[0]['ISU_ABBRV'] == '3S'
    assert data[0]['MKT_NM'] == 'KOSDAQ'
    assert data[0]['TDD_CLSPRC'] == '1,865'
    assert len(data[0]) == 17

    stock = Stock('20250814', market='KNX')
    data = stock.stock_price()

    assert data[0]['ISU_SRT_CD'] == '278990'
    assert data[0]['ISU_ABBRV'] == 'EMB'
    assert data[0]['MKT_NM'] == 'KONEX'
    assert data[0]['TDD_CLSPRC'] == '3,100'
    assert len(data[0]) == 17


@pytest.mark.skipif(False, reason='requires http request')
def test_stock_price_change():
    stock = Stock(end='20240123')
    data = stock.stock_price_change()

    assert data[597]['ISU_SRT_CD'] == '192080'  # ISU_SRT_CD (종목코드)
    assert data[597]['BAS_PRC'] == '43,358'     # BAS_PRC (시작일 기준가)
    assert data[597]['TDD_CLSPRC'] == '40,450'  # TDD_CLSPRC (종료일 종가)

    stock = Stock(end='20240123', adjusted_price=False)
    data = stock.stock_price_change()

    assert data[597]['ISU_SRT_CD'] == '192080'
    assert data[597]['BAS_PRC'] == '51,200'
    assert data[597]['TDD_CLSPRC'] == '40,450'


@pytest.mark.skipif(False, reason='requires http request')
def test_price_by_issue():
    stock = Stock(end='20250814')
    data = stock.price_by_issue('035420')  # NAVER

    assert data[0]['TDD_CLSPRC'] == '224,500'
    assert data[1]['TDD_CLSPRC'] == '225,000'
    assert data[6]['TDD_CLSPRC'] == '228,500'

    assert len(data) == 7
    assert len(data[0]) == 12
