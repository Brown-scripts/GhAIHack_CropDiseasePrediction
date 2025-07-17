"""
Test suite for the Crop Disease Treatment Recommendation API
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from config.settings import settings
from services.treatment_service import treatment_service
from services.cache import cache_manager


class TestAPI:
    """Test cases for main API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "supported_crops" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestDiseaseEndpoints:
    """Test cases for disease endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_get_supported_diseases(self):
        """Test getting supported diseases"""
        response = self.client.get("/api/v1/diseases")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "cashew" in data
        assert "cassava" in data
        assert "maize" in data
        assert "tomato" in data
    
    def test_get_diseases_by_crop(self):
        """Test getting diseases for specific crop"""
        response = self.client.get("/api/v1/diseases/cashew")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "anthracnose" in data
        assert "gumosis" in data
    
    def test_get_disease_symptoms(self):
        """Test getting disease symptoms"""
        response = self.client.get("/api/v1/symptoms/anthracnose")
        assert response.status_code == 200
        data = response.json()
        assert "disease_name" in data
        assert "symptoms" in data
        assert "causes" in data
        assert isinstance(data["symptoms"], list)
    
    def test_get_disease_symptoms_not_found(self):
        """Test getting symptoms for non-existent disease"""
        response = self.client.get("/api/v1/symptoms/nonexistent_disease")
        assert response.status_code == 404
    
    def test_search_diseases(self):
        """Test disease search functionality"""
        response = self.client.get("/api/v1/search?query=spots&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


class TestRecommendationEndpoints:
    """Test cases for recommendation endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @patch('services.location_service.get_coordinates')
    @patch('routes.suppliers.find_nearby_shops')
    def test_comprehensive_recommendation(self, mock_shops, mock_coords):
        """Test comprehensive recommendation endpoint"""
        # Mock location service
        mock_coords.return_value = (5.6037, -0.1870)  # Accra coordinates
        mock_shops.return_value = []
        
        # Test data
        request_data = {
            "disease": "anthracnose",
            "user_location": "Accra, Ghana",
            "severity": "moderate",
            "organic_preference": False
        }
        
        response = self.client.post("/api/v1/recommend/anthracnose", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "disease" in data
        assert "crop_type" in data
        assert "disease_info" in data
        assert "recommended_treatments" in data
        assert isinstance(data["recommended_treatments"], list)
    
    def test_quick_recommendation(self):
        """Test quick recommendation endpoint"""
        response = self.client.get("/api/v1/recommend/quick/anthracnose?severity=moderate")
        assert response.status_code == 200
        data = response.json()
        
        assert "disease" in data
        assert "top_treatments" in data
        assert "key_symptoms" in data
        assert isinstance(data["top_treatments"], list)


class TestSupplierEndpoints:
    """Test cases for supplier endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @patch('services.location_service.get_coordinates')
    @patch('services.overpass_service.find_nearby_shops')
    def test_get_nearby_suppliers(self, mock_shops, mock_coords):
        """Test getting nearby suppliers"""
        # Mock responses
        mock_coords.return_value = (5.6037, -0.1870)
        mock_shops.return_value = [
            {
                "name": "Test Agricultural Store",
                "latitude": 5.6037,
                "longitude": -0.1870,
                "type": "agrarian"
            }
        ]
        
        response = self.client.get("/api/v1/suppliers/nearby?location=Accra, Ghana&radius_km=10")
        assert response.status_code == 200
        data = response.json()
        
        assert "location" in data
        assert "suppliers" in data
        assert "total_count" in data
        assert isinstance(data["suppliers"], list)
    
    def test_get_available_products(self):
        """Test getting available product types"""
        response = self.client.get("/api/v1/suppliers/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "fertilizers" in data
        assert "pesticides" in data


class TestPriceEndpoints:
    """Test cases for price endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_get_treatment_prices(self):
        """Test getting treatment prices"""
        response = self.client.get("/api/v1/prices/mancozeb?location=Accra&max_results=5")
        assert response.status_code == 200
        data = response.json()
        
        assert "treatment_name" in data
        assert "prices" in data
        assert isinstance(data["prices"], list)
        if data["prices"]:
            price = data["prices"][0]
            assert "product_name" in price
            assert "price_ghs" in price
            assert "supplier" in price
    
    def test_compare_treatment_prices(self):
        """Test comparing multiple treatment prices"""
        response = self.client.post("/api/v1/prices/compare?treatments=mancozeb&treatments=copper&max_results_per_treatment=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # Two treatments


class TestTreatmentService:
    """Test cases for treatment service"""
    
    def test_get_disease_info(self):
        """Test getting disease information"""
        disease_info = treatment_service.get_disease_info("anthracnose")
        assert disease_info is not None
        assert disease_info.name == "anthracnose"
        assert disease_info.crop_type.value == "cashew"
        assert len(disease_info.symptoms) > 0
        assert len(disease_info.treatments) > 0
    
    def test_get_disease_info_not_found(self):
        """Test getting non-existent disease"""
        disease_info = treatment_service.get_disease_info("nonexistent_disease")
        assert disease_info is None
    
    def test_recommend_treatments(self):
        """Test treatment recommendations"""
        treatments = treatment_service.recommend_treatments(
            disease_name="anthracnose",
            severity="moderate",
            organic_preference=False
        )
        assert isinstance(treatments, list)
        assert len(treatments) > 0
        
        # Check treatment structure
        treatment = treatments[0]
        assert hasattr(treatment, 'name')
        assert hasattr(treatment, 'type')
        assert hasattr(treatment, 'effectiveness')
    
    def test_organic_treatments_filter(self):
        """Test organic treatment filtering"""
        organic_treatments = treatment_service.get_organic_treatments("anthracnose")
        assert isinstance(organic_treatments, list)
        
        for treatment in organic_treatments:
            assert treatment.type.value == "organic"
    
    def test_get_supported_diseases(self):
        """Test getting supported diseases"""
        diseases = treatment_service.get_supported_diseases()
        assert isinstance(diseases, dict)
        assert "cashew" in diseases
        assert "anthracnose" in diseases["cashew"]


class TestCacheManager:
    """Test cases for cache manager"""
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test basic cache operations"""
        # Test set and get
        key = "test_key"
        value = {"test": "data"}
        
        success = await cache_manager.set(key, value, ttl=60)
        assert success
        
        retrieved = await cache_manager.get(key)
        assert retrieved == value
        
        # Test delete
        success = await cache_manager.delete(key)
        assert success
        
        retrieved = await cache_manager.get(key)
        assert retrieved is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        stats = cache_manager.get_stats()
        assert isinstance(stats, dict)
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate_percent" in stats


# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
