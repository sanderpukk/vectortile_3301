# Skill Observation Log

Observations captured during task-oriented work. Each entry identifies a
potential skill improvement or new skill opportunity.

**Status key:** OPEN = not yet actioned | ACTIONED = skill updated/created |
DECLINED = user decided not to pursue

---

## 2026-07-05

### Observation 1: PDF text extraction on Windows needs pypdf fallback

**Status:** OPEN
**Date:** 2026-07-05
**Session context:** Reviewing ETAK→OMT transportation mapping; needed classifier tables from a data-model PDF
**Skill:** pdf (system skill — would route to pdf-extras)
**Type:** open-source
**Phase/Area:** Text extraction workflow

**Issue:** The harness Read tool could not render PDF pages ("pdftoppm is not installed") on Windows, and neither pdfplumber nor pypdf were installed. `pip install pypdf` plus a short extraction script to a scratchpad text file worked immediately, and Grep over the extracted text was an effective way to locate classifier tables in a 21-page document.

**Suggested improvement:** For Windows environments, note in the PDF workflow that the Read tool's page rendering depends on poppler and that `pip install pypdf` + extract-to-text + Grep is the fastest fallback for text-based (non-scanned) PDFs.

**Principle:** When a built-in tool has an OS-dependent binary dependency, the skill should name the cheapest pure-Python fallback so extraction proceeds without installing system packages.
