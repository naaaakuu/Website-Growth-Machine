"""Offline unit tests for the bounded, passive site crawler."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_site  # noqa: E402


class FakeResponse:
    def __init__(self, status, headers=None, body=b""):
        self.status = status
        self.headers = headers or {}
        self._body = body

    def read(self, _limit=None):
        return self._body


class MockOpener:
    """An urllib-compatible opener that records requested URLs and never uses a socket."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def open(self, request, timeout):
        url = request.full_url
        self.calls.append((url, timeout))
        item = self.routes[url]
        if isinstance(item, tuple) and item[0] == "error":
            _, status, headers = item
            raise HTTPError(url, status, "fixture", headers, io.BytesIO())
        return item


class SiteAuditTests(unittest.TestCase):
    def test_crawl_reports_metadata_redirects_broken_links_duplicates_and_alt_text(self):
        root = "https://example.test/"
        old = "https://example.test/old"
        new = "https://example.test/new"
        missing = "https://example.test/missing"
        html = b"""
            <html><head>
              <title>Shared Title</title>
              <meta name='description' content='Shared description'>
              <meta name='robots' content='index, follow'>
              <link rel='canonical alternate' href='/canonical'>
            </head><body>
              <h1>Home heading</h1>
              <a href='/old'>redirected</a><a href='/missing'>missing</a>
              <a href='https://outside.test/never-fetch'>outside</a>
              <script>document.write("<a href='/unsafe'>unsafe</a>")</script>
              <img src='/logo.svg' alt=' Company logo '><img src='/spacer.gif' alt=''>
            </body></html>
        """
        routes = {
            root: FakeResponse(200, {"content-type": "text/html; charset=utf-8"}, html),
            old: ("error", 301, {"location": "/new"}),
            new: FakeResponse(
                200,
                {"content-type": "text/html"},
                b"<title>Shared Title</title><meta name='description' content='Shared description'><h1>New</h1>",
            ),
            missing: ("error", 404, {}),
        }
        opener = MockOpener(routes)
        report = audit_site.SiteAuditor(root, max_pages=10, opener=opener, check_favicon=False).crawl()

        self.assertEqual(report["summary"]["pages_fetched"], 3)
        self.assertEqual([item["url"] for item in report["broken_internal_links"]], [missing])
        self.assertEqual(report["pages"][0]["canonical"], "https://example.test/canonical")
        self.assertEqual(report["pages"][0]["robots"], ["index, follow"])
        self.assertEqual(report["pages"][0]["h1"], "Home heading")
        self.assertEqual(report["redirect_chains"][0]["chain"], [old, new])
        self.assertEqual(report["nonempty_image_alt_observations"], [{"page": root, "src": "/logo.svg", "alt": "Company logo"}])
        self.assertEqual(len(report["duplicate_titles"]), 1)
        self.assertEqual(len(report["duplicate_meta_descriptions"]), 1)
        self.assertEqual(report["audit_issue_candidates"][0]["priority"], "MEDIUM")
        self.assertEqual(report["audit_issue_candidates"][0]["affected_url"], missing)
        self.assertFalse(any("outside.test" in call[0] or "/unsafe" in call[0] for call in opener.calls))

    def test_cross_origin_redirect_is_reported_but_not_followed(self):
        root = "https://example.test/"
        opener = MockOpener({root: ("error", 302, {"location": "https://outside.test/"})})
        report = audit_site.SiteAuditor(root, opener=opener, check_favicon=False).crawl()

        self.assertEqual([call[0] for call in opener.calls], [root])
        self.assertEqual(report["pages"][0]["error"], "cross_origin_redirect_blocked")
        self.assertEqual(report["audit_issue_candidates"][0]["priority"], "HIGH")
        self.assertEqual(report["summary"]["failed_pages"], 1)

    def test_favicon_evidence_collects_root_and_declared_icons(self):
        root = "https://example.test/"
        favicon = "https://example.test/favicon.ico"
        touch_icon = "https://example.test/apple-touch-icon.png"
        page = {"icon_links": [{"rel": "apple-touch-icon", "href": touch_icon, "sizes": "180x180"}]}
        opener = MockOpener(
            {
                favicon: FakeResponse(200, {"content-type": "image/x-icon"}, b"\x00"),
                touch_icon: ("error", 404, {}),
            }
        )
        auditor = audit_site.SiteAuditor(root, opener=opener, check_favicon=False)
        evidence = auditor._collect_favicon_evidence(page)

        self.assertEqual(evidence["root_favicon"], {"url": favicon, "status": 200, "error": None})
        self.assertEqual(len(evidence["declared_icons"]), 1)
        self.assertEqual(evidence["declared_icons"][0]["status"], 404)
        self.assertFalse(evidence["declared_icons"][0]["skipped_cross_origin"])

    def test_favicon_evidence_skips_cross_origin_declared_icons_without_fetching(self):
        root = "https://example.test/"
        favicon = "https://example.test/favicon.ico"
        cdn_icon = "https://cdn.other-test/icon.png"
        page = {"icon_links": [{"rel": "icon", "href": cdn_icon, "sizes": ""}]}
        opener = MockOpener({favicon: ("error", 404, {})})
        auditor = audit_site.SiteAuditor(root, opener=opener, check_favicon=False)
        evidence = auditor._collect_favicon_evidence(page)

        self.assertTrue(evidence["declared_icons"][0]["skipped_cross_origin"])
        self.assertFalse(any(cdn_icon in call[0] for call in opener.calls))

    def test_crawl_surfaces_pending_favicon_classification(self):
        root = "https://example.test/"
        favicon = "https://example.test/favicon.ico"
        opener = MockOpener(
            {
                root: FakeResponse(200, {"content-type": "text/html"}, b"<title>Home</title>"),
                favicon: ("error", 404, {}),
            }
        )
        auditor = audit_site.SiteAuditor(root, opener=opener)
        with self.assertRaises(NotImplementedError):
            auditor.crawl()

    def test_url_normalization_rejects_credential_and_non_http_urls(self):
        self.assertIsNone(audit_site.normalize_http_url("javascript:alert(1)", "https://example.test/"))
        self.assertIsNone(audit_site.normalize_http_url("https://user:pass@example.test/"))
        self.assertEqual(audit_site.normalize_http_url("/a#fragment", "https://EXAMPLE.test/"), "https://example.test/a")
        with self.assertRaises(ValueError):
            audit_site.SiteAuditor("file:///etc/passwd")


if __name__ == "__main__":
    unittest.main()
