"""An entity deduplication algorithm that uses a combination of fuzzy string matching, vector embeddings, and LLM-based selection to identify duplicates in a list of entities."""

# %% top_export
import inspect
from pydantic import BaseModel
from typing import Optional
from adulib.algos.str_matching import fuzzy_match, get_vector_dist_matrix, embedding_match
from adulib.llm import async_batch_embeddings
import rapidfuzz
from tqdm.asyncio import tqdm_asyncio
import asyncio

# %% top_export
default_system_prompt = inspect.cleandoc("""
You are an expert in entity deduplication. You will be shown a string and a list of similar-looking strings (some may be aliases, abbreviations, misspellings, or closely related variants, while others may be unrelated).

Your task is to identify which strings refer to the same entity as the reference. Return a Python list of **0-based indices** corresponding to the matching entries. Only include strings that could realistically refer to the same entity. Do not include unrelated strings. Do not explain your reasoning. If no strings match, return an empty list.
""".strip())

default_prompt_template = inspect.cleandoc("""
Entity: {entity}

Entity duplicate candidates:
{duplicate_candidates}
""".strip())

class Duplicates(BaseModel):
    duplicate_indices: list[int]

# %% top_export
async def select_duplicates(entity: str, duplicate_candidates: list[str], model, temperature, system_prompt, prompt_template):
    """
    Use an LLM to select which candidates from a list are duplicates of a given entity.

    Args:
        entity (str): The reference entity string.
        duplicate_candidates (list[str]): List of candidate strings to check for duplication.
        model: The LLM model to use.
        temperature: Sampling temperature for the LLM.

    Returns:
        tuple: (indices of matches in duplicate_candidates, matched candidate strings)
    """
    import adulib.llm
    import json
    
    duplicate_candidates = sorted(set(duplicate_candidates)) # This ensures consistent caching.

    res, cache_hit, call_log = await adulib.llm.async_single(
        model=model,
        system=system_prompt,
        prompt=prompt_template.format(
            entity=entity,
            duplicate_candidates="\n".join([f"{i}. {m}" for i, m in enumerate(duplicate_candidates, start=0)]),
        ),
        temperature=temperature,
        response_format=Duplicates,
    )
    
    match_indices = Duplicates(**json.loads(res)).duplicate_indices
    dup_indices = [duplicate_candidates.index(duplicate_candidates[i]) for i in match_indices]
    dup_strings = [duplicate_candidates[i] for i in match_indices]
    return dup_indices, dup_strings

# %% top_export
def find_disconnected_subgraphs(matches):
    """
    Given a list of pairwise matches (edges), find all disconnected subgraphs (connected components).

    Args:
        matches (list of tuple): List of pairs representing edges between nodes.

    Returns:
        list of set: Each set contains the nodes in one connected component.
    """
    from collections import defaultdict

    # Create a graph from the matches
    graph = defaultdict(set)
    for item1, item2 in matches:
        graph[item1].add(item2)
        graph[item2].add(item1)

    visited = set()
    subgraphs = []

    def dfs(node, current_subgraph):
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                current_subgraph.add(current)
                stack.extend(graph[current] - visited)

    # Find all disconnected subgraphs
    for node in graph:
        if node not in visited:
            current_subgraph = set()
            dfs(node, current_subgraph)
            subgraphs.append(current_subgraph)
            
    subgraphs = sorted([tuple(sorted(subgraph)) for subgraph in subgraphs]) # Sorting ensures consistent output

    return subgraphs

async def smart_dedup(
    entities: list[str],
    embedding_model: str,
    match_selection_model: str,
    max_fuzzy_str_matches: int = 5,
    min_fuzzy_str_match_score: float = 0,
    fuzzy_str_match_scorer=rapidfuzz.fuzz.ratio,
    num_embedding_matches: int = 5,
    embedding_batch_size: int = 1000,
    match_selection_temperature: float = 0.0,
    system_prompt: str = None,
    prompt_template: str = None,
    entity_embeddings: Optional[list[list[float]]] = None,
    use_fuzzy_str_matching: bool = True,
    use_embedding_matching: bool = True,
    verbose: bool = False,
):
    """
    Entity deduplication of a list of strings using fuzzy string matching and embedding-based similarity, 
    followed by model-assisted duplicate selection.
    
    Args:
        entities (list[str]): List of entity strings to deduplicate.
        embedding_model (str): Name or path of the embedding model to use.
        match_selection_model (str): Model identifier for selecting matches among candidates.
        max_fuzzy_str_matches (int, optional): Maximum number of fuzzy string match candidates per entity. Defaults to 5.
        min_fuzzy_str_match_score (float, optional): Minimum similarity score for fuzzy string matches. Defaults to 0.
        fuzzy_str_match_scorer (callable, optional): Scoring function for fuzzy string matching. Defaults to rapidfuzz.fuzz.ratio.
        num_embedding_matches (int, optional): Number of embedding-based match candidates per entity. Defaults to 5.
        embedding_batch_size (int, optional): Batch size for embedding computation. Defaults to 1000.
        match_selection_temperature (float, optional): Temperature parameter for match selection model. Defaults to 0.0.
        system_prompt (str, optional): Optional system prompt for the match selection model.
        prompt_template (str, optional): Optional prompt template for the match selection model.
        entity_embeddings (list[list[float]], optional): Precomputed embeddings for entities. If None, embeddings will be computed. Defaults to None.
        use_fuzzy_str_matching (bool, optional): If True, uses fuzzy string matching to find potential duplicates. Defaults to True.
        use_embedding_matching (bool, optional): If True, uses embedding-based matching to find potential
        verbose (bool, optional): If True, displays progress bars and additional output. Defaults to False.
        
    Returns:
        tuple[list[list[tuple[str, str]]], list[str]]:
            - List of disconnected subgraphs, each representing a group of duplicate entities.
            - List of entities without any detected matches.
    Notes:
        See `adulib.algos._dedup.system_prompt` and `adulib.algos._dedup.prompt_template` for prompt details.
    """
    
    """An entity deduplication algorithm that uses a combination of fuzzy string matching, vector embeddings, and LLM-based selection to identify duplicates in a list of entities."""
    
    # AUTOGENERATED! DO NOT EDIT! File to edit: ../../../../../../../../../Users/lukastk/dev/2025-03-25_00__adulib/pts/api/algos/01_smart_dedup.pct.py.
    
    # %% auto 0
    __all__ = ['entities', 'system_prompt', 'prompt_template', 'tasks', 'matches', 'entities_without_matches']
    
    # %% ../../../../../../../../../Users/lukastk/dev/2025-03-25_00__adulib/pts/api/algos/01_smart_dedup.pct.py 8
    _entities = set(entities)
    entities = list(_entities)
    
    # %% ../../../../../../../../../Users/lukastk/dev/2025-03-25_00__adulib/pts/api/algos/01_smart_dedup.pct.py 10
    if use_fuzzy_str_matching:
        fuzzy_match_candidates = [
            [
                candidate for candidate, _, _, in
                fuzzy_match(entity, _entities - {entity}, max_results=max_fuzzy_str_matches, min_similarity=min_fuzzy_str_match_score, scorer=fuzzy_str_match_scorer)
            ] for entity in entities
        ]
    else:
        fuzzy_match_candidates = [
            [] for _ in range(len(entities))
        ]
    
    # %% ../../../../../../../../../Users/lukastk/dev/2025-03-25_00__adulib/pts/api/algos/01_smart_dedup.pct.py 12
    if use_embedding_matching:
        if entity_embeddings is None:
            embeddings, _ = await async_batch_embeddings(
                model=embedding_model,
                input=entities,
                batch_size=1000,
                verbose=verbose,
            )
        else:
            if len(entity_embeddings) != len(entities):
                raise ValueError("Length of entity_embeddings must match length of entities.")
            embeddings = entity_embeddings  
    
        dist_matrix = get_vector_dist_matrix(embeddings, metric='cosine')
    
        embedding_match_candidates = [
            [entities[match_i] for match_i in embedding_match(i, dist_matrix, num_matches=num_embedding_matches)[0]]
            for i in range(len(entities))
        ]
    else:
        embedding_match_candidates = [
            [] for _ in range(len(entities))
        ]
    
    # %% ../../../../../../../../../Users/lukastk/dev/2025-03-25_00__adulib/pts/api/algos/01_smart_dedup.pct.py 16
    system_prompt = system_prompt or default_system_prompt
    prompt_template = prompt_template or default_prompt_template
    
    tasks = [
        select_duplicates(entity, set(fuzzy_candidates+embedding_candidates), match_selection_model, match_selection_temperature,
                          system_prompt=system_prompt, prompt_template=prompt_template)
        for entity, fuzzy_candidates, embedding_candidates in zip(entities, fuzzy_match_candidates, embedding_match_candidates)
    ]
    
    if verbose:
        results = await tqdm_asyncio.gather(*tasks, desc="Selecting duplicates", total=len(tasks))
    else:
        results = await asyncio.gather(*tasks)
      
    matches = []  
    entities_without_matches = []
    for entity, (dup_indices, dup_strings) in zip(entities, results):
        matches.extend([(entity, matched_entity) for matched_entity in dup_strings])
        if len(dup_strings) == 0:
            entities_without_matches.append(entity)
    return find_disconnected_subgraphs(matches), entities_without_matches