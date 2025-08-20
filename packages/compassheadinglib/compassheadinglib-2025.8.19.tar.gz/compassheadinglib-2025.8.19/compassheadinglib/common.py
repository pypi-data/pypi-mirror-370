def _instanceTypeCheck(inst,typeof):
    #tests if inst is of type typeof (or if typeof is a list any of the types in typeof) otherwise throws an error
    if not isinstance(typeof,list):
        typeof=[typeof]

    matchesAny = False

    for i in typeof:
        if isinstance(inst,i):
            matchesAny = True
            break

    if not matchesAny:
        acceptable = ', '.join([str(i) for i in typeof])
        
        isMultMsg=''
        if len(typeof)>1:
            isMultMsg='one of '
        
        raise TypeError('Variable type must be {}{}. Input was type {}.'.format(isMultMsg,acceptable,type(inst)))


class Heading(object):
    #host object for a single heading
    def __init__(self, name, abbr, azimuth, order, langs={},parent=None):
        self.name=name
        self.abbr=abbr
        self.azimuth=float(azimuth)
        self.order=order
        self.langs=langs
        self.parent=parent

    def __repr__(self):
        return self.name
    
    def __float__(self):
        return self.azimuth

    def __str__(self):
        return self.name

    def __abs__(self):
        return abs(self.azimuth)

    def __eq__(self,azimuthB):
        if isinstance(azimuthB,Heading):
            return self.azimuth == azimuthB.azimuth
        else:
            return self.azimuth == azimuthB
        
    def __gt__(self,azimuthB):
        return float(azimuthB)<self.azimuth
    
    def __lt__(self,azimuthB):
        return float(azimuthB)>self.azimuth

    def __ge__(self,azimuthB):
        return float(azimuthB)<=self.azimuth

    def __le__(self,azimuthB):
        return float(azimuthB)>=self.azimuth
    
    def rotate(self, degrees):
        new_azimuth = (self.azimuth + degrees) % 360
        return self.parent(new_azimuth)

    def port(self, degrees):
        assert degrees >= 0
        new_azimuth = (self.azimuth - degrees) % 360
        return self.parent(new_azimuth)

    def starboard(self, degrees):
        assert degrees >= 0
        new_azimuth = (self.azimuth + degrees) % 360
        return self.parent(new_azimuth)

    def left(self,degrees):
        return self.port(degrees)

    def right(self,degrees):
        return self.starboard(degrees)
    
    def __add__(self, other):
        if isinstance(other, Heading):
            new_azimuth = (self.azimuth + other.azimuth) % 360
        else:
            new_azimuth = (self.azimuth + float(other)) % 360
        return self.parent(new_azimuth)

    def __sub__(self, other):
        if isinstance(other, Heading):
            new_azimuth = (self.azimuth - other.azimuth) % 360
        else:
            new_azimuth = (self.azimuth - float(other)) % 360
        return self.parent(new_azimuth)

    def __radd__(self, other):
        # For when a number is added to a heading (number + heading)
        new_azimuth = (float(other) + self.azimuth) % 360
        return self.parent(new_azimuth)

    def __rsub__(self, other):
        # For when a heading is subtracted from a number (number - heading)
        new_azimuth = (float(other) - self.azimuth) % 360
        return self.parent(new_azimuth)
    
    def asDict(self):
        return {i:self.__dict__[i] for i in self.__dict__ if i not in ('langs','parent')}

    def translate(self,lang):
        new_lang=self.langs[lang.upper()]
        return Heading(
            new_lang['Heading'],
            new_lang['Abbreviation'],
            self.azimuth,
            self.order,
            self.langs,
            self.parent
        )

    def withBearing__(self,azimuth):
        return Heading(
            self.name,
            self.abbr,
            azimuth,
            self.order,
            self.langs,
            self.parent
        )

class _Headings(dict):
    #host object for a collection of headings (i.e. the Compass object)
    def __init__(self,c):
        self.iterlist__=[]
        for i in c:
            h=Heading(
                i['Heading'],
                i['Abbreviation'],
                i['Azimuth'],
                i['Order'],
                i['Lang'],
                self
            )
            if i['Heading'] not in c:
                self[i['Heading'].lower().replace(' ','-')]=h
            self.iterlist__.append(h)

    def __getitem__(self, key):
        if isinstance(key,str):
            return super().__getitem__(key)
        else:
            return self.iterlist__[key]

    def __getattr__(self, name):
        return self[name.lower()]

    def __setattr__(self, name, value):
        if '__' not in name:
            _instanceTypeCheck(value,Heading)
            self[name.lower()]=value
        else:
            self[name]=value

    def __delattr__(self, name):
        del self[name]

    def __iter__(self):
        return iter(self.iterlist__)

    def __repr__(self):
        return '< Headings {} >'.format(repr(self.keys()))

    def __call__(self,bearing,order=3):
        return self.findHeading(bearing,order)
    
    def asList(self):
        return [i.asDict() for i in self]

    def findHeading(self,bearing,order=3):
        #returns the nearest heading of order or below to the bearing entered
        s=361
        out=None

        for i in self.iterlist__:
            if i.order<=order:
                d=max(bearing,i.azimuth)-min(bearing,i.azimuth)
                if d < s:
                    s = d
                    out = i
                else:
                    return out.withBearing__(bearing)
        return out.withBearing__(bearing)

        