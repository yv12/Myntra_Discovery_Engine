"""
Loader for User Interviews (Fourth Source, n=4).
Highest-weight source capturing self-reported intentional behavior rather than complaint volume.
"""

import hashlib
from typing import List, Dict, Any

INTERVIEWS_DATA = [
    {
        "participant_id": "P1",
        "segment": "luxury_buyer",
        "categories": ["shoes", "watches", "premium_accessories"],
        "text": "I am a luxury buyer, mainly shopping for premium shoes and watches on Myntra Luxe. I use the wishlist extensively because of budget timing—these are high-ticket items (15k-40k). I save them to track availability and wait until I have the disposable budget or bonus payout. Once the money is sorted, I come back and buy it straight away. Wishlist is my financial queue, not casual bookmarking.",
        "stated_behavior": "Saves because of budget; buys when he has money. High intentionality, waits for liquidity.",
        "primary_motive": "budget_timing",
        "primary_blocker": "budget_constraint"
    },
    {
        "participant_id": "P2",
        "segment": "cautious_apparel_buyer",
        "categories": ["clothing", "western_wear"],
        "text": "I mostly buy clothes, but I have huge anxiety about the return process—couriers often delay pickup or dispute tags. Because of that, items with no reviews or only 1-2 generic ratings feel extremely risky. If a product has no customer reviews and no photos from buyers, I will leave it sitting in my wishlist indefinitely. I'm constantly worried about being deceived by studio lighting and airbrushed catalog photos.",
        "stated_behavior": "Fears returns; items with no reviews feel risky, worried about being deceived. Trust deficit.",
        "primary_motive": "fit_uncertainty",
        "primary_blocker": "no_reviews"
    },
    {
        "participant_id": "P3",
        "segment": "offline_skeptic",
        "categories": ["apparel", "tailored_wear"],
        "text": "I honestly don't use the wishlist feature much because I prefer buying clothes offline where I can touch the fabric and check the fit in person. My biggest hesitation with online fashion is trust: I believe deeply discounted items (50-70% off) on apps are discounted because they're factory seconds or defective with crooked stitching and color bleeding. Unless trust is proven by real people, I will not buy online.",
        "stated_behavior": "Doesn't wishlist. Buys offline to check fit. Believes discounted items are discounted because they're defective (stitching etc). Trust is the core blocker.",
        "primary_motive": "fit_uncertainty",
        "primary_blocker": "quality_doubt"
    },
    {
        "participant_id": "P4",
        "segment": "high_volume_browser",
        "categories": ["trend_fashion", "dresses", "tops"],
        "text": "I save dozens of items across different sales and moods, but then I completely forget to go back and check my wishlist. By the time I remember, either my mood has passed or items are sold out. What would actually convert me is seeing real buyer photos—catalog product photos on European models aren't enough to judge real Indian skin tone color matching, drape, and fabric thickness.",
        "stated_behavior": "Saves a lot, forgets to return to wishlist. Demands real buyer photos to judge true color and fabric quality; product photos are insufficient.",
        "primary_motive": "comparison_shortlist",
        "primary_blocker": "forgot_wishlist"
    }
]

def load_interviews() -> List[Dict[str, Any]]:
    """Loads and normalizes the 4 user interview records into the common schema."""
    records = []
    for item in INTERVIEWS_DATA:
        p_id = item["participant_id"]
        raw_text = item["text"]
        rec_id = hashlib.sha256(f"interview_{p_id}_{raw_text}".encode("utf-8")).hexdigest()[:16]
        
        records.append({
            "record_id": rec_id,
            "source": "interview",
            "created_at": "2026-06-15T10:00:00Z",
            "text": raw_text,
            "meta": {
                "participant_id": p_id,
                "segment": item["segment"],
                "categories": item["categories"],
                "stated_behavior": item["stated_behavior"],
                "primary_motive": item["primary_motive"],
                "primary_blocker": item["primary_blocker"]
            }
        })
    return records
