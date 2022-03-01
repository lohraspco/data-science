from dash.dependencies import Input, Output, State
import json
from two_component.config import *
from flask import send_from_directory
import os

default_stylesheet = [{"selector": 'node', 'style': {"opacity": 0.65, 'content': 'data(id)'}},
                      {"selector": 'edge', 'style': {"curve-style": "bezier", "opacity": 0.65, 'content': 'data(id)'}}]

styles = {'json-output': {'overflow-y': 'scroll',  'border': 'thin lightgrey solid'},
          'tab': {'height': 'calc(98vh - 105px)'}}


def assign_callbacks(app):
    @app.callback(Output('tap-node-json-output', 'children'),
                  [Input('cytoscape', 'tapNode')])
    def display_tap_node(data):
        return json.dumps(data, indent=2)

    @app.callback(Output('tap-edge-json-output', 'children'),
                  [Input('cytoscape', 'tapEdge')])
    def display_tap_edge(data):
        return json.dumps(data, indent=2)

    @app.callback(Output('cytoscape', 'layout'),
                  [Input('dropdown-layout', 'value')])
    def update_cytoscape_layout(layout):
        return {'name': layout}

    @app.callback(Output('cytoscape', 'stylesheet'),
                  [Input('cytoscape', 'tapNode'),
                   Input('input-follower-color', 'value'),
                   Input('input-following-color', 'value'),
                   Input('dropdown-node-shape', 'value')])
    def generate_stylesheet(node, follower_color, following_color, node_shape):
        if not node:
            return default_stylesheet

        stylesheet = [{"selector": 'node', 'style': {'opacity': 0.8, 'shape': node_shape, 'content': 'data(id)'}},
                      {'selector': 'edge',
                       'style': {'opacity': 0.8, "curve-style": "bezier", 'target-arrow-shape': 'triangle',
                                 'content': 'data(id)'}},
                      {"selector": 'node[id = "{}"]'.format(node['data']['id']), "style": {
                          'background-color': '#B10DC9',
                          "border-color": "purple",
                          "border-width": 2,
                          "border-opacity": 1,
                          "opacity": 1,
                          "label": "data(label)", "color": "#B10DC9", "text-opacity": 0,
                          "font-size": 12, 'z-index': 9999}}]

        for edge in node['edgesData']:
            if edge['source'] == node['data']['id']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['target']),
                    "style": {
                        'background-color': following_color,
                        'opacity': 0.9
                    }
                })
                stylesheet.append({
                    "selector": 'edge[id= "{}"]'.format(edge['id']),
                    "style": {
                            "mid-target-arrow-color": following_color,
                        "mid-target-arrow-shape": "vee",
                        "line-color": following_color,
                        'opacity': 0.9,
                        'z-index': 5000
                    }
                })

            if edge['target'] == node['data']['id']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['source']),
                    "style": {
                        'background-color': follower_color,
                        'opacity': 0.9,
                        'z-index': 9999
                    }
                })
                stylesheet.append({
                    "selector": 'edge[id= "{}"]'.format(edge['id']),
                    "style": {
                        "mid-target-arrow-color": follower_color,
                        "mid-target-arrow-shape": "vee",
                        "line-color": follower_color,
                        'opacity': 1,
                        'z-index': 5000
                    }
                })

        return stylesheet

    @app.callback(
        Output('label-checklist', 'options'),
        [Input('details-radiobutton', 'value')])
    def set_items_options(selected_item):

        return [{'label': i, 'value': i} for i in labelShow_options[selected_item]]

    # @app.callback(
    #     Output('label-checklist', 'value'),
    #     [Input('label-checklist', 'options')])
    # def set_items_value(available_options):
    #     print(available_options)
    #     return available_options

    @app.callback(
        Output('display-selected-values', 'children'),
        [Input('details-radiobutton', 'value'),
         Input('label-checklist', 'value')])
    def set_display_children(selected_cat, selected_item):
        return u'{} is a city in {}'.format(selected_item, selected_cat, )
