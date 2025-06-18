import pandas as pd
import os

def load_data(filename):
    path = os.path.join('./utils', filename)
    df = pd.read_csv(path, delim_whitespace=True, header=None)
    df.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'col5', 'S/N', 'col7', 'col8', 'ImagePath', 'col10', 'col11']
    df['ImageFilename'] = df['ImagePath'].apply(lambda x: os.path.basename(x).replace('.png', '_replot.png'))
    return df

