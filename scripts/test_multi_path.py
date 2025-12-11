from simple_optical_table import create_optical_table_figure

experiment = {
    'title': 'Two-path Test',
    'steps': [
        {'type':'laser', 'name':'Laser', 'x':1.0, 'y':3.0, 'position':(1.0,3.0)},
        {'type':'beam_splitter', 'name':'BS1', 'x':3.0, 'y':3.0, 'position':(3.0,3.0)},
        {'type':'mirror', 'name':'M1', 'x':5.0, 'y':2.0, 'position':(5.0,2.0)},
        {'type':'mirror', 'name':'M2', 'x':5.0, 'y':4.0, 'position':(5.0,4.0)},
        {'type':'beam_splitter', 'name':'BS2', 'x':7.0, 'y':3.0, 'position':(7.0,3.0)},
        {'type':'detector', 'name':'DetA', 'x':9.0, 'y':2.0, 'position':(9.0,2.0)},
        {'type':'detector', 'name':'DetB', 'x':9.0, 'y':4.0, 'position':(9.0,4.0)}
    ],
    'beam_path': [
        [(1.0,3.0),(3.0,3.0),(5.0,2.0),(7.0,3.0),(9.0,2.0)],
        [(1.0,3.0),(3.0,3.0),(5.0,4.0),(7.0,3.0),(9.0,4.0)]
    ]
}

fig = create_optical_table_figure(experiment)
fig.savefig('/tmp/two_path_test.png')
print('Saved /tmp/two_path_test.png')
