
# Grammar-Based Music Generation with Python

**Generate structured, creative music using context-free grammars, parse trees, and the music21 library.**

## 🌟 Description

This project demonstrates how musical compositions can be generated algorithmically using grammar rules—much like how sentences are formed in language. By defining musical "grammars" and leveraging powerful Python libraries, you can create random but musically coherent MIDI pieces, visualize their grammatical parse trees, and experiment with styles and structure.

**Key Features:**
- Define musical grammars for melodies, chord progressions, and full song structures  
- Add randomness for creative, unique outputs each time  
- Export generated music to MIDI/MusicXML and visualize the parse trees  
- Ready to extend with your own musical rules or integrate with machine learning

## Quickstart

### 1. Clone this repository

```bash
cd grammar-music-generator
```

### 2. Install dependencies

We recommend using a virtual environment.

```bash
pip install music21 matplotlib networkx pygraphviz
```
>

### 3. Run the main script

```bash
python music_generator.py
```

This will generate several MIDI files along with visualizations of their parse trees:
- `tonal_grammar_music.mid` — Standard song structure  
- `l_system_grammar_music.mid` — Recursive L-system pattern  
- `chord_grammar_music.mid` — Chord progression

Open the MIDI files with any DAW, sequencer, or a simple software synth.



## 🧩 Customizing Your Music

You can define your own grammars and rules!

Check out the functions `create_tonal_grammar`, `create_l_system_grammar`, and `create_chord_progression_grammar` in `music_generator.py`—or invent your own structures for melodies, rhythms, articulations, and more.

To add your own musical rules, simply extend or modify the grammar definitions in the Python code!

## Parse Tree Visualization

For every generated song, a `.png` file visualizing the parse tree will be created.  
This helps you see and debug how the grammar produced your music.

If you run into issues with parse tree rendering, see the note about installing Graphviz and PyGraphviz under [Dependencies](#dependencies).

## 🏗️ Dependencies

- [music21](music representations and MIDI)
- [matplotlib](for parse tree images)
- [networkx](parse tree graphs)
- [pygraphviz] (parse tree visualization backend)


## Author

P Manas

Happy composing!