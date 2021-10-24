import statistics

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


def make_question(index, label, question):

    return dbc.FormGroup(
        [
            dbc.Label(label, className="mt-2"),
            dbc.RadioItems(
                options=[
                    {
                        "label": option.split("=")[0].strip(),
                        "value": int(option.split("=")[1].strip()),
                    }
                    for option in question["Answer options"].splitlines()
                    if option
                ],
                id={
                    "type": "question-answer",
                    "id": f"{index}-{label}",
                },
                inline=True,
            ),
        ]
    )


def make_questions(category, questions):
    selections = [
        dbc.Card(
            dbc.CardBody(
                [
                    html.B(
                        [
                            "{}: ".format(question["Question number"]),
                            question["Question"].splitlines()[0],
                            *[html.P(q) for q in question["Question"].splitlines()[1:]],
                        ]
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fa-solid fa-info-circle mx-1"),
                                    "More Info",
                                ],
                                id={
                                    "type": "question-info",
                                    "index": f"{index}-info",
                                },
                                className="my-1",
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody(question["Information"])),
                                id={
                                    "type": "question-info-content",
                                    "index": f"{index}-info",
                                },
                                is_open=False,
                            ),
                        ]
                    ),
                    make_question(index, "Business", question),
                    make_question(index, "Supply Chain", question)
                    if not pd.isna(question["Supply chain"])
                    else None,
                ]
            ),
            className="m-3",
        )
        for index, question in questions.iterrows()
    ]
    return dbc.Tab(
        label=category,
        children=[
            dbc.Form(
                id=f"{category}-form",
                children=selections,
            ),
            html.Div(id={"type": "survey-results", "index": category}),
            dbc.Button(
                "Submit answers",
                id={"type": "survey-submit", "index": category},
                color="primary",
            ),
            html.Br(),
        ],
    )


groups = []
for category in data["Assessment"].unique():
    groups.append(make_questions(category, data[data["Assessment"] == category]))
groups.append(
    dbc.Tab(
        label="Report",
        children=[
            html.Div(
                [
                    html.Br(),
                    dbc.Button(
                        "Show Results",
                        id={"type": "survey-submit", "index": "results"},
                        color="primary",
                    ),
                    html.Div(id={"type": "survey-results", "index": "results"}),
                ]
            )
        ],
    ),
    dbc.Tab(
        label="Geographic",
        children=[
            
        ]
    )
)

meterial = (
    lambda x: "Low Risk"
    if x >= 4
    else ("Medium Risk" if x >= 2 and x < 4 else "High Risk")
)

rating = (
    lambda x: "Strong"
    if x >= 3
    else ("Good" if x >= 2 and x < 3 else ("Moderate" if x >= 1 and x < 2 else "Weak"))
)

priority = (
    lambda x: "Not a priority"
    if x >= 3
    else (
        "Low priority"
        if x >= 2 and x < 3
        else ("Priority" if x >= 1 and x < 2 else "High priority")
    )
)

from dash.dependencies import Input, Output, State, ALL, MATCH

external_stylesheets = [
    "https://seotest.buzz/dash/assets/styles/main.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta2/css/all.min.css",
]
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
    Output({"type": "question-info-content", "index": MATCH}, "is_open"),
    [Input({"type": "question-info", "index": MATCH}, "n_clicks")],
    [State({"type": "question-info-content", "index": MATCH}, "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


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
        table.groupby(["Issue", "Scope", "Assessment"])
        .agg({"Score": "sum"})  # sum of the answers instead
        .reset_index()
        .set_index(["Issue"])
    )

    meteriality = results[results["Assessment"] == "Materiality"]
    due_diligence = results[results["Assessment"] == "Due diligence"]
    mitigation = results[results["Assessment"] == "Mitigation"]

    meteriality["Materiality"] = meteriality["Score"].apply(meterial)
    due_diligence["Rating"] = due_diligence["Score"].apply(rating)
    mitigation["Rating"] = mitigation["Score"].apply(rating)

    due_diligence_average = due_diligence["Score"].mean()
    mitigation["combined_score"] = mitigation["Score"].apply(
        lambda x: statistics.mean([x, due_diligence_average])
    )

    meteriality_combined = meteriality.join(
        mitigation, on="Issue", how="outer", rsuffix="mitigation"
    ).reset_index()
    meteriality_combined["combined_rating"] = meteriality_combined[
        "combined_score"
    ].apply(rating)
    meteriality_combined["priority_score"] = meteriality_combined[
        ["Score", "combined_score"]
    ].mean(axis=1)
    meteriality_combined["priority"] = meteriality_combined["priority_score"].apply(
        priority
    )

    business_meteriality = meteriality_combined[
        meteriality_combined["Scope"] == "Business"
    ]
    supply_meteriality = meteriality_combined[
        meteriality_combined["Scope"] == "Supply Chain"
    ]
    combined_meteriality = (
        pd.concat([business_meteriality, supply_meteriality])
        .groupby(["Issue"])
        .agg({"Score": "mean", "combined_score": "mean", "priority_score": "mean"})
        .reset_index()
    )
    combined_meteriality["Scope"] = "Combined"
    combined_meteriality["Materiality"] = combined_meteriality["Score"].apply(meterial)
    combined_meteriality["combined_rating"] = combined_meteriality[
        "combined_score"
    ].apply(rating)
    combined_meteriality["priority"] = combined_meteriality["priority_score"].apply(
        priority
    )

    if button_id == "results":

        fig = px.scatter(
            combined_meteriality,
            x="Score",
            y="combined_score",
            text="Issue",
            labels={
                "combined_score": "Quality of due diligence",
                "Score": "Materiality of child rights issues",
            },
        )
        fig.update_layout(yaxis_range=[0, 4], xaxis_range=[0, 4])
        fig.update_traces(textposition="bottom right")
        fig.add_hline(y=2)
        fig.add_vline(x=2)

        bar = px.bar(
            combined_meteriality,
            y=["Score", "combined_score"],
            x="Issue",
            barmode="group",
            labels={
                "combined_score": "Due diligence",
                "Score": "Materiality",
            },
            title="Due diligence of material issues",
        )
        fig.update_layout(yaxis_range=[0, 4])

        tables.extend([dcc.Graph(figure=bar), dcc.Graph(figure=fig)])
        tables.extend(
            [
                html.Div(
                    [
                        html.Label(f"Scope: {scope['Scope'].iloc[0]}"),
                        DataTable(
                            data=scope.sort_values("Score").to_dict("records"),
                            columns=[
                                dict(id="Issue", name="Issue", type="text"),
                                dict(id="Score", name="Score (0-4)", type="numeric"),
                                dict(id="Materiality", name="Materiality", type="text"),
                                dict(
                                    name="Score (0-3)",
                                    id="combined_score",
                                    type="numeric",
                                ),
                                dict(name="Rating", id="combined_rating", type="text"),
                                dict(
                                    name="Score (0-3)",
                                    id="priority_score",
                                    type="numeric",
                                ),
                                dict(name="Priority", id="priority", type="text"),
                            ],
                            style_cell={"textAlign": "left"},
                            sort_by=[
                                {"column_id": "Material Score", "direction": "asc"}
                            ],
                            style_header_conditional=[
                                {
                                    "if": {"column_id": "Issue"},
                                    "backgroundColor": "lightBlue",
                                },
                                {
                                    "if": {"column_id": "Score"},
                                    "backgroundColor": "lightBlue",
                                },
                                {
                                    "if": {"column_id": "Materiality"},
                                    "backgroundColor": "lightBlue",
                                },
                                {
                                    "if": {"column_id": "combined_score"},
                                    "backgroundColor": "yellow",
                                },
                                {
                                    "if": {"column_id": "combined_rating"},
                                    "backgroundColor": "yellow",
                                },
                                {
                                    "if": {"column_id": "priority_score"},
                                    "backgroundColor": "green",
                                    "color": "white",
                                },
                                {
                                    "if": {"column_id": "priority"},
                                    "backgroundColor": "green",
                                    "color": "white",
                                },
                            ],
                        ),
                    ]
                )
                for scope in [
                    business_meteriality,
                    supply_meteriality,
                    combined_meteriality,
                ]
            ]
        )

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
                for scope in [
                    business_meteriality,
                    supply_meteriality,
                    combined_meteriality,
                ]
            ]
        )
    elif button_id == "Due diligence" or button_id == "Mitigation":

        results_frame = due_diligence if button_id == "Due diligence" else mitigation

        tables.extend(
            [
                html.Div(
                    [
                        html.Label(button_id),
                        DataTable(
                            data=results_frame.reset_index()
                            .sort_values("Score")
                            .to_dict("records"),
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
    app.run_server(debug=True, host="0.0.0.0")
