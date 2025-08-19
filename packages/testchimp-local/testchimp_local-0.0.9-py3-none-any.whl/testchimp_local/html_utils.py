import logging
from typing import Dict, List, Optional, Any
from playwright.async_api import Page
import hashlib
import json

logger = logging.getLogger(__name__)

class StrippedDOM:
    """
    Represents a stripped-down version of DOM for comparison purposes.
    Contains only significant structural elements that would indicate UI changes.
    """
    def __init__(self, url: str, title: str, main_content_hash: str, 
                 navigation_elements: List[str], form_elements: List[str],
                 interactive_elements: List[str], element_count: int):
        self.url = url
        self.title = title
        self.main_content_hash = main_content_hash
        self.navigation_elements = navigation_elements
        self.form_elements = form_elements
        self.interactive_elements = interactive_elements
        self.element_count = element_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'url': self.url,
            'title': self.title,
            'main_content_hash': self.main_content_hash,
            'navigation_elements': self.navigation_elements,
            'form_elements': self.form_elements,
            'interactive_elements': self.interactive_elements,
            'element_count': self.element_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrippedDOM':
        """Create from dictionary"""
        return cls(
            url=data['url'],
            title=data['title'],
            main_content_hash=data['main_content_hash'],
            navigation_elements=data['navigation_elements'],
            form_elements=data['form_elements'],
            interactive_elements=data['interactive_elements'],
            element_count=data['element_count']
        )

async def create_stripped_dom(page: Page) -> StrippedDOM:
    """
    Creates a stripped-down version of the DOM for comparison purposes.
    Extracts only significant structural elements that would indicate UI changes.
    """
    try:
        # Get basic page info
        url = page.url
        title = await page.title()
        
        # Get main content area (focus on the most important content)
        main_content = await page.evaluate("""
            () => {
                // Try to find main content area
                const main = document.querySelector('main') || 
                           document.querySelector('[role="main"]') ||
                           document.querySelector('#main') ||
                           document.querySelector('.main') ||
                           document.body;
                
                // Get text content and structure (excluding form input values and temporary elements)
                let textContent = main.textContent || '';
                
                // Remove form input values from text content to avoid triggering on form filling
                const inputs = main.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    if (input.value) {
                        textContent = textContent.replace(input.value, '');
                    }
                });
                
                // Remove text from temporary/transient elements (tooltips, popups, etc.)
                const temporaryElements = main.querySelectorAll('.tooltip, .popup, .modal, [aria-hidden="true"], [style*="position: absolute"][style*="z-index"]');
                temporaryElements.forEach(el => {
                    if (el.textContent) {
                        textContent = textContent.replace(el.textContent, '');
                    }
                });
                
                const elementCount = main.querySelectorAll('*').length;
                
                // Get navigation elements (exclude temporary/transient elements)
                const navElements = Array.from(document.querySelectorAll('nav, [role="navigation"], .nav, .navigation, header'))
                    .filter(el => {
                        // Exclude elements that are likely temporary (tooltips, popups, etc.)
                        const style = window.getComputedStyle(el);
                        const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                        const isTemporary = el.classList.contains('tooltip') || 
                                          el.classList.contains('popup') || 
                                          el.classList.contains('modal') ||
                                          el.getAttribute('aria-hidden') === 'true';
                        return isVisible && !isTemporary && (el.textContent?.trim() || '').length > 0;
                    })
                    .map(el => el.textContent?.trim() || '');
                
                // Get form elements (excluding content changes)
                const formElements = Array.from(document.querySelectorAll('form, input, select, textarea, button'))
                    .map(el => {
                        const tag = el.tagName.toLowerCase();
                        const type = el.getAttribute('type') || '';
                        const placeholder = el.getAttribute('placeholder') || '';
                        // Don't include value/content to avoid triggering on form filling
                        return `${tag}${type ? ':' + type : ''}${placeholder ? ':' + placeholder : ''}`;
                    });
                
                // Get interactive elements (buttons, links, etc.) - exclude temporary elements
                const interactiveElements = Array.from(document.querySelectorAll('button, a, [role="button"], [tabindex]'))
                    .filter(el => {
                        // Exclude temporary/interactive elements that shouldn't trigger UI change
                        const style = window.getComputedStyle(el);
                        const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                        const isTemporary = el.classList.contains('tooltip') || 
                                          el.classList.contains('popup') || 
                                          el.classList.contains('modal') ||
                                          el.getAttribute('aria-hidden') === 'true' ||
                                          el.style.position === 'absolute' && el.style.zIndex > 1000; // Likely overlay
                        return isVisible && !isTemporary;
                    })
                    .map(el => {
                        const tag = el.tagName.toLowerCase();
                        const text = el.textContent?.trim() || '';
                        const href = el.getAttribute('href') || '';
                        return `${tag}${text ? ':' + text : ''}${href ? ':' + href : ''}`;
                    });
                
                return {
                    textContent: textContent,
                    elementCount: elementCount,
                    navElements: navElements,
                    formElements: formElements,
                    interactiveElements: interactiveElements
                };
            }
        """)
        
        # Create hash of main content for quick comparison
        main_content_text = main_content.get('textContent', '')
        main_content_hash = hashlib.md5(main_content_text.encode()).hexdigest()
        
        # Extract lists
        navigation_elements = main_content.get('navElements', [])
        form_elements = main_content.get('formElements', [])
        interactive_elements = main_content.get('interactiveElements', [])
        element_count = main_content.get('elementCount', 0)
        
        return StrippedDOM(
            url=url,
            title=title,
            main_content_hash=main_content_hash,
            navigation_elements=navigation_elements,
            form_elements=form_elements,
            interactive_elements=interactive_elements,
            element_count=element_count
        )
        
    except Exception as e:
        logger.error(f"Error creating stripped DOM: {e}")
        # Return a minimal stripped DOM on error
        return StrippedDOM(
            url=page.url,
            title="",
            main_content_hash="",
            navigation_elements=[],
            form_elements=[],
            interactive_elements=[],
            element_count=0
        )

def has_significant_ui_changes(previous_dom: StrippedDOM, current_dom: StrippedDOM) -> bool:
    """
    Determines if there are significant UI changes between two stripped DOMs.
    Uses simple heuristics to detect meaningful changes.
    """
    # 1. URL change is always significant
    if previous_dom.url != current_dom.url:
        logger.info(f"URL changed from {previous_dom.url} to {current_dom.url}")
        return True
    
    # 2. Title change is significant
    if previous_dom.title != current_dom.title:
        logger.info(f"Title changed from '{previous_dom.title}' to '{current_dom.title}'")
        return True
    
    # 3. Main content hash change indicates significant content change
    if previous_dom.main_content_hash != current_dom.main_content_hash:
        # Additional check: if the change is very small, it might be noise
        # We'll still log it but be more conservative about what we consider significant
        logger.info("Main content hash changed - checking if significant")
        
        # For now, we'll consider hash changes as significant, but in the future
        # we could add more sophisticated analysis here
        return True
    
    # 4. Significant change in element count (more than 30% difference - more conservative)
    if previous_dom.element_count > 0:
        element_count_diff = abs(current_dom.element_count - previous_dom.element_count)
        element_count_ratio = element_count_diff / previous_dom.element_count
        if element_count_ratio > 0.3:  # Increased threshold to avoid noise
            logger.info(f"Element count changed significantly: {previous_dom.element_count} -> {current_dom.element_count}")
            return True
    
    # 5. Navigation elements changed significantly (require multiple changes to avoid noise)
    nav_diff = len(set(current_dom.navigation_elements) - set(previous_dom.navigation_elements))
    if nav_diff > 1:  # Require more than 1 change to avoid noise from temporary elements
        logger.info(f"Navigation elements changed: {nav_diff} new elements")
        return True
    
    # 6. Form elements changed significantly (require multiple changes to avoid noise)
    form_diff = len(set(current_dom.form_elements) - set(previous_dom.form_elements))
    if form_diff > 1:  # Require more than 1 change to avoid noise from dynamic form updates
        logger.info(f"Form elements changed: {form_diff} new elements")
        return True
    
    # 7. Interactive elements changed significantly (more conservative threshold)
    interactive_diff = len(set(current_dom.interactive_elements) - set(previous_dom.interactive_elements))
    if interactive_diff > 3:  # Increased threshold to avoid noise from tooltips, popups, etc.
        logger.info(f"Interactive elements changed: {interactive_diff} new elements")
        return True
    
    # No significant changes detected
    return False

def serialize_stripped_dom(dom: StrippedDOM) -> str:
    """Serialize stripped DOM to string for storage"""
    return json.dumps(dom.to_dict())

def deserialize_stripped_dom(data: str) -> StrippedDOM:
    """Deserialize stripped DOM from string"""
    return StrippedDOM.from_dict(json.loads(data))

async def get_element_id_mapping(page: Page) -> dict:
    """
    Get a mapping of element IDs to their HTML for LLM context.
    Returns a dict with id -> truncated HTML mapping.
    """
    try:
        element_map = await page.evaluate("""() => {
            const elements = document.querySelectorAll('[id], [data-testid], [data-test-id]');
            const mapping = {};
            
            elements.forEach(el => {
                const id = el.id || el.getAttribute('data-testid') || el.getAttribute('data-test-id') || 
                          el.getAttribute('data-cy') || el.getAttribute('data-qa');
                
                if (id) {
                    // Get the element's HTML but exclude children to save tokens
                    const tag = el.tagName.toLowerCase();
                    const attrs = Array.from(el.attributes)
                        .map(attr => `${attr.name}="${attr.value}"`)
                        .join(' ');
                    
                    const html = `<${tag} ${attrs}>`;
                    mapping[id] = html;
                }
            });
            
            return mapping;
        }""")
        
        return element_map
    except Exception as e:
        logger.error(f"Failed to get element ID mapping: {e}")
        return {} 