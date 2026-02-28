# Sea Harrier Model

I started the first draft model for the SHAR. NetLogo takes a little getting used to, but it's simplicity means you figure it out quickly. 

This code does the following
- Each carrier has roughly 2 SHAR pairs in the air. Their CAP is a random (x,y). They try to move to their CAP, intercept any dagger formations if they see them, and otherwise loiter at their CAP until they have to RTB. 
- Every so often, a yellow square pops up. The nearest carrier launches a SHAR pair to go strike it and return. 
- Strikes launch at max speed.
- Note: fuel burn and speed do NOT account for minutes-per-tick. 