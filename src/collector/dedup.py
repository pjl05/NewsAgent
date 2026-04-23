from typing import List, Dict, Any


def deduplicate_content(all_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """基于 content_id 去重"""
    seen_ids: set[str] = set()
    unique_content: List[Dict[str, Any]] = []

    for item in all_content:
        content_id = item.get("content_id")
        if content_id and content_id not in seen_ids:
            seen_ids.add(content_id)
            unique_content.append(item)

    return unique_content