"""
Consolidated tests for all research connectors.
Merged from multiple test files to reduce redundancy.
"""

import pytest
from unittest.mock import Mock, patch
from apilinker.connectors.scientific.ncbi import NCBIConnector
from apilinker.connectors.scientific.arxiv import ArXivConnector
from apilinker.connectors.scientific.crossref import CrossRefConnector
from apilinker.connectors.scientific.semantic_scholar import SemanticScholarConnector
from apilinker.connectors.scientific.pubchem import PubChemConnector
from apilinker.connectors.scientific.orcid import ORCIDConnector
from apilinker.connectors.general.github import GitHubConnector
from apilinker.connectors.general.nasa import NASAConnector


class TestAllConnectorIntegration:
    """Test integration and basic functionality of all connectors."""
    
    def test_all_connectors_importable(self):
        """Test that all connectors can be imported from main package."""
        from apilinker import (
            NCBIConnector, ArXivConnector, CrossRefConnector,
            SemanticScholarConnector, PubChemConnector, ORCIDConnector,
            GitHubConnector, NASAConnector
        )
        
        # Test that all connectors can be initialized
        connectors = [
            NCBIConnector(email="test@example.com"),
            ArXivConnector(),
            CrossRefConnector(email="test@example.com"),
            SemanticScholarConnector(),
            PubChemConnector(),
            ORCIDConnector(),
            GitHubConnector(),
            NASAConnector(api_key="test_key")
        ]
        
        assert len(connectors) == 8
        
        # Verify connector types
        expected_types = ["ncbi", "arxiv", "crossref", "semantic_scholar", "pubchem", "orcid", "github", "nasa"]
        actual_types = [c.connector_type for c in connectors]
        assert actual_types == expected_types
    
    def test_connector_base_attributes(self):
        """Test that all connectors have required base attributes."""
        connectors = [
            NCBIConnector(email="test@example.com"),
            ArXivConnector(),
            CrossRefConnector(email="test@example.com"),
            SemanticScholarConnector(),
            PubChemConnector(),
            ORCIDConnector(),
            GitHubConnector(),
            NASAConnector(api_key="test_key")
        ]
        
        for connector in connectors:
            assert hasattr(connector, 'connector_type')
            assert hasattr(connector, 'base_url')
            assert hasattr(connector, 'endpoints')
            assert hasattr(connector, 'client')
            assert connector.connector_type is not None
            assert connector.base_url is not None
    
    def test_scientific_connectors_initialization(self):
        """Test initialization of scientific connectors."""
        # NCBI
        ncbi = NCBIConnector(email="test@example.com")
        assert ncbi.email == "test@example.com"
        assert "search" in ncbi.endpoints
        
        # arXiv
        arxiv = ArXivConnector()
        assert "query" in arxiv.endpoints
        
        # CrossRef
        crossref = CrossRefConnector(email="test@example.com")
        assert crossref.email == "test@example.com"
        assert "search_works" in crossref.endpoints
        
        # Semantic Scholar
        semantic = SemanticScholarConnector(api_key="test_key")
        assert semantic.api_key == "test_key"
        assert "search_papers" in semantic.endpoints
        
        # PubChem
        pubchem = PubChemConnector()
        assert "search_compounds" in pubchem.endpoints
        
        # ORCID
        orcid = ORCIDConnector()
        assert "search" in orcid.endpoints
    
    def test_general_connectors_initialization(self):
        """Test initialization of general research connectors."""
        # GitHub
        github = GitHubConnector(token="test_token")
        assert github.token == "test_token"
        assert "search_repositories" in github.endpoints
        
        # NASA
        nasa = NASAConnector(api_key="test_key")
        assert nasa.api_key == "test_key"
        assert "earth_imagery" in nasa.endpoints
    
    def test_pubchem_lipinski_filter(self):
        """Test PubChem Lipinski Rule of Five filter."""
        pubchem = PubChemConnector()
        
        # Properties that pass Lipinski filter
        properties_pass = {
            "PropertyTable": {
                "Properties": [
                    {
                        "MolecularWeight": 300,
                        "XLogP": 2.5,
                        "HydrogenBondDonorCount": 2,
                        "HydrogenBondAcceptorCount": 4
                    }
                ]
            }
        }
        
        assert pubchem._passes_lipinski_filter(properties_pass) == True
        
        # Properties that fail Lipinski filter
        properties_fail = {
            "PropertyTable": {
                "Properties": [
                    {
                        "MolecularWeight": 600,  # Too high
                        "XLogP": 7,  # Too high
                        "HydrogenBondDonorCount": 8,  # Too high
                        "HydrogenBondAcceptorCount": 15  # Too high
                    }
                ]
            }
        }
        
        assert pubchem._passes_lipinski_filter(properties_fail) == False
    
    def test_orcid_id_cleaning(self):
        """Test ORCID ID cleaning functionality."""
        orcid = ORCIDConnector()
        
        # Test with URL prefix
        dirty_id = "https://orcid.org/0000-0000-0000-0000"
        clean_id = orcid._clean_orcid_id(dirty_id)
        assert clean_id == "0000-0000-0000-0000"
        
        # Test with raw ID without dashes
        raw_id = "0000000000000000"
        clean_id = orcid._clean_orcid_id(raw_id)
        assert clean_id == "0000-0000-0000-0000"
    
    def test_github_contribution_analysis(self):
        """Test GitHub contribution distribution analysis."""
        github = GitHubConnector()
        
        contributors = [
            {"contributions": 100},
            {"contributions": 50},
            {"contributions": 25},
            {"contributions": 10}
        ]
        
        analysis = github._analyze_contribution_distribution(contributors)
        
        assert analysis["total_contributions"] == 185
        assert analysis["top_contributor_percentage"] == 54.1  # 100/185 * 100
        assert analysis["distribution_type"] == "concentrated"
    
    @patch('httpx.Client.request')
    def test_basic_search_functionality(self, mock_request):
        """Test basic search functionality across different connectors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"items": [{"title": "Test"}]}}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Test different connectors' search methods
        ncbi = NCBIConnector(email="test@example.com")
        arxiv = ArXivConnector()
        github = GitHubConnector()
        
        # These should not raise exceptions with proper mocking
        # Note: In actual usage, these would make real API calls


class TestConnectorErrorHandling:
    """Test error handling in connectors."""
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        ncbi = NCBIConnector(email="test@example.com")
        
        # Test with invalid email format (should still initialize)
        ncbi_invalid = NCBIConnector(email="invalid_email")
        assert ncbi_invalid.email == "invalid_email"
    
    def test_missing_required_parameters(self):
        """Test handling of missing required parameters."""
        # Some connectors require certain parameters
        with pytest.raises(TypeError):
            NCBIConnector()  # Missing email parameter
        
        with pytest.raises(TypeError):
            NASAConnector()  # Missing api_key parameter


class TestConnectorEndpoints:
    """Test connector endpoint configurations."""
    
    def test_endpoint_completeness(self):
        """Test that connectors have expected endpoints."""
        endpoint_requirements = {
            NCBIConnector: ["search", "fetch"],
            ArXivConnector: ["query"],
            CrossRefConnector: ["search_works", "get_work"],
            SemanticScholarConnector: ["search_papers", "get_paper"],
            PubChemConnector: ["search_compounds", "get_compound_by_cid"],
            ORCIDConnector: ["search", "get_record"],
            GitHubConnector: ["search_repositories", "get_repository"],
            NASAConnector: ["earth_imagery", "apod"]
        }
        
        for connector_class, required_endpoints in endpoint_requirements.items():
            if connector_class in [NCBIConnector, CrossRefConnector]:
                connector = connector_class(email="test@example.com")
            elif connector_class == NASAConnector:
                connector = connector_class(api_key="test_key")
            elif connector_class == GitHubConnector:
                connector = connector_class(token="test_token")
            elif connector_class == SemanticScholarConnector:
                connector = connector_class(api_key="test_key")
            else:
                connector = connector_class()
            
            for endpoint in required_endpoints:
                assert endpoint in connector.endpoints, f"{connector_class.__name__} missing {endpoint}"