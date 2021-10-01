import pandas as pd
import dash
from dash_table import DataTable, FormatTemplate
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px


data = pd.read_excel("UNICEF_framework_V09.xlsx", sheet_name="All", skiprows=2)
data = data.set_index("Reference")


def make_brand(**kwargs):
    return html.Div(
        className="unicef-logo",
        children=[
            html.Div(
                className="unicef-logo__image",
                children=html.Img(
                    src="https://seotest.buzz/dash/assets/svgs/logo-unicef-large.svg",
                ),
            ),
            html.P(
                className="unicef-logo__heading",
                children=[
                    html.Strong(
                        "Survey Tool: ",
                        style={"fontSize": "medium"},
                    ),
                    html.Span("Generic"),
                ],
            ),
        ],
    )


def make_header(**kwargs):
    return html.Header(
        id="header",
        className="header",
        children=[
            html.Div(
                className="header__top",
                children=[
                    html.Div(
                        className="header__inner",
                        children=[
                            html.Div(
                                className="header__row",
                                children=[
                                    html.Div(
                                        className="header__col header__left",
                                        children=[
                                            html.Div(
                                                className="header__logo",
                                                children=[
                                                    make_brand(),
                                                ],
                                            ),
                                            html.Button(
                                                className="header__burger burger js-mobile-menu",
                                                children=[
                                                    html.Span(
                                                        "Menu",
                                                        className="screen-reader-text",
                                                    ),
                                                    html.Span(
                                                        className="burger__line burger__line--1"
                                                    ),
                                                    html.Span(
                                                        className="burger__line burger__line--2"
                                                    ),
                                                    html.Span(
                                                        className="burger__line burger__line--3"
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="header__col header__right",
                                        children=[
                                            html.Div(
                                                className="header__back",
                                                children=[
                                                    html.A(
                                                        "Back to Unicef.org",
                                                        href="https://www.unicef.org",
                                                        target="_blank",
                                                    )
                                                ],
                                            ),
                                            # html.Div(
                                            #     className="header__cta",
                                            #     children=[
                                            #         html.Div(
                                            #             className="header__search"
                                            #         ),
                                            #         html.A(
                                            #             "First Button",
                                            #             href="#",
                                            #             className="btn btn-outline btn-secondary",
                                            #         ),
                                            #         html.A(
                                            #             "Secound Button",
                                            #             href="#",
                                            #             className="btn btn-outline btn-secondary",
                                            #         ),
                                            #     ],
                                            # ),
                                        ],
                                    ),
                                ],
                            )
                        ],
                    )
                ],
            ),
            html.Div(
                className="header__bottom",
                children=[
                    html.Div(
                        className="header__inner",
                        children=[],
                    )
                ],
            ),
        ],
    )


def make_questions(category, questions):
    selections = [
        dbc.Card(
            dbc.CardBody(
                [
                    html.B(
                        "{}: {}".format(
                            question["Question number"], question["Question"]
                        )
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Business", className="mt-2"),
                            dbc.RadioItems(
                                options=[
                                    {
                                        "label": option.split("=")[0].strip(),
                                        "value": int(option.split("=")[1].strip()),
                                    }
                                    for option in question[
                                        "Answer options"
                                    ].splitlines()
                                    if option
                                ],
                                id={
                                    "type": "question-answer",
                                    "id": f"{index}-business",
                                },
                                inline=True,
                            ),
                        ]
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Supply Chain", className="mt-2"),
                            dbc.RadioItems(
                                options=[
                                    {
                                        "label": option.split("=")[0].strip(),
                                        "value": int(option.split("=")[1].strip()),
                                    }
                                    for option in question[
                                        "Answer options"
                                    ].splitlines()
                                    if option
                                ],
                                id={"type": "question-answer", "id": f"{index}-supply"},
                                inline=True,
                            ),
                        ]
                    )
                    if not pd.isna(question["Supply chain"])
                    else None,
                ]
            ),
            className="m-3",
        )
        for index, question in questions.iterrows()
    ]
    selections.extend(
        [
            dbc.Button(
                "Submit",
                id={"type": "survey-submit", "index": category},
                color="primary",
            )
        ]
    )
    return dbc.Tab(
        label=category,
        children=[
            dbc.Form(
                id=f"{category}-form",
                children=selections,
            ),
            html.Div(id={"type": "survey-results", "index": category}),
        ],
    )


groups = []
for category in data["Assessment"].unique():
    groups.append(make_questions(category, data[data["Assessment"] == category]))
groups.append(
    dbc.Tab(
        label="Report",
        children=[
            dbc.Button(
                "Show Results",
                id={"type": "survey-submit", "index": "results"},
                color="primary",
            ),
            html.Div(id={"type": "survey-results", "index": "results"}),
        ],
    )
)


from dash.dependencies import Input, Output, State, ALL, MATCH

external_stylesheets = ["https://seotest.buzz/dash/assets/styles/main.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        make_header(),
        html.Br(),
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row(
                    dbc.Col(
                        [
                            dbc.Tabs(groups),
                        ]
                    ),
                ),
            ],
        ),
    ],
    id="mainContainer",
)


@app.callback(
    Output({"type": "survey-results", "index": MATCH}, "children"),
    Input({"type": "survey-submit", "index": MATCH}, "n_clicks"),
    State({"type": "question-answer", "id": ALL}, "id"),
    State({"type": "question-answer", "id": ALL}, "value"),
    prevent_initial_call=True,
)
def display_dropdowns(click, id, value):

    button_id = dash.callback_context.inputs_list[0]["id"]["index"]
    print(button_id)

    ids = [item["id"] for item in id]
    values = [item if item else 0 for item in value]
    results = dict(zip(ids, values))
    table = pd.DataFrame.from_dict(results, orient="index", columns=["Score"])
    table.index = table.index.str.split("-", 1, expand=True)
    table.index.names = ["Reference", "Scope"]
    table.reset_index(inplace=True)
    table = table.astype({"Reference": int, "Score": int})
    table = table.join(data[["Assessment", "Issue"]], on="Reference")
    table.dropna(inplace=True, subset=["Scope"])

    tables = [html.Br()]

    results = (
        table.groupby(["Scope", "Issue", "Assessment"])
        .agg({"Score": "mean"})
        .reset_index()
    )

    meterial = (
        lambda x: "Not Material"
        if x >= 4
        else (
            "Less material"
            if x >= 3 and x < 4
            else ("Material" if x >= 1 and x < 3 else "Very material")
        )
    )

    rating = (
        lambda x: "Strong"
        if x >= 3
        else (
            "Good" if x >= 2 and x < 3 else ("Moderate" if x >= 1 and x < 2 else "Weak")
        )
    )

    def apply_rankings(assessment, score):
        if assessment == "Materiality":
            return meterial(score)
        else:
            return rating(score)

    results["Materiality"] = results.apply(
        lambda x: apply_rankings(x["Assessment"], x["Score"]), axis=1
    )
    results["Rating"] = results.apply(
        lambda x: apply_rankings(x["Assessment"], x["Score"]), axis=1
    )

    business = results[results["Scope"] == "business"].groupby(["Issue", "Materiality"])
        .agg({"Score": "mean"})
        .reset_index()
    supply = results[results["Scope"] == "supply"]

    combined = (
        pd.concat([business, supply])
        .groupby(["Issue"])
        .agg({"Score": "mean"})
        .reset_index()
    )
    combined["Scope"] = "Combined"

    combined["Materiality"] = combined["Score"].apply(meterial)

    survey_results = DataTable(
        data=results.sort_values("Score").to_dict("records"),
        columns=[
            dict(id="Issue", name="Issue", type="text"),
            dict(id="Score", name="Score", type="numeric"),
            dict(id="Materiality", name="Materiality", type="text"),
        ],
        style_cell={"textAlign": "left"},
        sort_by=[{"column_id": "Score", "direction": "asc"}],
    )

    assessment = results[results["Assessment"] == button_id]

    if button_id == "results":
        tables.append(survey_results)

    elif button_id == "Materiality":

        

        tables.extend(
            [
                html.Div(
                    [
                        html.Label(f"Scope: {scope['Scope'].iloc[0]}"),
                        DataTable(
                            data=scope.sort_values("Score").to_dict("records"),
                            columns=[
                                dict(id="Issue", name="Issue", type="text"),
                                dict(id="Score", name="Score", type="numeric"),
                                dict(id="Materiality", name="Materiality", type="text"),
                            ],
                            style_cell={"textAlign": "left"},
                            sort_by=[{"column_id": "Score", "direction": "asc"}],
                            style_data_conditional=[
                                {
                                    "if": {
                                        "filter_query": "{Score} < 1",
                                        "column_id": "Score",
                                    },
                                    "backgroundColor": "red",
                                    "color": "white",
                                },
                                {
                                    "if": {
                                        "filter_query": "{Score} >= 1 && {Score} < 2",
                                        "column_id": "Score",
                                    },
                                    "backgroundColor": "orange",
                                    "color": "white",
                                },
                                {
                                    "if": {
                                        "filter_query": "{Score} >= 2 && {Score} < 3",
                                        "column_id": "Score",
                                    },
                                    "backgroundColor": "yellow",
                                    "color": "black",
                                },
                            ],
                        ),
                    ]
                )
                for scope in [business, supply, combined]
            ]
        )
    elif button_id == "Due diligence" or button_id == "Mitigation":

        diligence = assessment.groupby(["Issue"]).agg({"Score": "mean"}).reset_index()

        diligence["Rating"] = diligence["Score"].apply(rating)

        tables.extend(
            [
                html.Div(
                    [
                        html.Label(button_id),
                        DataTable(
                            data=diligence.sort_values("Score").to_dict("records"),
                            columns=[
                                dict(id="Issue", name="Issue", type="text"),
                                dict(id="Score", name="Score", type="numeric"),
                                dict(id="Rating", name="Rating", type="text"),
                            ],
                            style_cell={"textAlign": "left"},
                            sort_by=[{"column_id": "Score", "direction": "asc"}],
                            style_data_conditional=[
                                {
                                    "if": {
                                        "filter_query": "{Score} < 1",
                                        "column_id": "Score",
                                    },
                                    "backgroundColor": "red",
                                    "color": "white",
                                },
                                {
                                    "if": {
                                        "filter_query": "{Score} >= 1 && {Score} < 2",
                                        "column_id": "Score",
                                    },
                                    "backgroundColor": "yellow",
                                    "color": "black",
                                },
                            ],
                        ),
                    ]
                )
            ]
        )

    return tables


if __name__ == "__main__":
    app.run_server(debug=True)
