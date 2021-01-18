# Based on https://github.com/allelos/vectors
# Changes were made to work with Micropython, such as using Complex instead of numbers.Real
# Also, added readibility, customized case and bug-fixes / feature expansion
import math

# def reduce(function, iterable, initializer=None):
#     it = iter(iterable)
#     if initializer is None:
#         value = next(it)
#     else:
#         value = initializer
#     for element in it:
#         value = function(value, element)
#     return value


class Point(object):
    """Point class: Reprepsents a point in the x, y, z space."""

    def __init__(self, X, Y, Z=0):
        self.X = X
        self.Y = Y
        self.Z = Z

    def __repr__(self):
        return '{0}({1}, {2}, {3})'.format(
            self.__class__.__name__,
            self.X,
            self.Y,
            self.Z
        )

    def __sub__(self, point):
        """Return a Point instance as the displacement of two points."""
        if type(point) is Point:
            return self.substract(point)
        else:
            raise TypeError

    def __add__(self, pt):
        if isinstance(pt, Point):
            if self.Z and pt.Z:
                return Point(pt.X + self.X, pt.Y + self.Y, pt.Z + self.Z)
            elif self.Z:
                return Point(pt.X + self.X, pt.Y + self.Y, self.Z)
            elif pt.Z:
                return Point(pt.X + self.X, pt.Y + self.Y, pt.Z)
            else:
                return Point(pt.X + self.X, pt.Y + self.Y)
        else:
            raise TypeError

    def __eq__(self, pt):
        return (
            self.X == pt.X and
            self.Y == pt.Y and
            self.Z == pt.Z
        )

    def to_list(self):
        '''Returns an array of [x,y,z] of the end points'''
        return [self.X, self.Y, self.Z]

    def substract(self, pt):
        """Return a Point instance as the displacement of two points."""
        if isinstance(pt, Point):
                return Point(pt.X - self.X, pt.Y - self.Y, pt.Z - self.Z)
        else:
            raise TypeError

    def Distance(self, OtherPoint):
        # Returns the distance to another sprite
        return (((OtherPoint.X-self.X)**2)+((OtherPoint.Y-self.Y)**2)+((OtherPoint.Z-self.Z)**2))**(1/2)



    @classmethod
    def from_list(cls, l):
        """Return a Point instance from a given list"""
        if len(l) == 3:
                X, Y, Z = map(float, l)
                return cls(X, Y, Z)
        elif len(l) == 2:
            x, y = map(float, l)
            return cls(X, Y)
        else:
            raise AttributeError


class Vector(Point):
    """Vector class: Representing a vector in 3D space.

    Can accept formats of:
    Cartesian coordinates in the x, y, z space.(Regular initialization)
    Spherical coordinates in the r, theta, phi space.(Spherical class method)
    Cylindrical coordinates in the r, theta, z space.(Cylindrical class method)
    """

    def __init__(self, X, Y, Z):
        '''Vectors are created in rectangular coordniates

        to create a vector in spherical or cylindrical
        see the class methods
        '''
        super(Vector, self).__init__(X, Y, Z)

    def __add__(self, vec):
        """Add two vectors together"""
        if(type(vec) == type(self)):
            return Vector(self.X + vec.X, self.Y + vec.Y, self.Z + vec.Z)
        elif isinstance(vec, complex):
            #elif isinstance(vec, Real):
            return self.add(vec)
        else:
            raise TypeError

    def __sub__(self, vec):
        """Subtract two vectors"""
        if(type(vec) == type(self)):
            return Vector(self.X - vec.X, self.Y - vec.Y, self.Z - vec.Z)
        elif isinstance(vec, complex):
            #elif isinstance(vec, Real):
            return Vector(self.X - vec, self.Y - vec, self.Z - vec)
        else:
            raise TypeError

    def __mul__(self, anotherVector):
        """Return a Vector instance as the cross product of two vectors"""
        return self.cross(anotherVector)

    def __str__(self):
        return "{0},{1},{2}".format(self.X, self.Y, self.Z)

    def __round__(self, n=None):
        if n is not None:
            return Vector(round(self.X, n), round(self.Y, n), round(self.Z, n))
        return Vector(round(self.X), round(self.Y), round(self.Z))

    def add(self, number):
        """Return a Vector as the product of the vector and a real number."""
        return self.from_list([x + number for x in self.to_list()])

    def multiply(self, number):
        """Return a Vector as the product of the vector and a real number."""
        return self.from_list([x * number for x in self.to_list()])

    def magnitude(self):
        """Return magnitude of the vector."""

        return abs( math.sqrt( self.X **2 + self.Y**2 + self.Z**2  )   )


        # return math.sqrt(
        #     reduce(lambda x, y: x + y, [x ** 2 for x in self.to_list()])
        # )

    def sum(self, vector):
        """Return a Vector instance as the vector sum of two vectors."""
        return self.from_list(
            [self.to_list()[i] + vector.to_list()[i] for i in range(3)]
        )

    def subtract(self, vector):
        """Return a Vector instance as the vector difference of two vectors."""
        return self.__sub__(vector)

    def dot(self, vector, theta=None):
        """Return the dot product of two vectors.

        If theta is given then the dot product is computed as
        v1*v1 = |v1||v2|cos(theta). Argument theta
        is measured in degrees.
        """
        if theta is not None:
            return (self.magnitude() * vector.magnitude() *
                    math.degrees(math.cos(theta)))
        return (reduce(lambda x, y: x + y,
                       [x * vector.to_list()[i] for i, x in enumerate(self.to_list())]))

    def cross(self, vector):
        """Return a Vector instance as the cross product of two vectors"""
        return Vector((self.Y * vector.Z - self.Z * vector.Y),
                      (self.Z * vector.X - self.X * vector.Z),
                      (self.X * vector.Y - self.Y * vector.X))

    def unit(self, Rescale=1):
        """Return a Vector instance of the unit vector. Optionally multiplies X,Y,Z by this """
        m = self.magnitude()
        #print("Unit:Magnitude=",m)
        if m == 0:
            return Vector(0,0,0)
        return Vector(
            (self.X / m) * Rescale,
            (self.Y / m) * Rescale,
            (self.Z / m) * Rescale
        )

    def angle(self, vector):
        """Return the angle between two vectors in degrees."""
        return math.degrees(
            math.acos(
                self.dot(vector) /
                (self.magnitude() * vector.magnitude())
            )
        )

    def parallel(self, vector):
        """Return True if vectors are parallel to each other."""
        if self.cross(vector).magnitude() == 0:
            return True
        return False

    def perpendicular(self, vector):
        """Return True if vectors are perpendicular to each other."""
        if self.dot(vector) == 0:
            return True
        return False

    def non_parallel(self, vector):
        """Return True if vectors are non-parallel.

        Non-parallel vectors are vectors which are neither parallel
        nor perpendicular to each other.
        """
        if (self.is_parallel(vector) is not True and
                self.is_perpendicular(vector) is not True):
            return True
        return False

    def rotate(self, angle, axis=(0, 0, 1)):
        """Returns the rotated vector. Assumes angle is in radians"""
        if not all(isinstance(a, int) for a in axis):
            raise ValueError
        x, y, z = self.X, self.Y, self.Z

        # Z axis rotation
        if(axis[2]):
            x = (self.X * math.cos(angle) - self.Y * math.sin(angle))
            y = (self.X * math.sin(angle) + self.Y * math.cos(angle))

        # Y axis rotation
        if(axis[1]):
            x = self.X * math.cos(angle) + self.Z * math.sin(angle)
            z = -self.X * math.sin(angle) + self.Z * math.cos(angle)

        # X axis rotation
        if(axis[0]):
            y = self.Y * math.cos(angle) - self.Z * math.sin(angle)
            z = self.Y * math.sin(angle) + self.Z * math.cos(angle)

        return Vector(x, y, z)

    def to_points(self):
        '''Returns an array of [x,y,z] of the end points'''
        return [self.X, self.Y, self.Z]

    @classmethod
    def from_points(cls, point1, point2):
        """Return a Vector instance from two given points."""
        if isinstance(point1, Point) and isinstance(point2, Point):
            displacement = point1.substract(point2)
            return cls(displacement.X, displacement.Y, displacement.Z)
        raise TypeError

    @classmethod
    def spherical(cls, mag, theta, phi=0):
        '''Returns a Vector instance from spherical coordinates'''
        return cls(
            mag * math.sin(phi) * math.cos(theta),  # X
            mag * math.sin(phi) * math.sin(theta),  # Y
            mag * math.cos(phi)  # Z
        )

    @classmethod
    def cylindrical(cls, mag, theta, z=0):
        '''Returns a Vector instance from cylindircal coordinates'''
        return cls(
            mag * math.cos(theta),  # X
            mag * math.sin(theta),  # Y
            z  # Z
        )
