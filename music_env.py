# music_parse_tree.py
import random
from graphviz import Digraph
from music21 import stream, note, chord, tempo, meter, dynamics, instrument
import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz-12.2.1-win64\bin"
from PIL import ImageGrab
import tkinter as tk
from tkinter import Canvas

# Recursive musical grammar with self-referential rules
MUSIC_CFG = {
    'Song': [['Intro', 'Section*', 'Outro']],
    'Section': [['Verse', 'Section'], ['Chorus', 'Section'], ['Bridge'], ['']],
    'Intro': [['C4', 'D4', 'E4', 'F4'], ['C4', 'E4', 'G4', 'B4']],
    'Verse': [['Phrase', 'Phrase'], ['Phrase', 'Rest', 'Phrase']],
    'Chorus': [['Harmony', 'ChordPhrase', 'NotePhrase']], 
    'Bridge': [['G4', 'A4', 'B4', 'C5'], ['E4', 'G4', 'A4', 'B4']],
    'Phrase': [['Note', 'Note', 'Note', 'Note'],
               ['Note', 'Phrase'],  
               ['Chord', 'Phrase']],
    'NotePhrase': [['Note', 'Note', 'Note', 'Note']],
    'ChordPhrase': [['Chord', 'Chord', 'Chord']], # Still use ChordPhrase for individual chord selection
    'Note': [['C4'], ['D4'], ['E4'], ['F4'], ['G4'], ['A4'], ['B4']],
    'Chord': [['C_maj'], ['G7'], ['F_maj'], ['A_min']], # Individual chords still available
    'Harmony': [['CommonCadence'], ['SimpleProgression']], # Define Harmony rule
    'Rest': [['r1']],
    'Outro': [['C4', 'G4', 'C4'], ['C4', 'E4', 'G4', 'C4']]
}

CHORD_MAP = {
    'C_maj': ['C4', 'E4', 'G4'],
    'G7': ['G4', 'B4', 'D4', 'F4'],
    'F_maj': ['F4', 'A4', 'C4'],
    'A_min': ['A4', 'C4', 'E4']
}

HARMONIC_PROGRESSIONS = {
    'CommonCadence': ['C_maj', 'F_maj', 'G7', 'C_maj'],
    'SimpleProgression': ['C_maj', 'G7', 'A_min', 'F_maj'],
}

class ParseTreeNode:
    def __init__(self, symbol, children=None):
        self.symbol = symbol
        self.children = children or []
        self.id = id(self)

def generate_parse_tree(grammar, start_symbol='Song', max_depth=5):
    """Generate parse tree with recursion and depth limiting, incorporating harmonic progressions"""
    def expand(symbol, depth, harmony_context=None):
        if depth > max_depth:
            return ParseTreeNode(symbol)

        if symbol == 'Harmony':
            # Choose a harmonic progression
            progression_name = random.choice(list(HARMONIC_PROGRESSIONS.keys()))
            progression = HARMONIC_PROGRESSIONS[progression_name]
            harmony_context = progression # Set harmony context for children
            return ParseTreeNode(symbol, [ParseTreeNode(progression_name)]) # Store progression name in parse tree

        if symbol == 'ChordPhrase':
            if harmony_context:
                # Use chord from harmonic progression
                chord_symbol = harmony_context.pop(0) # Get next chord in progression
                return ParseTreeNode(symbol, [ParseTreeNode(chord_symbol)])
            else:
                # Fallback to random chord if no harmony context
                production = random.choice(grammar[symbol])
                node = ParseTreeNode(symbol)
                for sym in production:
                    node.children.append(expand(sym, depth+1, harmony_context))
                return node


        if symbol not in grammar:
            return ParseTreeNode(symbol)

        production = random.choice(grammar[symbol])
        node = ParseTreeNode(symbol)
        for sym in production:
            if sym.endswith('*'):  # Handle Kleene star
                while random.random() < 0.7:  # 70% chance to continue
                    node.children.append(expand(sym[:-1], depth+1, harmony_context))
            else:
                node.children.append(expand(sym, depth+1, harmony_context))
        return node

    return expand(start_symbol, 0)

def visualize_parse_tree(parse_tree_root):
    """Visualize the parse tree using graphviz and save to parse_tree.png"""
    dot = Digraph(comment='Parse Tree', format='png')
    node_id = 0

    def add_nodes_edges(tree_node):
        nonlocal node_id
        current_id = node_id
        dot.node(str(current_id), tree_node.symbol)
        node_id += 1
        for child in tree_node.children:
            child_id = add_nodes_edges(child)
            dot.edge(str(current_id), str(child_id))
        return current_id

    add_nodes_edges(parse_tree_root)
    dot.render('parse_tree', view=False)  # Save to parse_tree.png

def visualize_music21_structure(score):
    """Create a Tkinter visualization of the music21 stream structure as a parse tree and save it to an image file"""
    root_tk = tk.Tk()
    root_tk.title("Music21 Structure Visualization")
    # root_tk.withdraw()  # Hide the window - now we want to show it

    canvas_width = 1200
    canvas_height = 800

    canvas = Canvas(root_tk, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack()

    # Extract music21 structure
    def extract_structure(element, parent_x, parent_y, level=0):
        # Start with the Song node
        if level == 0:
            canvas.create_oval(parent_x-30, parent_y-30, parent_x+30, parent_y+30, fill="lightblue")
            canvas.create_text(parent_x, parent_y, text="Song", font=("Arial", 12, "bold"))

            # Create section nodes
            sections = ["Intro", "Verse", "Chorus", "Bridge", "Outro"]
            section_width = canvas_width / (len(sections) + 1)

            # Draw section nodes based on actual content
            y_offset = 100
            current_section = None
            section_nodes = {}

            for i, section in enumerate(sections):
                section_x = (i + 1) * section_width
                section_nodes[section] = (section_x, parent_y + y_offset)

                
                section_exists = True 

                if section_exists:
                    # Draw section node
                    canvas.create_oval(section_x-25, parent_y+y_offset-25,
                                      section_x+25, parent_y+y_offset+25,
                                      fill="lightblue")
                    canvas.create_text(section_x, parent_y+y_offset,
                                      text=section, font=("Arial", 10))
                    # Connect to parent
                    canvas.create_line(parent_x, parent_y+30,
                                      section_x, parent_y+y_offset-25)

            # Now extract the actual notes/chords and connect them to sections
            notes_y = parent_y + y_offset + 100
            notes_per_row = 10
            note_spacing = canvas_width / (notes_per_row + 1)

            flat_notes = [e for e in element.recurse().notes]

            for i, note_obj in enumerate(flat_notes):
                row = i // notes_per_row
                col = i % notes_per_row

                note_x = (col + 1) * note_spacing
                note_y = notes_y + (row * 60)

                # Determine parent section (simplified logic)
                # In a real implementation, you'd analyze the temporal position
                parent_section = sections[min(i // 5, len(sections)-1)]
                parent_coords = section_nodes[parent_section]

                # Draw note node
                if 'Chord' in note_obj.classes:
                    node_text = '.'.join([p.nameWithOctave for p in note_obj.pitches])
                    fill_color = "#e6ccff"  # Light purple for chords
                else:
                    node_text = note_obj.nameWithOctave
                    fill_color = "#ccffcc"  # Light green for notes

                canvas.create_oval(note_x-20, note_y-20, note_x+20, note_y+20,
                                  fill=fill_color)
                canvas.create_text(note_x, note_y, text=node_text,
                                  font=("Arial", 8))

                # Connect to parent section
                canvas.create_line(parent_coords[0], parent_coords[1]+25,
                                  note_x, note_y-20)

    # Start visualization with the score
    extract_structure(score, canvas_width/2, 50)

    
    # try:
    #     canvas.update()
    #     image = ImageGrab.grab(bbox=(0, 0, canvas_width, canvas_height))
    #     image.save("music21_structure.png")
    #     print("Parse tree visualization saved as music21_structure.png")
    # except Exception as e:
    #     print(f"Error saving visualization: {str(e)}")

    # root_tk.destroy() 
    root_tk.mainloop() # Keep the window open


def parse_tree_to_music(node):
    """Convert parse tree to music21 stream, incorporating harmonic progressions"""
    score = stream.Score()
    score.append(tempo.MetronomeMark(number=120))
    part = stream.Part()

    def traverse(n, current_stream, harmony_progression=None):
        if n.symbol == 'Harmony':
            # Get the progression name from the child node
            if not n.children:
                print(f"Error: Harmony node has no children! Node: {n.symbol}")
                return
            progression_name_node = n.children[0]
            progression_name = progression_name_node.symbol
            harmony_progression = list(HARMONIC_PROGRESSIONS[progression_name]) # Create a copy to avoid modifying original

        if n.symbol == 'ChordPhrase':
            if harmony_progression:
                if harmony_progression: # Check again in case progression is empty
                    chord_symbol = harmony_progression.pop(0)
                    current_stream.append(chord.Chord(CHORD_MAP[chord_symbol]))
            else: # Fallback to random chord if no harmony context (shouldn't happen in Chorus)
                chord_choice = random.choice(list(CHORD_MAP.keys()))
                current_stream.append(chord.Chord(CHORD_MAP[chord_choice]))
        elif n.symbol in CHORD_MAP:
            current_stream.append(chord.Chord(CHORD_MAP[n.symbol]))
        elif n.symbol == 'r1':
            current_stream.append(note.Rest(quarterLength=1))
        elif len(n.symbol) == 2 and n.symbol[1] == '4':
            current_stream.append(note.Note(n.symbol))
        for child in n.children:
            traverse(child, current_stream, harmony_progression)

    traverse(node, part)
    score.append(part)
    return score

def main():
    # Generate and visualize parse tree
    parse_tree = generate_parse_tree(MUSIC_CFG)
    visualize_parse_tree(parse_tree) # Visualize parse tree using graphviz

    # Generate music
    score = parse_tree_to_music(parse_tree)

    # Save outputs
    score.write('midi', fp='recursive_music.mid')
    score.write('musicxml', fp='recursive_score.mxml')

    midi_file = 'recursive_music.mid'
    musicxml_file = 'recursive_score.mxml'

    print(f"Generated MIDI file: {midi_file}")
    print(f"Generated MusicXML file: {musicxml_file}")

    # Show musical structure first
    print("\nMusical structure:")
    score.show('text')

    visualize_music21_structure(score)
   

if __name__ == "__main__":
    main()
