# Noah's Coding Guide for Non-CS People!
This is intended to make it easier for the non-CS peeps to code their models. Other tips:
- Gemini is a good resource, provided you tell it you're working with NetLogo
- The NetLogo dictionary has all the built-in function descriptions. 

## The File Structure
- `root folder`: contains the main model and readme. Please put as few files here as possible.
- `main_model.nlogox`: the main netlogo file. Please put as little code as possible here to avoid clutter. Include your files at the top (see the examples).
- `turtles/`: contains all the turtle files. Each turtle gets a `*.nls` file that contains the code, a `readme.md` file that explains that's going on, and sometimes a `*.png` for graphics.
  - `shars/`: contains all the files for the shars
  - `carriers/`: contains all the files for the shars
  - For each new breed of turtle, create a new folder here.
- `utils/`: a folder with random functions that aren't specific to turtles but will be useful.
- `.gitignore`: This is a special file for use with Git. Various editors generate all sorts of extra files for convenience, but those files don't belong in the actual project. Add whatever you want to this file and Git will ignore them.

## Interacting with `main_model.nlogox'
- Including your file(s)
    - `__includes [ "<path to your file here>" ]`
    - Make sure you include whatever files you've written, or the main code won't be able to see the functions. Don't forget the folder structure. Use the existing code as an example
- `globals []`: These are the global variables. All files everywhere will be able to see these variables. If you modify these variables anywhwere, they're changed everywhere. I imagine the only variables we'll make global are the ones all the files *have* to see, like constants.
- `turtles-own []`: All turtles of all breeds will have these variables. Add content here sparingly. Stuff goes here so that you don't have to manually add it to a bunch of other turtles. If most of the turtles will have a variable, it makes sense to add it here. Honeslty, even these 2 variables might get removed later. 
- `breed [ <plural name> <singular name> ]`: These are all the breeds of turtles. Singular/plural names have distinct meanings in NetLogo. Breeds will be drawn in the order they're declared. Currently, carrier is declared first, so everything else will be displayed *on top* of the carriers.
- `to setup`: this is a procedure that does all the setup. It initializes turtles, patches, and global values. `reset-ticks` also helps with plotting. 
    - To initialize turtles, create a setup procedure in your file and call it here. Ex: `setup-carriers`. Notice how I left the setup of the SHARs to the carriers, and didn't include it here, since the SHARs will be hatched dynamically by the carriers.
- `to go`: This is the core loop that runs each tick. Basically, each turtle has a function that executes one tick. To run all the turtles, call the procedures.
    - I'm unsure if you can call the procedures directly or if you need the command `ask <turtle-plural> [ command(s) ]`
- Date stuff: note that date stuff isn't stuck at one turtle, but it's still not in the main file. This is an example of something that belongs in `util/`.
- That should be as much as you put into `main_model.nlogox`. Everything else should go in your `<turtle>_model.nls` file. Currently, the daggers are still here (but they shouldn't be). They were so simple I just left them there for basic testing. Once Grace implements all the FAA jets, that code will go into a separate file and the dagger code here will be removed.

## Writing your `<turtle>_model.nsl`
I'm going to use the carriers example. Replace carriers with whatever your turtle name is. Note: the name can be whatever you want, that's just what I went with. 
- `carriers-own []`: These are all the variables your breed will have. These need to be initialized in your setup procedure
- Bringing the breed into existence `to setup-carriers`: This procedure is called by `main_model.nlogox` so your breed of turtle can be initialized. This is where you create your turtles, especially the number, and initialize their values. 
- Creating turtles `create-carriers`: This is where you create the individual turtles of the breed. I only had 2 to create, but I needed distinct names for them, so Gemini just said it would be easier to make each one manually. I think you can also do it with lists if you need to.
- Hatching turtles `to launch-shars`: Any breed can create turtles of another breed with the `hatch-<breed plural> <# to hatch> [ <initializations> ]`. Since the SHARs launched from the carriers, it made sense to have the carriers create and manage them. Most of the other breeds will probably be hatched at start time, maybe with the exception of British ground troops being hatched from amphibious landing vehicles?
- Passing arguments to a procedure: check out `launch-shars [ num ms obj-xy ]`. This lets me launch SHARs and change up the number, the mission, and their target objective, while reusing aaaaaall the other code. 
    - For some reason, NetLogo requires you to create another local variable with `let`. Idk why. I ended up having to make 3 versions of the same variables...
- `to move-carriers`: This the logic that a turtle does each tick
    - A good structure for me was
        1. Get all the data from the surrounding patches/turtles that the logic needs to make decisions.
            - For example, I wanted to always do a check with the SHARs if they were out of fuel. I put that if statement here. If true, I changed state to `"rtb"` and ignored all other states.
        2.  Make decisions based on your current state. Since these are sequential, it may be helpful to do the higher priority state checks first. 
            - Structure 1: waterfall. All of the if statements run, but only 1 *should* be true, unless you change state in the middle of the logic (be careful with this). 
                ```
                if state = <state1> [ <state1 logic> ]
                if state = <state2> [ <state2 logic> ]
                ```
            - Structure 2: nested. Only 1 if statement will run. More annoying to manage imo

                ```
                ifelse state = <state1> [ 
                    <state1 logic> 
                ] [ 
                    ifelse state = <state2> [ 
                        <state2 logic> 
                    ] [ <other states> ] 
                ]
                ```
        3. Do whatever actions you do every time, regardless of state. For me, this was mostly just `forward speed` to actually move your stuff forward.
        4. Update UI stuff, like the label.
- Any helper functions you'll need, so you don't rewrite code in a bunch of different places. Here, `spawn-shars?` is a helper function. 

### Helpful Tips and Program Snippets
- Get a random number: `random <max>` or `random-float <max>`.
- Set to random location: `setxy random-xcor random-ycor`
- Getting the closest turtle of a breed to me: `let <var> min-one-of <breed plural> [distance myself]`
    - If you use this in logic, you'll have to check that `<var> != nobody` every time. you want to use it, or it will throw errors.
    - Closest turtle within a distance threshold: `if distance <var> < <threshold> [ <action> ]`
    - Ways to check if one turtle has "reached" another turtle or a location: 
        ```
        if distance patch <x> <y> < (speed) []
        if distance patch <x> <y> < (1.5 * speed)>[]
        if distance <var> < (speed) []
        if distance <var> < (1.5 * speed)
        ```
        The 1.5 multiplier prevents glitching in case the turtles overshoot. Sometimes `move-to <var>` along with `set speed 0` will also fix glitching. 
- Useful for turning slowly by doing math with headings: `subtract-headings`
- Set the icon `set shape "<whatever you named your icon>"`. Make icons in the Turtle Shape Editor. 
- Making a list (array in some languages): `(list <item0> <item2> ...)`. Index from 0
    - Indexing a list: `(item i <list name>)`
- Protip: start your state logic by setting the variables for that state right at the beginning. That way, whenever you want to change states, all you have to do is `set state <state>` instead of initializing a bunch of variables first. 
- Getting your turtle to point at a target/location: `facexy <x> <y>` or `face <target>`
- Getting a turtle with a specific value (SHAR `my-carrier` is an example): `let <my-var> one-of <breed plural> with [ <its-var> = <specific value>]`