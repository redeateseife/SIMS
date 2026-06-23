# services/inventory_service.py
#
# The Inventory class owns the DataFrame and exposes all mutation/query methods.
# This replaces the previous pattern of passing `df` into every free function.
# Consumers hold one Inventory instance (stored in st.session_state) and call
# methods on it — no raw pandas leaks into the UI layer.

from __future__ import annotations

import pandas as pd

from config import CSV_FILE

COLUMNS = ["ID", "ITEM", "QUANTITY", "RETAIL", "SALE", "LOCATION"]


def _format_price(price: str | float) -> str:
    """Ensure a price string is prefixed with '$'."""
    price = str(price).strip()
    return price if price.startswith("$") else f"${price}"


class Inventory:
    """Encapsulates the inventory DataFrame and all operations on it."""

    # ------------------------------------------------------------------
    # Construction / persistence
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        self._df: pd.DataFrame = self._load()

    def _load(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(CSV_FILE)
            df.columns = df.columns.str.strip()
            return df
        except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
            return pd.DataFrame(columns=COLUMNS)

    @property
    def df(self) -> pd.DataFrame:
        """Read-only access to the underlying DataFrame."""
        return self._df

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def filtered(self, location: str) -> pd.DataFrame:
        """Return rows for *location*, or all rows when location == 'ALL'."""
        if location == "ALL":
            return self._df
        return self._df[self._df["LOCATION"] == location]

    def locations(self) -> list[str]:
        """Sorted list of unique location codes present in the data."""
        return sorted(self._df["LOCATION"].dropna().unique())

    def selector_labels(self) -> pd.Series:
        """Human-readable labels for the item selector widget."""
        df = self._df
        return df["ITEM"] + " (" + df["LOCATION"] + " - ID: " + df["ID"].astype(str) + ")"

    def idle_inventory(self) -> pd.DataFrame:
        """
        Items that exist in more than one location.
        Non-hub rows are flagged; the hub is whichever location has the most stock.
        """
        item_counts = self._df.groupby("ITEM")["LOCATION"].nunique()
        multi_location_items = item_counts[item_counts > 1].index
        rows: list[dict] = []

        for item in multi_location_items:
            item_df = self._df[self._df["ITEM"] == item]
            hub = item_df.loc[item_df["QUANTITY"].idxmax()]

            non_hub = item_df[item_df["LOCATION"] != hub["LOCATION"]]
            for _, row in non_hub.iterrows():
                rows.append({
                    "Item Name":        item,
                    "Current Location": row["LOCATION"],
                    "Current Stock":    row["QUANTITY"],
                    "Target Hub":       hub["LOCATION"],
                    "Hub Stock":        hub["QUANTITY"],
                })

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def add_or_edit(
        self,
        item_id: int,
        item: str,
        quantity: int,
        retail: str,
        sale: str,
        location: str,
    ) -> None:
        """
        Add a new row or increment quantity on an existing (id, location) pair.

        Raises ValueError if *item_id* is already mapped to a different item name.
        """
        retail = _format_price(retail)
        sale   = _format_price(sale)

        id_mask = self._df["ID"] == item_id
        if id_mask.any():
            existing = self._df.loc[id_mask, "ITEM"].iloc[0].strip().upper()
            if existing != item:
                raise ValueError(f"ID {item_id} already belongs to '{existing}'.")

        loc_mask = id_mask & (self._df["LOCATION"] == location)
        if loc_mask.any():
            self._df.loc[loc_mask, "QUANTITY"]        += quantity
            self._df.loc[loc_mask, ["RETAIL", "SALE"]] = [retail, sale]
        else:
            new_row = pd.DataFrame([{
                "ID": item_id, "ITEM": item, "QUANTITY": quantity,
                "RETAIL": retail, "SALE": sale, "LOCATION": location,
            }])
            self._df = pd.concat([self._df, new_row], ignore_index=True)

    def remove(self, item_id: int, location: str, quantity: int) -> None:
        """Deduct *quantity* from (item_id, location) and drop rows that hit zero."""
        mask = (self._df["ID"] == item_id) & (self._df["LOCATION"] == location)
        self._df.loc[mask, "QUANTITY"] -= quantity
        self._df = self._df[self._df["QUANTITY"] > 0].reset_index(drop=True)