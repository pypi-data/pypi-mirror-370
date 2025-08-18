"""cython代码实现pandas.to_dict() api"""
from pandas.core.dtypes.common import is_numeric_dtype

cpdef dataframe_to_dict(df):
    cdef int i
    cdef int df_len
    cdef str col
    cdef dict col_arr_map
    cdef dict record
    cdef int le

    df_len = len(df)  # df的行数
    cols = list(df)  # df.columns.to_list()
    length = len(cols)  # df的列数
    col_arr_map = {}

    for i in range(length):
        if not is_numeric_dtype(df[cols[i]].dtype):  # 如果是不是数字类型，使用numpy array存储
            col_arr_map[cols[i]] = df[cols[i]].to_numpy()
        else:
            col_arr_map[cols[i]] = df[cols[i]].tolist()  # 如果是数字类型，则使用python原生list存储

    records = [None] * len(df)

    for i in range(df_len):
        record = dict()
        for j in range(length):
            record[cols[j]] = col_arr_map[cols[j]][i]
        records[i] = record
    return records