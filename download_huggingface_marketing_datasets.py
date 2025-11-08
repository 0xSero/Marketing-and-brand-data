#!/usr/bin/env python3
"""
Download marketing datasets from Hugging Face
"""

import json
from pathlib import Path
from datasets import load_dataset
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_and_save_dataset(dataset_name: str, output_file: str):
    """Download dataset from Hugging Face and save as JSONL"""

    logger.info(f"Downloading {dataset_name}...")

    try:
        # Load dataset
        dataset = load_dataset(dataset_name, trust_remote_code=True)

        # Get the split (usually 'train', sometimes 'default')
        if 'train' in dataset:
            data = dataset['train']
        elif 'default' in dataset:
            data = dataset['default']
        else:
            # Use first available split
            split_name = list(dataset.keys())[0]
            data = dataset[split_name]

        logger.info(f"Dataset loaded: {len(data)} rows")

        # Save as JSONL
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, item in enumerate(data):
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

                if (i + 1) % 1000 == 0:
                    logger.info(f"  Saved {i + 1} items...")

        logger.info(f"✓ Saved {len(data)} items to {output_file}")

        # Calculate size
        size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"  File size: {size_mb:.2f} MB")

        return len(data), size_mb

    except Exception as e:
        logger.error(f"✗ Failed to download {dataset_name}: {e}")
        return 0, 0


def main():
    logger.info("="*80)
    logger.info("HUGGING FACE MARKETING DATASETS DOWNLOADER")
    logger.info("="*80 + "\n")

    # List of marketing datasets to download
    datasets_to_download = [
        ("RafaM97/marketing_social_media", "data/hf_marketing_social_media.jsonl"),
        ("MuratcanKoylan/MarketingStructuralPrompts", "data/hf_marketing_prompts.jsonl"),
        ("dvilasuero/marketing", "data/hf_marketing_magpie.jsonl"),
        ("Andyrasika/banking-marketing", "data/hf_banking_marketing.jsonl"),
        ("dianalogan/Marketing-Budget-and-Actual-Sales-Dataset", "data/hf_marketing_budget_sales.jsonl"),
    ]

    total_items = 0
    total_size_mb = 0

    for dataset_name, output_file in datasets_to_download:
        items, size_mb = download_and_save_dataset(dataset_name, output_file)
        total_items += items
        total_size_mb += size_mb
        logger.info("")

    logger.info("="*80)
    logger.info("DOWNLOAD COMPLETE")
    logger.info("="*80)
    logger.info(f"Total items: {total_items:,}")
    logger.info(f"Total size: {total_size_mb:.2f} MB ({total_size_mb/1024:.3f} GB)")
    logger.info("="*80)


if __name__ == '__main__':
    main()
