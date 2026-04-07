This project studies the Falklands War between Argentina and British forces. The conflict is simulated using NetLogo agent based modeling. There are 2 simulators.

Overall Simulator Runtime: for a given trial:
- The naval-air battle will be run first. 
- The ground battle wil lbe run second and use some of the outputs from the naval-air battle as inputs.
- The data from both trials will be stored as a row in a .csv.
- The data from all trials will be stored in a single .csv.

# 1. main_model.nlogox 
Purpose: simulates the naval-air battle.

Forces (agents)
- Argentinian Forces
    - Attack planes (FAA): skyhawks, daggers, mirages, super etendards
- British Forces
    - Defense planes: sea harriers (SHARs)
    - Aircraft carriers
    - Destroyers
    - Frigates
    - Amphibious landing ships

Simulator Inputs
- The trial ID: each naval-air battle trial gets a corresponding ground battle trial
- Aircraft carrier spawn locations
- Threshold for the number of FAA jets lost when the air battle ends (default to 21 jets lost)

Simulator Runtime
- Spawn carriers at their spawn location
- Starts on 21 May, 00:00
- Ends on Air_Battle_End

Simulator Outputs
- Ground_Battle_Start: The date and time when all non-sunk amphibious ships reach their final target
- Air_Battle_End: The date and time when the number of FAA jets lost equals the threshold
- The number of British destroyers and frigates remaining and their locations by Ground_Battle_Start
- The dates, types, and locations of any British destroyers or frigates sunk between Ground_Battle_Start and Air_Battle_End
- The number of aircraft carriers sunk by Air_Battle_End
- The number of SHARs lost by Air_Battle_End
- The number of FAA jets destroyed by Air_Battle_End, and how that jet was destroyed (lost, SHAR, boats, etc.)
- The number of each type of British boat lost by Air_Battle_End, and how that boat was destroyed
- The number of amhpibious ships load by Air_Battle_End

# 2. main_ground_model.nlogox
Purpose: simulates the ground battle

Forces (agents)
- Argentinian Forces
- British Forces

Simulator Inputs
- The trial ID: each naval-air battle trial gets a corresponding ground battle trial
- Ground_Battle_Start: The date and time when all non-sunk amphibious ships reach their final target
- Air_Battle_End: The date and time when the number of FAA jets lost equals the threshold
- The number of British destroyers and frigates remaining and their locations by Ground_Battle_Start
- The dates, types, and locations of any British destroyers or frigates sunk between Ground_Battle_Start and Air_Battle_End

Simulator Runtime
- Spawn ground troops at their spawn location
- Starts on Ground_Battle_Start
- Ends on Ground_Battle_End 

Simulator Outputs
- Ground_Battle_End: the date and time when either the British forces take/reach their final target (Port Stanley) or all British ground forces are destroyed
- The number of days of conflict between 21 May 00:00 and Ground_Battle_End
- The number of British forces killed by Ground_Battle_End
- The number of Argentian forces killed by Ground_Battle_End
