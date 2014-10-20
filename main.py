#!/usr/bin/python

import sys
import graph_tool as gt
sys.path.append('/lfs/local/0/optas/Oasis/music_graph/music21')
import music21 as m21

def readMidiFile(file_path):
    mf = m21.midi.MidiFile()
    mf.open(file_path)
    mf.read()
    mf.close()
    return m21.midi.translate.midiFileToStream(mf)

def buildGraph(score):
    g = gt.Graph(directed=True)
    eprop_count = g.new_edge_property('short')
    vertex_edge_db = VertexEdgeDb()

    curr_note = None
    last_note = None
    curr_vertex = None
    last_vertex = None
    for note in score.flat.notes:
        last_note = curr_note
        last_vertex = curr_vertex
        curr_note = note
        curr_vertex = vertex_edge_db.getOrAddVertex(curr_note, g)
        if last_note is None:
            continue
        # Add edge and increment edge count as weight.
        e = vertex_edge_db.getOrAddEdge(g, last_vertex, curr_vertex)
        eprop_count[e] += 1
        print 'Note %s -> %s ==> Edge (%d, %d)' % (
                str(vertex_edge_db.noteHash(last_note)),
                str(vertex_edge_db.noteHash(curr_note)),
                last_vertex, curr_vertex)
    g.ep['count'] = eprop_count
    print '-- edge weight --'
    print eprop_count.a
    return g

class VertexEdgeDb:
    def __init__(self):
        self.vertex_map = {} # indexed by noteHash()
        self.edge_map = {}

    def getOrAddVertex(self, note, graph):
        key = self.noteHash(note)
        if key not in self.vertex_map:
            self.vertex_map[key] = graph.add_vertex()
        return self.vertex_map[key]

    def noteHash(self, note):
        # Hash by a tuple (pitches, duration), where pitches is another tuple,
        # converted by an array of pitches sorted by ascending order.
        pitches = sorted([x.midi for x in note.pitches])
        return tuple(pitches), note.duration.quarterLength

    def getOrAddEdge(self, graph, src, dst):
        key = self.edgeHash(src, dst)
        if key not in self.edge_map:
            self.edge_map[key] = graph.add_edge(src, dst)
        return self.edge_map[key]

    def edgeHash(self, src, dst):
        # Hash by a tuple (src, dst) of vertex ID.
        return src, dst

if __name__ == '__main__':
    s = readMidiFile('midi/teddybear.mid')
    g = buildGraph(s)
