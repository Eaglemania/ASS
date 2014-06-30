class CollisionGroups(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        print 'GET', key
        return val

    def __setitem__(self, key, val):
        print 'SET', key, val
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        print 'update', args, kwargs
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
