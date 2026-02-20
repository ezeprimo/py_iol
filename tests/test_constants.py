"""
Tests para pyIol.constants
"""

from pyIol.constants import (
    API_BASE_URL,
    DEFAULT_COUNTRY,
    DEFAULT_MARKET,
    DEFAULT_ORDER_VALIDITY_HOURS,
    DEFAULT_SETTLEMENT_TERM,
    TOKEN_URL,
    USER_AGENT,
    Countries,
    CPDSegments,
    CPDStates,
    Markets,
    OperationStates,
    SettlementTerms,
)


class TestURLConstants:
    """Tests para constantes de URL"""

    def test_token_url(self):
        """Verifica que TOKEN_URL tenga el formato correcto"""
        assert TOKEN_URL == "https://api.invertironline.com/token"
        assert TOKEN_URL.startswith("https://")

    def test_api_base_url(self):
        """Verifica que API_BASE_URL tenga el formato correcto"""
        assert API_BASE_URL == "https://api.invertironline.com/api/v2"
        assert API_BASE_URL.startswith("https://")
        assert "v2" in API_BASE_URL

    def test_user_agent(self):
        """Verifica que USER_AGENT este definido"""
        assert USER_AGENT == "pyIol/1.0"
        assert "pyIol" in USER_AGENT


class TestMarkets:
    """Tests para la clase Markets"""

    def test_bcba_market(self):
        """Verifica el mercado BCBA"""
        assert Markets.BCBA == "bCBA"

    def test_nyse_market(self):
        """Verifica el mercado NYSE"""
        assert Markets.NYSE == "nYSE"

    def test_nasdaq_market(self):
        """Verifica el mercado NASDAQ"""
        assert Markets.NASDAQ == "nASDAQ"

    def test_amex_market(self):
        """Verifica el mercado AMEX"""
        assert Markets.AMEX == "aMEX"

    def test_bcs_market(self):
        """Verifica el mercado BCS"""
        assert Markets.BCS == "bCS"

    def test_rofx_market(self):
        """Verifica el mercado ROFX"""
        assert Markets.ROFX == "rOFX"

    def test_all_markets_lowercase_first_letter(self):
        """Verifica que todos los mercados tengan la primera letra en minuscula"""
        markets = [
            Markets.BCBA,
            Markets.NYSE,
            Markets.NASDAQ,
            Markets.AMEX,
            Markets.BCS,
            Markets.ROFX,
        ]
        for market in markets:
            assert market[0].islower(), f"Market {market} should start with lowercase"


class TestSettlementTerms:
    """Tests para la clase SettlementTerms"""

    def test_t0_term(self):
        """Verifica el plazo T0"""
        assert SettlementTerms.T0 == "t0"

    def test_t1_term(self):
        """Verifica el plazo T1"""
        assert SettlementTerms.T1 == "t1"

    def test_t2_term(self):
        """Verifica el plazo T2"""
        assert SettlementTerms.T2 == "t2"

    def test_t3_term(self):
        """Verifica el plazo T3"""
        assert SettlementTerms.T3 == "t3"

    def test_all_terms_lowercase(self):
        """Verifica que todos los plazos esten en minusculas"""
        terms = [SettlementTerms.T0, SettlementTerms.T1, SettlementTerms.T2, SettlementTerms.T3]
        for term in terms:
            assert term.islower(), f"Term {term} should be lowercase"


class TestOperationStates:
    """Tests para la clase OperationStates"""

    def test_all_state(self):
        """Verifica el estado 'todas'"""
        assert OperationStates.ALL == "todas"

    def test_pending_state(self):
        """Verifica el estado 'pendientes'"""
        assert OperationStates.PENDING == "pendientes"

    def test_finished_state(self):
        """Verifica el estado 'terminadas'"""
        assert OperationStates.FINISHED == "terminadas"

    def test_cancelled_state(self):
        """Verifica el estado 'canceladas'"""
        assert OperationStates.CANCELLED == "canceladas"


class TestCountries:
    """Tests para la clase Countries"""

    def test_argentina(self):
        """Verifica el pais Argentina"""
        assert Countries.ARGENTINA == "argentina"

    def test_usa(self):
        """Verifica el pais USA"""
        assert Countries.USA == "estados_Unidos"


class TestCPDStates:
    """Tests para la clase CPDStates"""

    def test_vigentes(self):
        """Verifica el estado 'vigentes'"""
        assert CPDStates.VIGENTES == "vigentes"

    def test_vencidos(self):
        """Verifica el estado 'vencidos'"""
        assert CPDStates.VENCIDOS == "vencidos"

    def test_todos(self):
        """Verifica el estado 'todos'"""
        assert CPDStates.TODOS == "todos"


class TestCPDSegments:
    """Tests para la clase CPDSegments"""

    def test_avalados(self):
        """Verifica el segmento 'avalados'"""
        assert CPDSegments.AVALADOS == "avalados"

    def test_patrocinados(self):
        """Verifica el segmento 'patrocinados'"""
        assert CPDSegments.PATROCINADOS == "patrocinados"

    def test_garantizados(self):
        """Verifica el segmento 'garantizados'"""
        assert CPDSegments.GARANTIZADOS == "garantizados"

    def test_todos(self):
        """Verifica el segmento 'todos'"""
        assert CPDSegments.TODOS == "todos"


class TestDefaultValues:
    """Tests para los valores por defecto"""

    def test_default_market(self):
        """Verifica que el mercado por defecto sea BCBA"""
        assert DEFAULT_MARKET == Markets.BCBA

    def test_default_settlement_term(self):
        """Verifica que el plazo por defecto sea T1"""
        assert DEFAULT_SETTLEMENT_TERM == SettlementTerms.T1

    def test_default_country(self):
        """Verifica que el pais por defecto sea Argentina"""
        assert DEFAULT_COUNTRY == Countries.ARGENTINA

    def test_default_order_validity_hours(self):
        """Verifica que la validez por defecto de órdenes sea 3 horas"""
        assert DEFAULT_ORDER_VALIDITY_HOURS == 3
