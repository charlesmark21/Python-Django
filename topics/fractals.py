# from mobject import Mobject, Point, Mobject1D
from mobject.vectorized_mobject import VMobject, VGroup, VectorizedPoint
from scene import Scene
from animation.transform import Transform
from animation.simple_animations import ShowCreation
from topics.geometry import Line, Polygon, RegularPolygon

from helpers import *

def rotate(points, angle = np.pi, axis = OUT):
    if axis is None:
        return points
    matrix = rotation_matrix(angle, axis)
    points = np.dot(points, np.transpose(matrix))
    return points

def fractalify(vmobject, order = 3, *args, **kwargs):
    for x in range(order):
        fractalification_iteration(vmobject)
    return vmobject

def fractalification_iteration(vmobject, 
                               dimension = 1.05, 
                               num_inserted_anchors_range = range(1, 4)
                               ):
    num_points = vmobject.get_num_points()
    if num_points > 0:
        # original_anchors = vmobject.get_anchors()
        original_anchors = [
            vmobject.point_from_proportion(x)
            for x in np.linspace(0, 0.99, num_points)
        ]
        new_anchors = []
        for p1, p2, in zip(original_anchors, original_anchors[1:]):
            num_inserts = random.choice(num_inserted_anchors_range)
            inserted_points = [
                interpolate(p1, p2, alpha)
                for alpha in np.linspace(0, 1, num_inserts+2)[1:-1]
            ]
            mass_scaling_factor = 1./(num_inserts+1)
            length_scaling_factor = mass_scaling_factor**(1./dimension)
            target_length = np.linalg.norm(p1-p2)*length_scaling_factor
            curr_length = np.linalg.norm(p1-p2)*mass_scaling_factor
            #offset^2 + curr_length^2 = target_length^2
            offset_len = np.sqrt(target_length**2 - curr_length**2)
            unit_vect = (p1-p2)/np.linalg.norm(p1-p2)
            offset_unit_vect = rotate_vector(unit_vect, np.pi/2)
            inserted_points = [
                point + u*offset_len*offset_unit_vect
                for u, point in zip(it.cycle([-1, 1]), inserted_points)
            ]
            new_anchors += [p1] + inserted_points
        new_anchors.append(original_anchors[-1])
        vmobject.set_points_as_corners(new_anchors)
    vmobject.submobjects = [
        fractalification_iteration(submob, dimension, num_inserted_anchors_range)
        for submob in vmobject.submobjects
    ]
    return vmobject


class SelfSimilarFractal(VMobject):
    CONFIG = {
        "order" : 5,
        "num_subparts" : 3,
        "height" : 4,
        "colors" : [RED, WHITE],
        "stroke_width" : 1,
        "fill_opacity" : 1,
        "propogate_style_to_family" : True,
    }
    def init_colors(self):
        VMobject.init_colors(self)
        self.gradient_highlight(*self.colors)

    def generate_points(self):
        order_n_self = self.get_order_n_self(self.order)
        if self.order == 0:
            self.submobjects = [order_n_self]
        else:
            self.submobjects = order_n_self.submobjects
        return self

    def get_order_n_self(self, order):
        if order == 0:
            result = self.get_seed_shape()
        else:
            subparts = [
                self.get_order_n_self(order - 1)
                for x in range(self.num_subparts)
            ]
            self.arrange_subparts(*subparts)
            result = VGroup(*subparts)

        result.scale_to_fit_height(self.height)
        result.center()
        return result

    def get_seed_shape(self):
        raise Exception("Not implemented")

    def arrange_subparts(self, *subparts):
        raise Exception("Not implemented")


class Sierpinski(SelfSimilarFractal):
    def get_seed_shape(self):
        return Polygon(
            RIGHT, np.sqrt(3)*UP, LEFT,
        )

    def arrange_subparts(self, *subparts):
        tri1, tri2, tri3 = subparts
        tri1.move_to(tri2.get_corner(DOWN+LEFT), UP)
        tri3.move_to(tri2.get_corner(DOWN+RIGHT), UP)


class DiamondFractal(SelfSimilarFractal):
    CONFIG = {
        "num_subparts" : 4,
        "height" : 4,
        "colors" : [GREEN_E, YELLOW],
    }
    def get_seed_shape(self):
        return RegularPolygon(n = 4)

    def arrange_subparts(self, *subparts):
        # VGroup(*subparts).rotate(np.pi/4)
        for part, vect in zip(subparts, compass_directions(start_vect = UP+RIGHT)):
            part.next_to(ORIGIN, vect, buff = 0)
        VGroup(*subparts).rotate(np.pi/4)


class PentagonalFractal(SelfSimilarFractal):
    CONFIG = {
        "num_subparts" : 5,
        "colors" : [MAROON_B, YELLOW, RED]
    }
    def get_seed_shape(self):
        return RegularPolygon(n = 5, start_angle = np.pi/2)

    def arrange_subparts(self, *subparts):
        phi = (1 + np.sqrt(5))/2
        for x, part in enumerate(subparts):
            part.shift(0.95*part.get_height()*UP)
            part.rotate(2*np.pi*x/5)


######## Space filling curves ############

class FractalCurve(VMobject):
    CONFIG = {
        "radius"      : 3,
        "order"       : 5,
        "colors" : [RED, GREEN],
        "monochromatic" : False,
        "stroke_width" : 3,
        "propogate_style_to_family" : True,
    }

    def generate_points(self):
        points = self.get_anchor_points()
        if self.monochromatic:
            self.set_points_as_corners(points)
        else:
            for triplet in zip(points, points[1:], points[2:]):
                corner = VMobject()
                corner.set_points_as_corners(triplet)
                self.add(corner)

    def init_colors(self):
        VMobject.init_colors(self)
        self.gradient_highlight(*self.colors)

    def get_anchor_points(self):
        raise Exception("Not implemented")


class LindenmayerCurve(FractalCurve):
    CONFIG = {
        "axiom"        : "A",
        "rule"         : {},
        "scale_factor" : 2,
        "radius"       : 3,
        "start_step"   : RIGHT,
        "angle"        : np.pi/2,
    }

    def expand_command_string(self, command):
        result = ""
        for letter in command:
            if letter in self.rule:
                result += self.rule[letter]
            else:
                result += letter
        return result

    def get_command_string(self):
        result = self.axiom
        for x in range(self.order):
            result = self.expand_command_string(result)
        return result

    def get_anchor_points(self):
        step = float(self.radius) * self.start_step 
        step /= (self.scale_factor**self.order)
        curr = np.zeros(3)
        result = [curr]
        for letter in self.get_command_string():
            if letter is "+":
                step = rotate(step, self.angle)
            elif letter is "-":
                step = rotate(step, -self.angle)
            else:
                curr = curr + step
                result.append(curr)
        return np.array(result) - center_of_mass(result)


class SelfSimilarSpaceFillingCurve(FractalCurve):
    CONFIG = {
        "offsets" : [],
        #keys must awkwardly be in string form...
        "offset_to_rotation_axis" : {},
        "scale_factor" : 2,
        "radius_scale_factor" : 0.5,
    }
    def transform(self, points, offset):
        """
        How to transform the copy of points shifted by
        offset.  Generally meant to be extended in subclasses
        """
        copy = np.array(points)
        if str(offset) in self.offset_to_rotation_axis:
            copy = rotate(
                copy, 
                axis = self.offset_to_rotation_axis[str(offset)]
            )
        copy /= self.scale_factor,
        copy += offset*self.radius*self.radius_scale_factor
        return copy

    def refine_into_subparts(self, points):
        transformed_copies = [
            self.transform(points, offset)
            for offset in self.offsets
        ]
        return reduce(
            lambda a, b : np.append(a, b, axis = 0),
            transformed_copies
        )


    def get_anchor_points(self):
        points = np.zeros((1, 3))
        for count in range(self.order):
            points = self.refine_into_subparts(points)
        return points

    def generate_grid(self):
        raise Exception("Not implemented")



class HilbertCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "offsets" : [
            LEFT+DOWN,
            LEFT+UP,
            RIGHT+UP,
            RIGHT+DOWN,
        ],
        "offset_to_rotation_axis" : {
            str(LEFT+DOWN)  : RIGHT+UP,
            str(RIGHT+DOWN) : RIGHT+DOWN,
        },
     }


class HilbertCurve3D(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "offsets" : [ 
           LEFT+DOWN+OUT,
           LEFT+UP+OUT,
           LEFT+UP+IN,
           LEFT+DOWN+IN,
           RIGHT+DOWN+IN,                                               
           RIGHT+UP+IN,
           RIGHT+UP+OUT,
           RIGHT+DOWN+OUT,
        ],
        "offset_to_rotation_axis" : {}#TODO
    }

class PeanoCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "colors" : [PURPLE, TEAL],
        "offsets" : [
            LEFT+DOWN,
            LEFT,
            LEFT+UP,
            UP,
            ORIGIN,
            DOWN,
            RIGHT+DOWN,
            RIGHT,
            RIGHT+UP,
        ],
        "offset_to_rotation_axis" : {
            str(LEFT)   : UP,       
            str(UP)     : RIGHT,    
            str(ORIGIN) : LEFT+UP,  
            str(DOWN)   : RIGHT, 
            str(RIGHT)  : UP,   
        },
        "scale_factor" : 3,
        "radius_scale_factor" : 2.0/3,
    }

class TriangleFillingCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "colors" : [MAROON, YELLOW],
        "offsets" : [
            LEFT/4.+DOWN/6.,
            ORIGIN,
            RIGHT/4.+DOWN/6.,
            UP/3.,
        ],
        "offset_to_rotation_axis" : {
            str(ORIGIN): RIGHT,
            str(UP/3.) : UP,
        },
        "scale_factor" : 2,
        "radius_scale_factor" : 1.5,
    }

# class HexagonFillingCurve(SelfSimilarSpaceFillingCurve):
#     CONFIG = {
#         "start_color" : WHITE,
#         "end_color"   : BLUE_D,
#         "axis_offset_pairs" : [
#             (None,                1.5*DOWN + 0.5*np.sqrt(3)*LEFT),
#             (UP+np.sqrt(3)*RIGHT, 1.5*DOWN + 0.5*np.sqrt(3)*RIGHT),
#             (np.sqrt(3)*UP+RIGHT, ORIGIN),            
#             ((UP, RIGHT),         np.sqrt(3)*LEFT),
#             (None,                1.5*UP + 0.5*np.sqrt(3)*LEFT),
#             (None,                1.5*UP + 0.5*np.sqrt(3)*RIGHT),
#             (RIGHT,               np.sqrt(3)*RIGHT),
#         ],
#         "scale_factor" : 3,
#         "radius_scale_factor" : 2/(3*np.sqrt(3)),
#     }

#     def refine_into_subparts(self, points):
#         return SelfSimilarSpaceFillingCurve.refine_into_subparts(
#             self,
#             rotate(points, np.pi/6, IN)
#         )


class UtahFillingCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "colors" : [WHITE, BLUE_D],
        "axis_offset_pairs" : [

        ],
        "scale_factor" : 3,
        "radius_scale_factor" : 2/(3*np.sqrt(3)),
    }


class FlowSnake(LindenmayerCurve):
    CONFIG = {
        "colors" : [YELLOW, GREEN],
        "axiom"       : "A",
        "rule" : {
            "A" : "A-B--B+A++AA+B-",
            "B" : "+A-BB--B-A++A+B",
        },
        "radius"       : 6, #TODO, this is innaccurate
        "scale_factor" : np.sqrt(7),
        "start_step"   : RIGHT,
        "angle"        : -np.pi/3,
    }
    def __init__(self, **kwargs):
        LindenmayerCurve.__init__(self, **kwargs)
        self.rotate(-self.order*np.pi/9)

class SierpinskiCurve(LindenmayerCurve):
    CONFIG = {
        "colors" : [RED, WHITE],
        "axiom" : "B",
        "rule" : {
            "A" : "+B-A-B+",
            "B" : "-A+B+A-",
        },
        "radius"       : 6, #TODO, this is innaccurate
        "scale_factor" : 2,
        "start_step"   : RIGHT,
        "angle"        : -np.pi/3,
    }

class KochSnowFlake(LindenmayerCurve):
    CONFIG = {
        "colors" : [BLUE_D, WHITE, BLUE_D],
        "axiom"        : "A--A--A--",
        "rule"         : {
            "A" : "A+A--A+A"
        },
        "radius"       : 4,
        "scale_factor" : 3,
        "start_step"   : RIGHT,
        "angle"        : np.pi/3
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.scale_factor = 2*(1+np.cos(self.angle))
        LindenmayerCurve.__init__(self, **kwargs)

class KochCurve(KochSnowFlake):
    CONFIG = {
        "axiom" : "A--"
    }
        


class StellarCurve(LindenmayerCurve):
    CONFIG = {
        "start_color" : RED,
        "end_color"   : BLUE_E,
        "rule" : {
            "A" : "+B-A-B+A-B+",
            "B" : "-A+B+A-B+A-",
        },
        "scale_factor" : 3,
        "angle" : 2*np.pi/5,
    }

class SnakeCurve(FractalCurve):
    CONFIG = {
        "start_color" : BLUE,
        "end_color"   : YELLOW,
    }
    def get_anchor_points(self):
        result = []
        resolution = 2**self.order
        step = 2.0*self.radius / resolution
        lower_left = ORIGIN + \
                     LEFT*(self.radius - step/2) + \
                     DOWN*(self.radius - step/2)

        for y in range(resolution):
            x_range = range(resolution)
            if y%2 == 0:
                x_range.reverse()
            for x in x_range:
                result.append(
                    lower_left + x*step*RIGHT + y*step*UP
                )
        return result



class SpaceFillingCurveScene(Scene):
    @staticmethod
    def args_to_string(CurveClass, order):
        return CurveClass.__name__ + "Order" + str(order)

    @staticmethod
    def string_to_args(arg_str):
        curve_class_name, order_str = arg_str.split()
        space_filling_curves = dict([
            (Class.__name__, Class)
            for Class in get_all_descendent_classes(FractalCurve)
        ])
        if curve_class_name not in space_filling_curves:
            raise Exception(
                "%s is not a space filling curve"%curve_class_name
            )
        CurveClass = space_filling_curves[curve_class_name]
        return CurveClass, int(order_str)

class TransformOverIncreasingOrders(SpaceFillingCurveScene):
    def setup(self, CurveClass):
        sample = CurveClass(order = 1)
        self.curve = Line(3*LEFT, 3*RIGHT)
        self.curve.gradient_highlight(
            sample.start_color, 
            sample.end_color
        )
        self.CurveClass = CurveClass
        self.order = 0

    def construct(self, CurveClass, max_order):
        self.setup(CurveClass)
        while self.order < max_order:
            self.increase_order()
        self.dither()

    def increase_order(self, *other_anims):
        self.order += 1
        new_curve = self.CurveClass(order = self.order)
        self.play(
            Transform(self.curve, new_curve),
            *other_anims,
            run_time = 3/np.sqrt(self.order)
        )


class DrawSpaceFillingCurve(SpaceFillingCurveScene):
    def construct(self, CurveClass, order):
        curve = CurveClass(order = order)
        self.play(ShowCreation(curve), run_time = 10)
        self.dither()














