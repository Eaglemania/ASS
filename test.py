
class Test(object):
    def __init__(self):
        self.whatever = "stuff"

    def __del__(self):
        print "yo"

class Sub(Test):
    def what(self):
        pass

a = Test()
a = Sub()
a = Sub()
print a
