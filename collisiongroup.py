class CollisionGroup(list):
    #will check its objects against the mask_objects.
    #mask is a list of names from other groups.
    
    def __init__(self, mask):
        list.__init__(self)
        self.mask = mask #list with names from other groups
        
    def mask_objects(self):
        #yields objects from the other groups in self.mask
        for group in self.mask:
            for obj in group:
                yield obj
        
    def check(self):
        #check collisions for every object against self.mask_objects()
        for obj in self:
            for other in self.mask_objects():
                obj.colliding_with(other)
            
    def optimize(self, collision_groups):
        #maybe stupid but i just went with it.
        #when a group is created, mask will be a list of group names(keys in the collision_groups dict)
        #once all groups are created and the game runs, group names will be switched to groups directly...
        #so a group can be referenced before it exists, as long as it's created sometime before the game is launched.
        print "before:", self
        self.mask = [collision_groups[name] for name in self.mask]
        print "after:", self
        
    def __str__(self):
        return "%s mask: %s" % (self.__class__.__name__, self.mask)

class CollisionGroupMe(CollisionGroup):
    #will check its objects against themselfs and self.mask_objects().
    
    def check(self):
        #check collisions for every object against itself and self.mask_objects()
        for obj in xrange(len(self)):
            for other in xrange(obj+1, len(self)):
                self[obj].colliding_with(self[other])

            for other in self.mask_objects():
                self[obj].colliding_with(other)
            
class CollisionGroups(dict):
    #subclassed dict, so that a collision group is made simply by setting it in the dict
    #so that setting/getting is uniform
    #set: collision_groups["name"] = ["name", "or_other_name", "s"]
    #get: collision_groups["name"] ... strangly enough.
    def __setitem__(self, name, mask):
        if name in mask:
            mask.remove(name)
            group = CollisionGroupMe(mask)
        else:
            group = CollisionGroup(mask)
        dict.__setitem__(self, name, group)
        print "Set %s %s" % (group.__class__.__name__, name)

    def optimize(self):
        print "collision_groups =", collision_groups
        print "optimizing collision_groups"
        for group in self.values():
            group.optimize(self)
        print "collision_groups optimized"
        print "collision_groups =", collision_groups
        
    def check(self):
        for group in self.values():
            group.check()
        
                
collision_groups = CollisionGroups()

if __name__ == "__main__":
    collision_groups["test"] = [] #objects added to this group won't check shit
    collision_groups["bob"] = ["test"] # check test, those lazy bastards
    collision_groups["nut"] = ["nut", "test", "bob"] # themselfs, test and bob
    collision_groups.optimize()
