from pathlib import Path

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

DOCS_DIR = Path(__file__).parent.parent / "docs"
DOCS_FILES = DOCS_DIR.glob("**/*.md")


@pytest.mark.parametrize("example", find_examples(*DOCS_FILES), ids=str)
def test_docs(example: CodeExample, eval_example: EvalExample):
    """Test the package's documentation."""
    eval_example.set_config(line_length=88)
    if eval_example.update_examples:
        eval_example.format(example)
        eval_example.run_print_update(example)
    else:
        eval_example.lint(example)
        eval_example.run_print_check(example)
