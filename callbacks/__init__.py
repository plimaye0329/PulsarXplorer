from .callback import register_callbacks as register_scatter_callbacks

def register_all_callbacks(app):
    register_scatter_callbacks(app)

