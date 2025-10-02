import logging
import httpx
import json
import re
from typing import Dict, Any, Optional, List, Tuple
import os
from datetime import datetime

from ..models.citation_models import (
    SourceMetadata, Author, SourceType, CitationStyle
)

logger = logging.getLogger(__name__)


class CitationAIService:
    """
    AI-powered citation features using Google Generative Language (Gemini) API.

    Key features:
    - ALWAYS calls ListModels first and logs the result (or the exact error body).
    - Uses x-goog-api-key header (works even when query param is restricted).
    - Falls back to simple regex extraction if Gemini is unavailable.
    - Handles Markdown-fenced JSON and sanitizes year to avoid Pydantic errors.
    """

    # Candidate models to prefer (ordered by speed -> capability)
    PREFERRED_MODELS = [
        "gemini-1.5-flash-001",
        "gemini-1.5-flash",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
    ]

    CANDIDATE_VERSIONS = ["v1beta", "v1"]

    def __init__(self, gemini_api_key: str = ""):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.requested_version = os.getenv("GEMINI_API_VERSION", "auto").strip().lower()
        self.requested_model = os.getenv("GEMINI_MODEL", "auto").strip()

        self.api_version: Optional[str] = None
        self.model: Optional[str] = None
        self.base_url: Optional[str] = None

        if self.api_key:
            logger.info(f"Citation AI Service initialized with API key: {self.api_key[:20]}...")
        else:
            logger.warning("⚠️ Citation AI Service initialized WITHOUT API key - AI features will not work!")

    # ---------------------------
    # Utilities
    # ---------------------------

    @staticmethod
    def _sanitize_year(year: Optional[int]) -> Optional[int]:
        """Ensure year is between 1000 and the current year; otherwise return None."""
        if year is None:
            return None
        try:
            y = int(year)
            current_year = datetime.utcnow().year
            if 1000 <= y <= current_year:
                return y
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_fenced_json(text: str) -> str:
        """Extract JSON from ```json ... ``` or ``` ... ``` fenced blocks, else return stripped text."""
        text = text.strip()
        m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
        s = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        s = re.sub(r"\s*```$", "", s)
        return s.strip()

    # ---------------------------
    # Fallback (no-AI) extractor
    # ---------------------------

    def _extract_metadata_simple(self, text: str) -> SourceMetadata:
        title_match = (
            re.search(r'["\'](.+?)["\']', text) or
            re.search(r'(?:cite|paper|article)[\s:]+(.+?)(?:by|from)', text, re.I)
        )
        author_match = re.search(r'by\s+(\w+(?:\s+\w+)?)', text, re.I)
        year_match = re.search(r'\b(19|20)\d{2}\b', text)

        authors = []
        if author_match:
            name = author_match.group(1).strip()
            parts = name.split()
            if len(parts) == 1:
                authors.append(Author(first_name="", last_name=parts[0]))
            else:
                authors.append(Author(first_name=parts[0], last_name=" ".join(parts[1:])))

        if not authors:
            authors = [Author(first_name="Unknown", last_name="Author")]

        year_val = self._sanitize_year(int(year_match.group(0)) if year_match else None)

        return SourceMetadata(
            source_type=SourceType.JOURNAL_ARTICLE,
            title=title_match.group(1) if title_match else text[:100],
            authors=authors,
            year=year_val,
            publication="Unknown Publication",
        )

    # ---------------------------
    # Public API
    # ---------------------------

    async def extract_metadata_from_text(self, text: str) -> SourceMetadata:
        if not self.api_key:
            logger.warning("No Gemini API key, using simple extraction")
            return self._extract_metadata_simple(text)

        try:
            await self._resolve_model_with_listmodels()
            prompt = self._build_extraction_prompt(text)
            response = await self._call_gemini_generate_content(prompt)
            data = self._parse_json_response(response)
            data["year"] = self._sanitize_year(data.get("year"))
            meta = self._dict_to_metadata(data)
            logger.info(f"✅ Extracted metadata: {meta.title}")
            return meta
        except Exception as e:
            logger.error(f"❌ AI extraction failed: {e}; falling back to simple extraction")
            return self._extract_metadata_simple(text)

    async def extract_metadata_from_doi(self, doi: str) -> SourceMetadata:
        try:
            url = f"https://api.crossref.org/works/{doi}"
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=10)
                r.raise_for_status()
                data = r.json()
            work = data.get("message", {})

            authors = [
                Author(first_name=a.get("given", ""), last_name=a.get("family", ""))
                for a in work.get("author", []) or []
            ]

            year_val = None
            for path in ("published-print", "published-online", "issued"):
                try:
                    year_candidate = work.get(path, {}).get("date-parts", [[None]])[0][0]
                    year_val = self._sanitize_year(year_candidate)
                    if year_val:
                        break
                except Exception:
                    pass

            return SourceMetadata(
                source_type=SourceType.JOURNAL_ARTICLE,
                title=(work.get("title", [""]) or [""])[0],
                authors=authors or [Author(first_name="Unknown", last_name="Author")],
                year=year_val,
                publication=(work.get("container-title", [""]) or [""])[0],
                volume=work.get("volume"),
                issue=work.get("issue"),
                pages=work.get("page"),
                doi=doi,
            )
        except Exception as e:
            logger.error(f"DOI extraction error: {e}")
            raise

    async def extract_metadata_from_url(self, url: str) -> SourceMetadata:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, timeout=10, follow_redirects=True)
                r.raise_for_status()
                html = r.text

            await self._resolve_model_with_listmodels()
            prompt = self._build_url_extraction_prompt(url, html[:5000])
            response = await self._call_gemini_generate_content(prompt)
            data = self._parse_json_response(response)
            data["year"] = self._sanitize_year(data.get("year"))
            meta = self._dict_to_metadata(data)
            meta.url = url
            logger.info(f"Extracted URL metadata: {meta.title}")
            return meta
        except Exception as e:
            logger.error(f"URL extraction error: {e}")
            raise

    async def validate_citation(self, citation: str, style: CitationStyle) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "is_valid": False,
                "errors": ["GEMINI_API_KEY not configured"],
                "suggestions": [],
                "corrected_citation": citation,
            }
        try:
            await self._resolve_model_with_listmodels()
            prompt = f"""
You are a citation expert. Validate the following {style.value.upper()} citation:

Citation: {citation}

Check for:
1. Correct formatting
2. Missing required elements
3. Punctuation errors
4. Capitalization issues

Return JSON:
{{
  "is_valid": true/false,
  "errors": ["error1", "error2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "corrected_citation": "corrected version if needed"
}}
"""
            response = await self._call_gemini_generate_content(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Citation validation error: {e}")
            return {
                "is_valid": False,
                "errors": [str(e)],
                "suggestions": [],
                "corrected_citation": citation,
            }

    # ---------------------------
    # Prompt builders
    # ---------------------------

    def _build_extraction_prompt(self, text: str) -> str:
        return f"""
You are an expert citation metadata extractor. Extract bibliographic information from the following text:

Text: "{text}"

Extract and return ONLY valid JSON (no markdown, no explanation):
{{
  "source_type": "journal_article",
  "title": "full title",
  "authors": [{{"first_name": "First", "last_name": "Last", "middle_name": null}}],
  "year": 2024,
  "publication": "journal or publisher name",
  "volume": null,
  "issue": null,
  "pages": null,
  "doi": null,
  "url": null,
  "publisher": null,
  "conference_name": null,
  "institution": null
}}

Return ONLY the JSON object, nothing else.
"""

    def _build_url_extraction_prompt(self, url: str, html_snippet: str) -> str:
        return f"""
Extract citation metadata from this webpage:

URL: {url}
HTML Preview: {html_snippet}

Determine the source type (article, blog post, report, etc.) and extract metadata.

Return ONLY valid JSON:
{{
  "source_type": "website",
  "title": "page title",
  "authors": [{{"first_name": "First", "last_name": "Last"}}],
  "year": 2024,
  "publication": "website name",
  "url": "{url}",
  "access_date": "YYYY-MM-DD"
}}

Return ONLY the JSON object.
"""

    # ---------------------------
    # Gemini API: model resolution + call
    # ---------------------------

    async def _resolve_model_with_listmodels(self) -> None:
        """
        Call ListModels and choose a model that supports generateContent.
        Logs the exact failure body if ListModels doesn't work, so you know what to fix.
        """
        if self.api_version and self.model and self.base_url:
            # already resolved
            return

        headers = {"x-goog-api-key": self.api_key}
        versions_to_try = (
            [self.requested_version] if self.requested_version in self.CANDIDATE_VERSIONS else self.CANDIDATE_VERSIONS
        )

        async with httpx.AsyncClient() as client:
            for ver in versions_to_try:
                list_url = f"https://generativelanguage.googleapis.com/{ver}/models"
                try:
                    r = await client.get(list_url, headers=headers, timeout=15)
                    if r.status_code != 200:
                        logger.error(f"ListModels FAILED [{ver}] {r.status_code}: {r.text[:400]}")
                        continue

                    payload = r.json()
                    models = payload.get("models", []) or []
                    logger.info(f"ListModels ok ({ver}) - found {len(models)} models")
                    # Try requested model first (if provided)
                    if self.requested_model != "auto":
                        for m in models:
                            name = m.get("name", "")
                            methods = set(m.get("supportedGenerationMethods", []) or [])
                            # Name is 'models/<model-id>' -> check end
                            if name.endswith(self.requested_model) and "generateContent" in methods:
                                self.api_version = ver
                                self.model = self.requested_model
                                self.base_url = f"https://generativelanguage.googleapis.com/{ver}/models"
                                logger.info(f"Resolved requested model: {ver}/{self.model}")
                                return

                    # Otherwise pick a preferred model that supports generateContent
                    for wanted in self.PREFERRED_MODELS:
                        for m in models:
                            name = m.get("name", "")
                            methods = set(m.get("supportedGenerationMethods", []) or [])
                            if name.endswith(wanted) and "generateContent" in methods:
                                self.api_version = ver
                                self.model = wanted
                                self.base_url = f"https://generativelanguage.googleapis.com/{ver}/models"
                                logger.info(f"Resolved model via ListModels: {ver}/{wanted}")
                                return

                    # If we saw models but none matched, log the first few for debugging
                    logger.warning("ListModels returned models, but none matched preferred list with generateContent.")
                    for m in models[:5]:
                        logger.warning(f"Available model: {m.get('name')} methods={m.get('supportedGenerationMethods')}")

                except Exception as e:
                    logger.error(f"ListModels exception for {ver}: {e}")

        # If nothing worked:
        raise RuntimeError(
            "Gemini ListModels failed or returned no suitable models. "
            "Please ensure the Generative Language API is enabled for your project, "
            "billing is enabled, and your API key is not restricted from this API."
        )

    async def _call_gemini_generate_content(self, prompt: str) -> str:
        """
        Call generateContent on the resolved version/model using the header API key.
        """
        if not (self.api_version and self.model and self.base_url):
            raise RuntimeError("Gemini model not resolved")

        url = f"{self.base_url}/{self.model}:generateContent"
        headers = {"x-goog-api-key": self.api_key}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=headers, json=payload, timeout=30)
            logger.info(f"Gemini generateContent [{self.api_version}/{self.model}] -> {r.status_code}")
            if r.status_code != 200:
                logger.error(f"Gemini generateContent error: {r.status_code} - {r.text[:400]}")
                raise RuntimeError(f"Gemini generateContent error: {r.status_code}")

            data = r.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Gemini response body: {e}; body={str(data)[:400]}")
                raise ValueError("Invalid Gemini API response structure")

    # ---------------------------
    # JSON parsing & dict->model
    # ---------------------------

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        if response is None:
            raise ValueError("Empty AI response")
        candidate = self._extract_fenced_json(response)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nResponse: {candidate[:500]}...")
            raise ValueError("AI returned invalid JSON") from e

    def _dict_to_metadata(self, data: Dict[str, Any]) -> SourceMetadata:
        authors = []
        for author in data.get("authors", []) or []:
            authors.append(Author(
                first_name=(author or {}).get("first_name", ""),
                last_name=(author or {}).get("last_name", ""),
                middle_name=(author or {}).get("middle_name"),
            ))
        if not authors:
            authors = [Author(first_name="Unknown", last_name="Author")]

        st = data.get("source_type", "journal_article")
        try:
            source_type = SourceType(st)
        except ValueError:
            source_type = SourceType.JOURNAL_ARTICLE

        year_val = self._sanitize_year(data.get("year"))

        return SourceMetadata(
            source_type=source_type,
            title=data.get("title", "Untitled"),
            authors=authors,
            year=year_val,
            publication=data.get("publication"),
            volume=data.get("volume"),
            issue=data.get("issue"),
            pages=data.get("pages"),
            doi=data.get("doi"),
            url=data.get("url"),
            publisher=data.get("publisher"),
            conference_name=data.get("conference_name"),
            institution=data.get("institution"),
            access_date=data.get("access_date"),
        )
