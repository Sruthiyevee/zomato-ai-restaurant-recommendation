# Zomato AI Restaurant Recommendation Service - Architecture Design Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [STEP 1 – Input the Zomato Data](#step-1--input-the-zomato-data)
4. [STEP 2 – User Input](#step-2--user-input)
5. [STEP 3 – Integration Layer](#step-3--integration-layer)
6. [STEP 4 – Recommendation Engine](#step-4--recommendation-engine)
7. [STEP 5 – Display to the User](#step-5--display-to-the-user)
8. [STEP 6 – Web Interface & API Layer](#step-6--web-interface--api-layer)
9. [System Architecture Diagram](#system-architecture-diagram)
10. [Technology Stack](#technology-stack)
11. [Future Extensibility](#future-extensibility)

---

## Executive Summary

This document outlines the architecture design for a Zomato AI Restaurant Recommendation Service that leverages the ManikaSaini/zomato-restaurant-recommendation dataset from Hugging Face and integrates Groq LLM for intelligent restaurant recommendations. The system is designed with a CLI-first approach while maintaining extensibility for future Web UI integration.

The architecture follows a five-phase development approach, ensuring clear separation of concerns between data ingestion, user interaction, business logic, AI-powered recommendations, and result presentation.

---

## System Overview

### Core Objectives

The system aims to provide personalized restaurant recommendations by:
- Processing the Zomato restaurant dataset from Hugging Face
- Accepting user inputs: city and price range
- Applying intelligent filtering and business logic
- Leveraging Groq LLM for context-aware recommendation ranking
- Delivering formatted, ranked results through a CLI interface

### High-Level Architecture

The system is structured into five distinct layers:

1. **Data Layer**: Dataset ingestion, cleaning, preprocessing, and storage
2. **Input Layer**: User input collection and validation via CLI
3. **Integration Layer**: Business logic, filtering pipeline, and data orchestration
4. **AI Layer**: Groq LLM integration for recommendation generation
5. **Output Layer**: Result formatting and display

### Design Principles

- **Separation of Concerns**: Each phase handles distinct responsibilities
- **Extensibility**: Architecture supports future Web UI without core changes
- **Modularity**: Components are loosely coupled and independently testable
- **Performance**: Optimized for fast query response times
- **Reliability**: Graceful degradation when external services are unavailable

---

## STEP 1 – Input the Zomato Data

### Dataset Ingestion

**Data Source**
- **Provider**: Hugging Face Datasets
- **Dataset**: ManikaSaini/zomato-restaurant-recommendation
- **Access Method**: Hugging Face Datasets API/library
- **Initialization**: One-time bulk load during system setup

**Ingestion Strategy**

The ingestion process follows these steps:

1. **Connection Establishment**
   - Initialize connection to Hugging Face Datasets repository
   - Authenticate using Hugging Face credentials (if required)
   - Verify dataset availability and version

2. **Data Loading**
   - Load complete dataset into memory for initial processing
   - Handle large dataset sizes through streaming or batch processing
   - Monitor memory usage and implement pagination if necessary

3. **Schema Discovery**
   - Analyze dataset structure to identify all available fields
   - Map dataset columns to internal data model
   - Document field types, constraints, and data quality

4. **Metadata Extraction**
   - Extract dataset version information
   - Capture dataset statistics (total records, date ranges)
   - Store metadata for audit and version tracking

**Expected Dataset Fields**

Based on typical Zomato restaurant datasets, the system expects:
- Restaurant identification (ID, name)
- Location data (city, address, coordinates)
- Cuisine information (type, categories)
- Pricing data (price range, cost indicators)
- Ratings and reviews (average rating, review count, review text)
- Operational details (hours, delivery options)
- Additional attributes (features, specialties)

### Data Cleaning

**Cleaning Objectives**

Ensure data quality and consistency for reliable recommendations:

1. **Missing Value Handling**
   - Identify fields with missing values
   - Apply appropriate strategies:
     - Critical fields (name, city): Flag for exclusion if missing
     - Optional fields (reviews): Use default values or mark as unavailable
     - Numerical fields (ratings): Apply statistical imputation or exclude
   - Document missing value patterns for quality assessment

2. **Duplicate Detection and Removal**
   - Identify duplicate restaurants using:
     - Exact name and location matching
     - Fuzzy matching for name variations
     - Coordinate-based proximity detection
   - Retain highest quality record (most reviews, most recent data)
   - Merge complementary information when appropriate

3. **Data Type Validation**
   - Verify numerical fields (ratings, prices) are within valid ranges
   - Validate categorical fields against predefined lists
   - Ensure date/timestamp fields are properly formatted
   - Correct type mismatches or flag for manual review

4. **Normalization**
   - Standardize restaurant names (remove extra spaces, special characters)
   - Normalize city names (handle variations, abbreviations)
   - Unify cuisine category naming (merge similar categories)
   - Standardize price range representations

5. **Outlier Detection**
   - Identify and handle extreme values in ratings
   - Flag restaurants with suspicious review patterns
   - Remove or flag data points outside reasonable ranges

6. **Text Data Cleaning**
   - Clean review text (remove HTML, special characters)
   - Normalize encoding issues
   - Handle multilingual content appropriately

### Preprocessing

**Preprocessing Activities**

Transform cleaned data into formats optimized for filtering and recommendation:

1. **Feature Engineering**
   - **Price Range Categorization**: Map raw price data to standardized categories (Budget, Mid-Range, Premium, Luxury)
   - **Rating Normalization**: Scale ratings to consistent 0-5 scale
   - **Review Sentiment Indicators**: Extract sentiment signals from review text
   - **Popularity Metrics**: Calculate composite popularity scores based on rating and review count
   - **Cuisine Vectorization**: Create categorical encodings for cuisine types

2. **Geospatial Processing**
   - Validate and normalize coordinate data
   - Create geospatial indices for efficient city-based queries
   - Group restaurants by geographic regions
   - Calculate distance matrices if needed for proximity-based recommendations

3. **Text Processing**
   - Tokenize review text for analysis
   - Extract key phrases and specialties from reviews
   - Generate text embeddings for semantic search (optional, for future enhancements)
   - Aggregate review summaries per restaurant

4. **Indexing Preparation**
   - Create indices on frequently queried fields:
     - City index for geographic filtering
     - Price range index for cost-based filtering
     - Rating index for quality-based sorting
     - Composite indices for multi-criteria queries

5. **Data Enrichment**
   - Calculate derived metrics:
     - Review recency scores
     - Rating distribution statistics
     - Cuisine diversity indicators
   - Generate restaurant feature vectors for similarity calculations

### Storage Strategy

**Storage Architecture**

Design storage solution to support efficient querying and future scalability:

1. **Primary Data Store**

   **Database Selection Considerations**:
   - Support for structured restaurant data
   - Efficient querying on city and price range
   - Scalability for large datasets
   - Support for geospatial queries

   **Schema Design**:
   - **Restaurant Master Table**:
     - Primary key: restaurant_id
     - Core fields: name, city, cuisine, price_range, rating, review_count
     - Location: address, latitude, longitude
     - Metadata: created_date, last_updated
   
   - **Review Aggregation Table**:
     - Foreign key: restaurant_id
     - Aggregated metrics: average_rating, total_reviews, sentiment_score
     - Review summaries and key phrases

   - **Feature Vectors Table**:
     - Foreign key: restaurant_id
     - Computed features: popularity_score, cuisine_encoding, feature_vector

2. **Indexing Strategy**

   **Primary Indexes**:
   - City index: Enable fast geographic filtering
   - Price range index: Support cost-based queries
   - Composite index (city, price_range): Optimize combined queries
   - Rating index: Support quality-based sorting

   **Secondary Indexes**:
   - Cuisine index: For cuisine-based filtering (future enhancement)
   - Restaurant name index: For search functionality (future enhancement)

3. **Caching Layer**

   **Cache Strategy**:
   - **In-Memory Cache** (e.g., Redis):
     - Cache frequently accessed city-restaurant mappings
     - Store pre-filtered candidate sets for common queries
     - Cache LLM responses for identical queries (optional)
   
   **Cache Invalidation**:
   - TTL-based expiration for dynamic data
   - Manual invalidation on dataset updates
   - LRU eviction policy for memory management

4. **Data Partitioning**

   **Partitioning Strategy**:
   - Partition by city: Enables efficient geographic filtering
   - Partition by price range: Supports cost-based queries
   - Horizontal partitioning for scalability

5. **Backup and Recovery**

   - Regular backups of processed dataset
   - Version control for dataset updates
   - Recovery procedures for data corruption

---

## STEP 2 – User Input

### Collect City and Price

**Input Requirements**

The system collects two primary inputs from users:

1. **City Selection**
   - User provides city name as text input
   - System validates against available cities in dataset
   - Supports exact matching and fuzzy matching for typos

2. **Price Range Selection**
   - User selects from predefined categories:
     - Budget (Low-cost options)
     - Mid-Range (Moderate pricing)
     - Premium (Higher-end establishments)
     - Luxury (Top-tier dining)
   - System maps user selection to dataset price ranges

**CLI Interaction Design**

**Interaction Flow**:

1. **Welcome and Introduction**
   - Display system welcome message
   - Brief explanation of available features
   - Instructions for input format

2. **City Input Prompt**
   - Prompt: "Enter city name: "
   - Provide autocomplete suggestions as user types (if supported)
   - Display list of available cities if input is ambiguous
   - Allow case-insensitive input

3. **Price Range Selection**
   - Display available price range options with descriptions
   - Prompt: "Select price range (1-4): "
   - Show clear mapping between numbers and categories
   - Allow re-selection if user makes error

4. **Confirmation Step**
   - Display selected city and price range
   - Prompt for confirmation before processing
   - Allow modification if incorrect

5. **Processing Indicator**
   - Show progress indicator while processing
   - Display estimated wait time if available

**Input Collection Methods**

- **Interactive Mode**: Step-by-step prompts with validation
- **Command-Line Arguments**: Direct input via CLI flags (advanced users)
- **Batch Mode**: Accept input from file (future enhancement)

### Input Validation

**Validation Rules**

1. **City Validation**

   **Validation Steps**:
   - Check if city exists in dataset
   - Handle case variations (case-insensitive matching)
   - Implement fuzzy matching for common typos
   - Suggest closest matches if exact match not found

   **Error Handling**:
   - If city not found: Display error message with suggestions
   - If multiple matches: Present list for user selection
   - If input empty: Prompt for re-entry
   - Maximum retry attempts: 3 before suggesting help

2. **Price Range Validation**

   **Validation Steps**:
   - Verify selection is within valid range (1-4 or category name)
   - Map numeric input to category names
   - Handle both numeric and text inputs

   **Error Handling**:
   - If invalid selection: Display valid options and prompt again
   - If out of range: Show error with valid range
   - Default to Mid-Range if validation fails after retries

3. **Input Sanitization**

   **Sanitization Steps**:
   - Trim whitespace from all inputs
   - Remove special characters that could cause issues
   - Normalize encoding (handle Unicode properly)
   - Escape inputs to prevent injection attacks

4. **Business Logic Validation**

   **Additional Checks**:
   - Verify restaurants exist for selected city and price combination
   - Check minimum data quality (e.g., minimum number of restaurants)
   - Warn if selection results in very few options

### CLI Interaction Design

**User Experience Principles**

1. **Clarity**
   - Clear, concise prompts
   - Helpful error messages
   - Progress indicators for long operations

2. **Forgiveness**
   - Allow input correction without restarting
   - Provide undo/back options
   - Graceful handling of invalid inputs

3. **Feedback**
   - Immediate validation feedback
   - Confirmation of selections
   - Status updates during processing

**CLI Interface Components**

1. **Input Handler**
   - Manages user input collection
   - Handles keyboard input and special keys
   - Supports input history (up/down arrows)

2. **Validator**
   - Performs real-time validation
   - Provides immediate feedback
   - Suggests corrections

3. **Session Manager**
   - Maintains user session state
   - Stores current selections
   - Enables query refinement

4. **Help System**
   - Context-sensitive help
   - Usage examples
   - Available commands documentation

**Error Recovery**

- **Retry Mechanism**: Allow multiple attempts for invalid input
- **Suggestion System**: Provide helpful suggestions for corrections
- **Fallback Options**: Default values when appropriate
- **Clear Error Messages**: Explain what went wrong and how to fix it

---

## STEP 3 – Integration Layer

### Business Logic

**Core Business Rules**

The integration layer implements the following business logic:

1. **Filtering Logic**
   - Apply city filter to extract restaurants in specified location
   - Apply price range filter to match cost categories
   - Combine filters using AND logic (both must match)
   - Handle edge cases (no matches, too many matches)

2. **Quality Thresholds**
   - Apply minimum quality standards:
     - Minimum rating threshold (configurable, default: 3.0)
     - Minimum review count (configurable, default: 10)
   - Filter out restaurants below quality thresholds
   - Log quality filtering decisions for transparency

3. **Candidate Selection**
   - Limit candidate set size for LLM processing (e.g., top 50 restaurants)
   - Rank candidates by composite score before LLM:
     - Rating weight: 40%
     - Review count weight: 30%
     - Recency weight: 20%
     - Popularity weight: 10%
   - Ensure diversity in candidate set (avoid all same cuisine)

4. **Data Enrichment Rules**
   - Aggregate review data per restaurant
   - Calculate sentiment scores
   - Extract key features and specialties
   - Prepare context for LLM processing

**Component Responsibilities**

1. **Filter Manager**
   - **Purpose**: Apply geographic and price-based filters
   - **Input**: User city and price range
   - **Output**: Filtered restaurant candidate list
   - **Operations**:
     - Query database with city filter
     - Apply price range matching
     - Apply quality thresholds
     - Return candidate set

2. **Enrichment Engine**
   - **Purpose**: Enhance restaurant data with aggregated features
   - **Input**: Filtered restaurant list
   - **Output**: Enriched restaurant objects with features
   - **Operations**:
     - Fetch review aggregations
     - Calculate composite scores
     - Extract key phrases from reviews
     - Prepare structured data for LLM

3. **Orchestration Service**
   - **Purpose**: Coordinate component interactions
   - **Input**: User inputs and system state
   - **Output**: Structured data for recommendation engine
   - **Operations**:
     - Invoke filter manager
     - Trigger enrichment engine
     - Manage error handling
     - Coordinate with LLM service

### Filtering Pipeline

**Multi-Stage Filtering Architecture**

The filtering process operates through sequential stages:

**Stage 1: Geographic Filtering**
- **Input**: User-specified city
- **Process**:
  - Query database using city index
  - Extract all restaurants in specified city
  - Filter out inactive or closed restaurants (if status available)
- **Output**: City-filtered restaurant set

**Stage 2: Price Range Filtering**
- **Input**: User-specified price range + city-filtered set
- **Process**:
  - Match restaurants to price category
  - Apply price normalization if needed
  - Handle restaurants with missing price data (exclude or use default)
- **Output**: City + price filtered restaurant set

**Stage 3: Quality Filtering**
- **Input**: City + price filtered set
- **Process**:
  - Apply minimum rating threshold
  - Apply minimum review count threshold
  - Filter restaurants with insufficient data quality
- **Output**: Quality-filtered restaurant set

**Stage 4: Candidate Optimization**
- **Input**: Quality-filtered set
- **Process**:
  - Calculate composite scores for ranking
  - Select top N candidates (e.g., 20-50 restaurants)
  - Ensure diversity (cuisine variety, location spread)
  - Prepare for LLM processing
- **Output**: Optimized candidate set for recommendation engine

**Filtering Pipeline Flow**

```
User Input (City, Price Range)
         ↓
[Geographic Filter]
  → Query by city
  → Extract matching restaurants
         ↓
[Price Range Filter]
  → Match price categories
  → Apply price normalization
         ↓
[Quality Filter]
  → Apply rating threshold
  → Apply review count threshold
         ↓
[Candidate Optimization]
  → Calculate composite scores
  → Select top N candidates
  → Ensure diversity
         ↓
Enriched Candidate Set
  → Ready for LLM processing
```

### Data Flow Between Components

**End-to-End Data Flow**

1. **Input Phase**
   - CLI collects city and price range
   - Validator confirms inputs
   - Session manager stores selections

2. **Filtering Phase**
   - Orchestration service receives validated inputs
   - Filter manager queries database
   - Geographic and price filters applied sequentially
   - Quality filters applied
   - Candidate optimization performed

3. **Enrichment Phase**
   - Enrichment engine receives candidate list
   - Fetches additional data (reviews, features)
   - Calculates aggregated metrics
   - Prepares structured data objects

4. **Preparation Phase**
   - Orchestration service formats data for LLM
   - Creates prompt context
   - Validates data completeness
   - Passes to recommendation engine

5. **Recommendation Phase**
   - Recommendation engine processes enriched data
   - LLM generates rankings
   - Results returned to orchestration service

6. **Output Phase**
   - Output formatter structures results
   - CLI displays formatted recommendations

**Data Transformation Points**

1. **Raw Input → Normalized Parameters**
   - User text input → Standardized city name
   - User selection → Price range category

2. **Database Query → Filtered Set**
   - Full dataset → City-filtered restaurants
   - City set → Price-filtered restaurants

3. **Filtered Set → Enriched Objects**
   - Restaurant IDs → Full restaurant objects with features
   - Basic data → Aggregated metrics and summaries

4. **Enriched Objects → LLM Context**
   - Structured data → Formatted prompt text
   - Restaurant features → Natural language descriptions

5. **LLM Response → Structured Results**
   - Natural language response → Parsed recommendation objects
   - Rankings → Formatted display structure

**Component Interfaces**

**Filter Manager Interface**:
- **Input**: City (string), Price Range (enum)
- **Output**: List of restaurant IDs with basic metadata
- **Error Handling**: Returns empty list if no matches, logs warnings

**Enrichment Engine Interface**:
- **Input**: List of restaurant IDs
- **Output**: List of enriched restaurant objects
- **Error Handling**: Handles missing data gracefully, uses defaults

**Orchestration Service Interface**:
- **Input**: User inputs (city, price range)
- **Output**: Structured data ready for LLM
- **Error Handling**: Comprehensive error handling with fallbacks

---

## STEP 4 – Recommendation Engine

### Integrate Groq LLM

**Groq LLM Integration Architecture**

**Service Configuration**

1. **API Connection**
   - **Provider**: Groq API
   - **Connection Type**: REST API over HTTPS
   - **Authentication**: API key-based authentication
   - **Endpoint**: Groq API endpoint for LLM inference

2. **Client Setup**
   - Initialize Groq API client with credentials
   - Configure connection parameters:
     - Timeout settings (default: 30 seconds)
     - Retry configuration (exponential backoff)
     - Rate limiting handling
   - Implement connection pooling for efficiency

3. **Model Selection**
   - Select appropriate Groq model (e.g., Llama, Mixtral)
   - Consider model capabilities:
     - Context window size
     - Response quality
     - Inference speed
     - Cost efficiency

4. **Error Handling**
   - **Network Failures**: Retry with exponential backoff
   - **API Errors**: Parse error responses, implement fallback
   - **Timeout Handling**: Graceful timeout with user notification
   - **Rate Limiting**: Queue requests, implement backoff
   - **Service Unavailable**: Fallback to deterministic ranking

5. **Performance Optimization**
   - Batch processing for multiple queries (if supported)
   - Caching responses for identical queries
   - Request optimization to minimize token usage
   - Connection reuse for multiple requests

**Integration Points**

- **Input**: Structured restaurant data with user preferences
- **Processing**: LLM inference via Groq API
- **Output**: Ranked recommendations with reasoning
- **Error Recovery**: Fallback to content-based ranking

### Prompt Design Strategy

**Prompt Architecture**

The prompt is structured to provide context and guide LLM reasoning:

**1. System Role Definition**

```
You are an expert restaurant recommendation assistant with deep knowledge 
of dining experiences, cuisines, and local food culture. Your expertise 
includes understanding restaurant quality, value, and matching restaurants 
to user preferences.
```

**2. Context Section**

Provide comprehensive restaurant information:

- **Restaurant List**: For each candidate restaurant, include:
  - Name and cuisine type
  - Average rating and review count
  - Price range category
  - Key specialties or features extracted from reviews
  - Notable characteristics (ambiance, service quality indicators)

- **Data Format**: Structured, consistent format for easy parsing
- **Completeness**: Include all relevant information for informed decisions

**3. User Preference Section**

Explicitly state user requirements:

- **City**: User's selected city
- **Price Range**: User's selected price category
- **Context**: Any additional preferences (if collected in future)

**4. Task Definition**

Clear instructions for the LLM:

- **Objective**: Rank restaurants that best match user preferences
- **Ranking Criteria**:
  - Relevance to price range
  - Quality (ratings and reviews)
  - Value proposition
  - Uniqueness and standout features
- **Output Requirements**:
  - Rank top 5-10 restaurants
  - Provide brief reasoning for each recommendation
  - Ensure variety in recommendations
  - Only recommend from provided list (prevent hallucination)

**5. Output Format Specification**

Define exact response structure:

- **Format**: JSON structure with specific fields
- **Required Fields**:
  - Rank (integer)
  - Restaurant name (string)
  - Cuisine (string)
  - Rating (float)
  - Reasoning (string explaining why recommended)
- **Constraints**: 
  - Only restaurants from provided list
  - Rankings must be unique
  - Reasoning must be specific and relevant

**Prompt Optimization Techniques**

1. **Few-Shot Learning**
   - Include example input-output pairs
   - Demonstrate desired reasoning style
   - Show format expectations

2. **Explicit Constraints**
   - "Only recommend restaurants from the provided list"
   - "Do not invent restaurants or details"
   - "Base recommendations solely on provided data"

3. **Temperature Settings**
   - Use low temperature (0.3-0.5) for consistent, deterministic output
   - Balance between creativity and consistency

4. **Token Management**
   - Optimize prompt length to stay within context limits
   - Prioritize essential information
   - Use concise descriptions

5. **Output Validation**
   - Request JSON format for structured parsing
   - Include schema validation in prompt
   - Request explicit confirmation of list adherence

**Prompt Template Structure**

```
[System Role]
[Context: Restaurant Data]
[User Preferences]
[Task Instructions]
[Output Format]
[Examples (optional)]
```

### Recommendation Logic

**Recommendation Approach**

The system uses a **hybrid recommendation strategy**:

1. **Content-Based Filtering** (Pre-LLM)
   - Filter by city and price range
   - Apply quality thresholds
   - Rank by composite scores
   - Select diverse candidate set

2. **LLM-Powered Ranking** (Primary)
   - LLM analyzes candidate restaurants
   - Considers multiple factors:
     - Exact match to user criteria
     - Quality indicators (ratings, reviews)
     - Value proposition
     - Unique features and specialties
   - Generates intelligent ranking with reasoning

3. **Post-Processing** (If needed)
   - Validate LLM output
   - Ensure diversity in final recommendations
   - Apply business rules if necessary

**LLM Reasoning Process**

The LLM performs the following reasoning steps:

1. **Data Comprehension**
   - Understand restaurant attributes
   - Identify key differentiators
   - Recognize quality indicators

2. **User Alignment**
   - Match restaurants to user's price range
   - Consider city context
   - Identify best-fit options

3. **Differentiation**
   - Identify unique value propositions
   - Highlight standout features
   - Distinguish similar restaurants

4. **Ranking**
   - Order restaurants by fit and appeal
   - Balance multiple factors
   - Ensure logical ranking

5. **Justification**
   - Generate clear reasoning for each rank
   - Explain why restaurant fits user needs
   - Highlight key strengths

**Ranking Criteria**

The LLM considers these factors (in order of importance):

1. **Relevance** (40%)
   - Exact match to price range
   - City alignment
   - User preference fit

2. **Quality** (30%)
   - High ratings
   - Positive review sentiment
   - Review count (credibility)

3. **Value** (20%)
   - Quality-to-price ratio
   - Unique offerings
   - Standout features

4. **Diversity** (10%)
   - Variety in cuisine types
   - Different dining experiences
   - Balanced recommendations

**Fallback Strategy**

If LLM service is unavailable:

1. **Deterministic Ranking**
   - Use pre-calculated composite scores
   - Rank by: (rating × 0.5) + (review_count_normalized × 0.3) + (popularity × 0.2)
   - Apply diversity sampling

2. **Graceful Degradation**
   - Inform user of fallback mode
   - Still provide quality recommendations
   - Maintain system functionality

3. **Error Recovery**
   - Retry LLM call with exponential backoff
   - Log errors for monitoring
   - Alert administrators if persistent failures

### CLI-First Design (WebUI-Ready Architecture)

**Architecture Abstraction**

The recommendation engine is designed with clear separation between core logic and interface:

**Core Recommendation Service**
- **Purpose**: Pure business logic for recommendations
- **Input**: Structured data (city, price range, restaurant candidates)
- **Output**: Structured recommendation objects (JSON-serializable)
- **Interface**: Language-agnostic, can be called from any client

**Interface Adapters**
- **CLI Adapter**: Converts CLI inputs to service format, formats outputs for terminal
- **Web API Adapter** (Future): Converts HTTP requests to service format, returns JSON responses
- **Mobile Adapter** (Future): Converts mobile app inputs, returns mobile-optimized responses

**Abstraction Layers**

```
┌─────────────────────────────────────┐
│   User Interface Layer              │
│   (CLI / Web UI / Mobile)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Interface Adapter Layer            │
│   (Input/Output Formatting)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Recommendation Engine Core         │
│   (Business Logic, LLM Integration)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Data & Integration Layer           │
│   (Filtering, Enrichment)            │
└──────────────────────────────────────┘
```

**CLI Implementation Details**

**CLI-Specific Components**:
- **Input Handler**: Parses command-line arguments and interactive prompts
- **Output Formatter**: Converts structured recommendations to terminal-friendly text
- **Session Manager**: Maintains CLI session state

**CLI Features**:
- Interactive prompts for user input
- Formatted text output with colors/formatting (optional)
- Progress indicators
- Error messages in user-friendly format

**WebUI Readiness**

**Design for Future Extension**:

1. **Structured Output**
   - Recommendation engine returns JSON objects
   - No formatting logic in core engine
   - Adapter layer handles presentation

2. **Stateless Design**
   - No CLI-specific state in core logic
   - Session management in adapter layer
   - Enables horizontal scaling

3. **API-Ready Structure**
   - Core service can be wrapped in REST API
   - Standard request/response format
   - Easy integration with web frameworks

4. **Modular Components**
   - Each component independently testable
   - Clear interfaces between layers
   - Easy to add new interface types

**Future Web UI Integration Path**

1. **Add REST API Layer**
   - Wrap recommendation service in HTTP endpoints
   - Define API routes (POST /recommendations)
   - Handle request/response serialization

2. **Frontend Integration**
   - Web UI calls REST API
   - Receives JSON responses
   - Formats for web display

3. **Shared Core Logic**
   - Same recommendation engine used by CLI and Web UI
   - Consistent recommendation quality
   - Single source of truth for business logic

---

## STEP 5 – Display to the User

### Output Formatting

**Display Strategy**

The output formatting layer transforms structured recommendation data into human-readable format for CLI display.

**Formatting Principles**

1. **Clarity**: Information is easy to scan and understand
2. **Hierarchy**: Most important information is most prominent
3. **Consistency**: Uniform formatting across all recommendations
4. **Completeness**: Include all relevant information without overwhelming
5. **Aesthetics**: Clean, professional appearance

**Output Structure**

**Header Section**:
- System title/header
- Query summary (city, price range)
- Total number of recommendations
- Query timestamp (optional)

**Recommendation Section**:
- Individual restaurant recommendations
- Ranked in order of relevance
- Consistent formatting for each entry

**Footer Section**:
- Additional information (if needed)
- Next steps or options
- Session continuation prompts

**Formatting Details**

**Text Formatting** (if terminal supports):
- **Bold**: Restaurant names, section headers
- **Colors**: Ratings (green for high, yellow for medium), ranks
- **Separators**: Visual dividers between sections
- **Indentation**: Hierarchical information structure

**Layout Design**:

```
═══════════════════════════════════════════════════════════
    ZOMATO AI RESTAURANT RECOMMENDATIONS
═══════════════════════════════════════════════════════════

City: [CITY_NAME]
Price Range: [PRICE_CATEGORY]
Recommendations: [COUNT]

───────────────────────────────────────────────────────────

#1 [RESTAURANT_NAME]
   Cuisine: [CUISINE_TYPE]
   Rating: ★★★★☆ (4.5/5.0) | Reviews: 1,234
   Price: [PRICE_RANGE]
   
   Why Recommended: [LLM_REASONING]
   
   Key Features: [FEATURES]

───────────────────────────────────────────────────────────

#2 [RESTAURANT_NAME]
   [Similar structure...]

───────────────────────────────────────────────────────────

[Additional recommendations...]

═══════════════════════════════════════════════════════════
```

### Ranked Recommendations

**Ranking Presentation**

**Visual Hierarchy**:
- **Rank Number**: Prominently displayed (e.g., #1, #2)
- **Restaurant Name**: Bold or highlighted
- **Key Metrics**: Rating and review count clearly visible
- **Reasoning**: Explanatory text for why restaurant is recommended

**Ranking Information**

Each recommendation displays:

1. **Rank Position**
   - Clear rank number (#1, #2, etc.)
   - Visual indicator of position

2. **Restaurant Identity**
   - Restaurant name (primary identifier)
   - Cuisine type (secondary identifier)

3. **Quality Indicators**
   - **Rating**: Visual star representation (★★★★☆) and numerical (4.5/5.0)
   - **Review Count**: Total number of reviews (credibility indicator)
   - **Rating Trend**: If available (improving/declining)

4. **Price Information**
   - Price range category
   - Visual indicator (e.g., $$ for Mid-Range)

5. **Recommendation Reasoning**
   - LLM-generated explanation
   - Highlights why restaurant fits user needs
   - Mentions key strengths

6. **Key Features**
   - Distinctive attributes
   - Specialties or unique offerings
   - Notable characteristics

**Ranking Logic Display**

- Rankings are ordered by LLM-determined relevance
- Each rank includes justification
- Visual separation between recommendations
- Consistent information structure

### Response Structure

**Structured Response Format**

The system generates responses in a structured format that supports both human-readable display and programmatic processing.

**Response Object Schema**

```
Response Object
├── Request Context
│   ├── City: [string]
│   ├── Price Range: [string]
│   ├── Query Timestamp: [datetime]
│   └── Query ID: [unique identifier]
│
├── Metadata
│   ├── Total Candidates Evaluated: [integer]
│   ├── Recommendations Generated: [integer]
│   ├── Processing Time: [duration in seconds]
│   ├── LLM Model Used: [string]
│   └── Fallback Mode: [boolean] (if LLM unavailable)
│
├── Recommendations Array
│   ├── Recommendation 1
│   │   ├── Rank: [integer]
│   │   ├── Restaurant ID: [string]
│   │   ├── Name: [string]
│   │   ├── Cuisine: [string]
│   │   ├── Rating: [float]
│   │   ├── Review Count: [integer]
│   │   ├── Price Range: [string]
│   │   ├── LLM Reasoning: [string]
│   │   ├── Key Features: [array of strings]
│   │   └── Score: [float] (optional, composite score)
│   │
│   ├── Recommendation 2
│   │   └── [Same structure...]
│   │
│   └── [Additional recommendations...]
│
└── Supplementary Information
    ├── Query Execution Log: [array of log entries]
    ├── Warnings: [array of warning messages]
    └── Session Continuation: [prompt for next action]
```

**Response Variations**

**Standard Response**:
- Full recommendation details
- Complete reasoning
- All available information

**Compact Response**:
- Essential information only
- Abbreviated reasoning
- Suitable for limited terminal space

**Verbose Response**:
- Extended details
- Additional restaurant attributes
- Review excerpts
- Related information

**JSON Export**:
- Machine-readable format
- Complete structured data
- For programmatic use or future integration

**Display Modes**

1. **Interactive Mode**
   - Step-by-step display
   - User can scroll through recommendations
   - Option to view details for specific restaurant

2. **Batch Mode**
   - Complete output at once
   - Suitable for scripting or file output
   - Includes all recommendations

3. **Summary Mode**
   - Top 3-5 recommendations only
   - Quick overview
   - Option to expand for full list

**Post-Display Interaction**

**CLI Continuity Features**:

1. **Additional Queries**
   - Prompt: "Would you like to search again? (y/n)"
   - Allow new city/price selection
   - Maintain session context

2. **Query Refinement**
   - Option to adjust previous search
   - Modify city or price range
   - Re-run with new parameters

3. **Detail View**
   - Option to view detailed information for specific restaurant
   - Expand recommendation details
   - Show additional attributes

4. **Export Options**
   - Save recommendations to file
   - Export as JSON
   - Copy to clipboard (if supported)

5. **Session Management**
   - View query history within session
   - Compare different searches
   - Clear session and start fresh

**Error Display**

If errors occur during processing:

- **Clear Error Messages**: Explain what went wrong
- **Recovery Suggestions**: Provide actionable guidance
- **Partial Results**: Display available recommendations if possible
- **Retry Options**: Allow user to retry failed operations


---

## STEP 6 – Web Interface & API Layer

### System Overview

This phase introduces a modern web-based interface and a RESTful API layer to replace/augment the CLI. This allows for a more interactive and user-friendly experience.

### API Layer (FastAPI)

**Purpose**: Expose the Recommendation Engine logic via HTTP endpoints using FastAPI.

**Endpoint Design**:

1.  **Metadata Endpoints**
    *   `GET /api/v1/cities`: Returns list of available cities from the database.
        *   Used to populate the city selection dropdown on the frontend.
    *   `GET /api/v1/prices`: Returns available price ranges.

2.  **Recommendation Endpoints**
    *   `POST /api/v1/recommendations`: Generates recommendations.
        *   **Input Body**:
            ```json
            {
              "city": "Bangalore",
              "price_range": "Mid-Range"
            }
            ```
        *   **Response**:
            ```json
            {
              "success": true,
              "recommendations": [ ... ], // List of recommendation objects
              "count": 5
            }
            ```

**Integration**:
*   The API layer imports `RecommendationEngine` and `ZomatoDataStorage`.
*   It handles the request/response cycle and error serialization.

### Web Frontend

**Technology**: HTML5, CSS3, Vanilla JavaScript (ES6+).

**Features**:
1.  **City Selection**: A searchable dropdown (datalist or custom select) populated by the `/cities` API.
2.  **Price Selection**: Visual cards or buttons for Budget, Mid-Range, Premium, Luxury.
3.  **Search Action**: Asynchronous fetch request to the API.
4.  **Results Display**:
    *   Responsive grid/list of restaurant cards.
    *   Rich formatting for ratings (Stars).
    *   "Why Recommended" section highlighted.
5.  **Loading States**: Visual feedback (spinners/skeletons) during API calls.

**Directory Structure (`phase_6_web/`)**:
*   `main.py`: FastAPI application entry point.
*   `static/`: CSS, JS, and Images.
*   `templates/`: HTML files (Jinaja2 or static HTML).

---

## System Architecture Diagram

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CLI Interface                            │  │
│  │  (Input Collection, Output Display, Session Mgmt)    │  │
│  └───────────────────────┬──────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  INTEGRATION LAYER                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Orchestration Service                        │  │
│  │  (Component Coordination, Error Handling)            │  │
│  └───┬──────────────────────────────────────────────┬───┘  │
│      │                                              │       │
│  ┌───▼──────────────┐                    ┌─────────▼────┐  │
│  │  Filter Manager  │                    │  Enrichment   │  │
│  │  (Geographic,    │                    │  Engine       │  │
│  │   Price Filter)  │                    │  (Feature     │  │
│  └───┬──────────────┘                    │   Aggregation)│  │
│      │                                   └─────────┬────┘  │
└──────┼─────────────────────────────────────────────┼───────┘
       │                                             │
┌───────▼─────────────────────────────────────────────▼─────┐
│                    DATA LAYER                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Primary Database (Restaurant Master Data)           │  │
│  │  - Restaurant information                            │  │
│  │  - Location data                                     │  │
│  │  - Ratings and reviews                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Feature Store (Aggregated Features)                 │  │
│  │  - Composite scores                                  │  │
│  │  - Review aggregations                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cache Layer (Frequently Accessed Data)              │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              RECOMMENDATION ENGINE LAYER                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Groq LLM Integration                                │  │
│  │  - API Client                                        │  │
│  │  - Prompt Construction                               │  │
│  │  - Response Parsing                                  │  │
│  │  - Error Handling & Fallback                         │  │
│  └───────────────────────┬──────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    OUTPUT LAYER                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Output Formatter                                     │  │
│  │  (Structured Results → Human-Readable Format)        │  │
│  └───────────────────────┬──────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    CLI DISPLAY                               │
│  (Formatted Recommendations to Terminal)                    │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
[User Input: City + Price Range]
           ↓
    [Input Validation]
           ↓
    [Session Storage]
           ↓
[Orchestration Service]
           ↓
    ┌──────┴──────┐
    ↓             ↓
[Filter Manager] [Enrichment Engine]
    ↓             ↓
[Database Query] [Feature Aggregation]
    ↓             ↓
[Filtered Set]   [Enriched Data]
    └──────┬──────┘
           ↓
[LLM Prompt Construction]
           ↓
    [Groq LLM API]
           ↓
[Ranked Recommendations]
           ↓
[Output Formatter]
           ↓
[CLI Display]
```

---

## Technology Stack

### Core Technologies

| Component | Technology Category | Purpose |
|-----------|-------------------|---------|
| **Data Ingestion** | Hugging Face Datasets | Load Zomato dataset from Hugging Face |
| **Data Storage** | SQL Database (SQLite) | Store restaurant master data and features |
| **Caching** | Redis (Optional) | Cache frequently accessed data and query results |
| **AI/LLM** | Groq API | Generate intelligent restaurant recommendations |
| **CLI Framework** | Python (Standard Lib) | Command-line interface implementation |
| **Data Processing** | Python (Pandas/NumPy) | Data cleaning, preprocessing, feature engineering |
| **Web Backend** | FastAPI + Uvicorn | RESTful API for web client |
| **Web Frontend** | HTML5, CSS3, JS (Vanilla) | Interactive user interface |

### Design Patterns

1. **Layered Architecture**: Clear separation between data, business logic, and presentation
2. **Adapter Pattern**: Interface adapters for CLI and future Web UI
3. **Strategy Pattern**: Different ranking strategies (LLM vs. deterministic)
4. **Factory Pattern**: Component creation and initialization
5. **Observer Pattern**: Event handling and logging (if needed)

### Integration Points

- **Hugging Face Datasets API**: Dataset loading and updates
- **Groq API**: LLM inference for recommendations
- **Database**: Data persistence and querying
- **Cache**: Performance optimization

---

## STEP 6 – Web Interface & API Layer

### System Overview

This phase introduces a modern web-based interface and a RESTful API layer to replace/augment the CLI. This allows for a more interactive and user-friendly experience.

### API Layer (FastAPI)

**Purpose**: Expose the Recommendation Engine logic via HTTP endpoints using FastAPI.

**Endpoint Design**:

1.  **Metadata Endpoints**
    *   `GET /api/v1/cities`: Returns list of available cities from the database.
        *   Used to populate the city selection dropdown on the frontend.
    *   `GET /api/v1/prices`: Returns available price ranges.

2.  **Recommendation Endpoints**
    *   `POST /api/v1/recommendations`: Generates recommendations.
        *   **Input Body**:
            ```json
            {
              "city": "Bangalore",
              "price_range": "Mid-Range"
            }
            ```
        *   **Response**:
            ```json
            {
              "success": true,
              "recommendations": [ ... ], // List of recommendation objects
              "count": 5
            }
            ```

**Integration**:
*   The API layer imports `RecommendationEngine` and `ZomatoDataStorage`.
*   It handles the request/response cycle and error serialization.

### Web Frontend

**Technology**: HTML5, CSS3, Vanilla JavaScript (ES6+).

**Features**:
1.  **City Selection**: A searchable dropdown (datalist or custom select) populated by the `/cities` API.
2.  **Price Selection**: Visual cards or buttons for Budget, Mid-Range, Premium, Luxury.
3.  **Search Action**: Asynchronous fetch request to the API.
4.  **Results Display**:
    *   Responsive grid/list of restaurant cards.
    *   Rich formatting for ratings (Stars).
    *   "Why Recommended" section highlighted.
5.  **Loading States**: Visual feedback (spinners/skeletons) during API calls.

**Directory Structure (`phase_6_web/`)**:
*   `main.py`: FastAPI application entry point.
*   `static/`: CSS, JS, and Images.
*   `templates/`: HTML files (Jinaja2 or static HTML).

---

## Future Extensibility

### Web UI Integration

**Architecture Extension**:

1. **REST API Layer**
   - Wrap recommendation service in HTTP endpoints
   - Define standard API routes
   - Handle request/response serialization
   - Implement authentication (if needed)

2. **Frontend Framework**
   - Web UI consumes REST API
   - Real-time updates and interactive features
   - Enhanced user experience with visualizations

3. **Shared Core**
   - Same recommendation engine for CLI and Web UI
   - Consistent business logic
   - Unified data layer

### Advanced Features

**Potential Enhancements**:

1. **User Profiles**
   - Persistent user preferences
   - Historical recommendation tracking
   - Personalized ranking adjustments

2. **Collaborative Filtering**
   - User similarity analysis
   - "Users who liked X also liked Y" recommendations

3. **Real-Time Updates**
   - Live review ingestion
   - Dynamic rating updates
   - Real-time availability status

4. **Multi-Criteria Recommendations**
   - Additional filters (cuisine, rating, distance)
   - Preference weighting
   - Advanced filtering options

5. **Recommendation Explanations**
   - Enhanced reasoning display
   - Visual explanations
   - Comparison features

### Scalability Considerations

**Horizontal Scaling**:
- Stateless service design
- Database replication
- Load balancing for API layer
- Distributed caching

**Performance Optimization**:
- Query optimization
- Advanced indexing strategies
- Response caching
- Batch processing for updates

---

## Conclusion

This architecture design provides a comprehensive foundation for the Zomato AI Restaurant Recommendation Service. The five-phase approach ensures clear separation of concerns, from data ingestion through user display, while maintaining extensibility for future enhancements.

The system leverages Groq LLM for intelligent recommendations while maintaining a robust fallback mechanism. The CLI-first design with WebUI-ready architecture ensures the system can evolve to support multiple interfaces without core changes.

Key strengths of this architecture:
- **Modularity**: Components are independently testable and maintainable
- **Extensibility**: Easy to add new features and interfaces
- **Reliability**: Graceful degradation and error handling
- **Performance**: Optimized for fast query responses
- **Scalability**: Designed to handle growth in data and users

The architecture supports the core requirements while providing a clear path for future expansion and enhancement.
