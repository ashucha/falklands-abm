# I'm not as familiar with NetLogo as I am with python, so I started writing out my model behavior in python. Once I'm happy with the logic I'll convert it. 

from enum import Enum, auto
from random import random
import uuid

class Weather(Enum):
    CLEAR = auto()
    WEATHER = auto()

class Mission(Enum):
    CAP = 1
    STRIKE = 2

class Speed(Enum):
    CRUISE = 1
    MAX = 2

class Carrier(Enum):
    HERMES = 'Hermes'
    INVINCIBLE = 'Invincible'

class BoatType(Enum):
    CARRIER = 'CARRIER'

class AcftType(Enum):
    SHAR = 'SHAR'
    MIRAGE = 'MIRAGE'
    DAGGER = 'DAGGER'
    SUE = 'SUE'
    SKYHAWK = 'SKYHAWK'
    
class Turtle:
    def __init__(self, tpt, loc: Coord, type):
        self.uuid = uuid.uuid1()
        self.tpt = tpt # time per tick
        self.loc = loc
        self.type = type

    def get_loc(self):
        return self.loc
    
    def tick(self): 
        '''Will be implemented by children'''
        pass

class Boat(Turtle):
    def __init__(self, tpt, loc: Coord, type: BoatType, name = None):
        super().__init__(tpt, loc, type)
        self.name = name

class Aircraft(Turtle):
    def __init__(self, tpt, loc: Coord, type: list[AcftType]):
        super().__init__(tpt, loc, type)

class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class FAA_Aircraft(Aircraft):
    def __init__(self, tpt, loc, type, altitude):
        super().__init__(tpt, loc, type)
        self.altitude = altitude

class Task(Enum):
    CAP_TRANSIT = auto()
    LOITER = auto()
    INVESTIGATE = auto()
    INTERCEPT = auto()
    URGENT_INTERCEPT = auto()
    AIR_ENG = auto() # air engagement
    STRIKE = auto() # strike run
    RTB = auto() # return to the carrier

TIME_PER_TICK = 2.0/60.0 # measured in hours
MAX_FUEL = 830 # imp gal
OBJ_THRESHOLD = 0 # basically impossible that your location will match exactly, just need to be close enough 
AIM9L_RANGE = 0
VIS_CONTACT_RANGE_CLEAR = 0
VIS_CONTACT_RANGE_WEATHER = 0

class SHAR(Aircraft):
    def __init__(self, tpt, loc: Coord, speed, carrier: Boat, mission, objective: Coord, name = None, target = None, task = Task.TRANSIT):
        '''
        Params
            tpt: Time Per Tick. So the class can calculate values as a function of time
            loc: launch loc
            speed: starting speed
            carrier: which carrier it launched from and will return to
            mission: the purpose of the flight
            task: describes it's current task
            tgt_loc: the location it's currently flying to
        '''
        super().__init__(tpt, loc, type = [AcftType.SHAR, AcftType.SHAR])
        self.carrier = carrier
        self.speed = speed
        self.mission = mission
        self.fuel = MAX_FUEL
        self.set_task(task, objective, target)

        self.munitions = {'Gun':[True, True]}
        match self.mission:
            case Mission.CAP:
                self.munitions['AIM9L'] = [2,2] # modeling a 2 ship
            case Mission.STRIKE:
                if random() > 0.5:
                    self.munitions['Mk17'] = [2,2] # modeling a 2 ship
                else:
                    self.munitions['BL755'] = [2,2] # modeling a 2 ship

    def get_heading(self):
        return Coord(self.objective.x - self.loc.x, self.objective.y - self.loc.y)

    def set_task(self, task: Task, objective = None, target: Turtle = None):
        self.task = task
        self.objective = objective
        self.target = target # None unless it has a designated turtle/formation it's attempting to intercept

        match self.task:
            case Task.CAP_TRANSIT:
                self.speed = Speed.CRUISE
                self.heading = self.get_heading()
            case Task.LOITER: # will stay in place but still burn fuel
                self.speed = Speed.CRUISE
                self.heading = None
            case Task.INVESTIGATE: # cued by boats but no visual confirmation of enemy 
                self.speed = Speed.CRUISE
                self.heading = self.get_heading()
            case Task.INTERCEPT: # visual confirmation of enemy
                self.speed = Speed.MAX
                self.objective = self.target.get_loc()
                self.heading = self.get_heading()
            case Task.URGENT_INTERCEPT:
                self.speed = Speed.MAX
                self.heading = self.get_heading()
            case Task.AIR_ENG: # will stay in place but still burn fuel
                self.speed = Speed.MAX
                self.heading = None
            case Task.STRIKE: 
                self.speed = Speed.CRUISE
                self.heading = self.get_heading()
            case Task.RTB: 
                self.speed = Speed.CRUISE
                self.objective = self.carrier.get_loc()
                self.heading = self.get_heading()

    def check_rtb(self):
        if self.mission == Mission.CAP:
            # TODO check if 10min loiter time is up
            if self.loiter_time <= 0:
                return True
        # TODO check if I'm at bingo fuel based on the current location
        
        # TODO check if I have remaining munitions
        _, val = self.munitions.items()
        if 0 in val and self.task != Task.AIR_ENG: # if either SHAR is out of munitions, ignore if in AIR_ENG because switch to guns
            return True
        
        return False
    
    def check_visual_contact(self) -> FAA_Aircraft:
        '''Returns the closest enemy formation within visual range'''
        if self.get_weather == Weather.CLEAR:
            thresh = VIS_CONTACT_RANGE_CLEAR
        else:
            thresh = VIS_CONTACT_RANGE_WEATHER

        closest_contact = None
        min_dist = 99999999

        for f in FAA_formations: # this would be global variable
            dist = abs(self.loc - f.loc)
            if dist <= thresh and dist < min_dist: # if there's a formation within visual range
                closest_contact = f
                min_dist = dist

        return closest_contact

    def get_weather(self) -> Weather:
        ...

    def do_task(self): # RESUME WORK HERE: Working through the logic of stuff. Specifically INTERCEPT and AIR_ENG
        '''Core decision loops'''
        # TODO Key question: do we want to move THEN decide? Or decide THEN move? Currently decide then move.
        if self.check_rtb(): 
            self.set_task(Task.RTB)
        vc_contact = self.check_visual_contact() # only calculate this once per 2 ship

        match self.task:
            case Task.CAP_TRANSIT:
                if not vc_contact is None: # if the SHAR spots enemy aircraft in range
                    self.set_task(task=Task.INTERCEPT, target=vc_contact)
                    self.do_task()
                    return
                if abs(self.objective - self.loc) <= OBJ_THRESHOLD: # you reached the target 
                    self.set_task(task=Task.LOITER)
                else: # you haven't reached the target yet
                    self.move()
            case Task.LOITER: # will stay in place but still burn fuel
                # TODO do something to reduce the amount of loiter time remaining
                self.move()
            case Task.INVESTIGATE: # cued by boats but no visual confirmation of enemy 
                # TODO hang around at objective until visual contact with enemy
                self.move()
            case Task.INTERCEPT: # visual confirmation of enemy
                # TODO if not in_range of enemy: move, else: task = AIR_ENG
                if abs(self.target.loc - self.loc) <= AIM9L_RANGE: # within firing range
                    self.set_task(task=Task.AIR_ENG)
                    self.do_task()
                    return
                else: 
                    self.move()
            case Task.URGENT_INTERCEPT:
                # TODO if not in_range of enemy: move, else: task = AIR_ENG
                self.move()
            case Task.AIR_ENG: # will stay in place but still burn fuel
                # TODO do RNG every 2min to check kills, depends on if the SHAR is using guns or missiles
                # TODO if AIR_ENG is resolved: set task appropriately
                ...
            case Task.STRIKE: 
                # TODO if not reached_obj: move, else: task = RTB
                self.move()
            case Task.RTB: 
                self.move()
        
    def get_fuel_burn(self) -> float:
        '''Returns the fuel consumed in this tick as a function of Time per Tick and current speed'''
        ...

    def get_move_dist(self) -> Coord:
        '''Returns the (x,y) distance traveled in this tick as a function of Time per Tick, current speed, and current heading'''
        match self.speed:
            case Speed.CRUISE:
                ...
            case Speed.MAX:
                ...

    def move(self):
        self.fuel -= self.get_fuel_burn()
        if not self.heading is None: # otherwise stay in place
            self.loc += self.get_move_dist() 

    def tick(self):
        self.do_task()
        
