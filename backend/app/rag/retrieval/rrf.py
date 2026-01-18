from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    results_list: List[List[Dict[str, Any]]],
    k: int = 60,
    top_k: int = None,
) -> List[Dict[str, Any]]:
    """Reciprocal Rank Fusion (RRF) for combining multiple ranked result lists

    RRF combines multiple ranked lists by summing reciprocal ranks:
    score = sum(1 / (k + rank_i)) for each result

    Args:
        results_list: List of result lists to combine
            Each result dict should have 'document_id' and 'score'
        k: RRF constant (higher k = more weight to higher ranks)
        top_k: Number of top results to return

    Returns:
        Combined and sorted list of unique results
    """
    if not results_list:
        return []

    # Initialize score map
    score_map: Dict[str, float] = {}

    # Process each result list
    for results in results_list:
        for rank, result in enumerate(results):
            doc_id = result.get("document_id")
            if doc_id is None:
                continue

            # Calculate RRF score
            rrf_score = 1.0 / (k + rank + 1)

            # Add to score map
            if doc_id in score_map:
                score_map[doc_id] += rrf_score
            else:
                score_map[doc_id] = rrf_score

    # Convert to list of results
    combined = []
    for doc_id, score in score_map.items():
        # Find the first result with this document_id to get metadata
        metadata = None
        for results in results_list:
            for result in results:
                if result.get("document_id") == doc_id:
                    metadata = {k: v for k, v in result.items() if k != "score"}
                    break
            if metadata:
                break

        combined.append({
            "document_id": doc_id,
            "score": score,
            **metadata,
        })

    # Sort by RRF score (descending)
    combined.sort(key=lambda x: x["score"], reverse=True)

    # Apply top_k limit
    if top_k is not None:
        combined = combined[:top_k]

    return combined


def weighted_score_fusion(
    results_list: List[List[Dict[str, Any]]],
    weights: List[float] = None,
    top_k: int = None,
) -> List[Dict[str, Any]]:
    """Weighted Score Fusion (WSF) for combining multiple result lists

    WSF normalizes scores and combines them with weights:
    normalized_score = (score - min) / (max - min)
    combined_score = sum(weight * normalized_score)

    Args:
        results_list: List of result lists to combine
            Each result dict should have 'document_id' and 'score'
        weights: List of weights for each result list (defaults to equal weights)
        top_k: Number of top results to return

    Returns:
        Combined and sorted list of unique results
    """
    if not results_list:
        return []

    if weights is None:
        weights = [1.0] * len(results_list)

    if len(weights) != len(results_list):
        raise ValueError("Number of weights must match number of result lists")

    # Initialize score map
    score_map: Dict[str, Dict[str, Any]] = {}

    # Normalize and combine scores
    for i, results in enumerate(results_list):
        if not results:
            continue

        # Find min and max for normalization
        scores = [r.get("score", 0) for r in results]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score

        if score_range == 0:
            # All scores are the same
            normalized_scores = [1.0] * len(results)
        else:
            normalized_scores = [
                (score - min_score) / score_range
                for score in scores
            ]

        # Combine with weights
        weight = weights[i]
        for result, norm_score in zip(results, normalized_scores):
            doc_id = result.get("document_id")
            if doc_id is None:
                continue

            weighted_score = weight * norm_score

            if doc_id in score_map:
                score_map[doc_id]["score"] += weighted_score
                score_map[doc_id]["rank"] = min(
                    score_map[doc_id]["rank"],
                    result.get("rank", 0)
                )
            else:
                metadata = {k: v for k, v in result.items() if k != "score"}
                score_map[doc_id] = {
                    "document_id": doc_id,
                    "score": weighted_score,
                    "rank": result.get("rank", 0),
                    **metadata,
                }

    # Convert to list and sort
    combined = list(score_map.values())
    combined.sort(key=lambda x: x["score"], reverse=True)

    # Apply top_k limit
    if top_k is not None:
        combined = combined[:top_k]

    return combined


def deduplicate_results(
    results: List[Dict[str, Any]],
    key: str = "document_id",
) -> List[Dict[str, Any]]:
    """Remove duplicate results keeping the highest scored one

    Args:
        results: List of results to deduplicate
        key: Key to use for deduplication

    Returns:
        Deduplicated results
    """
    seen: Dict[str, Dict[str, Any]] = {}

    for result in results:
        doc_id = result.get(key)
        if doc_id is None:
            continue

        if doc_id in seen:
            # Keep the one with higher score
            if result.get("score", 0) > seen[doc_id].get("score", 0):
                seen[doc_id] = result
        else:
            seen[doc_id] = result

    return list(seen.values())
