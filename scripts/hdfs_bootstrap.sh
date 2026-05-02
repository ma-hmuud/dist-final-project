#!/usr/bin/env bash
set -euo pipefail

docker compose -f docker-compose.hdfs.yml up -d

echo "Waiting for HDFS NameNode..."
until docker exec demand-forecasting-namenode hdfs dfsadmin -safemode get >/dev/null 2>&1; do
  sleep 2
done

echo "Waiting for HDFS to leave safe mode..."
if ! timeout 60 docker exec demand-forecasting-namenode hdfs dfsadmin -safemode wait; then
  echo "Safe mode did not exit automatically; leaving safe mode for local single-node HDFS."
  docker exec demand-forecasting-namenode hdfs dfsadmin -safemode leave
fi

docker exec demand-forecasting-namenode hdfs dfs -mkdir -p /demand_forecasting/raw
docker exec demand-forecasting-namenode hdfs dfs -mkdir -p /demand_forecasting/processed
docker exec demand-forecasting-namenode hdfs dfs -mkdir -p /demand_forecasting/outputs
docker exec demand-forecasting-namenode hdfs dfs -chmod -R 777 /demand_forecasting

echo "HDFS is ready:"
docker exec demand-forecasting-namenode hdfs dfs -ls /
