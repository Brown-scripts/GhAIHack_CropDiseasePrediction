# GhAI Crop Disease Prediction & Treatment Recommendation API

A comprehensive FastAPI-based system for crop disease identification and treatment recommendations specifically designed for Ghanaian agriculture. This project provides intelligent recommendations for treating crop diseases affecting cashew, cassava, maize, and tomato crops.

## 🌾 Project Overview

This API system helps farmers and agricultural professionals in Ghana by:
- Providing detailed information about crop diseases
- Recommending appropriate treatments based on disease severity and user preferences
- Locating nearby agricultural suppliers
- Offering price information for treatments (mock data due to scraping limitations)
- Supporting both chemical and organic treatment options

### Supported Crops & Diseases 

**Cashew**: anthracnose, gumosis, leaf_miner, red_rust, healthy
**Cassava**: bacterial_blight, brown_spot, green_mite, mosaic, healthy  
**Maize**: fall_armyworm, grasshopper, leaf_beetle, leaf_blight, leaf_spot, streak_virus, healthy
**Tomato**: leaf_blight, leaf_curl, septoria_leaf_spot, verticillium_wilt, healthy

## 🏗️ Architecture & Approach

### Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Caching**: In-memory caching for performance optimization
- **Location Services**: OpenStreetMap Nominatim & Overpass API
- **Data Validation**: Pydantic models
- **Testing**: Pytest with async support
- **Deployment**: Deployed on Render

### Key Components

1. **Disease Database** (`data/disease_database.py`)
   - Comprehensive disease information with symptoms, causes, and treatments
   - Scientific names and detailed treatment protocols
   - Cost estimates and effectiveness ratings

2. **Treatment Service** (`services/treatment_service.py`)
   - Intelligent treatment recommendation engine
   - Severity-based filtering
   - Organic vs chemical treatment preferences

3. **Location Services** (`services/location_service.py`, `services/overpass_service.py`)
   - GPS coordinate resolution
   - Nearby agricultural supplier discovery
   - Ghana-specific location handling

4. **Caching System** (`services/cache.py`)
   - In-memory caching for improved performance
   - Configurable TTL for different data types
   - Cache statistics and health monitoring

5. **API Routes**
   - `/api/diseases` - Disease information endpoints
   - `/api/recommend` - Treatment recommendation endpoints
   - `/api/suppliers` - Agricultural supplier location
   - `/api/prices` - Treatment pricing (mock data)

## 🚀 Getting Started

### Prerequisites
- Python 3.11.9 (specified in `.python-version` file)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GhAIHack_CropDiseasePrediction
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration** (Optional)
   Create a `.env` file in the project root:
   ```env
   DEBUG=true
   LOG_LEVEL=INFO
   ```

### Running the Application

**Development Mode:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Usage Examples

### Get Disease Information
```bash
# Get all supported diseases
curl http://localhost:8000/api/diseases

# Get diseases for specific crop
curl http://localhost:8000/api/diseases/cashew

# Get detailed disease symptoms
curl http://localhost:8000/api/symptoms/anthracnose
```

### Get Treatment Recommendations
```bash
# Comprehensive recommendation
curl -X POST http://localhost:8000/api/recommend/anthracnose \
  -H "Content-Type: application/json" \
  -d '{
    "user_location": "Accra, Ghana",
    "severity": "moderate",
    "organic_preference": false
  }'

# Quick recommendation
curl http://localhost:8000/api/recommend/quick/anthracnose?severity=moderate
```

### Find Agricultural Suppliers
```bash
# Find nearby suppliers
curl "http://localhost:8000/api/suppliers/nearby?location=Accra, Ghana&radius_km=10"

# Get available product types
curl http://localhost:8000/api/suppliers/products
```

### Get Treatment Prices
```bash
# Get prices for specific treatment
curl "http://localhost:8000/api/prices/mancozeb?location=Accra&max_results=5"
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_main.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Coverage
The test suite covers:
- API endpoint functionality
- Disease information retrieval
- Treatment recommendation logic
- Supplier location services
- Cache operations
- Error handling

## 🚧 Known Limitations & Challenges

### Web Scraping Issues
**Challenge**: The original plan included real-time price scraping from agricultural supplier websites and marketplaces.

**Issue**: Web scraping was blocked by target websites due to:
- Anti-bot protection mechanisms
- Rate limiting
- CAPTCHA challenges
- IP blocking

**Current Solution**: Mock price data is generated based on realistic market prices for common treatments. The pricing module (`routes/prices.py`) contains the framework for real scraping but uses mock data for demonstration.

**Future Improvements**:
- Partner with agricultural suppliers for API access
- Implement rotating proxy systems
- Use official price databases from Ghana's Ministry of Agriculture
- Integrate with e-commerce platforms via official APIs

### Other Considerations
- **Location Accuracy**: Depends on OpenStreetMap data quality in rural areas
- **Treatment Database**: Currently static; could benefit from dynamic updates
- **Language Support**: Currently English-only; local language support would improve accessibility

## 🔧 Configuration

### Environment Variables
```env
# Application
APP_NAME="Crop Disease Treatment Recommendation API"
APP_VERSION="1.0.0"
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Cache TTL (seconds)
CACHE_TTL_DEFAULT=3600
CACHE_TTL_DISEASE_INFO=86400
CACHE_TTL_SUPPLIERS=1800
CACHE_TTL_PRICES=900

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🚀 Deployment

### Render Deployment
The project is deployed on Render with the following configuration:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Python Version:** Specified in `.python-version` file (3.11.9)

**Deployment Steps:**
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set the build and start commands above
4. Deploy automatically on git push

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Ghana's Ministry of Agriculture for disease classification standards
- OpenStreetMap community for location data
- GhAI Hackathon organizers and participants

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the API documentation at `/docs` endpoint

---

**Note**: This project was developed during the GhAI Hackathon with the goal of supporting Ghanaian farmers through technology-driven agricultural solutions.
