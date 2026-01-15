"""AI-powered categorization of protest events using Azure OpenAI."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
from diskcache import Cache
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from tqdm.asyncio import tqdm_asyncio

load_dotenv()

# Azure OpenAI configuration from environment
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://mim-openai-superduper.openai.azure.com")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

if not AZURE_API_KEY:
    raise ValueError("AZURE_OPENAI_KEY environment variable not set")

# Initialize cache
cache_dir = Path(__file__).parent.parent.parent / "data" / "cache"
cache_dir.mkdir(parents=True, exist_ok=True)
cache = Cache(str(cache_dir))

# Load categorization schema
schema_path = Path(__file__).parent.parent.parent / "categorization_schema.json"
with open(schema_path) as f:
    SCHEMA = json.load(f)


client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
)


async def classify_event(
    topic: str,
    organizer: str | None = None,
    city: str | None = None,
) -> dict[str, Any]:
    """
    Classify a protest event using Azure OpenAI GPT-4-mini.

    Results are cached to avoid reprocessing the same events.

    Args:
        topic: The protest topic/theme
        organizer: The organizer name (optional)
        city: The city where the protest occurred (optional)

    Returns:
        Dictionary with 'groups' (list) and 'topics' (list) classifications
    """
    # Check cache first
    cache_key = f"classify_v1:{topic}:{organizer}:{city}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Create prompt
    prompt = f"""Analyze this German protest/demonstration registration and classify it.

Event details:
- Topic: {topic}
- Organizer: {organizer or "Unknown"}
- City: {city or "Unknown"}

Classification schema:
- Groups: {json.dumps([g["name"] for g in SCHEMA["groups"]], ensure_ascii=False)}
- Topics: {json.dumps([t["name"] for t in SCHEMA["topics"]], ensure_ascii=False)}

Instructions:
1. Identify any matching protest groups/organizations (can be multiple or none)
2. Identify relevant topic categories (can be multiple, typically 1-3)
3. Return ONLY a JSON object with this exact format:
{{
  "groups": ["group1", "group2"],
  "topics": ["topic1", "topic2"]
}}

Important:
- Use exact names from the schema
- Return empty lists [] if no matches
- Be inclusive - if uncertain, include the category
- Consider keyword variations and context
"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at categorizing German political demonstrations. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=200,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        # Cache the result
        cache.set(cache_key, result)
        return result

    except Exception as e:
        print(f"Error classifying event: {e}")
        return {"groups": [], "topics": []}


async def categorize_dataset(df: pd.DataFrame, max_concurrent: int = 50, save_interval: int = 1000, output_path: str | None = None) -> pd.DataFrame:
    """
    Categorize all events in a dataset using Azure OpenAI.

    Only processes events that don't have categories yet.
    Uses async processing with semaphore for rate limiting.

    Args:
        df: DataFrame with columns: topic, organizer (optional), city (optional)
        max_concurrent: Maximum concurrent API requests (default 50)
        save_interval: Save progress every N events (default 1000)
        output_path: Path to save incremental progress (optional)

    Returns:
        DataFrame with added columns: protest_groups, protest_topics
    """
    # Check which rows need processing
    if "protest_groups" not in df.columns:
        df["protest_groups"] = None
    if "protest_topics" not in df.columns:
        df["protest_topics"] = None

    needs_processing = df["protest_groups"].isna() | df["protest_topics"].isna()
    indices_to_process = list(df[needs_processing].index)

    if len(indices_to_process) == 0:
        print("All events already categorized!")
        return df

    print(f"Categorizing {len(indices_to_process)} events (max {max_concurrent} concurrent)...")

    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async def classify_with_semaphore(idx):
        async with semaphore:
            row = df.loc[idx]
            result = await classify_event(
                topic=str(row.get("topic", "")),
                organizer=str(row.get("organizer", "")) if pd.notna(row.get("organizer")) else None,
                city=str(row.get("city", "")) if pd.notna(row.get("city")) else None,
            )
            return idx, result

    # Process with progress bar
    from tqdm.asyncio import tqdm
    pbar = tqdm(total=len(indices_to_process), desc="Categorizing events")
    processed = 0

    # Process in batches to allow incremental saves
    batch_size = save_interval
    for i in range(0, len(indices_to_process), batch_size):
        batch_indices = indices_to_process[i:i + batch_size]
        tasks = [classify_with_semaphore(idx) for idx in batch_indices]

        # Gather results for this batch
        batch_results = await asyncio.gather(*tasks)

        # Update dataframe with batch results
        for idx, result in batch_results:
            df.at[idx, "protest_groups"] = json.dumps(result.get("groups", []))
            df.at[idx, "protest_topics"] = json.dumps(result.get("topics", []))

        processed += len(batch_results)
        pbar.update(len(batch_results))

        # Save incremental progress
        if output_path:
            df.to_csv(output_path, index=False)
            pbar.set_postfix(saved=processed)

    pbar.close()
    return df


def categorize_dataset_sync(input_path: str | Path, output_path: str | Path, resume: bool = True) -> None:
    """
    Synchronous wrapper for categorizing a dataset.

    Args:
        input_path: Path to input CSV
        output_path: Path to output CSV with categories
        resume: If True and output exists, resume from previous progress
    """
    output_path = Path(output_path)

    # Resume from previous progress if exists
    if resume and output_path.exists():
        print(f"Resuming from {output_path}...")
        df = pd.read_csv(output_path)
    else:
        df = pd.read_csv(input_path)

    # Run async categorization with incremental saves
    df = asyncio.run(categorize_dataset(df, output_path=str(output_path)))

    # Save final result
    df.to_csv(output_path, index=False)
    print(f"✓ Categorized dataset saved to {output_path}")

    # Print stats
    df["groups_list"] = df["protest_groups"].apply(lambda x: json.loads(x) if pd.notna(x) else [])
    df["topics_list"] = df["protest_topics"].apply(lambda x: json.loads(x) if pd.notna(x) else [])

    total_groups = df["groups_list"].apply(len).sum()
    total_topics = df["topics_list"].apply(len).sum()

    print(f"\nStatistics:")
    print(f"  Events categorized: {len(df)}")
    print(f"  Total group assignments: {total_groups}")
    print(f"  Total topic assignments: {total_topics}")
    print(f"  Avg groups per event: {total_groups/len(df):.2f}")
    print(f"  Avg topics per event: {total_topics/len(df):.2f}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python categorize.py <input_csv> <output_csv>")
        sys.exit(1)

    categorize_dataset_sync(sys.argv[1], sys.argv[2])
