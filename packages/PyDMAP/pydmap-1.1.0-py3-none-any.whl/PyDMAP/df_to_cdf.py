import re
import numpy as np
import pandas as pd
from spacepy import pycdf
from datetime import datetime, timezone
    
def convert_column_to_tt2000(col):
    """Convert a datetime64 or float-based epoch column to TT2000, safely elementwise."""
    if np.issubdtype(col.dtype, np.datetime64):
        return np.array([
            pycdf.lib.datetime_to_tt2000(t.to_pydatetime())
            for t in col
        ])

    elif np.issubdtype(col.dtype, np.floating):
        return np.array([
            pycdf.lib.datetime_to_tt2000(datetime.fromtimestamp(t, tz=timezone.utc))
            for t in col
        ])

    else:
        raise TypeError(f"Unsupported time column type: {col.dtype}")


def convert_column_to_tt2000_newer(col):
    """Convert a datetime64 or float-based epoch column to TT2000."""
    if np.issubdtype(col.dtype, np.datetime64):
        return pycdf.lib.datetime_to_tt2000(
            [t.to_pydatetime() for t in col]
        )
    elif np.issubdtype(col.dtype, np.floating):
        # Safe for Python 3.12+
        return np.array([
            pycdf.lib.datetime_to_tt2000(datetime.fromtimestamp(t, tz=timezone.utc))
            for t in col
        ])
    else:
        raise TypeError(f"Unsupported time column type: {col.dtype}")

def test_df_to_cdf(fname=None):
    try:
        import PyDMAP
    except:
        print("PyDMAP tools not enabled, find/install PyDMAP package")
        return
    try:
        import supermag_tools
    except:
        print("SuperMAG tools not enabled, find/install supermag_tools.py")
        return
    
    if fname == None:
        fname = "../sample_data/20141231.supermag.grdvec.60s.rev-0006.dmap"
    mydmap, err = PyDMAP.read_datamap(fname)
    df = supermag_tools.pydmap_to_dataframe(mydmap)
    fname2 = re.sub(r".dmap",".cdf",fname)
    df_to_cdf(df, fname2)
    
def df_to_cdf(df, filename, time_column=None):
    if time_column == None: time_column = df.keys()[0]
    print("Time column is ",time_column)
    if time_column not in df.columns:
        raise ValueError(f"Time column '{time_column}' not found in DataFrame")

    # Convert time to TT2000
    cdf_epochs = convert_column_to_tt2000(df[time_column])

    with pycdf.CDF(filename, '') as cdf:
        # Add Epoch time
        cdf['Epoch'] = cdf_epochs
        cdf['Epoch'].attrs.update({
            'VAR_TYPE': 'support_data',
            'TIME_SCALE': 'TT2000',
            'UNITS': 'ns',
            'FIELDNAM': 'Epoch',
        })

        for col in df.columns:
            if col == time_column:
                continue

            series = df[col]
            kind = series.dtype.kind

            if kind in {'f', 'i'}:
                # float or int
                cdf[col] = series.to_numpy()
                cdf[col].attrs.update({
                    'FIELDNAM': col,
                    'DEPEND_0': 'Epoch'
                })

            elif kind in {'O', 'U', 'S'}:
                # String column
                strings = series.astype(str)
                maxlen = strings.str.len().max()
                fixed_strs = strings.str.ljust(maxlen).astype(f'S{maxlen}')
                cdf[col] = fixed_strs.to_numpy()
                cdf[col].attrs.update({
                    'FIELDNAM': col,
                    'DEPEND_0': 'Epoch'
                })

            else:
                print(f"Skipping column {col} with unsupported dtype {series.dtype}")

        # Global metadata (customize as needed)
        cdf.attrs.update({
            'Title': 'Auto-generated CDF from DataFrame',
            'Generated_by': 'df_to_cdf()',
        })

    print(f"✅ CDF written to: {filename}")

if __name__ == "__main__":
    test_df_to_cdf("../sample_data/20141231.supermag.grdvec.60s.rev-0006.dmap")
    #test_df_to_cdf("../sample_data/2015_LRM.mag.60s.rev-0006.dmap")
    
