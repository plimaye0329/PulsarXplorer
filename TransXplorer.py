from dash import Dash
from layout import create_layout
from utils.data import load_data
from callbacks import register_all_callbacks

df = load_data()

app = Dash(__name__)
app.layout = create_layout(df)

register_all_callbacks(app, df)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)

