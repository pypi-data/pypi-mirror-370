"""Additional tests for company client to improve coverage"""

from unittest.mock import patch

import pytest

from fmp_data.company.models import CompanyExecutive, CompanyPeer, CompanyProfile, Quote
from fmp_data.market.models import CompanySearchResult


class TestCompanyClientCoverage:
    """Tests to improve coverage for CompanyClient"""

    @pytest.fixture
    def company_profile_data(self):
        """Mock company profile data"""
        return {
            "symbol": "AAPL",
            "price": 195.50,
            "beta": 1.25,
            "volAvg": 50000000,
            "mktCap": 3000000000000,
            "lastDiv": 0.96,
            "range": "140.00-200.00",
            "changes": 2.50,
            "companyName": "Apple Inc.",
            "currency": "USD",
            "cik": "0000320193",
            "isin": "US0378331005",
            "cusip": "037833100",
            "exchange": "NASDAQ",
            "exchangeShortName": "NASDAQ",
            "industry": "Consumer Electronics",
            "website": "https://www.apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones...",  # noqa: E501
            "ceo": "Tim Cook",
            "sector": "Technology",
            "country": "US",
            "fullTimeEmployees": "164000",
            "phone": "408-996-1010",
            "address": "One Apple Park Way",
            "city": "Cupertino",
            "state": "CA",
            "zip": "95014",
            "dcfDiff": 15.25,
            "dcf": 180.25,
            "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
            "ipoDate": "1980-12-12",
            "defaultImage": False,
            "isEtf": False,
            "isActivelyTrading": True,
            "isAdr": False,
            "isFund": False,
        }

    @pytest.fixture
    def company_executive_data(self):
        """Mock company executive data"""
        return {
            "title": "Chief Executive Officer",
            "name": "Tim Cook",
            "pay": 91600000,
            "currencyPay": "USD",
            "gender": "male",
            "yearBorn": 1960,
            "titleSince": 2011,
        }

    @pytest.fixture
    def quote_data(self):
        """Mock quote data"""
        return {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 195.50,
            "changesPercentage": 1.28,
            "changePercentage": 1.28,  # Add the required field
            "change": 2.47,
            "dayLow": 193.00,
            "dayHigh": 196.50,
            "yearHigh": 200.00,
            "yearLow": 140.00,
            "marketCap": 3000000000000,
            "priceAvg50": 185.25,
            "priceAvg200": 175.50,
            "exchange": "NASDAQ",
            "volume": 55000000,
            "avgVolume": 50000000,
            "open": 193.50,
            "previousClose": 193.03,
            "eps": 6.13,
            "pe": 31.88,
            "earningsAnnouncement": "2024-02-01T21:30:00.000+0000",
            "sharesOutstanding": 15350000000,
            "timestamp": 1704067200,
        }

    @patch("httpx.Client.request")
    def test_get_company_profile(
        self, mock_request, fmp_client, mock_response, company_profile_data
    ):
        """Test fetching company profile"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_profile_data]
        )

        # get_profile returns a single CompanyProfile, not a list
        result = fmp_client.company.get_profile("AAPL")

        assert isinstance(result, CompanyProfile)
        assert result.symbol == "AAPL"
        assert result.company_name == "Apple Inc."
        assert result.mkt_cap == 3000000000000

    @patch("httpx.Client.request")
    def test_get_key_executives(
        self, mock_request, fmp_client, mock_response, company_executive_data
    ):
        """Test fetching key executives"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_executive_data]
        )

        # get_executives returns a list of CompanyExecutive
        result = fmp_client.company.get_executives("AAPL")

        assert len(result) == 1
        executive = result[0]
        assert isinstance(executive, CompanyExecutive)
        assert executive.name == "Tim Cook"
        assert executive.title == "Chief Executive Officer"
        assert executive.pay == 91600000

    @patch("httpx.Client.request")
    def test_get_quote(self, mock_request, fmp_client, mock_response, quote_data):
        """Test fetching company quote"""
        mock_request.return_value = mock_response(
            status_code=200, json_data=[quote_data]
        )

        # get_quote returns a single Quote object
        result = fmp_client.company.get_quote("AAPL")

        assert isinstance(result, Quote)
        assert result.symbol == "AAPL"
        assert result.price == 195.50
        assert result.market_cap == 3000000000000

    @patch("httpx.Client.request")
    def test_get_company_profile_with_multiple_symbols(
        self, mock_request, fmp_client, mock_response, company_profile_data
    ):
        """Test fetching company profiles for multiple symbols"""
        # Modify data for second company
        second_profile = company_profile_data.copy()
        second_profile["symbol"] = "MSFT"
        second_profile["companyName"] = "Microsoft Corporation"

        mock_request.return_value = mock_response(
            status_code=200, json_data=[company_profile_data, second_profile]
        )

        # When passing multiple symbols, get_profile could return multiple profiles
        result = fmp_client.company.get_profile("AAPL,MSFT")

        # If multiple profiles returned in a list response
        if isinstance(result, list):
            assert len(result) == 2
            assert result[0].symbol == "AAPL"
            assert result[1].symbol == "MSFT"
        else:
            # Single profile for single symbol
            assert result.symbol == "AAPL"

    @patch("httpx.Client.request")
    def test_search_companies(self, mock_request, fmp_client, mock_response):
        """Test searching companies"""
        search_results = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "currency": "USD",
                "stockExchange": "NASDAQ Global Select",
                "exchangeShortName": "NASDAQ",
            },
            {
                "symbol": "APLE",
                "name": "Apple Hospitality REIT, Inc.",
                "currency": "USD",
                "stockExchange": "New York Stock Exchange",
                "exchangeShortName": "NYSE",
            },
        ]

        mock_request.return_value = mock_response(
            status_code=200, json_data=search_results
        )

        # search_company is in the market client, not company client
        result = fmp_client.market.search_company("apple", limit=2)

        assert len(result) == 2
        assert isinstance(result[0], CompanySearchResult)
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "APLE"

    @patch("httpx.Client.request")
    def test_get_company_peers(self, mock_request, fmp_client, mock_response):
        """Test fetching company peers"""
        # CompanyPeer expects objects with symbol and companyName fields
        peers_data = [
            {
                "symbol": "MSFT",
                "companyName": "Microsoft Corporation",
                "price": 400.0,
                "mktCap": 3000000000000,
            },
            {
                "symbol": "GOOGL",
                "companyName": "Alphabet Inc.",
                "price": 150.0,
                "mktCap": 2000000000000,
            },
            {
                "symbol": "META",
                "companyName": "Meta Platforms Inc.",
                "price": 500.0,
                "mktCap": 1300000000000,
            },
            {
                "symbol": "AMZN",
                "companyName": "Amazon.com Inc.",
                "price": 180.0,
                "mktCap": 1900000000000,
            },
            {
                "symbol": "NVDA",
                "companyName": "NVIDIA Corporation",
                "price": 900.0,
                "mktCap": 2200000000000,
            },
        ]

        mock_request.return_value = mock_response(status_code=200, json_data=peers_data)

        result = fmp_client.company.get_company_peers("AAPL")

        assert len(result) == 5
        assert isinstance(result[0], CompanyPeer)
        assert result[0].symbol == "MSFT"
        assert result[0].name == "Microsoft Corporation"
