from abc import ABC, abstractmethod
import json
import random
import datetime
import math

# this exception is raised when a pet passes away
class PassedAway(Exception):
    pass

class Pet(ABC):
  STATS = ["hunger", "hydration", "love", "hygiene", "health"]
  adoption_time: datetime.datetime
  last_update: float
  money: float
  name: str
  picture_path: str
  lifetime_stats: dict[str, list[float]]
  
  # this method returns all current stats for a pet as a dictionary
  def current_stats(self):
    return {stat : lifetime[-1] for stat, lifetime in self.lifetime_stats.items()}
  
  # this method gets a specific current stat
  def get_stat(self, stat):
    current_stats =  self.current_stats()
    
    # Guard clause: Invalid stat
    if stat not in current_stats:
      raise ValueError(f"No stat named '{stat}' was found for a(n) '{self.type}'")
    
    return current_stats[stat]
  
  # this method changes a stat by some amount
  def regulate_stat(self, stat, change):
    current_stats =  self.current_stats()
    
    # Guard clause: Invalid stat
    if stat not in current_stats:
      raise ValueError(f"No stat named '{stat}' was found for a(n) '{self.TYPE}'")
    
    # change current stat
    self.lifetime_stats[stat][-1] += change
    
    # stat shouldn't go over 1
    if self.lifetime_stats[stat][-1] > 1.0:
      self.lifetime_stats[stat][-1] = 1.0
      
    # stat shouldn't go below 0
    if self.lifetime_stats[stat][-1] < 0:
      
      # if the stat is health, game over
      if stat == 'health':
        raise PassedAway(f"{self.name} went to a better place")
      
      self.lifetime_stats[stat][-1] = 0
      
      
  
    return

  # this function updates a pet after a minute has ellapsed
  @abstractmethod
  def update(self, time): 
    
    # pythonic variables
    current_stats =  self.current_stats()
    pet_dict =  self.__dict__
    
    # check if its night time
    is_night = not (6 <= time.hour <= 19)
    
    # update each stat
    for stat, stat_value in current_stats.items():
      
      # get the depletion rate for current stat
      rate = pet_dict[stat + '_rate']
      
      # calculate the stat decay based on the time of the day
      if is_night:
        depletion = - (rate / 6000) * self.sleep_efficiency 
      else:
        depletion = - (rate / 6000)
      
      # calculate the new stat, with some variability
      new_stat = stat_value + depletion * (1.05 - random.random() * 0.1 ) # +- 5% variance
        
      # add updated stat to the lifetime tracker
      self.lifetime_stats[stat].append(new_stat)
      
    # health extra check
    current_stats =  self.current_stats()
    
    # if any stat is less than 0.3, there should be a health and happiness penalty
    if any(value < 0.3 for value in current_stats.values()):
      self.regulate_stat("health", - (8 / 6000)) # decrease current health
      self.regulate_stat("love",   - (6 / 6000)) # decrease current love
      
    # if any stat is less than 0.1, there should be a significant health and happiness penalty
    if any(value < 0.3 for value in current_stats.values()):
      self.regulate_stat("health", - (64 / 6000)) # decrease current health
      self.regulate_stat("love",   - (48 / 6000)) # decrease current love
    
    # set the last update time to the time sent in
    self.last_update = time
    
    # if health went below zero, pet is dead
    if self.get_stat("health") < 0:
      raise PassedAway(f"{self.name} went to a better place")
    
    return
  
  # this method registers any acquired costs
  def add_cost(self, new_cost):
    self.money += new_cost
    return
  
  # this function turns the pet into a json-like dictionary
  def serialize(self):
    
    json_dictionary = dict(self.__dict__)
    json_dictionary["type"] = self.TYPE # used to encode the type of the pet

    return json_dictionary
  
  # this is an auxiliary function that shouldn't be called outside of this file
  # given a string, it tries to find a corresponding sub-class
  @classmethod 
  def find_subclass(cls, TYPE):
    for sub_cls in cls.__subclasses__():
        
        if sub_cls.TYPE == TYPE:
          return sub_cls
      
    raise ValueError(f"No subclass of {cls.name} found with the name '{TYPE}'")
    
    
  # this method recreates a pet given a json-like dictionary
  @classmethod
  def deserialize(cls, json_dictionary):
    # if the function is called from the Pet class, we need to find the appropiate type
    if cls == Pet:
      # appropiate type    
      sub_cls = cls.find_subclass(json_dictionary["type"])
      
      # making a copy of the dictionary so that we can delete the type key
      # we need to delete it since it was artificially added on the serialize function
      dict_copy = dict(json_dictionary)
      del dict_copy["type"]
      
      # call the function from the appropiate type with the prunned dictionary
      return sub_cls.deserialize(dict_copy)
    
    # the function was called from an appropiate type
    # create a new object with an inner dictionary equal to the given json-like dictionary
    else:
      pet = cls()
      pet.__dict__ = json_dictionary
      
    return pet
  
  # this method creates a new pet based on some adoption parameters
  @classmethod
  def adopt(cls, name, price, adoption_time, picture_path, *ignore, TYPE = ""):
    
    # Guard Clause: No way to infer pet type
    if cls == Pet and type == "":
      raise ValueError("Cannot infer subclass when 'type' is an empty string")
    
    # Guard Clause: No instances of an abstract class, find the apropiate subclass
    if cls == Pet:
      sub_cls = cls.find_subclass(TYPE)
      return sub_cls.adopt(name, price, adoption_time, picture_path)
    
    # Creating the pet    
    pet = cls()
    pet.money: float = price
    pet.name: str = name
    pet.adoption_time: datetime.datetime = adoption_time
    pet.last_update: datetime.datetime = adoption_time
    pet.picture_path: str = picture_path
    
    key = cls.TYPE
    
    # reading in the base stats
    with open("pets/base_rates.json", 'r') as DATA_FILE:  ## MIGHT BREAK WHEN INTEGRATING!! if so, change path
      DATA = json.load(DATA_FILE)
      base_rates = DATA.get(key, DATA["default"])
    
    # some randomness
    for rate_key, rate_value in base_rates.items():
      base_rates[rate_key] = rate_value * (1.05 - random.random() * 0.1 ) # +- 5% variance
    
    # assigning other fields the lazy way
    pet.__dict__.update(base_rates)
    pet.lifetime_stats: dict[str, list[float]] = {stat : [1.0] for stat in cls.STATS}
    
    return pet
  

      
    
