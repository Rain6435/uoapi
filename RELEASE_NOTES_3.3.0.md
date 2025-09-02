# Schedulo API v3.3.0 Release Notes

## 🚀 Enhanced Single Course API with Structured Sections

This minor release significantly improves the single course API endpoint with better data structure, accuracy, and performance.

### ✨ Major Features

#### 1. **New Single Course Discovery Method**
- Direct course queries that bypass bulk discovery
- Significant performance improvement for single course requests
- More reliable course finding for specific course codes

#### 2. **Restructured Single Course Response**
- **Before**: Flat list of sections with naming issues
- **After**: Properly grouped sections with components
```json
{
  "sections": [
    {
      "section": "A",
      "components": [
        {"name": "A", "schedule_type": "Lecture", ...},
        {"name": "A1", "schedule_type": "Tutorial", ...},
        {"name": "A2", "schedule_type": "Tutorial", ...}
      ]
    },
    {
      "section": "B", 
      "components": [...]
    }
  ]
}
```

#### 3. **Component Names**
- Added proper component names (A, A1, A2, B, B1, B2, etc.)
- Better representation of university course structure
- Clearer for client applications to handle registration requirements

### 🐛 Bug Fixes

#### 1. **Section Naming Issues**
- Fixed cases where course status ("Open", "Full") was misread as section name
- Proper extraction of section identifiers from Banner data

#### 2. **Credits Parsing**
- Fixed issue where CRN numbers were mistakenly used as credits
- Added validation to detect and correct such parsing errors
- Sensible defaults for different component types

#### 3. **Data Accuracy**
- Improved parsing logic for Carleton Banner system
- Better handling of malformed data

### 🔧 API Improvements

#### 1. **Enhanced Performance**
- Single course endpoint now uses direct queries
- No longer limited by bulk discovery constraints
- Faster response times for specific course lookups

#### 2. **Professor Rating Integration**
- Added optional Rate My Professor ratings for single course endpoints
- Integrated with existing rating system

#### 3. **Better Error Handling**
- More robust parsing with graceful fallbacks
- Improved error messages and validation

### 📚 Documentation Updates

#### 1. **Comprehensive API Documentation**
- Updated README.md with new endpoint structure
- Added examples for all major API endpoints
- Included response format documentation

#### 2. **Interactive Examples**
- Real JSON response examples
- Clear usage patterns for different scenarios
- Better organization of API features

### 🔄 Backward Compatibility

- All existing endpoints remain functional
- No breaking changes to current API contracts
- Gradual migration path for improved features

### 🏗️ Technical Improvements

#### 1. **Architecture**
- Added `discover_single_course()` method to base provider
- Carleton-specific optimized implementation
- Extensible pattern for other universities

#### 2. **Response Models**
- New Pydantic models for structured responses
- Better type safety and validation
- Cleaner separation of concerns

#### 3. **Code Organization**
- Enhanced base provider functionality
- Better abstraction of university-specific logic
- Improved maintainability

### 📋 API Changes Summary

#### New Endpoints Structure
- `/universities/{university}/courses/{course_code}/live` - Enhanced structured response
- Maintains all existing functionality with improved data format

#### Enhanced Features
- Component names in course sections
- Grouped section organization  
- Optional professor ratings
- Fixed data parsing issues
- Direct single course queries

### 🎯 Next Steps

To use the PyPI package, run:
```bash
pip install --upgrade schedulo-api
```

For development installation:
```bash
git clone https://github.com/Rain6435/uoapi.git
cd uoapi
git checkout v3.3.0
pip install -e .
```

### 🚀 Server Usage

Start the enhanced API server:
```bash
schedulo server --port 8000
```

Visit the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

This release represents a significant step forward in providing clean, structured, and accurate university course data through the Schedulo API.