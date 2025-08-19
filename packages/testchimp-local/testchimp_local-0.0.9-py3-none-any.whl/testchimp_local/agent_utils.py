from typing import List, Dict, Any
from .datas import ViewportNickname,BugCaptureForCategory,BugCaptureReport,ScreenTestScenarioResultList,TestLocation,TestScenarioResultList,BugCategory,Bug,ScreenDetail,ScreenStateDetail,ExplorationResult,ScreenStates,ExistingScreenStateMap,AppMindMap,ScreenState,ExplorationStatus,Journey,ExplorationTask,ExplorationConfig,RecordingMetadata,JourneyExecutionStatus
from urllib.parse import urlparse
from enum import Enum,IntEnum
from typing import Optional
import hashlib
from typing import Any
import re
from bs4 import BeautifulSoup, Comment
from collections import deque
from browser_use.browser.views import BrowserStateSummary, BrowserStateHistory
from typing import List, Dict, Any, Tuple
from browser_use.agent.views import (AgentOutput)
from playwright.async_api import Page
import re
import json
from typing import Dict, List, Any, Optional, Union
from collections import defaultdict

def calculate_bug_hash(bug: Bug) -> str:
    data = f"{bug.category or ''}:{bug.severity or ''}:{bug.rule or ''}:{bug.location or ''}:{bug.screen or ''}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def clean_app_mind_map(app_mind_map: AppMindMap) -> AppMindMap:
    # Extract input value combinations
    combos = app_mind_map.inputValueCombinations

    # Clean the screens by removing unwanted properties from the states
    cleaned_screens = [
        ScreenDetail(
            name=screen.name,
            url=screen.url,
            isInitialScreen=screen.isInitialScreen,
            type=screen.type,
            description=screen.description,     
            displayMetadata=None,
            states=[
                ScreenStateDetail(
                    state=state.state,
                    screenshotUrl=None,
                    sourceMap=None
                ) for state in screen.states
            ],
            explorationStatus=screen.explorationStatus,
            significance=screen.significance,
            tags=screen.tags
        ) for screen in app_mind_map.screens
    ]

    # If there are input value combinations, find the "best" one
    if combos:
        # Find the input value combination with the maximum number of keys
        best_combination = max(combos, key=lambda item: len(item.input_values) if item.input_values else 0)

        # Return a cleaned AppMindMap with the best input combination
        return AppMindMap(
            screens=cleaned_screens,
            appDetail=app_mind_map.appDetail,
            inputValueCombinations=[best_combination],
            initialUrl=app_mind_map.initialUrl
        )

    # Return the cleaned AppMindMap without input value combinations
    return AppMindMap(
        screens=cleaned_screens,
        appDetail=app_mind_map.appDetail,
        inputValueCombinations=[],
        initialUrl=app_mind_map.initialUrl
    )


def is_valid_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"]
    except Exception:
        return False


def get_bug_category(category: Optional[str]) -> BugCategory:
    if not category:
        return BugCategory.OTHER

    normalized_category = category.strip().upper()

    category_map = {
        "UNKNOWN_BUG_CATEGORY": BugCategory.UNKNOWN_BUG_CATEGORY,
        "OTHER": BugCategory.OTHER,
        "ACCESSIBILITY": BugCategory.ACCESSIBILITY,
        "SECURITY": BugCategory.SECURITY,
        "VISUAL": BugCategory.VISUAL,
        "PERFORMANCE": BugCategory.PERFORMANCE,
        "FUNCTIONAL": BugCategory.FUNCTIONAL,
        "NETWORK": BugCategory.NETWORK,
        "USABILITY": BugCategory.USABILITY,
        "COMPATIBILITY": BugCategory.COMPATIBILITY,
        "DATA_INTEGRITY": BugCategory.DATA_INTEGRITY,
        "INTERACTION": BugCategory.INTERACTION,
        "LOCALIZATION": BugCategory.LOCALIZATION,
        "RESPONSIVENESS": BugCategory.RESPONSIVENESS,
        "LAYOUT": BugCategory.LAYOUT,
    }

    return category_map.get(normalized_category, BugCategory.OTHER)

def get_screen_state_hash(screen_state:ScreenState)->str:
    return f'{screen_state.name}|{screen_state.state}'

async def get_llm_friendly_dom(page: Page) -> str:
    """
    Extract a token-efficient representation of the DOM from a Playwright page object.
    The output is optimized for LLM analysis of visual layout, accessibility, and usability issues.
    Paths are excluded to reduce token usage and focus on meaningful content.
    
    Args:
        page: A Playwright page object representing the loaded webpage
        
    Returns:
        A string containing the structured DOM representation
    """
    # Execute JavaScript in the page to extract relevant DOM information using an iterative approach
    dom_data = await page.evaluate("""() => {
        // Helper function to check if element is visible
        function isElementVisible(el) {
            if (!el.getBoundingClientRect) return false;
            
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                return false;
            }
            
            const rect = el.getBoundingClientRect();
            // Element has zero size
            if (rect.width === 0 || rect.height === 0) {
                return false;
            }
            
            return true;
        }
        
        // Function to get accessible name
        function getAccessibleName(el) {
            // Check various attributes and properties used for accessibility
            return el.getAttribute('aria-label') || 
                   el.getAttribute('alt') || 
                   el.getAttribute('title') ||
                   (el.hasAttribute('aria-labelledby') ? 
                       document.getElementById(el.getAttribute('aria-labelledby'))?.textContent : null) ||
                   null;
        }
        
        // Get computed contrast ratio for text elements
        function getContrastInfo(el) {
            if (!['P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'SPAN', 'A', 'BUTTON', 'LABEL'].includes(el.tagName)) {
                return null;
            }
            
            const style = window.getComputedStyle(el);
            const bgColor = style.backgroundColor;
            const textColor = style.color;
            
            // Only include if the colors seem meaningful
            if (bgColor === 'rgba(0, 0, 0, 0)' || textColor === 'rgb(0, 0, 0)') {
                return null;
            }
            
            return {
                textColor: textColor,
                bgColor: bgColor
            };
        }
        
        // Non-recursive approach to process DOM
        function processDOM() {
            const result = [];
            const nodesToProcess = [{node: document.documentElement, depth: 0, path: '/html'}];
            const MAX_DEPTH = 10; // Limit depth to keep token count reasonable
            const MAX_ELEMENTS = 500; // Limit total elements
            let processedCount = 0;
            
            while (nodesToProcess.length > 0 && processedCount < MAX_ELEMENTS) {
                const {node, depth} = nodesToProcess.shift();
                processedCount++;
                
                // Skip processing if too deep
                if (depth > MAX_DEPTH) continue;
                
                // Skip comment nodes, script tags, style tags, and svg internals
                if (node.nodeType === Node.COMMENT_NODE ||
                    node.nodeName === 'SCRIPT' ||
                    node.nodeName === 'STYLE' ||
                    node.nodeName === 'NOSCRIPT' ||
                    (node.nodeName !== 'SVG' && node.namespaceURI === 'http://www.w3.org/2000/svg')) {
                    continue;
                }
                
                // Skip hidden elements
                if (node.nodeType === Node.ELEMENT_NODE && !isElementVisible(node)) {
                    continue;
                }
                
                // Process text nodes
                if (node.nodeType === Node.TEXT_NODE) {
                    const text = node.textContent.trim();
                    if (text) {
                        result.push({
                            type: 'text',
                            content: text.length > 100 ? text.substring(0, 100) + '...' : text
                        });
                    }
                    continue;
                }
                
                // Process element nodes
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const elementInfo = {
                        tag: node.nodeName.toLowerCase()
                    };
                    
                    // Add important attributes for accessibility and styling
                    const importantAttrs = ['id', 'class', 'role', 'aria-label', 'aria-labelledby', 
                                           'aria-describedby', 'aria-hidden', 'tabindex', 'alt', 'title'];
                    
                    const attrs = {};
                    for (const attr of importantAttrs) {
                        if (node.hasAttribute(attr)) {
                            // Truncate class names if too long
                            if (attr === 'class') {
                                const classes = node.getAttribute(attr).split(' ');
                                if (classes.length > 3) {
                                    attrs[attr] = classes.slice(0, 3).join(' ') + ' ...';
                                } else {
                                    attrs[attr] = node.getAttribute(attr);
                                }
                            } else {
                                attrs[attr] = node.getAttribute(attr);
                            }
                        }
                    }
                    
                    // Add tag-specific important attributes
                    if (node.nodeName === 'A') {
                        attrs['href'] = node.getAttribute('href');
                    } else if (node.nodeName === 'IMG') {
                        attrs['src'] = node.getAttribute('src')?.split('/').pop() || 'image';
                        attrs['alt'] = node.getAttribute('alt');
                    } else if (['INPUT', 'BUTTON', 'SELECT', 'TEXTAREA'].includes(node.nodeName)) {
                        attrs['type'] = node.getAttribute('type');
                        attrs['placeholder'] = node.getAttribute('placeholder');
                        attrs['required'] = node.hasAttribute('required');
                        attrs['disabled'] = node.hasAttribute('disabled');
                    }
                    
                    // Only add attributes if there are any
                    if (Object.keys(attrs).length > 0) {
                        elementInfo.attributes = attrs;
                    }
                    
                    // Add accessibility information
                    const accessibleName = getAccessibleName(node);
                    if (accessibleName) {
                        elementInfo.a11yName = accessibleName;
                    }
                    
                    // Add ARIA attributes
                    const ariaAttrs = {};
                    for (const attr of node.getAttributeNames()) {
                        if (attr.startsWith('aria-') && !importantAttrs.includes(attr)) {
                            ariaAttrs[attr] = node.getAttribute(attr);
                        }
                    }
                    if (Object.keys(ariaAttrs).length > 0) {
                        elementInfo.aria = ariaAttrs;
                    }
                    
                    // Add positioning data for layout analysis
                    if (node.getBoundingClientRect) {
                        const rect = node.getBoundingClientRect();
                        const viewport = {
                            width: window.innerWidth,
                            height: window.innerHeight
                        };
                        
                        // Only include position if element is visible
                        if (rect.width > 0 && rect.height > 0) {
                            elementInfo.position = {
                                x: Math.round(rect.left),
                                y: Math.round(rect.top),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                inViewport: (
                                    rect.top >= 0 && 
                                    rect.left >= 0 && 
                                    rect.bottom <= viewport.height &&
                                    rect.right <= viewport.width
                                )
                            };
                        }
                    }
                    
                    // Add contrast information for text elements
                    const contrast = getContrastInfo(node);
                    if (contrast) {
                        elementInfo.contrast = contrast;
                    }
                    
                    // For leaf nodes with text, add the text content
                    if (node.childNodes.length === 0 || 
                        (node.childNodes.length === 1 && node.firstChild.nodeType === Node.TEXT_NODE)) {
                        const text = node.textContent.trim();
                        if (text) {
                            elementInfo.text = text.length > 100 ? text.substring(0, 100) + '...' : text;
                        }
                    }
                    
                    // Add the element to our result
                    result.push(elementInfo);
                    
                    // Queue child nodes for processing (in reverse to maintain document order when using shift())
                    const childElements = Array.from(node.childNodes);
                    for (let i = 0; i < childElements.length; i++) {
                        const child = childElements[i];
                        nodesToProcess.unshift({
                            node: child, 
                            depth: depth + 1
                        });
                    }
                }
            }
            
            return result;
        }
        
        // Get page metadata
        const metadata = {
            title: document.title,
            url: window.location.href,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
        
        // Process the DOM iteratively
        const domElements = processDOM();
        
        // Gather key headings for page structure
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => {
            return {
                level: parseInt(h.tagName.charAt(1)),
                text: h.textContent.trim(),
                id: h.id || null
            };
        }).slice(0, 20); // Limit to 20 headings
        
        // Get meta tags for SEO and description
        const metaTags = {};
        document.querySelectorAll('meta').forEach(meta => {
            const name = meta.getAttribute('name') || meta.getAttribute('property');
            const content = meta.getAttribute('content');
            if (name && content) {
                metaTags[name] = content;
            }
        });
        
        // Get color palette information
        const colors = {
            background: window.getComputedStyle(document.body).backgroundColor,
        };
        
        // Get font information
        const fontInfo = {
            bodyFont: window.getComputedStyle(document.body).fontFamily,
            bodySize: window.getComputedStyle(document.body).fontSize
        };
        
        // Count elements by type for summary
        const elementCounts = {};
        document.querySelectorAll('*').forEach(el => {
            const tag = el.tagName.toLowerCase();
            elementCounts[tag] = (elementCounts[tag] || 0) + 1;
        });
        
        return {
            metadata,
            headings,
            metaTags,
            colors,
            fontInfo,
            elementCounts,
            domElements
        };
    }""")
    
    # Format the DOM data as a JSON string
    dom_json = json.dumps(dom_data, indent=None)
    
    # Create a summary to put at the beginning
    summary = f"""Page: {dom_data['metadata']['title']} ({dom_data['metadata']['url']})
Viewport: {dom_data['metadata']['viewport']['width']}x{dom_data['metadata']['viewport']['height']}
Main Font: {dom_data['fontInfo']['bodyFont']} at {dom_data['fontInfo']['bodySize']}
Element Count: {sum(dom_data['elementCounts'].values())} total elements
"""
    
    # Add top element types
    top_elements = sorted(dom_data['elementCounts'].items(), key=lambda x: x[1], reverse=True)[:10]
    summary += "Top elements: " + ", ".join([f"{tag}: {count}" for tag, count in top_elements]) + "\n\n"
    
    # Add headings as a table of contents
    if dom_data['headings']:
        summary += "Page Structure:\n"
        for h in dom_data['headings']:
            summary += f"{'  ' * (h['level']-1)}• {h['text']}\n"
        summary += "\n"
    
    # Add important meta tags
    important_meta = ['description', 'keywords', 'viewport', 'og:title', 'og:description']
    meta_summary = {k: v for k, v in dom_data['metaTags'].items() if k in important_meta}
    if meta_summary:
        summary += f"Meta Tags:\n{json.dumps(meta_summary, indent=2)}\n\n"
        
    # Return the combined summary and DOM data
    return summary + "DOM Elements:\n" + dom_json





def extract_actions_and_selector_map(agent_output: AgentOutput, current_browser_state: BrowserStateSummary) -> tuple[list[Any], dict[int, dict[str, Any]]]:
    """
    Given an AgentOutput and the current BrowserStateSummary, returns:
    - The list of root action model objects (e.g., InputTextActionModel, ClickElementByIndexActionModel, etc.)
    - A filtered selector map: {index: {tag_name, attributes, shadow_root, is_interactive, is_top_element, is_in_viewport, highlight_index}}
      Only for indices referenced by actions in agent_output.
    """
    actual_actions = []
    used_indices = set()

    for action_model in agent_output.action:
        # Extract the root action model (e.g., InputTextActionModel, ClickElementByIndexActionModel, etc.)
        root_action = getattr(action_model, 'root', None)
        if root_action is not None:
            actual_actions.append(root_action)
            index = None
            if hasattr(root_action, 'get_index'):
                index = root_action.get_index()
            elif hasattr(action_model, 'get_index'):
                # fallback to ActionModel.get_index if root doesn't have it
                index = action_model.get_index()
            if index is not None:
                used_indices.add(index)
        else:
            # fallback: if no root, add the action_model itself
            actual_actions.append(action_model)
            if hasattr(action_model, 'get_index'):
                index = action_model.get_index()
                if index is not None:
                    used_indices.add(index)

    filtered_selector_map = {}
    for index, node in current_browser_state.selector_map.items():
        if index in used_indices:
            filtered_selector_map[index] = {
                "tag_name": getattr(node, "tag_name", None),
                "attributes": getattr(node, "attributes", None),
                "shadow_root": getattr(node, "shadow_root", None),
                "is_interactive": getattr(node, "is_interactive", None),
                "is_top_element": getattr(node, "is_top_element", None),
                "is_in_viewport": getattr(node, "is_in_viewport", None),
                "highlight_index": getattr(node, "highlight_index", None),
            }

    return actual_actions, filtered_selector_map

def get_node_fingerprint(node) -> tuple:
    attrs = node.attributes or {}
    class_list = attrs.get("class", "").split()

    return (
        node.tag_name,
        attrs.get("id"),
        attrs.get("role"),
        attrs.get("type"),
        tuple(sorted(class_list)),
        node.is_interactive,
        node.is_top_element,
        node.is_in_viewport,
        node.shadow_root,
    )

def has_ui_likely_changed(prev: BrowserStateSummary, current: BrowserStateSummary) -> bool:
    if not prev:
        return True

    # Simple checks first
    if prev.url != current.url or prev.title != current.title:
        return True

    # Collect semantic fingerprints
    prev_fingerprints = set(get_node_fingerprint(node) for node in prev.selector_map.values())
    curr_fingerprints = set(get_node_fingerprint(node) for node in current.selector_map.values())

    added = curr_fingerprints - prev_fingerprints
    removed = prev_fingerprints - curr_fingerprints

    # Allow small changes like input typing: tolerate minor deltas (e.g., <2 node diffs)
    if len(added) + len(removed) > 2:
        return True

    return False

def filter_test_scenarios_by_location(
    test_scenario_results: TestScenarioResultList,
    location: TestLocation
) -> TestScenarioResultList:
    filtered_screens = []

    for screen in test_scenario_results.screenScenarios or []:
        if location.screenName and screen.screenName != location.screenName:
            continue  # skip if screen name doesn't match

        if location.screenState:
            # filter stateScenarios within matching screen
            filtered_states = [
                state for state in screen.stateScenarios or []
                if state.stateName == location.screenState
            ]
            if filtered_states:
                filtered_screens.append(ScreenTestScenarioResultList(
                    screenName=screen.screenName,
                    stateScenarios=filtered_states
                ))
        else:
            # no state specified, include entire screen
            filtered_screens.append(screen)

    return TestScenarioResultList(screenScenarios=filtered_screens)

def get_bug_capture_report(bugs: List[Bug]) -> BugCaptureReport:
    category_map: Dict[str, List[Bug]] = defaultdict(list)

    # Group bugs by category
    for bug in bugs:
        category = bug.category or "OTHER"
        category_map[category].append(bug)

    # Sort bugs within each category by severity (high to low) and then by description
    category_reports: List[BugCaptureForCategory] = []
    for category, bug_list in category_map.items():
        bug_list.sort(key=lambda b: (-(b.severity or 0), b.description or ""))
        category_reports.append(BugCaptureForCategory(category=category, bugs=bug_list))

    return BugCaptureReport(categoryReport=category_reports)

VIEWPORT_PRESETS = {
    ViewportNickname.LAPTOP: {"width": 1366, "height": 768},
    ViewportNickname.WIDESCREEN: {"width": 1920, "height": 1080},
    ViewportNickname.MOBILE: {"width": 375, "height": 812},
    ViewportNickname.TABLET: {"width": 768, "height": 1024},
}