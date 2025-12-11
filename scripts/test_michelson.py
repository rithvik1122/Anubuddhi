from simple_optical_table import create_optical_table_figure

# Michelson Interferometer with backtracking path
experiment = {
    'title': 'Michelson Interferometer',
    'steps': [
        {'type':'laser', 'name':'HeNe Laser', 'x':1.0, 'y':3.0, 'position':(1.0,3.0)},
        {'type':'beam_splitter', 'name':'50:50 BS', 'x':3.0, 'y':3.0, 'position':(3.0,3.0)},
        {'type':'mirror', 'name':'Fixed Mirror', 'x':3.0, 'y':5.0, 'position':(3.0,5.0)},
        {'type':'mirror', 'name':'Movable Mirror', 'x':5.0, 'y':3.0, 'position':(5.0,3.0)},
        {'type':'detector', 'name':'Screen', 'x':1.0, 'y':1.0, 'position':(1.0,1.0)}
    ],
    'beam_path': [
        [(1.0, 3.0), (3.0, 3.0), (3.0, 5.0), (3.0, 3.0), (5.0, 3.0), (3.0, 3.0), (1.0, 1.0)]
    ]
}

fig = create_optical_table_figure(experiment)
fig.savefig('/tmp/michelson_test.png', dpi=150, bbox_inches='tight')
print('Saved /tmp/michelson_test.png')
print(f'Beam path has {len(experiment["beam_path"][0])} points with backtracking through BS')
