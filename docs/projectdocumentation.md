# Multi-Agent Content Generation System

## Problem Statement

The challenge requires designing and implementing a modular agentic automation system that transforms a minimal product dataset into structured, machine-readable content pages. The system must autonomously generate marketing-ready pages (FAQ, product description, and comparison) without manual intervention, demonstrating production-grade agent orchestration, template-driven content generation, and reusable logic blocks.

**Key Constraints:**
- System must operate solely on provided product data (no external research)
- Content generation must be fully automated via multi-agent workflow
- Output must be clean, machine-readable JSON
- Architecture must demonstrate clear agent boundaries, orchestration patterns, and extensibility

## Solution Overview

This system implements a two-agent architecture that transforms raw product data into three distinct content pages through a sequential pipeline:

1. **AnalystAgent**: Ingests raw product data, normalizes it into structured models, generates 15 categorized user questions, and creates a fictional competitor product for comparison purposes.

2. **PublisherAgent**: Consumes the enriched agent state and assembles pages using template-driven generation, combining deterministic logic blocks with LLM-generated content.

The system employs a template engine that supports three content sources:
- **Logic Blocks**: Deterministic functions that transform data (e.g., benefits list formatting, price comparison)
- **Question Subsets**: Filtered and answered user questions by category
- **Instruction-Based**: LLM-generated content from structured prompts

All pages are output as validated JSON structures, ensuring machine-readability and type safety through Pydantic models.

## Scopes & Assumptions

### In Scope
- Multi-agent orchestration with clear separation of concerns
- Template-driven page generation for FAQ, Product Description, and Comparison pages
- Reusable content logic blocks for deterministic transformations
- Automated question generation (15 questions across 5 categories)
- Fictional competitor product generation for comparison pages
- JSON output with validated structure
- Error handling and retry logic for external API calls

### Out of Scope
- External data research or fact-checking
- UI/website rendering (output is JSON only)
- User interaction or CLI interfaces
- Caching or persistence of LLM responses
- Testing framework (not required by assignment)
- Real-time API or HTTP endpoints

### Assumptions
- Product data is provided in the specified JSON-like format
- Gemini API key is available via environment variable
- Python 3.14+ environment is available
- System operates on single product dataset per execution
- Competitor products are fictional and generated, not researched
- All content generation uses provided product data only (no external facts)

## System Design

### Architecture Overview

The system follows a **sequential pipeline architecture** with clear state transitions:

```
RAW_DATA → [AnalystAgent] → AgentState → [PublisherAgent] → PageOutput (×3)
```

### Agent Design

#### AnalystAgent
**Responsibility**: Data ingestion, normalization, and enrichment

**Input**: Raw product data dictionary
**Output**: `AgentState` containing:
- Normalized `ProductData` model
- 15 categorized `UserQuestion` objects
- Fictional `CompetitorProduct` model

**Key Operations**:
1. Price normalization (extracts numeric value from formatted strings)
2. Data structure transformation (raw dict → Pydantic model)
3. Question generation via LLM (15 questions across 5 categories)
4. Competitor product fabrication via LLM

**Agent Boundaries**:
- No knowledge of page templates or output formats
- Focuses solely on data enrichment
- Returns state object, no side effects

#### PublisherAgent
**Responsibility**: Template-driven page assembly

**Input**: `AgentState`, template key (string)
**Output**: `PageOutput` model with sections and metadata

**Key Operations**:
1. Template resolution from `TEMPLATES` dictionary
2. Section-by-section assembly:
   - Logic block execution (deterministic)
   - Question filtering and answering (LLM-assisted)
   - Instruction-based content generation (LLM)
3. Metadata generation (title, description)

**Agent Boundaries**:
- No knowledge of raw input data format
- Operates exclusively on `AgentState`
- Template-agnostic (can generate any template type)

### Orchestration Flow

The system implements a **sequential state machine** pattern:

1. **Initialization**: `main.py` ensures output directory exists
2. **Analysis Phase**: `AnalystAgent.run(raw_data)` executes:
   - Data parsing and normalization
   - Question generation (LLM call)
   - Competitor generation (LLM call)
   - Returns `AgentState`
3. **State Persistence**: `AgentState` saved to `internal_state.json` for debugging/reuse
4. **Publishing Phase**: `PublisherAgent.build_page(state, template_key)` executes for each template:
   - Template structure iteration
   - Section content generation (mixed: logic + LLM)
   - Page assembly
   - Returns `PageOutput`
5. **Output Persistence**: Each page saved as JSON file

**State Transitions**:
- `RAW_DATA` (dict) → `ProductData` (Pydantic model)
- `ProductData` + LLM → `UserQuestion[]` + `CompetitorProduct`
- `AgentState` → `PageOutput` (via template processing)

### Template Engine Design

The template system is **declarative and extensible**:

**Template Structure**:
```python
{
  "page_type": "Page Name",
  "structure": [
    {
      "section": "Section Heading",
      "source": "logic_block" | "subset_questions" | (default: instruction),
      "function": "method_name",  # if source == "logic_block"
      "filter": "category",       # if source == "subset_questions"
      "instruction": "prompt"     # if default
    }
  ]
}
```

**Content Generation Strategies**:

1. **Logic Blocks** (`source: "logic_block"`):
   - Deterministic functions in `ContentLogicBlocks` class
   - Transform data structures into formatted content
   - Examples: `extract_benefits_list()`, `compare_prices()`
   - No LLM calls, pure data transformation

2. **Question Subsets** (`source: "subset_questions"`):
   - Filters `AgentState.generated_questions` by category
   - Answers each question via LLM call
   - Returns list of Q&A pairs

3. **Instruction-Based** (default):
   - LLM generates content from structured prompt
   - Context includes `AgentState` serialization
   - Custom instruction per section

**Extensibility**:
- New pages: Add template to `TEMPLATES` dict
- New logic blocks: Add methods to `ContentLogicBlocks`
- New question categories: Extend `UserQuestion.category` Literal type

### Data Models

**Input Model**: `ProductData`
- Validates and normalizes raw input
- Type-safe fields with Pydantic validation
- Handles optional fields gracefully

**Intermediate Model**: `AgentState`
- Encapsulates all enriched data
- Passed between agents
- Persisted for debugging

**Output Model**: `PageOutput`
- Structured page representation
- Sections array with flexible content types
- Metadata (title, description) for SEO

### Error Handling & Resilience

**LLM Call Retry Logic**:
- Exponential backoff on quota errors (429)
- Base delay: 20s with jitter
- Maximum 5 retries
- Graceful degradation on failure

**Data Validation**:
- Pydantic models validate all data structures
- JSON parsing errors handled with fallbacks
- Missing data handled via Optional fields

**Price Comparison**:
- Handles missing/invalid prices
- Fallback message on comparison errors

### BaseAgent Abstraction

Both agents inherit from `BaseAgent`, which provides:
- Shared LLM client configuration
- Retry logic wrapper
- JSON vs. text response handling
- Consistent error handling

This abstraction ensures:
- DRY principle (no code duplication)
- Consistent API interaction patterns
- Easy extension for new agent types

## System Flow Diagram
![System Flow Diagram](/diagrams/system-flow.png)

## Template Processing Flow
![Template Processing Flow Diagram](/diagrams/template-processing-flow.png)

## Key Design Decisions

1. **Two-Agent Architecture**: Separates data enrichment from content generation, enabling independent testing and extension.

2. **State Object Pattern**: `AgentState` serves as contract between agents, ensuring loose coupling.

3. **Template-Driven Generation**: Declarative templates enable new page types without code changes.

4. **Mixed Content Strategies**: Combines deterministic logic (fast, reliable) with LLM generation (flexible, contextual).

5. **Pydantic Models**: Type safety and validation at every stage, catching errors early.

6. **BaseAgent Abstraction**: Shared retry logic and LLM configuration reduces duplication.

7. **JSON-First Output**: Machine-readable format enables downstream processing, API integration, or rendering.

## Extensibility Points

- **New Agents**: Inherit from `BaseAgent`, implement specific responsibility
- **New Templates**: Add to `TEMPLATES` dict with structure definition
- **New Logic Blocks**: Add methods to `ContentLogicBlocks` class
- **New Question Categories**: Extend `UserQuestion.category` Literal
- **New Output Formats**: Extend `PageOutput` model or add transformation layer
