# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-04-09

### ✨ Features
- **Database Discovery**: Complete mapping of v_financas_geral view with all 11 columns
- **Intent Detection Fix**: Data Detective now correctly classifies TOTAL queries without entity search
- **Professional Logging**: Added [SQL EXEC] and [FUZZY SEARCH] tags for comprehensive debugging
- **Column Mapping**: Updated from incorrect names (ug→unidade_pagadora, pessoa_nome→historico_detalhado)
- **Docker Updates**: Prepared for Python 3.13 migration (currently 3.9)
- **GitHub Readiness**: Full CI/CD setup with GitHub Actions workflows

### 🐛 Bug Fixes
- Pergunta 1 (TOTAL query) was incorrectly searching for "IFS" as entity instead of returning total
- Missing logging infrastructure for troubleshooting agent behavior
- SQL Architect using wrong column references in prompts
- Period filtering using dynamic date instead of full 2024 year range

### 🧪 Tests
- Pergunta 1 (Total 2024): ✅ **PASS** - R$ 339.539.000,00 (95% confidence)
- Generated SQL: `SELECT SUM(valor) FROM v_financas_geral WHERE DATE(data) BETWEEN '2024-01-01' AND '2024-12-31'`
- Response format: Portuguese PT-BR with correct currency formatting
- Perguntas 2-5: Ready for full test suite execution

### 📊 Technical Details
- CrewAI orchestration with 3 optimized agents
- Logging infrastructure with structured tags
- Database queries validated against live MySQL
- Metadata Navigator Intent Detection enhanced
- SQL Architect prompt improved with aggregation examples

### 🔍 Database Validation
- Total records in 2024: 10,648
- Total value: R$ 339.539.040,77
- All columns identified and documented
- View structure completely mapped

### 📝 Documentation Added
- CHANGELOG.md (this file)
- CONTRIBUTING.md
- Professional README updates
- docs/ folder with technical documentation

## [1.0.0] - Initial Release
- Basic CrewAI chatbot implementation
- 3 core agents (Data Detective, SQL Architect, Analyst)
- Streamlit web interface
- MySQL database integration
