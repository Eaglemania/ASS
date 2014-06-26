class CollisionGroup(list):
    #will check objects in its container against the mask.
    #mask is a list of names from other groups.
    #ie: in ass, bullets don't collide with other bullets,
    #but they collide with units and obstacles so,
    #CollisionGroup("bullet", ["unit", "obstacle"])
    
    def __init__(self, name, mask = []):
        list.__init__(self)
        self.name = name
        self.container = [] #objects belonging to this group, which should check against the mask, get put in here
        self.mask = mask #list of containers from other groups

        print "Created %s" % (self)
        
    def mask_objects(self):
        #yields objects from the other groups containers in self.mask
        for group in self.mask:
            for obj in group.container:
                yield obj
        
    def check(self):
        #checks collisions for every object in self.container against self.mask_objects()
        for obj in self.container:
            for other in self.mask_objects():
                obj.collision(other)

class CollisionGroupMe(CollisionGroup):
    #will check objects in its container, against the container and the mask.
    #use this, if objects from the group WILL check each other
    #ie: units collide with other units
    
    def check(self):
        #checks collisions for every object in self.container against self.container and self.mask_objects()
        for obj in xrange(len(self.container)):
            for other in xrange(obj+1, len(self.container)):
                self.container[obj].collision(self.container[other])

            for other in self.mask_objects():
                self.container[obj].collision(other)

class CollisionGroups(dict):
    #subclassed dict, so that a collision group is made simply by setting it in the dict
    #so that setting/getting is uniform
    #set: collision_groups["name"] = ["name", "or_other_name", "s"]
    #get: collision_groups["name"] ... strangly enough.
    def __setitem__(self, name, mask):
        if name in mask:
            mask.remove(name)
            mask = CollisionGroupMe(name, mask)
        else:
            mask = CollisionGroup(name, mask)
        dict.__setitem__(self, name, mask)

    def optimize(self):
        #maybe stupid but i just went with it.
        #when a group is created, mask will be a list of group names(keys in the collision_groups dict)
        #once all groups are created and the game runs, group names will be switched to groups directly...
        #so a group can be referenced before it exists, as long as it's created sometime before the game is launched.
        print "optimizing collision_groups"
        for group_name in self:
            group = dict.__getitem__(self, group_name)
            new_mask = []
            print "before: ", group
            for name in group.mask:
                new_mask.append(dict.__getitem__(self, name))
            group.mask = new_mask
            print "after: ", group
        print "collision_groups optimized"
        
    def check(self):
        #collision for every group
        for group in self:
            dict.__getitem__(self, group).check()
                
collision_groups = CollisionGroups()

if __name__ == "__main__":
    collision_groups["test"] = [] #objects added to this group won't check shit
    collision_groups["bob"] = ["test"] # check test, those lazy bastards
    collision_groups["nut"] = ["nut", "test", "bob"] # themselfs, test and bob
    collision_groups.optimize()
    collision_groups.check()
