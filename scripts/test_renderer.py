from simple_optical_table import create_optical_table_figure

# Mach-Zehnder style components
experiment = {
    'title': 'Mach-Zehnder Test',
    'steps': [
        {'type':'laser', 'name':'Laser', 'x':1.0, 'y':3.0, 'position':(1.0,3.0)},
        {'type':'beam_splitter', 'name':'BS1', 'x':3.0, 'y':3.0, 'position':(3.0,3.0)},
        {'type':'mirror', 'name':'M1', 'x':5.0, 'y':2.0, 'position':(5.0,2.0)},
        {'type':'mirror', 'name':'M2', 'x':5.0, 'y':4.0, 'position':(5.0,4.0)},
        {'type':'beam_splitter', 'name':'BS2', 'x':7.0, 'y':3.0, 'position':(7.0,3.0)},
        {'type':'detector', 'name':'Det', 'x':9.0, 'y':3.0, 'position':(9.0,3.0)}
    ]
}

fig = create_optical_table_figure(experiment)
fig.savefig('/tmp/mz_test.png')
print('Saved /tmp/mz_test.png')
