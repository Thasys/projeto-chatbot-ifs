# 🤝 Contributing to IFS Chatbot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the IFS Chatbot project.

## Getting Started

### Prerequisites
- Python 3.13+
- Git
- GitHub account
- MySQL database access (for development)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/seu-usuario/projeto-chatbot-ifs.git
cd projeto-chatbot-ifs
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Testing

### Run quick test (single question)
```bash
python quick_test.py
```

### Run full test suite (5 questions)
```bash
python test_simples_v2.py
```

### Run unit tests
```bash
python -m pytest tests/ -v
```

## Code Style

### Requirements
- **Type Hints**: Mandatory in all functions
- **Docstrings**: Write in Portuguese (PT-BR)
- **Logging**: Use tags like [MODULO] for clarity
- **PEP 8**: Follow Python style guidelines

### Example Function
```python
def execute_sql(query: str, connection: Any) -> List[Dict]:
    """
    Executa uma query SQL contra o banco de dados.
    
    Args:
        query: SQL para executar
        connection: Conexão com MySQL
        
    Returns:
        Lista de dicionários com dados
    """
    logger.info(f"[SQL EXEC] Executando: {query[:50]}...")
    # ... implementation
```

### Example Docstring (PT-BR)
```python
def search_entity_fuzzy(termo: str, lista: List[str], threshold: float = 80) -> List:
    """
    Busca fuzzy por similaridade de string.
    
    Utiliza RapidFuzz para encontrar matches aproximados.
    
    Args:
        termo: Termo a buscar
        lista: Lista para buscar
        threshold: Limite de similaridade (0-100)
        
    Returns:
        Lista de matches ordenados por score
    """
```

## Git Workflow

### Branch Naming
```
feature/nome-da-funcionalidade    # Nova feature
fix/descricao-do-bug              # Correção de bug
docs/descricao-docs               # Documentação
refactor/descricao-refatoracao    # Refatoração
```

### Commit Messages
Format: `<type>: <subject>`

Examples:
```
feat: Add fuzzy search to entity matching
fix: Correct TOTAL query intent detection
docs: Update README with deployment instructions
refactor: Simplify SQL query builder
test: Add tests for data validation
```

### Pull Request Process

1. **Create feature branch**
```bash
git checkout -b feature/sua-feature
```

2. **Make changes and test**
```bash
python test_simples_v2.py
python -m pytest tests/ -v
```

3. **Commit changes**
```bash
git add .
git commit -m "feat: Descrição da feature"
```

4. **Push to GitHub**
```bash
git push origin feature/sua-feature
```

5. **Open Pull Request on GitHub**
   - Provide clear PR title and description
   - Reference related issues if applicable
   - Ensure all tests pass before submitting

## Architecture Overview

### Three Core Agents

**1. Data Detective (Metadata Navigator)**
- Extracts intent from user query
- Identifies entities (campus, expense type, etc)
- Returns JSON with intent classification

**2. SQL Expert (SQL Architect)**
- Generates optimized SQL from intent + entities
- Handles aggregations (SUM, COUNT, AVG)
- Applies data filters

**3. Public Transparency Analyst**
- Formats SQL results
- Translates to Portuguese PT-BR
- Calculates confidence scores

### Database
- View: `v_financas_geral` (11 columns)
- Key columns: data, valor, unidade_pagadora, tipo_despesa, historico_detalhado
- 2024 Data: 10,648 records, R$ 339.539.040,77 total

## Key Files

- `crew_definition_v2.py`: Agent definitions and prompts
- `tools.py`: SQL execution and fuzzy search
- `app_v2.py`: Streamlit interface
- `db_connection.py`: MySQL connector
- `etl_scripts/`: ETL pipeline

## Common Tasks

### Add a new agent capability
1. Update `crew_definition_v2.py` with new task
2. Add corresponding tool in `tools.py`
3. Test with `quick_test.py`
4. Document in README.md

### Fix a bug
1. Create issue describing the bug
2. Create `fix/bug-name` branch
3. Apply fix and test thoroughly
4. PR with description of root cause
5. Reference issue in PR

### Improve documentation
1. Update relevant .md files
2. Keep examples current
3. Test code examples if provided
4. PR with "docs:" prefix

## Reporting Issues

When reporting bugs, please include:
- **Description**: Clear explanation of the issue
- **Steps to Reproduce**: How to trigger the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, etc
- **Logs**: Relevant debug output (use [MODULO] tags)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing issues on GitHub
- Review CONTRIBUTING.md carefully
- Ask in pull request comments
- Contact maintainers if needed

---

**Thank you for contributing to IFS Chatbot! 🎉**
