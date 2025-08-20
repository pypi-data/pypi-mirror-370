### SIBI-DST

Data Science Toolkit built with Python, Pandas, Dask, OpenStreetMaps, NetworkX, SQLAlchemy, GeoPandas, and Folium.

## Example Use Cases

1. **Build DataCubes, DataSets, and DataObjects** from diverse data sources, including **relational databases, Parquet files, Excel (`.xlsx`), delimited tables (`.csv`, `.tsv`), JSON, and RESTful APIs**.
2. **Comprehensive DataFrame Management** utilities for efficient data handling, transformation, and optimization using **Pandas** and **Dask**.
3. **Flexible Data Sharing** with client applications by writing to **Data Warehouses in Clickhouse, local filesystems, and cloud storage platforms** such as **S3**.
4. **Microservices for Data Access** – Build scalable **API-driven services** using **RESTful APIs (`Django REST Framework`, `FastAPI`)** for high-performance data exchange.
5. **Geospatial Analysis** – Utilize **OpenStreetMaps** and **GeoPandas** for advanced geospatial data processing and visualization.

## Supported Technologies

- **Data Processing**: Pandas, Dask
- **Databases & Storage**: SQLAlchemy, Parquet, S3, Clickhouse
- **Mapping & Geospatial Analysis**: OpenStreetMaps, OSMnx, Geopy
- **API Development**: Django REST Framework, FastAPI

## Installation

```bash
# with pip

pip install sibi-dst  # Install only the main package
pip install sibi-dst[geospatial] # Install with geospatial dependencies
pip install sibi-dst[dev,test,geospatial]  # Install all optional dependencies


```
