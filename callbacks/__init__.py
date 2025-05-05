from .scatter import register_callbacks as register_scatter_callbacks

def register_all_callbacks(app, df):
    register_scatter_callbacks(app, df)

