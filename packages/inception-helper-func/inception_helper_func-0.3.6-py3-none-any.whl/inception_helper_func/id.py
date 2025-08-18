import re
import random
from datetime import datetime, timezone
from typing import Optional, Callable, Any


def generate_id(
    owner: str,
    place_owner_after_prefix: bool = False,
    created_by: str = "",
    include_creator: bool = False,
    prefix: str = "",
    random_digits: int = 4,
    cast_func: Callable[[int], Any] = str,
    separator: str = "",
    include_timestamp: bool = False,
) -> str:
    """
    Generate a unique identifier by combining various components.

    Args:
        owner: Required. The owner ID or name.
        place_owner_after_prefix: If True, places the owner ID right after prefix.
        created_by: Optional. ID or name of the creator.
        include_creator: If True, appends the created_by value.
        prefix: Optional prefix string.
        random_digits: Number of digits for the random number.
        cast_func: Function to convert the random number (default: str).
        separator: Separator between components.
        include_timestamp: If True, adds the current timestamp.

    Returns:
        str: The generated ID.
    """
    owner = str(owner).strip()

    if random_digits < 1:
        raise ValueError("random_digits must be greater than 0")

    if include_creator and not created_by:
        raise ValueError("created_by is required when include_creator is True")

    if created_by:
        created_by = str(created_by).strip()

    components = []

    if prefix:
        components.append(prefix)

    if place_owner_after_prefix:
        components.append(owner)

    # Generate random number
    rand_value = random.randrange(10 ** (random_digits - 1), 10**random_digits)
    components.append(cast_func(rand_value))

    # Include timestamp
    if include_timestamp:
        try:
            components.append(datetime.now().strftime("%Y%m%d%H%M%S"))
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {e}")

    if not place_owner_after_prefix:
        components.append(owner)

    if include_creator and created_by:
        components.append(created_by)

    return separator.join(filter(None, components))


def slugify_name(name: str) -> str:
    return (
        "-".join(re.sub(r"[^a-zA-Z0-9\s]+", "", word.strip()) for word in name.split())
        .strip()
        .lower()
    )

def generate_sku(
    profile_name: Optional[str],
    category: str,
    brand: str,
    variant: Optional[str] = None,
    sub_category: Optional[str] = None,
    separator: str = '-',
    max_length: Optional[int] = None,
    ndigits: int = 4,
    code_cast_func: Callable[[int], str] = str
) -> str:
    """
    Generate a standardized SKU (Stock Keeping Unit) with optional components.

    Args:
        profile (str, optional): User or department profile identifier.
        category (str): Main category name (e.g., "Clothing").
        brand (str): Brand name (e.g., "Nike").
        variant (str, optional): Product variant (e.g., "Black Large").
        sub_category (str, optional): Sub-category (e.g., "T-Shirt").
        separator (str): Separator between SKU parts (default: "-").
        max_length (int, optional): Maximum allowed SKU length.
        ndigits (int): Number of digits in the sequence portion (default: 4).
        code_cast_func (callable): Function to convert sequence number to string (default: str).

    Returns:
        str: Generated SKU.
    """
    def clean_part(value: Optional[str], length: int, upper=True, segment_len=2) -> str:
        if not value:
            return ''
        parts = value.strip().split()
        shortened = ''.join(p[:segment_len] for p in parts)[:length]
        shortened = shortened.replace('-', '')
        return shortened.upper() if upper else shortened

    def random_sequence(ndigits: int) -> str:
        rand_num = random.randrange(10 ** (ndigits - 1), 10 ** ndigits)
        year_suffix = datetime.now(timezone.utc).strftime('%y')
        return f"{year_suffix}{code_cast_func(rand_num)}"

    # Generate SKU parts
    parts = [
        clean_part(profile_name, 4),
        clean_part(category, 3),
        clean_part(sub_category, 3) if sub_category else '',
        clean_part(brand, 2),
        clean_part(variant, 4) if variant else '',
        random_sequence(ndigits)
    ]

    # Filter out empty parts and join with separator
    sku = separator.join(filter(None, parts))

    return sku[:max_length] if max_length else sku






if __name__ == "__main__":
    # Sample test cases
    test_cases = [
        {"owner": "1234567890", "prefix": "test_", "separator": "-"},
        {
            "owner": "1234567890",
            "created_by": "creator123",
            "include_creator": True,
            "prefix": "test_",
            "separator": "-",
        },
        {
            "owner": "1234567890",
            "prefix": "test_",
            "separator": "-",
            "include_timestamp": True,
        },
        {
            "owner": "1234567890",
            "prefix": "test_",
            "separator": "-",
            "include_timestamp": True,
            "timestamp_format": "%Y%m%d",
        },
    ]

    for case in test_cases:
        try:
            result = generate_id(**case)
            print(f"Test case {case}: {result}")
        except Exception as e:
            print(f"Test case {case} failed: {e}")


    # Example usage of generate_sku
    sku = generate_sku(
        profile="Warehouse A",
        category="Clothing",
        brand="Nike",
        variant="Black L",
        sub_category="T-Shirt",
        max_length=20,
        separator=''
    )
    print(sku)  # Example: "WAACLOTSNIBL240123"

