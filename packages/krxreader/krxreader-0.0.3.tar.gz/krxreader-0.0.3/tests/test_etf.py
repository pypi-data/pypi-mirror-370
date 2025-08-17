import pytest

from krxreader.etf import ETF


@pytest.mark.skipif(False, reason='requires http request')
def test_search_issue():
    etf = ETF()

    item = etf.search_issue('102110')
    assert item == ('TIGER 200', '102110', 'KR7102110004')

    item = etf.search_issue('TIGER 200')
    assert item == ('TIGER 200', '102110', 'KR7102110004')

    item = etf.search_issue('489250')
    assert item == ('KODEX 미국배당다우존스', '489250', 'KR7489250001')

    item = etf.search_issue('KODEX 미국배당다우존스')
    assert item == ('KODEX 미국배당다우존스', '489250', 'KR7489250001')


@pytest.mark.skipif(False, reason='requires http request')
def test_etf_price():
    etf = ETF('20250814')
    data = etf.etf_price()

    assert data[16]['ISU_SRT_CD'] == '105190'
    assert data[16]['ISU_ABBRV'] == 'ACE 200'
    assert data[16]['IDX_IND_NM'] == '코스피 200'
    assert data[16]['TDD_CLSPRC'] == '43,955'
    assert len(data[16]) == 22


@pytest.mark.skipif(False, reason='requires http request')
def test_etf_price_rate():
    etf = ETF(end='20250814')
    data = etf.etf_price_rate()

    assert data[828]['ISU_SRT_CD'] == '360750'
    assert data[828]['ISU_ABBRV'] == 'TIGER 미국S&P500'
    assert data[828]['BAS_PRC'] == '21,850'
    assert data[828]['CLSPRC'] == '22,145'
    assert len(data[828]) == 9


@pytest.mark.skipif(False, reason='requires http request')
def test_price_by_issue():
    etf = ETF(end='20250814')
    data = etf.price_by_issue('489250')

    assert data[0]['TDD_CLSPRC'] == '10,335'
    assert data[1]['TDD_CLSPRC'] == '10,200'
    assert data[6]['TDD_CLSPRC'] == '10,185'

    assert len(data) == 7
    assert len(data[0]) == 19


@pytest.mark.skipif(False, reason='requires http request')
def test_all_etf_issues():
    etf = ETF()
    data = etf.all_etf_issues()

    assert len(data[0]) == 17


@pytest.mark.skipif(False, reason='requires http request')
def test_portfolio_deposit_file():
    etf = ETF('20250814')
    data = etf.portfolio_deposit_file('0086B0')

    assert data[0]['COMPST_ISU_NM'] == '맥쿼리인프라'
    assert data[1]['COMPST_ISU_NM'] == 'ESR켄달스퀘어리츠'
    assert data[2]['COMPST_ISU_NM'] == 'SK리츠'

    assert len(data) == 11
    assert len(data[0]) == 9
