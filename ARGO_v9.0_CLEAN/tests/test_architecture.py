"""
Architecture Validation Tests
Tests that enforce clean architecture principles
"""
import pytest
from pathlib import Path
import ast
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_no_version_suffixes_in_core():
    """Core modules should not have version suffixes"""
    core_path = Path(__file__).parent.parent / "core"
    
    versioned = []
    for file in core_path.glob("*.py"):
        if any(suffix in file.stem for suffix in ['_v', '_f', '_old', '_backup']):
            versioned.append(file.name)
    
    assert len(versioned) == 0, f"Found versioned files in core: {versioned}"


def test_single_bootstrap():
    """Should only have one bootstrap.py"""
    root = Path(__file__).parent.parent
    bootstraps = list(root.rglob("bootstrap*.py"))
    
    assert len(bootstraps) == 1, f"Found multiple bootstrap files: {bootstraps}"
    assert bootstraps[0].name == "bootstrap.py"


def test_single_rag_engine():
    """Should only have one rag_engine.py"""
    root = Path(__file__).parent.parent
    rag_engines = list(root.rglob("rag_engine*.py"))
    
    assert len(rag_engines) == 1, f"Found multiple RAG engines: {rag_engines}"
    assert rag_engines[0].name == "rag_engine.py"


def test_no_direct_llm_in_app():
    """App should not instantiate LLMs directly"""
    app_files = list(Path(__file__).parent.parent.glob("app*.py"))
    
    for app_file in app_files:
        content = app_file.read_text()
        
        assert 'ChatOpenAI(' not in content, f"{app_file.name} has direct ChatOpenAI"
        assert 'ChatAnthropic(' not in content, f"{app_file.name} has direct ChatAnthropic"


def test_extractors_is_single_source():
    """Only extractors.py should create text splitters"""
    root = Path(__file__).parent.parent
    
    violations = []
    for py_file in root.rglob("*.py"):
        if py_file.name == "extractors.py":
            continue
        
        try:
            content = py_file.read_text()
            if 'RecursiveCharacterTextSplitter(' in content:
                violations.append(py_file.relative_to(root))
        except:
            pass
    
    assert len(violations) == 0, f"Direct text splitter usage in: {violations}"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
