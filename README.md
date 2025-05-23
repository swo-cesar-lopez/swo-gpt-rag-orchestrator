# Enterprise RAG Orchestrator

This Orchestrator is part of the **Enterprise RAG (GPT-RAG)** Solution Accelerator.

To learn more about the Enterprise RAG, please go to [https://aka.ms/gpt-rag](https://aka.ms/gpt-rag).

## How the Orchestrator Works

The **Enterprise RAG Orchestrator** efficiently manages user interactions by coordinating various modules and plugins to generate accurate responses. The core of its functionality revolves around the `get_answer` function in [code_orchestration.py](https://github.com/Azure/gpt-rag-orchestrator/blob/main/orc/code_orchestration.py), which processes user queries through a structured workflow.

### Orchestration Flow

1. **Initialization**:
   - **Conversation Management**: Retrieves or creates a conversation record from Cosmos DB using the `conversation_id`.
   - **Setup**: Initializes necessary variables, loads the bot description, and prepares the Semantic Kernel for processing.

2. **Processing User Input (`get_answer` Function)**:
   - **Input Handling**: Captures the latest user query and appends it to the conversation history.
   - **Guardrails**: Performs initial checks, such as filtering blocked words to ensure content compliance.
   - **RAG Flow**:
     - **Language Detection**: Identifies the language of the user input.
     - **Conversation Summarization**: Summarizes the conversation history to maintain context.
     - **Intent Triage**: Determines the intent behind the user query (e.g., question answering, follow-up).
     - **Data Retrieval**: Utilizes retrieval plugins to fetch relevant information based on the identified intent.
     - **Answer Generation**: Generates a coherent response by integrating retrieved data and conversation context.
   - **Final Guardrails**: Ensures the generated answer meets quality standards by checking for blocked content and grounding.

3. **Response Synthesis and Delivery**:
   - **Updating Conversation**: Saves the generated answer and relevant metadata back to Cosmos DB.
   - **Delivery**: Formats and sends the response to the user, completing the interaction cycle.

## Cloud Deployment

To deploy the orchestrator in the cloud for the first time, please follow the deployment instructions provided in the [Enterprise RAG repo](https://github.com/Azure/GPT-RAG?tab=readme-ov-file#getting-started).  
   
These instructions include the necessary infrastructure templates to provision the solution in the cloud.  
   
Once the infrastructure is provisioned, you can redeploy just the orchestrator component using the instructions below:

First, please confirm that you have met the prerequisites:

 - Azure Developer CLI: [Download azd for Windows](https://azdrelease.azureedge.net/azd/standalone/release/1.5.0/azd-windows-amd64.msi), [Other OS's](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd).
 - Git: [Download Git](https://git-scm.com/downloads)
 - Python 3.10: [Download Python](https://www.python.org/downloads/release/python-31011/)

Then just clone this repository and reproduce the following commands within the gpt-rag-orchestrator directory:  

```
azd auth login  
azd env refresh  
azd deploy  
```

> Note: when running the ```azd env refresh```, use the same environment name, subscription, and region used in the initial provisioning of the infrastructure.

### Alternative Cloud Deployment

If you deployed the GPT-RAG infrastructure manually, you can use Azure Functions Core Tools as an alternative to `azd` for deployment:

```bash
func azure functionapp publish FUNCTION_APP_NAME
```

*Replace `FUNCTION_APP_NAME` with the name of your Orchestrator Function App before running the command.*

After completing the deployment, run the following command to confirm that the function was successfully deployed:

```bash
func azure functionapp list-functions FUNCTION_APP_NAME
```

You can download Azure Functions Core Tools from this [link](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python#install-the-azure-functions-core-tools).


## Running Locally with VS Code  
   
[How can I test the solution locally in VS Code?](docs/LOCAL_DEPLOYMENT.md)

### Evaluating

[How to test the orchestrator performance?](docs/LOADTEST.md)

## Contributing

We appreciate your interest in contributing to this project! Please refer to the [CONTRIBUTING.md](https://github.com/Azure/GPT-RAG/blob/main/CONTRIBUTING.md) page for detailed guidelines on how to contribute, including information about the Contributor License Agreement (CLA), code of conduct, and the process for submitting pull requests.

Thank you for your support and contributions!

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

## Fallback System

The orchestrator includes an intelligent fallback system that provides area-specific contact information when no relevant information is found in the RAG system. This system:

1. Analyzes the user's query to determine the most relevant business area
2. Provides contact information for the identified area
3. Falls back to general administration contact if no specific area is identified

### Configuration

The fallback system uses a separate Azure Storage Account for its configuration. To set it up:

1. Create a new Storage Account in Azure
2. Create a container named `fallback-config` (or your preferred name)
3. Upload the areas configuration JSON file as `areas.json`
4. Configure the environment variables with your storage account details

### Environment Variables

- `FALLBACK_ENABLED`: Enable/disable the fallback system (default: true)
- `FALLBACK_STORAGE_ACCOUNT_NAME`: Name of the Azure Storage Account for fallback configuration
- `FALLBACK_STORAGE_CONNECTION_STRING`: Connection string for the fallback storage account
- `FALLBACK_CONTAINER`: Azure Blob Storage container name (default: fallback-config)
- `FALLBACK_BLOB`: Configuration file name (default: areas.json)

### Configuration File Format

```json
{
  "company_areas": [
    {
      "area_id": "hr",
      "area_name": "Recursos Humanos",
      "keywords": ["personal", "empleado", "licencia", "vacaciones", "beneficios", "nómina", "contratación"],
      "contact": {
        "name": "María González",
        "email": "maria.gonzalez@oxfam.org",
        "phone": "+1-555-0123"
      },
      "description": "Políticas de personal, beneficios y administración de empleados"
    }
  ],
  "default_contact": {
    "name": "Administración General",
    "email": "admin@oxfam.org",
    "phone": "+1-555-0000"
  },
  "last_updated": "2025-05-23T10:00:00Z"
}
```

### How It Works

1. When the RAG system finds no relevant information for a query
2. The fallback system analyzes the query text
3. Matches keywords against defined business areas
4. Returns contact information for the most relevant area
5. If no area matches, returns the default contact information
