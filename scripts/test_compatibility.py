#!/usr/bin/env python3
"""
Teste de Compatibilidade - Python 3.12/3.13
Valida que todas as dependências funcionam corretamente
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_python_version():
    """Verificar versão do Python"""
    logger.info("=" * 60)
    logger.info("TEST 1: Python Version")
    logger.info("=" * 60)

    version = sys.version_info
    logger.info(
        f"Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 10:
        logger.info("✅ Versão compatível com PythonAnywhere")
        return True
    else:
        logger.error("❌ Versão incompatível")
        return False


def test_imports():
    """Testar imports críticos"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Critical Imports")
    logger.info("=" * 60)

    imports = {
        'streamlit': 'Streamlit (Web UI)',
        'crewai': 'CrewAI (AI Agents)',
        'sqlalchemy': 'SQLAlchemy (ORM)',
        'pandas': 'Pandas (Data Processing)',
        'rapidfuzz': 'RapidFuzz (Fuzzy Search)',
        'mysql.connector': 'MySQL Connector',
        'langchain_openai': 'LangChain OpenAI',
        'unidecode': 'Unidecode (Normalization)',
    }

    all_ok = True
    for module_name, description in imports.items():
        try:
            __import__(module_name)
            logger.info(f"✅ {description:30} ({module_name})")
        except ImportError as e:
            logger.error(f"❌ {description:30} ({module_name})")
            logger.error(f"   Error: {e}")
            all_ok = False

    return all_ok


def test_streamlit():
    """Testar Streamlit especificamente"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Streamlit Setup")
    logger.info("=" * 60)

    try:
        import streamlit as st
        logger.info(f"✅ Streamlit Version: {st.__version__}")
        logger.info(f"✅ Streamlit Location: {st.__file__}")
        return True
    except Exception as e:
        logger.error(f"❌ Streamlit Error: {e}")
        return False


def test_crewai():
    """Testar CrewAI"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: CrewAI Setup")
    logger.info("=" * 60)

    try:
        from crewai import Agent, Task, Crew
        logger.info(f"✅ CrewAI imports successful")
        logger.info(f"✅ Agent, Task, Crew classes available")
        return True
    except Exception as e:
        logger.error(f"❌ CrewAI Error: {e}")
        return False


def test_database():
    """Testar database drivers"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Database Drivers")
    logger.info("=" * 60)

    drivers = {
        'mysql.connector': 'MySQL Connector',
        'pymysql': 'PyMySQL (Alternative)',
        'sqlalchemy': 'SQLAlchemy'
    }

    all_ok = False
    for module, name in drivers.items():
        try:
            __import__(module)
            logger.info(f"✅ {name:30} ({module})")
            all_ok = True
        except ImportError:
            logger.warning(f"⚠️  {name:30} ({module}) - optional")

    return all_ok


def test_file_imports():
    """Testar imports dos arquivos do projeto"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Project File Imports")
    logger.info("=" * 60)

    try:
        # Tentar importar módulos principais
        sys.path.insert(0, '.')

        # Aqui varíamos pois alguns imports podem faltar por falta de .env
        try:
            from tools import execute_query
            logger.info(f"✅ tools.py - execute_query function")
        except ImportError as e:
            logger.warning(
                f"⚠️  tools.py import error (expected if .env missing): {e}")

        logger.info(f"✅ Project imports testable")
        return True

    except Exception as e:
        logger.error(f"❌ Project import error: {e}")
        return False


def main():
    """Executar todos os testes"""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"COMPATIBILITY TEST STARTED: {datetime.now()}")
    logger.info(f"{'=' * 60}\n")

    results = {
        'Python Version': test_python_version(),
        'Critical Imports': test_imports(),
        'Streamlit': test_streamlit(),
        'CrewAI': test_crewai(),
        'Database Drivers': test_database(),
        'Project Imports': test_file_imports(),
    }

    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:25} {status}")

    logger.info(f"\n{passed}/{total} tests passed")

    if passed == total:
        logger.info(
            "\n✅ ALL TESTS PASSED - Ready for PythonAnywhere deployment!")
        return 0
    else:
        logger.info("\n⚠️  SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
