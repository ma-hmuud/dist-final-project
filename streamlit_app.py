from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models" / "best_demand_forecasting_model"
METRICS_PATH = BASE_DIR / "outputs" / "model_metrics.csv"


st.set_page_config(
    page_title="Demand Forecasting Control Room",
    page_icon="DF",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Source+Serif+4:opsz,wght@8..60,400;8..60,650&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 12% 15%, rgba(255, 190, 92, 0.18), transparent 28rem),
            radial-gradient(circle at 88% 0%, rgba(73, 132, 255, 0.20), transparent 30rem),
            linear-gradient(135deg, #10151f 0%, #18202c 45%, #111827 100%);
        color: #f6efe2;
    }

    .hero {
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 28px;
        padding: 2rem;
        background: rgba(255,255,255,0.08);
        box-shadow: 0 24px 80px rgba(0,0,0,0.32);
    }

    .hero h1 {
        font-family: 'Archivo Black', sans-serif;
        font-size: 3rem;
        line-height: 1;
        margin-bottom: 0.5rem;
        letter-spacing: -0.04em;
    }

    .hero p, .role-card, .metric-card {
        font-family: 'Source Serif 4', serif;
        font-size: 1.05rem;
    }

    .role-card, .metric-card {
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        background: rgba(255,255,255,0.07);
        min-height: 118px;
    }

    div[data-testid="stMetricValue"] {
        color: #ffd166;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_spark_model():
    from pyspark.ml.pipeline import PipelineModel
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName("Demand Forecasting Streamlit App")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    model = PipelineModel.load(str(MODEL_DIR))
    return spark, model


def load_metrics() -> pd.DataFrame:
    if METRICS_PATH.exists():
        return pd.read_csv(METRICS_PATH)
    return pd.DataFrame(columns=["Model", "RMSE", "MAE", "R2"])


st.markdown(
    """
    <div class="hero">
        <h1>Demand Forecasting Control Room</h1>
        <p>
            A lightweight deployment GUI for the PySpark demand forecasting model.
            Use it after running the notebook to load the saved Spark ML pipeline and
            estimate daily product demand.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

role_cols = st.columns(4)
roles = [
    ("Mahmoud Ahmed", "Data Engineer + Big Data Engineer"),
    ("Mohamed ElSayed", "Machine Learning Engineer"),
    ("Abdelrahman Ayman", "Data Analyst"),
    ("Seif Ihab", "MLOps Engineer"),
]
for column, (member, role) in zip(role_cols, roles):
    column.markdown(f'<div class="role-card"><b>{member}</b><br>{role}</div>', unsafe_allow_html=True)

st.write("")

metrics_df = load_metrics()
if not metrics_df.empty:
    best_row = metrics_df.sort_values("RMSE").iloc[0]
    metric_cols = st.columns(4)
    metric_cols[0].metric("Best Model", str(best_row["Model"]))
    metric_cols[1].metric("RMSE", f"{best_row['RMSE']:.2f}")
    metric_cols[2].metric("MAE", f"{best_row['MAE']:.2f}")
    metric_cols[3].metric("R2", f"{best_row['R2']:.3f}")
else:
    st.info("Run the notebook first to generate model metrics and train the saved model.")

left, right = st.columns([1, 1])

with left:
    st.subheader("Forecast Inputs")
    stock_code = st.text_input("Stock Code", value="85123A")
    country = st.text_input("Country", value="United Kingdom")
    day_of_week = st.slider("Day of Week (Spark: Sunday=1, Saturday=7)", 1, 7, 2)
    month = st.slider("Month", 1, 12, 12)
    day_index = st.number_input("Day Index", min_value=0, value=4350, step=1)
    lag_1 = st.number_input("Demand Yesterday", min_value=0.0, value=25.0, step=1.0)
    lag_7 = st.number_input("Demand 7 Days Ago", min_value=0.0, value=20.0, step=1.0)
    rolling_7 = st.number_input("7-Day Average Demand", min_value=0.0, value=22.0, step=1.0)
    invoice_count = st.number_input("Invoice Count", min_value=1.0, value=3.0, step=1.0)

with right:
    st.subheader("Prediction")
    st.caption("The app uses the Spark ML pipeline saved by the notebook.")
    run_prediction = st.button("Predict Demand", type="primary", use_container_width=True)

    if run_prediction:
        if not MODEL_DIR.exists():
            st.error("Saved model not found. Run the notebook first so it creates models/best_demand_forecasting_model.")
        else:
            try:
                spark, model = load_spark_model()
                input_pdf = pd.DataFrame(
                    [
                        {
                            "StockCode": stock_code,
                            "Country": country,
                            "DayOfWeek": int(day_of_week),
                            "Month": int(month),
                            "IsWeekend": 1.0 if day_of_week in (1, 7) else 0.0,
                            "DayIndex": int(day_index),
                            "Lag1Quantity": float(lag_1),
                            "Lag7Quantity": float(lag_7),
                            "Rolling7AvgQuantity": float(rolling_7),
                            "InvoiceCount": float(invoice_count),
                        }
                    ]
                )
                prediction = model.transform(spark.createDataFrame(input_pdf)).select("prediction").first()[0]
                st.metric("Predicted Daily Demand", f"{max(prediction, 0):.0f} units")
                st.success("Prediction completed with the saved Spark ML model.")
            except Exception as exc:
                st.error("Could not start Spark or load the model.")
                st.code(str(exc))
                st.warning("Check that Java 17 or 21 is active and that the notebook has been run successfully.")

st.divider()
st.subheader("Model Metrics")
if metrics_df.empty:
    st.write("No metrics file found yet.")
else:
    st.dataframe(metrics_df, use_container_width=True)
