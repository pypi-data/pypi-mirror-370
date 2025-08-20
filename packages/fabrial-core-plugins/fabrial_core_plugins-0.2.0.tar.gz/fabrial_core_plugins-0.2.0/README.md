Built-in plugins for [Fabrial](https://github.com/Maughan-Lab/fabrial.git).

## Categories

### Flow Control
Steps for controlling the flow of the sequence.

#### `Hold`
Hold for a specified duration.

#### `Loop`
Repeat the nested steps a specified number of times. Data for the nested steps is placed in a `Loop` directory.

#### `Simultaneous`
Run the nested steps "simultaneously". In reality, this rapidly switches between the nested steps; when one pauses, another resumes.
