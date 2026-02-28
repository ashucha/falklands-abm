# Sea Harrier Model

I started the first draft model for the SHAR. NetLogo takes a little getting used to, but it's simplicity means you figure it out quickly. 

This code does the following
- There are 2 carriers. These serve as refueling and rearming points for the SHARs. Every so often, they'll RTB to the nearest carrier to refuel and rearm.
- There are 3 SHAR pairs. They spawn at a random (x,y) and their CAP is a different random (x,y). They try to move to their CAP, intercept any dagger formations if they see them, and otherwise loiter at their CAP until they have to RTB. 
- There's 1 dagger formation generated every 100 ticks. It spawns at a random (x,y) and flies in a straight line until it spots a carrier. Once it connects with the carrier, it immediately tries to return to it's spawn location. If it reaches its spawn location, it "lands" and disappears from the map. 

Also I had to manually draw all the icons with the Tools > Shapes Editor. It was annoying...

Please copy and paste/reuse my code if it makes your lives easier. 