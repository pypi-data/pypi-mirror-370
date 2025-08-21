# Automatic data type display
import pandas as pd
df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
tv.print_dataframe(df)  # Shows data types automatically

# Manual data type specification
data = [['Alice', '25'], ['Bob', '30']]
headers = ['Name', 'Age']
data_types = ['<str>', '<i64>']
tv.print_table(data, headers, data_types)

# Data type utilities
from tidy_viewer_py import map_dtype, auto_map_dtypes
map_dtype('int64', 'pandas')  # Returns '<i64>'
auto_map_dtypes(['object', 'int64'])  # Returns ['<str>', '<i64>']
