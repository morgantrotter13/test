# AI SaaS Platform

A full-stack AI SaaS platform with a FastAPI backend and React frontend for content creation workflows.

## Features

### Backend
- **Modular Prompt Engine**: Load prompts from text files with Jinja2 templating support
- **Prompt Registry**: Centralized registry for managing prompts with metadata, categories, and tags
- **Workflow System**: Define and execute workflows that chain prompts together
- **Workflow Runner**: Execute workflows with automatic variable passing between steps
- **Optional LLM Execution**: If `OPENAI_API_KEY` is set, rendered prompts are sent to OpenAI and responses are returned
- **Content Creation Workflow**: Pre-built workflow for brand analysis → strategy → post generation
- **RESTful API**: Clean API endpoints for prompt and workflow management
- **Hot Reload**: Reload prompts and workflows without restarting the server

### Frontend
- **Modern React UI**: Beautiful, responsive interface built with React and Vite
- **Content Creation Form**: Intuitive form for inputting brand information
- **Workflow Visualization**: Step-by-step display of workflow results
- **Copy-to-Clipboard**: Easy copying of generated content
- **Real-time Updates**: Live feedback during content generation

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── prompt_engine/       # Prompt engine module
│   │   ├── __init__.py
│   │   ├── engine.py        # Prompt loading and rendering
│   │   ├── registry.py     # Prompt registry with metadata
│   │   ├── workflow.py     # Workflow definition system
│   │   ├── runner.py       # Workflow execution runner
│   │   └── factory.py       # Factory for initializing components
│   ├── workflow/            # Workflow engine module (legacy)
│   │   ├── __init__.py
│   │   └── engine.py        # Workflow orchestration
│   └── routes/              # API routes
│       ├── __init__.py
│       ├── prompts.py       # Prompt endpoints
│       └── workflows.py     # Workflow endpoints
├── prompts/                 # Prompt text files (created automatically)
├── workflows/               # Workflow JSON files (created automatically)
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx          # Main app component
│   │   └── App.css          # Styles
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd test
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Backend Server

Start the FastAPI server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Development Server

In a separate terminal, start the React frontend:

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

**Note**: Make sure the backend is running before starting the frontend, as the frontend needs to communicate with the API.

- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Usage

### Prompts

Prompts are stored as text files in the `prompts/` directory. They support Jinja2 templating for variable injection.

#### Example Prompt (`prompts/greeting.txt`):
```
Hello {{ name }}! Welcome to our AI SaaS platform.

Your account type is: {{ account_type }}
```

#### API Endpoints:

- `GET /api/v1/prompts/` - List all prompts
- `GET /api/v1/prompts/{prompt_name}` - Get a specific prompt
- `POST /api/v1/prompts/{prompt_name}/render` - Render a prompt with variables
- `POST /api/v1/prompts/` - Create a new prompt
- `POST /api/v1/prompts/reload` - Reload all prompts from filesystem

#### Example: Render a Prompt

```bash
curl -X POST "http://localhost:8000/api/v1/prompts/greeting/render" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "name": "John",
      "account_type": "Premium"
    }
  }'
```

### Workflows

Workflows are stored as JSON files in the `workflows/` directory. They define sequences of prompts and how to merge their results.

#### Example Workflow (`workflows/customer_onboarding.json`):
```json
{
  "name": "customer_onboarding",
  "description": "Onboard a new customer with welcome message and setup instructions",
  "steps": [
    {
      "id": "welcome",
      "type": "prompt",
      "prompt": "greeting",
      "variables": {
        "account_type": "{{ account_type }}"
      }
    },
    {
      "id": "setup",
      "type": "prompt",
      "prompt": "setup_instructions",
      "variables": {
        "user_name": "{{ name }}"
      }
    },
    {
      "id": "merge",
      "type": "merge",
      "strategy": "concat",
      "sources": ["welcome", "setup"]
    }
  ]
}
```

#### API Endpoints:

- `GET /api/v1/workflows/` - List all workflows
- `GET /api/v1/workflows/{workflow_name}` - Get a specific workflow
- `POST /api/v1/workflows/{workflow_name}/execute` - Execute a workflow
- `POST /api/v1/workflows/` - Create a new workflow
- `POST /api/v1/workflows/reload` - Reload all workflows from filesystem

#### Example: Execute a Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/customer_onboarding/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "name": "John",
      "account_type": "Premium"
    }
  }'
```

### Content Creation Workflow

The system includes a pre-built content creation workflow that chains three prompts:
1. **Brand Analysis** - Analyzes brand voice, messaging, and positioning
2. **Strategy** - Creates content strategy based on brand analysis
3. **Post Generation** - Generates social media posts based on brand and strategy

#### API Endpoints:

- `GET /api/v1/workflows/content-creation` - Get the content creation workflow definition
- `POST /api/v1/workflows/content-creation/execute` - Execute the content creation workflow

#### Example: Execute Content Creation Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/workflows/content-creation/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "TechStart Inc",
    "industry": "SaaS",
    "target_audience": "Small business owners and entrepreneurs",
    "brand_values": "Innovation, Simplicity, Customer-first",
    "brand_info": "We provide cloud-based solutions for small businesses",
    "content_goals": "Increase brand awareness and drive sign-ups",
    "platform": "LinkedIn",
    "post_frequency": "3 times per week",
    "content_themes": "Product updates, customer success, industry insights",
    "post_topic": "Announcing our new feature release",
    "tone": "professional",
    "post_type": "announcement",
    "include_cta": true
  }'
```

The workflow automatically passes outputs between steps:
- Brand analysis output → Strategy step
- Brand analysis + Strategy outputs → Post generation step

### Prompt Registry

The prompt registry provides metadata management for prompts:

- `GET /api/v1/prompts/registry` - List registered prompts with metadata
- `GET /api/v1/prompts/registry?category=analysis` - Filter by category
- `GET /api/v1/prompts/registry?tag=brand` - Filter by tag

Registered prompts include:
- **brand_analysis** - Brand analysis prompt (category: analysis)
- **strategy** - Content strategy prompt (category: strategy)
- **post_generation** - Post generation prompt (category: generation)

## Configuration

Configuration is managed through `app/config.py`. You can override settings using environment variables or a `.env` file:

- `PROMPTS_DIR`: Directory for prompt files (default: "prompts")
- `WORKFLOWS_DIR`: Directory for workflow files (default: "workflows")
- `CORS_ORIGINS`: CORS allowed origins (default: ["*"])
- `OPENAI_API_KEY`: Set to enable LLM calls (if unset, templates are returned without LLM)
- `OPENAI_MODEL`: Model name (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE`: Temperature for generation (default: 0.7)
- `OPENAI_MAX_TOKENS`: Max tokens for generation (default: 800)

## Development

The server runs with auto-reload enabled by default. When you modify prompt or workflow files, you can use the reload endpoints to refresh them without restarting the server.

## License

MIT
