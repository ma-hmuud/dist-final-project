# PySpark Demand Forecasting Final Project

This project predicts e-commerce product demand using PySpark, HDFS, Spark MLlib, and a small Streamlit deployment GUI. It uses the public UCI Online Retail dataset.

## Team Roles

- Mahmoud Ahmed: Data Engineer (Ingestion & Storage) and Big Data Engineer (Optimization & Performance)
- Mohamed ElSayed: Machine Learning Engineer (Model Development)
- Abdelrahman Ayman: Data Analyst (Exploration & Insights)
- Seif Ihab: MLOps Engineer (Deployment & Monitoring)

## Project Files

- `demand_forecasting_pyspark.ipynb`: main notebook for ingestion, cleaning, EDA, features, modeling, optimization, and MLOps notes.
- `streamlit_app.py`: basic deployment GUI for loading the saved Spark ML model and making a demand prediction.
- `PROJECT_DOCUMENTATION.md`: full project documentation for submission.
- `docker-compose.hdfs.yml`: local HDFS NameNode/DataNode setup.
- `hadoop.env`: Hadoop/HDFS configuration used by Docker Compose.
- `scripts/hdfs_bootstrap.sh`: starts HDFS and creates `/demand_forecasting` directories.
- `requirements.txt`: Python dependencies.
- `data/`: local raw dataset cache created by the notebook.
- `outputs/`: local charts, metrics, and prediction exports created by the notebook.
- `models/`: saved Spark ML pipeline model created by the notebook.

## Requirements

- Python 3 with virtual environment support.
- Docker and Docker Compose for the local HDFS services.
- Java 17 or Java 21 for Spark. Java 26 is currently too new for this Spark runtime.
- A project-local Java 21 runtime is installed under `.jdk/`; the notebook automatically uses it when present.

## Environment Setup

Create and activate the virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If Spark fails with `ClassNotFoundException: jdk.internal.ref.Cleaner`, switch to Java 17 or 21:

```bash
export JAVA_HOME=/path/to/jdk-17
export PATH="$JAVA_HOME/bin:$PATH"
java -version
```

Or use the project-local Java 21 runtime:

```bash
export JAVA_HOME="$(pwd)/.jdk/jdk-21.0.11+10"
export PATH="$JAVA_HOME/bin:$PATH"
java -version
```

## HDFS Setup

Start local HDFS:

```bash
bash scripts/hdfs_bootstrap.sh
```

Useful HDFS URLs and paths:

- NameNode UI: `http://localhost:9870`
- HDFS URI used by Spark: `hdfs://localhost:9000`
- Project root in HDFS: `/demand_forecasting`
- Cleaned data path: `/demand_forecasting/processed/clean_online_retail_parquet`
- Prediction output path: `/demand_forecasting/outputs/best_model_predictions_parquet`

Stop HDFS when finished:

```bash
docker compose -f docker-compose.hdfs.yml down
```

## Running the Notebook

Start HDFS first, then run:

```bash
jupyter lab demand_forecasting_pyspark.ipynb
```

The notebook performs:

- Dataset download from UCI Online Retail.
- Excel-to-CSV conversion for Spark ingestion using an explicit Spark-compatible `file://` local URI.
- PySpark cleaning and preprocessing.
- Partitioned Parquet write to HDFS.
- EDA with product, country, monthly, and seasonal demand insights.
- Lag and rolling feature engineering.
- Time-aware train/test split.
- Linear Regression, Random Forest, and Gradient Boosted Trees training.
- RMSE, MAE, and R2 evaluation.
- Saved model under `models/best_demand_forecasting_model`.
- Charts and metrics under `outputs/`.

## Running the Deployment GUI

After the notebook trains and saves the model:

```bash
streamlit run streamlit_app.py
```

The Streamlit app shows:

- Team role cards.
- Best model metrics from `outputs/model_metrics.csv`.
- A demand prediction form.
- A Spark ML model prediction using `models/best_demand_forecasting_model`.

## Deliverables Covered

- Cleaned and processed dataset: saved to HDFS as Parquet.
- Demand forecasting model: saved Spark ML pipeline.
- Optimized Spark pipeline: partitioning, caching, adaptive execution, and HDFS storage.
- Visualization: product, country, monthly demand, and prediction trend charts.
- Full documentation: this README plus explanatory notebook sections.

## Notes

The project is designed for local development but follows distributed-data concepts. In production, HDFS replication would normally be set to 3 or more. The local Docker HDFS setup uses replication factor 1 because it runs a single DataNode.
