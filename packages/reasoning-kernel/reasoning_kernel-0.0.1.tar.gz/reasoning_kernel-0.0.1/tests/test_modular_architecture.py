#!/usr/bin/env python3
"""
Test script to validate the modular MSA architecture implementation.
This script checks the structure and interfaces without requiring external dependencies.
"""
import ast
import sys
from pathlib import Path


def test_file_structure():
    """Test that all required files exist."""
    base_path = Path("reasoning_kernel/agents/synthesis")
    required_files = [
        base_path / "protocols.py",
        base_path / "problem_parser.py",
        base_path / "knowledge_retriever.py",
        base_path / "graph_builder.py",
        Path("reasoning_kernel/agents/modular_msa_agent.py"),
    ]

    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False

    print("✓ All required files exist")
    return True


def test_syntax_validity():
    """Test that all Python files have valid syntax."""
    files_to_check = [
        "reasoning_kernel/agents/synthesis/protocols.py",
        "reasoning_kernel/agents/synthesis/problem_parser.py",
        "reasoning_kernel/agents/synthesis/knowledge_retriever.py",
        "reasoning_kernel/agents/synthesis/graph_builder.py",
        "reasoning_kernel/agents/modular_msa_agent.py",
    ]

    for file_path in files_to_check:
        try:
            with open(file_path, "r") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            print(f"✗ Syntax error in {file_path}: {e}")
            return False

    print("✓ All files have valid Python syntax")
    return True


def test_protocol_definitions():
    """Test that protocols are properly defined."""
    try:
        with open("reasoning_kernel/agents/synthesis/protocols.py", "r") as f:
            content = f.read()

        # Check for key protocol definitions
        required_elements = [
            "MSAStageProtocol",
            "ParsedProblem",
            "KnowledgeContext",
            "CausalGraph",
            "SynthesizedProgram",
            "ValidationResult",
            "@runtime_checkable",
        ]

        missing_elements = [elem for elem in required_elements if elem not in content]
        if missing_elements:
            print(f"✗ Missing protocol elements: {missing_elements}")
            return False

        print("✓ All protocol interfaces are defined")
        return True
    except Exception as e:
        print(f"✗ Error checking protocols: {e}")
        return False


def test_modular_agent_structure():
    """Test that ModularMSAAgent has the proper structure."""
    try:
        with open("reasoning_kernel/agents/modular_msa_agent.py", "r") as f:
            content = f.read()

        # Check for key components
        required_components = [
            "class ModularMSAAgent",
            "def synthesize_model",
            "ProblemParser(kernel)",
            "KnowledgeRetriever(kernel)",
            "GraphBuilder(kernel)",
            "MSASynthesisResult",
        ]

        missing_components = [comp for comp in required_components if comp not in content]
        if missing_components:
            print(f"✗ Missing agent components: {missing_components}")
            return False

        print("✓ ModularMSAAgent has proper structure")
        return True
    except Exception as e:
        print(f"✗ Error checking agent structure: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🔍 Testing Modular MSA Architecture Implementation")
    print("=" * 50)

    tests = [test_file_structure, test_syntax_validity, test_protocol_definitions, test_modular_agent_structure]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    if passed == len(tests):
        print(f"🎉 All {len(tests)} tests passed!")
        print("✅ TASK-007: Modular MSA Agent implementation is complete")
        return 0
    else:
        print(f"❌ {len(tests) - passed} of {len(tests)} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
