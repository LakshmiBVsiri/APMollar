import os
import duckdb
import pandas as pd
import streamlit as st
from tools.sql_tool import ensure_db, run_sql, get_schema_markdown, SCHEMA_HINT
from tools.charts import auto_chart
from agent import nl_to_sql, post_answer_enrichment, _call_gemini

# ============================================================
# Streamlit Page Setup
# ============================================================
st.set_page_config(page_title="Olist AI Business Assistant", layout="wide")
st.title("Olist AI Business Assistant")
st.caption("An intelligent, data-driven business analysis system for Olist e-commerce operations.")

# ============================================================
# Sidebar Navigation
# ============================================================
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Select Mode", ["Data Analyst", "Business Chatbot", "Overall Data Insights"])

DATA_DIR = "data/olist"
DB_PATH = ".cache/olist.duckdb"

# ============================================================
# Data Analyst Mode
# ============================================================
if mode == "Data Analyst":
    st.header("Ask About Olist Data")

    st.info("Note: The dataset used in this application contains records from the years 2016 to 2018. "
            "Please enter your query below (for example: 'Identify the top product categories by sales in 2018').")

    if not os.path.exists(DATA_DIR):
        st.error("Please ensure that all Olist CSV files are placed inside the 'data/olist/' directory.")
    else:
        con = ensure_db(DB_PATH, DATA_DIR)
        st.sidebar.success("Database is ready.")

        # User question input
        question = st.text_input("Enter your question")

        # Initialize session state
        if "df" not in st.session_state:
            st.session_state.df = pd.DataFrame()
        if "question" not in st.session_state:
            st.session_state.question = ""

        if st.button("Ask"):
            with st.spinner("Generating SQL query..."):
                sql = nl_to_sql(question, SCHEMA_HINT, "Gemini", "gemini-2.0-flash")

            st.session_state.question = question
            st.code(sql, language="sql")

            # SQL explanation
            st.subheader("SQL Query Explanation")
            with st.spinner("Analyzing SQL query..."):
                explain_sql_prompt = f"""
In 2 or 3 sentences Explain this SQL query in clear business terms and it should be easily understable of non- business people. Describe what data it retrieves, how it filters, 
and what type of business insight it provides. Avoid technical SQL jargon.

SQL:
{sql}
"""
                sql_explanation = _call_gemini(explain_sql_prompt)
            st.info(f"Explanation:\n\n{sql_explanation}")

            # Execute SQL
            with st.spinner("Running query..."):
                df = run_sql(con, sql)

            if "error" in df.columns:
                st.error(df["error"].iloc[0])
            else:
                st.session_state.df = df
                st.success("Query executed successfully.")
                st.dataframe(df, use_container_width=True)

                # Auto Chart Visualization
                st.subheader("Visual Representation of Data")
                auto_chart(df)

                # Causal reasoning and insights
                with st.spinner("Generating insights..."):
                    summary = post_answer_enrichment(question, df, "Gemini", "gemini-2.0-flash")
                st.markdown(summary)

        # Database Schema
        if st.checkbox("Show Database Schema"):
            st.markdown(get_schema_markdown(con))

# ============================================================
# Business Chatbot Mode
# ============================================================
elif mode == "Business Chatbot":
    st.header("Olist Business Chatbot Assistant")
    st.write("This chatbot answers only business-related questions about the Olist e-commerce dataset, "
             "including topics such as sales, customers, reviews, deliveries, and performance trends.")

    # Chat memory
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Enter your business-related question here..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Business domain filter
        business_keywords = [
            "sales", "revenue", "profit", "order", "delivery", "customer",
            "review", "product", "category", "performance", "trend", "market",
            "growth", "delay", "payment", "seller", "demand", "price",
            "shipment", "olist", "business", "return", "region", "state"
        ]

        if not any(word in prompt.lower() for word in business_keywords):
            with st.chat_message("assistant"):
                refusal_msg = (
                    "I can only respond to business-related questions about the Olist e-commerce dataset and its operations."
                )
                st.warning(refusal_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": refusal_msg})
        else:
            # Generate business insight
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your question..."):
                    business_prompt = f"""
You are a senior business analyst specializing in Olist e-commerce operations.

Answer only business, data, and performance-related questions about Olist.
If the question is unrelated to Olist or e-commerce analytics, politely refuse.

Focus on insights related to sales, customers, reviews, orders, delivery, payments, or product categories.

User question: "{prompt}"

Respond in two to three sentences using clear and professional business language.
"""
                    response = _call_gemini(business_prompt)
                    st.markdown(response)

            st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Clear chat
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []
        st.sidebar.success("Chat cleared.")

# ============================================================
# Overall Data Insights Mode
# ============================================================
elif mode == "Overall Data Insights":
    st.header("Comprehensive Analysis of Olist E-commerce Data")
    st.write("This section provides a consolidated business summary of Olist's performance between 2016 and 2017.")

    if not os.path.exists(DATA_DIR):
        st.error("Please ensure that Olist CSV files are available in the 'data/olist/' directory.")
    else:
        con = ensure_db(DB_PATH, DATA_DIR)
        st.sidebar.success("Database is ready.")

        with st.spinner("Analyzing dataset..."):
            # Load main tables
            orders = con.execute("SELECT * FROM olist_orders").df()
            items = con.execute("SELECT * FROM olist_order_items").df()
            payments = con.execute("SELECT * FROM olist_order_payments").df()
            products = con.execute("SELECT * FROM olist_products").df()
            customers = con.execute("SELECT * FROM olist_customers").df()

            # Metrics
            total_orders = len(orders)
            total_customers = customers["customer_id"].nunique()
            total_products = products["product_id"].nunique()
            total_sales = payments["payment_value"].sum()
            avg_order_value = payments["payment_value"].mean()

            st.markdown("### Key Business Metrics")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Orders", f"{total_orders:,}")
            col2.metric("Unique Customers", f"{total_customers:,}")
            col3.metric("Unique Products", f"{total_products:,}")
            col4.metric("Total Sales", f"R$ {total_sales:,.2f}")
            col5.metric("Average Order Value", f"R$ {avg_order_value:,.2f}")

            # Monthly sales trend
            orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
            orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
            monthly_sales = (
                orders.merge(payments, on="order_id")
                .groupby("month")["payment_value"]
                .sum()
                .reset_index()
            )

            st.markdown("### Monthly Sales Trend")
            st.line_chart(monthly_sales.set_index("month"))

            # Regional distribution
            st.markdown("### Sales Distribution by State")
            geo_sales = (
                orders.merge(customers, on="customer_id")
                .merge(payments, on="order_id")
                .groupby("customer_state")["payment_value"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            st.bar_chart(geo_sales.set_index("customer_state"))

            # Top product categories
            st.markdown("### Top Product Categories by Revenue")
            top_categories = (
                items.merge(products, on="product_id")
                .merge(payments, on="order_id")
                .groupby("product_category_name")["payment_value"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .head(10)
            )
            st.bar_chart(top_categories.set_index("product_category_name"))

            # AI-generated summary
            st.markdown("### AI-Generated Business Insights")
            overall_prompt = f"""
You are a business analyst. Based on the Olist dataset summary, provide a concise performance overview:
- Total Orders: {total_orders}
- Unique Customers: {total_customers}
- Unique Products: {total_products}
- Total Sales: R$ {total_sales:,.2f}
- Average Order Value: R$ {avg_order_value:,.2f}
- Top Product Categories: {', '.join(top_categories['product_category_name'].head(5).tolist())}
- States with Highest Sales: {', '.join(geo_sales['customer_state'].head(5).tolist())}
- Period: 2016–2017

Describe business performance, customer concentration, top-performing categories, and possible areas for improvement.
Provide 4–5 key insights.
"""
            insights = _call_gemini(overall_prompt)
            st.info(insights)
