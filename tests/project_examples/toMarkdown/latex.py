"""!@file
@brief Implement LaTeX validation helpers used by the Pix2Tex phase.
@details Executes sequential validation gates: delimiter balance,
``pylatexenc`` parsing, MathJax compatibility filters, and matplotlib parsing.
"""

from __future__ import annotations

import logging
import re
from typing import Iterable

import matplotlib  # type: ignore[reportMissingImports]

matplotlib.use("Agg")  # garantisce il rendering headless
import matplotlib.pyplot as plt  # noqa: E402  # type: ignore[reportMissingImports]
from matplotlib import mathtext  # noqa: E402  # type: ignore[reportMissingImports]
from pylatexenc.latexwalker import LatexWalker, LatexWalkerError  # noqa: E402  # type: ignore[reportMissingImports]

#: @brief Module logger used for validation diagnostics.
LOG = logging.getLogger("tomarkdown.latex")


def _strip_markdown_delimiters(latex: str) -> str:
    """!@brief Strip outer markdown math delimiters from LaTeX payload.
    @details Normalizes formula text by trimming whitespace and surrounding
    dollar delimiters before syntax validation.
    @param latex {str} Raw markdown or LaTeX expression candidate.
    @return {str} Delimiter-stripped expression used by validators.
    """

    return latex.strip().strip("$ ").strip()


def _iter_chars(content: str) -> Iterable[str]:
    """!@brief Iterate expression tokens preserving ``\\left``/``\\right``.
    @details Scans input string and emits control tokens as atomic units to
    preserve delimiter semantics for stack-based validation.
    @param content {str} LaTeX expression without outer markdown delimiters.
    @return {Iterable[str]} Ordered token stream used by delimiter checks.
    """

    i = 0
    while i < len(content):
        if content.startswith(r"\left", i):
            yield r"\left"
            i += 5
            continue
        if content.startswith(r"\right", i):
            yield r"\right"
            i += 6
            continue
        yield content[i]
        i += 1


def _validate_delimiters(latex: str) -> bool:
    """!@brief Validate paired delimiters in a LaTeX expression.
    @details Applies stack-based matching for ``()`` ``[]`` ``{}`` and
    ``\\left``/``\\right`` markers. Returns ``False`` on first mismatch.
    @param latex {str} Raw expression candidate potentially containing markdown delimiters.
    @return {bool} True when all delimiters are balanced; otherwise False.
    """

    mapping = {"{": "}", "[": "]", "(": ")"}
    stack: list[str] = []
    for token in _iter_chars(_strip_markdown_delimiters(latex)):
        if token == r"\left":
            stack.append("left-right")
            continue
        if token == r"\right":
            if not stack or stack.pop() != "left-right":
                return False
            continue
        if token in mapping:
            stack.append(mapping[token])
            continue
        if token in mapping.values():
            if not stack or token != stack.pop():
                return False
    return len(stack) == 0


def _validate_with_pylatexenc(latex: str) -> bool:
    """!@brief Parse LaTeX with ``pylatexenc``.
    @details Executes syntactic parse to reject malformed expressions and logs
    parsing failures at debug level.
    @param latex {str} Raw expression candidate potentially containing markdown delimiters.
    @return {bool} True when parser accepts the expression; otherwise False.
    """

    clean = _strip_markdown_delimiters(latex)
    try:
        LatexWalker(clean).get_latex_nodes()
        return True
    except LatexWalkerError as exc:
        LOG.debug("pylatexenc validation failed: %s", exc)
        return False
    except Exception as exc:  # pragma: no cover - defensive
        LOG.debug("Unexpected pylatexenc error: %s", exc)
        return False


#: @brief TeX tokens rejected for MathJax compatibility.
FORBIDDEN_TEX_TOKENS = [r"\atop", r"\atopwithdelims", r"\overwithdelims"]
#: @brief Regex matching empty styled groups that break rendering.
EMPTY_GROUP_RE = re.compile(r"\\(?:mathrm|mathit|mathbf|mathsf|mathtt|textrm|textbf|textit)\s*\{\s*\}")
#: @brief Regex matching unsupported environment declarations.
BEGIN_ENV_RE = re.compile(r"\\(?:begin|end)\s*\{[^}]+\}", re.IGNORECASE)


def _validate_mathjax_compat(latex: str) -> bool:
    """!@brief Validate expression compatibility with markdown MathJax rendering.
    @details Rejects formulas containing unsupported tokens, empty groups, or
    environment directives; then verifies parser acceptance through mathtext.
    @param latex {str} Raw expression candidate potentially containing markdown delimiters.
    @return {bool} True when expression is MathJax-compatible; otherwise False.
    """
    formula = _strip_markdown_delimiters(latex)
    lowered = formula.lower()
    for token in FORBIDDEN_TEX_TOKENS:
        if token in lowered:
            LOG.debug("MathJax compatibility failed: forbidden token %s", token)
            return False
    if "{}" in formula:
        LOG.debug("MathJax compatibility failed: empty group detected")
        return False
    if EMPTY_GROUP_RE.search(formula):
        LOG.debug("MathJax compatibility failed: empty styled group detected")
        return False
    env_match = BEGIN_ENV_RE.search(formula)
    if env_match:
        LOG.debug(
            "MathJax compatibility failed: unsupported environment %s",
            env_match.group(0),
        )
        return False
    try:
        parser = mathtext.MathTextParser("path")
        parser.parse(f"${formula}$")
        return True
    except Exception as exc:
        LOG.debug("MathJax compatibility parse failed: %s", exc)
        return False


def _validate_with_matplotlib(latex: str) -> bool:
    """!@brief Validate LaTeX by rendering with matplotlib mathtext.
    @details Performs headless rendering attempt as final compatibility gate.
    Ensures figure resources are closed on both success and failure paths.
    @param latex {str} Raw expression candidate potentially containing markdown delimiters.
    @return {bool} True when rendering succeeds; otherwise False.
    """

    formula = _strip_markdown_delimiters(latex)
    if not formula:
        return False
    try:
        plt.figure(figsize=(1, 1))
        plt.text(0.5, 0.5, f"${formula}$")
        plt.close()
        return True
    except Exception as exc:
        LOG.debug("matplotlib validation failed: %s", exc)
        try:
            plt.close()
        except Exception:
            pass
        return False


def validate_latex_formula(latex: str) -> bool:
    """!@brief Validate LaTeX formula through all configured gates.
    @details Runs sequential validators for empty input, delimiter balance,
    parser correctness, MathJax compatibility, and renderability. Complexity is
    O(n) for token scanning plus parser/render costs.
    @param latex {str} Raw formula candidate from Pix2Tex output.
    @return {bool} True when formula passes every validation stage; otherwise False.
    """

    if not latex or not latex.strip():
        return False
    if not _validate_delimiters(latex):
        return False
    if not _validate_with_pylatexenc(latex):
        return False
    if not _validate_mathjax_compat(latex):
        return False
    if not _validate_with_matplotlib(latex):
        return False
    return True
