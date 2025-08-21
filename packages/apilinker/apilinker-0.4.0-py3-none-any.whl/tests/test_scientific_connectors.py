"""
Tests for scientific API connectors.
"""

import pytest
from unittest.mock import Mock, patch
from apilinker.connectors.scientific.ncbi import NCBIConnector
from apilinker.connectors.scientific.arxiv import ArXivConnector


class TestNCBIConnector:
    """Test suite for NCBI connector."""
    
    def setup_method(self):
        """Set up test environment."""
        self.connector = NCBIConnector(
            email="test@example.com",
            api_key="test_key"
        )
    
    def test_initialization(self):
        """Test NCBI connector initialization."""
        assert self.connector.email == "test@example.com"
        assert self.connector.api_key == "test_key"
        assert self.connector.base_url == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        assert "search" in self.connector.endpoints
        assert "fetch" in self.connector.endpoints
    
    @patch('httpx.Client.request')
    def test_search_pubmed(self, mock_request):
        """Test PubMed search functionality."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "esearchresult": {
                "idlist": ["12345", "67890"],
                "count": "2",
                "retmax": "2"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.connector.search_pubmed("CRISPR", max_results=2)
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        # Check that PubMed-specific parameters were included
        params = call_args[1]['params']
        assert params['db'] == 'pubmed'
        assert params['term'] == 'CRISPR'
        assert params['retmax'] == 2
        assert params['email'] == 'test@example.com'
        assert params['api_key'] == 'test_key'
        
        # Check result
        assert result == mock_response.json.return_value
    
    @patch('httpx.Client.request')
    def test_search_genbank(self, mock_request):
        """Test GenBank search functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "esearchresult": {
                "idlist": ["NM_001234", "NM_005678"],
                "count": "2"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.connector.search_genbank("BRCA1", max_results=2)
        
        # Verify parameters
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['db'] == 'nuccore'  # nucleotide database
        assert params['term'] == 'BRCA1'
        
        assert result == mock_response.json.return_value
    
    @patch('httpx.Client.request')
    def test_get_article_summaries(self, mock_request):
        """Test getting article summaries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "12345": {
                    "title": "Test Article",
                    "authors": [{"name": "Smith J"}]
                }
            }
        }
        mock_request.return_value = mock_response
        
        result = self.connector.get_article_summaries(["12345"])
        
        # Verify parameters
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['db'] == 'pubmed'
        assert params['id'] == '12345'
        
        assert result == mock_response.json.return_value
    
    @patch('httpx.Client.request')
    def test_get_full_articles(self, mock_request):
        """Test getting full article text."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Article abstract text..."
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = self.connector.get_full_articles(["12345"], format="abstract")
        
        # Verify parameters
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['db'] == 'pubmed'
        assert params['rettype'] == 'abstract'
        assert params['retmode'] == 'text'
        
        assert result == "Article abstract text..."


class TestArXivConnector:
    """Test suite for arXiv connector."""
    
    def setup_method(self):
        """Set up test environment."""
        self.connector = ArXivConnector()
        
        # Sample arXiv XML response for testing
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <title>Test Paper on Machine Learning</title>
    <summary>This is a test paper abstract about machine learning techniques.</summary>
    <author>
      <name>John Smith</name>
    </author>
    <author>
      <name>Jane Doe</name>
    </author>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
    <published>2023-01-01T09:00:00Z</published>
    <updated>2023-01-02T10:00:00Z</updated>
    <link href="http://arxiv.org/abs/2301.00001v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/2301.00001v1.pdf" rel="related" type="application/pdf"/>
    <arxiv:comment>10 pages, 3 figures</arxiv:comment>
    <arxiv:journal_ref>Test Journal 2023</arxiv:journal_ref>
    <arxiv:doi>10.1000/test.doi</arxiv:doi>
  </entry>
</feed>'''
    
    def test_initialization(self):
        """Test arXiv connector initialization."""
        assert self.connector.base_url == "http://export.arxiv.org/api"
        assert "query" in self.connector.endpoints
        assert self.connector.auth_config is None  # No auth needed
    
    @patch('httpx.Client.request')
    def test_search_papers(self, mock_request):
        """Test paper search functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.sample_xml
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        results = self.connector.search_papers("machine learning", max_results=1)
        
        # Verify the request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['search_query'] == 'machine learning'
        assert params['max_results'] == 1
        
        # Verify parsed results
        assert len(results) == 1
        paper = results[0]
        assert paper['title'] == 'Test Paper on Machine Learning'
        assert paper['arxiv_id'] == '2301.00001v1'
        assert len(paper['authors']) == 2
        assert 'John Smith' in paper['authors']
        assert 'Jane Doe' in paper['authors']
        assert 'cs.AI' in paper['categories']
        assert 'cs.LG' in paper['categories']
        assert paper['comment'] == '10 pages, 3 figures'
        assert paper['journal_reference'] == 'Test Journal 2023'
        assert paper['doi'] == '10.1000/test.doi'
    
    @patch('httpx.Client.request')
    def test_get_paper_by_id(self, mock_request):
        """Test getting specific paper by ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.sample_xml
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = self.connector.get_paper_by_id("2301.00001")
        
        # Verify the request
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['id_list'] == '2301.00001'
        assert params['max_results'] == 1
        
        # Verify result
        assert result is not None
        assert result['arxiv_id'] == '2301.00001v1'
    
    @patch('httpx.Client.request') 
    def test_search_by_author(self, mock_request):
        """Test searching by author name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.sample_xml
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        results = self.connector.search_by_author("John Smith")
        
        # Verify the search query format
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['search_query'] == 'au:"John Smith"'
        assert params['sortBy'] == 'submittedDate'
        
        assert len(results) == 1
    
    def test_parse_date(self):
        """Test date parsing functionality."""
        # Test valid ISO date
        date_str = "2023-01-01T09:00:00Z"
        result = self.connector._parse_date(date_str)
        assert result == "2023-01-01T09:00:00+00:00"
        
        # Test invalid date
        invalid_date = "invalid-date"
        result = self.connector._parse_date(invalid_date)
        assert result == invalid_date  # Should return original
        
        # Test None
        result = self.connector._parse_date(None)
        assert result is None
    
    def test_xml_parsing_edge_cases(self):
        """Test XML parsing with missing elements."""
        minimal_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/test</id>
    <title>Minimal Paper</title>
  </entry>
</feed>'''
        
        results = self.connector._parse_arxiv_response(minimal_xml)
        
        assert len(results) == 1
        paper = results[0]
        assert paper['title'] == 'Minimal Paper'
        assert paper['authors'] == []  # No authors in minimal XML
        assert paper['categories'] == []  # No categories
        
    def test_invalid_xml_handling(self):
        """Test handling of invalid XML."""
        invalid_xml = "<invalid><xml"
        
        with pytest.raises(ValueError, match="Failed to parse arXiv XML"):
            self.connector._parse_arxiv_response(invalid_xml)