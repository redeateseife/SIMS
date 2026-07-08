# services/inventory_service.py

from __future__ import annotations
import pandas as pd
from datetime import date
from config import CSV_FILE

COLUMNS = [
    "ID", "ITEM", "CATEGORY", "QUANTITY",
    "COST", "PRICE", "LOCATION",
    "LAST_UPDATED", "LAST_SOLD"
]

IDLE_THRESHOLD_DAYS = 30


def _format_price(price: str | float) -> str:
    price = str(price).strip()
    return price if price.startswith("$") else f"${price}"


def _derive_status(quantity: int) -> str:
    if quantity <= 0:
        return "NO STOCK"
    if quantity <= 5:
        return "LOW STOCK"
    return "IN STOCK"


class Inventory:
    
    # ------------------------------------------------------------------
    # Construction / persistence
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        self._df: pd.DataFrame = self._load()

    def _load(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(CSV_FILE)
            df.columns = df.columns.str.strip()

            # Drop STATUS if it exists in the CSV — always derived at runtime
            if "STATUS" in df.columns:
                df = df.drop(columns=["STATUS"])

            # Ensure LAST_SOLD column exists for older CSV files
            if "LAST_SOLD" not in df.columns:
                df["LAST_SOLD"] = pd.NaT

            # Parse date columns
            df["LAST_UPDATED"] = pd.to_datetime(df["LAST_UPDATED"], errors="coerce")
            df["LAST_SOLD"]    = pd.to_datetime(df["LAST_SOLD"],    errors="coerce")

            # Derive STATUS from QUANTITY at load time
            df["STATUS"] = df["QUANTITY"].apply(_derive_status)

            return df
        except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
            return pd.DataFrame(columns=COLUMNS + ["STATUS"])

    @property
    def df(self) -> pd.DataFrame:
        # Read-only access to the underlying DataFrame
        return self._df

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def filtered(self, location: str) -> pd.DataFrame:
        # Return rows for *location*, or all rows when location == 'ALL'
        # Appends derived PROFIT and MARGIN columns at display time
        if location == "ALL":
            df = self._df.copy()
        else:
            df = self._df[self._df["LOCATION"] == location].copy()

        df = self._append_derived(df)
        return df

    def locations(self) -> list[str]:
        # Sorted list of unique location codes present in the data
        return sorted(self._df["LOCATION"].dropna().unique())

    def selector_labels(self) -> pd.Series:
        # Human-readable labels for the item selector widget
        df = self._df
        return df["ITEM"] + " (" + df["LOCATION"] + " - ID: " + df["ID"].astype(str) + ")"

    def idle_inventory(self, days: int = IDLE_THRESHOLD_DAYS) -> pd.DataFrame:    
        # Items with stock remaining but no recorded sale in the last X days
        # Requires LAST_SOLD to be populated; rows with null LAST_SOLD are excluded
        cutoff = pd.Timestamp.today() - pd.Timedelta(days=days)

        mask = (
            (self._df["QUANTITY"] > 0) &
            (self._df["LAST_SOLD"].notna()) &
            (self._df["LAST_SOLD"] < cutoff)
        )

        idle_df = self._df[mask].copy()
        idle_df["DAYS_SINCE_SOLD"] = (
            pd.Timestamp.today() - idle_df["LAST_SOLD"]
        ).dt.days

        return idle_df[[
            "ID", "ITEM", "CATEGORY", "QUANTITY",
            "LOCATION", "LAST_SOLD", "DAYS_SINCE_SOLD"
        ]].reset_index(drop=True)

    # ------------------------------------------------------------------
    # Derived columns (never stored in CSV)
    # ------------------------------------------------------------------

    @staticmethod
    def _append_derived(df: pd.DataFrame) -> pd.DataFrame:
        # Append PROFIT and MARGIN columns, derived from COST and PRICE
        def parse_price(series: pd.Series) -> pd.Series:
            return pd.to_numeric(
                series.astype(str).str.replace("$", "", regex=False),
                errors="coerce"
            )

        cost  = parse_price(df["COST"])
        price = parse_price(df["PRICE"])

        df["PROFIT"] = (price - cost).round(2).apply(lambda x: f"${x:.2f}")
        df["MARGIN"] = (
            ((price - cost) / price * 100)
            .round(1)
            .apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
        )

        return df

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def add_or_edit(
        self,
        item_id:  int,
        item:     str,
        category: str,
        quantity: int,
        cost:     str,
        price:    str,
        location: str,
    ) -> None:
        # Add new row or update existing (id, location) pair.
        # ValueError if *item_id* is already mapped
        
        cost  = _format_price(cost)
        price = _format_price(price)
        today = str(date.today())

        id_mask = self._df["ID"] == item_id
        if id_mask.any():
            existing = self._df.loc[id_mask, "ITEM"].iloc[0].strip().upper()
            if existing != item:
                raise ValueError(f"ID {item_id} already belongs to '{existing}'.")

        loc_mask = id_mask & (self._df["LOCATION"] == location)
        if loc_mask.any():
            self._df.loc[loc_mask, "QUANTITY"]    += quantity
            self._df.loc[loc_mask, "COST"]         = cost
            self._df.loc[loc_mask, "PRICE"]        = price
            self._df.loc[loc_mask, "LAST_UPDATED"] = today
        else:
            new_row = pd.DataFrame([{
                "ID":           item_id,
                "ITEM":         item,
                "CATEGORY":     category,
                "QUANTITY":     quantity,
                "COST":         cost,
                "PRICE":        price,
                "LOCATION":     location,
                "LAST_UPDATED": today,
                "LAST_SOLD":    pd.NaT,
            }])
            self._df = pd.concat([self._df, new_row], ignore_index=True)

        # Recompute STATUS after any quantity change
        self._df["STATUS"] = self._df["QUANTITY"].apply(_derive_status)

    def record_sale(self, item_id: int, location: str, quantity: int) -> None:
        # Deduct *quantity* from (item_id, location), update LAST_SOLD, 
        # and recompute STATUS. Rows that reach zero are marked NO STOCK 
        # and retained, not dropped
        
        today = str(date.today())
        mask  = (self._df["ID"] == item_id) & (self._df["LOCATION"] == location)

        self._df.loc[mask, "QUANTITY"]     -= quantity
        self._df.loc[mask, "LAST_SOLD"]    = today
        self._df.loc[mask, "LAST_UPDATED"] = today

        # Recompute STATUS across entire DataFrame after quantity change
        self._df["STATUS"] = self._df["QUANTITY"].apply(_derive_status)

    def remove(self, item_id: int, location: str, quantity: int) -> None:
        # Deduct *quantity* from (item_id, location)
        self.record_sale(item_id, location, quantity)
