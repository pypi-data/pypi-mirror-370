from typing import Optional
from pydantic import BaseModel
from playwright.async_api import async_playwright
from playwright.async_api import Page, Frame, Cookie
from .datas import NavigationLink
from typing import Any, Dict, List
from urllib.parse import urlparse
from urllib.parse import urlparse, urlunparse

class CheckSiteAccessResponse(BaseModel):
    accessible: bool
    final_url: Optional[str] = None
    status_code: Optional[int] = None
    error: Optional[str] = None

def ensure_https(raw_url: str) -> str:
    if not raw_url.startswith(("http://", "https://")):
        return "https://" + raw_url
    return raw_url

def is_aria_403(aria_snapshot: dict) -> bool:
    """
    Heuristic check on ARIA snapshot to detect 403/Forbidden page,
    ignoring hidden or non-visible nodes.
    """
    if not aria_snapshot:
        return False

    forbidden_keywords = [
        "forbidden",
        "access denied",
        "not authorized",
        "authentication required",
        "unauthorized",
        "403",
        "you don't have permission"
    ]

    def search_node(node: dict) -> bool:
        # Skip hidden nodes
        if node.get("hidden") or node.get("visible") is False:
            return False

        name = (node.get("name") or "").lower()
        role = (node.get("role") or "").lower()
        description = (node.get("description") or "").lower()
        combined_text = f"{name} {description} {role}"

        if any(keyword in combined_text for keyword in forbidden_keywords):
            return True

        for child in node.get("children", []):
            if search_node(child):
                return True
        return False

    return search_node(aria_snapshot)

    
def extract_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc  # returns 'app.example.com'

async def extract_navigation_links_from_page(page: Page) -> List[NavigationLink]:
    raw_links = await page.evaluate(
        """
(() => {
    function getRole(el) {
        return el.getAttribute('role') || el.tagName.toLowerCase();
    }

    function normalizeUrl(u) {
        try {
            const url = new URL(u, window.location.href);
            return url.pathname + url.search;
        } catch {
            return null;
        }
    }

    function getVisualDepth(el) {
        let depth = 0;
        while (el && el !== document.body) {
            depth++;
            el = el.parentElement;
        }
        return depth;
    }

    function getSemanticDepth(el) {
        let depth = 0;
        while (el && el !== document.body) {
            if (['NAV', 'MAIN', 'SECTION', 'ASIDE', 'HEADER', 'FOOTER'].includes(el.tagName)) {
                depth++;
            }
            el = el.parentElement;
        }
        return depth;
    }

    function getContainerType(el) {
        while (el && el !== document.body) {
            const tag = el.tagName.toLowerCase();
            if (['nav', 'main', 'section', 'aside', 'header', 'footer', 'dialog'].includes(tag)) {
                return tag;
            }
            el = el.parentElement;
        }
        return 'unknown';
    }

    function getArea(containerType) {
        switch (containerType) {
            case 'nav':
            case 'header':
                return 'topNav';
            case 'footer':
                return 'footer';
            case 'aside':
                return 'sidebar';
            case 'dialog':
                return 'modal';
            case 'main':
            case 'section':
                return 'mainContent';
            default:
                return 'uncategorized';
        }
    }

    const jsSnippets = [
        /window\\.location\\.href\\s*=\\s*['"]([^'"]+)['"]/,
        /location\\.assign\\(\\s*['"]([^'"]+)['"]\\s*\\)/,
        /navigate\\(\\s*['"]([^'"]+)['"]\\s*\\)/,
        /router\\.push\\(\\s*['"]([^'"]+)['"]\\s*\\)/,
        /router\\.replace\\(\\s*['"]([^'"]+)['"]\\s*\\)/,
        /this\\.\\$router\\.push\\(\\s*['"]([^'"]+)['"]\\s*\\)/,
        /this\\.\\$router\\.replace\\(\\s*['"]([^'"]+)['"]\\s*\\)/,
        /\\.href\\s*=\\s*['"]([^'"]+)['"]/,
        /navigateTo\\(\\s*['"]([^'"]+)['"]\\s*\\)/
    ];

    const results = [];

    const elements = Array.from(document.querySelectorAll('a, button, [onclick], [role="link"], [role="button"]'))
        .filter(el => el.offsetParent !== null);

    for (const el of elements) {
        let normalizedUrl = null;

        if (el.tagName.toLowerCase() === 'a' && el.href) {
            normalizedUrl = normalizeUrl(el.getAttribute('href'));
        } else {
            const onclick = el.getAttribute('onclick') || '';
            const outerHTML = el.outerHTML;

            for (const re of jsSnippets) {
                const match = onclick.match(re) || outerHTML.match(re);
                if (match) {
                    normalizedUrl = normalizeUrl(match[1]);
                    if (normalizedUrl) break;
                }
            }
        }

        if (normalizedUrl) {
            const containerType = getContainerType(el);
            const area = getArea(containerType);

            results.push({
                normalizedUrl,
                elementType: el.tagName.toLowerCase(),
                label: el.innerText.trim(),
                role: getRole(el),
                visible: true,
                semanticDepth: getSemanticDepth(el),
                visualDepth: getVisualDepth(el),
                containerType,
                area
            });
        }
    }

    return results;
})()
        """
    )

    return [NavigationLink(**link) for link in raw_links]


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    # Normalize the path (remove trailing slash) and remove query & fragment
    normalized_path = parsed.path.rstrip('/')
    canonical = urlunparse((parsed.scheme, parsed.netloc, normalized_path, '', '', ''))
    return canonical

def get_endpoint_key(method: str, url: str) -> str:
    return f"{method.upper()} {canonicalize_url(url)}"

def get_normalized_url(url:str | None)->str:
    if(not url):
        return ""
    return url.removeprefix("https://").removeprefix("http://")