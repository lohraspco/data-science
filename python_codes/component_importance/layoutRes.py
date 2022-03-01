import dash_core_components as dcc
import dash_html_components as html
import networkx as nx

import dash_cytoscape as cyto
import gu.dash_reusable_components as drc
from two_component.config import *

default_stylesheet = [{"selector": 'node', 'style': {"opacity": 0.20, 'content': 'data(id)'}, "text-wrap": "wrap"},
                      {"selector": 'edge',
                       'style': {"curve-style": "bezier", 'target-arrow-shape': 'triangle', "opacity": 0.65,
                                 'content': 'data(id)'}, "text-wrap": "wrap"}, ]

styles = {'json-output': {'overflow-y': 'scroll', 'height': 'calc(50% - 25px)', 'border': 'thin lightgrey solid'},
          'tab': {'height': 'calc(98vh - 105px)'}}


def layoutGen(G):
    tab1 = [drc.SectionTitle(title='Layout', size=3, color='white'),
            drc.NamedDropdown(name='Layout', id='dropdown-layout',
                              options=drc.DropdownOptionsList('random', 'grid', 'circle',
                                                              'concentric', 'breadthfirst', 'cose'),
                              value='breadthfirst', clearable=False),

            drc.NamedDropdown(name='Node Shape', id='dropdown-node-shape', value='ellipse',
                              clearable=False,
                              options=drc.DropdownOptionsList('ellipse', 'triangle', 'rectangle',
                                                              'diamond', 'pentagon', 'hexagon', 'heptagon',
                                                              'octagon', 'star', 'polygon', )),

            drc.NamedInput(name='Followers Color', id='input-follower-color', type='text',
                           value='#0074D9', ),

            drc.NamedInput(name='Following Color', id='input-following-color', type='text',
                           value='#FF4136', ),
            dcc.RadioItems(
                id='details-radiobutton',
                options=[{'label': k, 'value': k} for k in labelShow_options.keys()],
                value='detailed'),
            dcc.Checklist(id='label-checklist'),
            html.Div(id='display-selected-values')]

    tab2 = [html.Div(style=styles['tab'],
                     children=[html.P('Node Object JSON:'),
                               html.Pre(id='tap-node-json-output', style=styles['json-output']),
                               html.P('Edge Object JSON:'),
                               html.Pre(id='tap-edge-json-output', style=styles['json-output'])
                               ])]
    rowss = []
    lay = []
    lay.append(html.Div([dcc.Location(id='url', refresh=False),
                         html.Link(rel='stylesheet', href='../gu/static/bWLwgP.css')]))

    cytoEl = cyto.Cytoscape(id='cytoscape', elements=G,
                            layout={'name': 'preset'},
                            style={'height': '95vh', 'width': '800'})
    rowss.append(html.Div([cytoEl], className='six columns', style={'display': 'inline-block'}))
    # children=[cyto.Cytoscape(id='cytoscape', elements=cy_edges + cy_nodes,
    #                                                  style={'height': 'calc(100vh - 16px)', 'width': '100%'})]))
    rowss.append(html.Div(className='six columns',
                          # style={'height': '100vh', 'float': 'right',
                          #        'background-color': '#f5f0f0', 'margin': '-7.8px'},
                          children=[dcc.Tabs(id='tabs', children=[
                              dcc.Tab(label='Control Panel', children=tab1),
                              dcc.Tab(label='JSON', children=tab2)]), ]))
    lay.append(html.Div(className='row', children=rowss))
    lay.append(html.Div(html.Img(src='/assets/verification.jpg')))
    return html.Div(lay)
