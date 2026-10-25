import sys
import pandas as pd
import pydantic
import streamlit

print("Python:", sys.version.split()[0])
print("pandas:", pd.__version__)
print("pydantic:", pydantic.VERSION)
print("streamlit:", streamlit.__version__)
print("Setup OK")
