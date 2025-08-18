import plotly.graph_objects as go
from plotly.graph_objects import Figure

from risk_kit.expert_scorecard.models import ExpertScorecard


class ScorecardVisualizer:
    """
    Simple table-based visualizer for Expert Scorecards.

    Provides a clean table view showing:
    - Feature names and families
    - Bucket definitions and points
    - Feature weights
    """

    def __init__(self, scorecard: ExpertScorecard):
        self.scorecard = scorecard

    def create_scorecard_table(self) -> Figure:
        table_data = self.scorecard.get_table_data()

        all_rows = []
        for _, feature_rows in table_data.items():
            all_rows.extend(feature_rows)

        headers = list(all_rows[0].keys())
        display_headers = [h.replace("_", " ").title() for h in headers]

        values = []
        for header in headers:
            column_values = [row.get(header, "") for row in all_rows]
            values.append(column_values)

        fig = go.Figure(
            data=[
                go.Table(
                    header={
                        "values": display_headers,
                        "fill_color": "lightblue",
                        "align": "left",
                        "font": {"size": 12, "color": "black"},
                        "height": 40,
                    },
                    cells={
                        "values": values,
                        "fill_color": "white",
                        "align": "left",
                        "font": {"size": 11},
                        "height": 30,
                    },
                )
            ]
        )

        num_rows = len(all_rows)
        fig.update_layout(
            title={
                "text": f"<b>{self.scorecard.name}</b><br><sub>{self.scorecard.description} (v{self.scorecard.version})</sub>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            height=max(400, num_rows * 35 + 150),
            margin={"l": 20, "r": 20, "t": 80, "b": 20},
        )

        return fig

    def to_html(self) -> str:

        fig = self.create_scorecard_table()
        return fig.to_html(include_plotlyjs="cdn")

    def save_html(self, filename: str) -> None:
        fig = self.create_scorecard_table()
        fig.write_html(filename)
