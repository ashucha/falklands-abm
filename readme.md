# 1982 Falklands War Agent-Based Modeling

Netlogo simulation for the Falklands War. Project for CSE/INTA 6742 Mod, Sim, and Military Gaming at Georgia Tech.

This code does the following:

- There are 2 carriers. They wander around. They launch harriers every so often.
- Each carrier has roughly 2 SHAR pairs in the air. Their CAP is a random (x,y). They try to move to their CAP, intercept any dagger formations if they see them, and otherwise loiter at their CAP until they have to RTB.
- There's 1 dagger formation generated every 100 ticks. It spawns at a random (x,y) along the edges and flies in a straight line until it spots a carrier. Once it connects with the carrier, it immediately tries to return to it's spawn location. If it reaches its spawn location, it "lands" and disappears from the map.
- To demo the SHAR airstrikes feature (for before the GR3s arrive), every so often, a yellow square pops up. The nearest carrier launches a SHAR pair to go strike it and return. Dynamic launching also halfway demos SHAR alert aircraft.
- I added plotting to show air cover performance over time.
- I added datetime utilities to track the current date (so we can do scheduled events) and the overall number of days of the conflict.
- For funsies I made the ocean textured.
- The labels can be adjusted with `stat?` and the drop down, but the setup I found most useful was the dynamic agents display their state, and the boats display their names.

The code is arranged like so:

- `root folder`: contains the main model and readme. Please put as few files here as possible.
- `main_model.nlogox`: the main netlogo file. Please put as little code as possible here to avoid clutter. Include your files at the top (see the examples).
- `turtles/`: contains all the turtle files. Each turtle gets a `*.nls` file that contains the code, a `readme.md` file that explains that's going on, and sometimes a `*.png` for graphics.
  - `shars/`: contains all the files for the shars
  - `carriers/`: contains all the files for the shars
  - For each new breed of turtle, create a new folder here.
- `utils/`: a folder with random functions that aren't specific to turtles but will be useful.
- `.gitignore`: This is a special file for use with Git. Various editors generate all sorts of extra files for convenience, but those files don't belong in the actual project. Add whatever you want to this file and Git will ignore them.

Also I had to manually draw all the icons with the Tools > Shapes Editor. It was annoying... Note: powerpoint now has "Edit Picture" which can use AI to remove backgrounds. It's very good.

Please copy and paste/reuse my code if it makes your lives easier.
