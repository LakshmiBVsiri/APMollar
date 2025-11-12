import os, time, duckdb, pandas as pd

SCHEMA_HINT = """
Tables:
  olist_orders(order_id, customer_id, order_status, order_purchase_timestamp)
  olist_order_items(order_id, order_item_id, product_id, seller_id, price, freight_value)
  olist_products(product_id, product_category_name)
  olist_order_payments(order_id, payment_type, payment_value)
  olist_customers(customer_id, customer_city, customer_state)
Joins: orders <-> order_items <-> products <-> payments <-> customers
"""

def ensure_db(db_path, data_dir):
    """
    Safely creates or connects to the DuckDB database.
    Prevents write-write conflicts during Streamlit reruns.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    lock_file = db_path + ".lock"

    # Prevent concurrent builds
    while os.path.exists(lock_file):
        print("⚠️ Another Streamlit instance is building the DB. Waiting 2s...")
        time.sleep(2)

    con = duckdb.connect(db_path, read_only=False)
    existing = {r[0] for r in con.execute("SHOW TABLES").fetchall()}

    try:
        if not existing:
            open(lock_file, "w").close()  # create lock
            print("🔧 Building DuckDB tables...")

            csvs = {
                "olist_orders": "olist_orders_dataset.csv",
                "olist_order_items": "olist_order_items_dataset.csv",
                "olist_products": "olist_products_dataset.csv",
                "olist_order_payments": "olist_order_payments_dataset.csv",
                "olist_customers": "olist_customers_dataset.csv",
            }

            for table, fname in csvs.items():
                fpath = os.path.join(data_dir, fname)
                if not os.path.exists(fpath):
                    print(f"⚠️ Missing {fname}, skipping this table.")
                    continue
                print(f"📥 Importing {fname} → {table}")
                con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('{fpath}')")

            print("✅ DuckDB database created successfully.")
        else:
            print("✅ Existing DuckDB found, skipping rebuild.")
        return con
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)

def run_sql(con, sql):
    try:
        return con.execute(sql).df()
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def get_schema_markdown(con):
    rows = con.execute("SHOW TABLES").fetchall()
    md = ["**Tables:**"]
    for (t,) in rows:
        cols = con.execute(f"DESCRIBE {t}").fetchall()
        md.append(f"- {t}: " + ", ".join(c[0] for c in cols))
    return "\n".join(md)
