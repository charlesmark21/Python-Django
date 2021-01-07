#!/usr/bin/env python

from manimlib.imports import *

# To watch one of these scenes, run the following:
# python -m manim example_scenes.py SquareToCircle
# Use -s to skip to the end and just save the final frame
# Use -w to write the animation to a file
# Use -o to write it to a file and open it once done
# Use -n <number> to skip ahead to the n'th animation of a scene.


class OpeningManimExample(Scene):
    def construct(self):
        title = TextMobject("This is some \\LaTeX")
        basel = TexMobject(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeIn(basel, UP),
        )
        self.wait()

        transform_title = TextMobject("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStartMap(FadeOut, basel, shift=DOWN),
        )
        self.wait()

        fade_comment = TextMobject("""
            You probably don't want to over use\\\\
            Transforms, though, a simple fade often\\\\
            looks nicer.
        """)
        fade_comment.next_to(
            transform_title, DOWN,
            buff=LARGE_BUFF,
            aligned_edge=LEFT
        )
        self.play(FadeIn(fade_comment, shift=DOWN))
        self.wait(3)

        grid = NumberPlane()
        grid_title = TextMobject(
            "But manim is for illustrating math, not text",
        )
        grid_title.to_edge(UP)
        grid_title.add_background_rectangle()

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title, shift=LEFT),
            FadeOut(fade_comment, shift=LEFT),
            FadeIn(grid_title),
            ShowCreation(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        grid_transform_title = TextMobject(
            "This is a non-linear function applied to the grid"
        )
        grid_transform_title.set_stroke(BLACK, 5, background=True)
        grid_transform_title.to_edge(UP)
        grid.prepare_for_nonlinear_transform()
        self.play(
            ApplyPointwiseFunction(
                lambda p: p + np.array([np.sin(p[1]), np.sin(p[0]), 0]),
                grid,
                run_time=5,
            ),
            FadeOut(grid_title),
            FadeIn(grid_transform_title),
        )
        self.wait()


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(square.apply_complex_function, np.exp)
        self.wait()


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        square = Square()

        self.play(ShowCreation(square))
        self.wait()
        self.play(ReplacementTransform(square, circle))
        self.wait()

        # This opens an iPython termnial where you can keep writing
        # lines as if they were part of this construct method
        self.embed()
        # Try typing the following lines
        # self.play(circle.stretch, 4, {"dim": 0})
        # self.play(Rotate(circle, TAU / 4))
        # self.play(circle.shift, 2 * RIGHT, circle.scale, 0.25)
        # circle.insert_n_curves(10)
        # self.play(circle.apply_complex_function, lambda z: z**2)


class TexTransformExample(Scene):
    def construct(self):
        kw = {
            "substrings_to_isolate": ["B", "C", "="]
        }
        lines = VGroup(
            # Surrounding substrings with double braces
            # will ensure that those parts are separated
            # out in the TexMobject.  For example, here the
            # TexMobject will have 5 submobjects, corresponding
            # to the strings [A^2, +, B^2, =, C^2]
            TexMobject("{{A^2}} + {{B^2}} = {{C^2}}"),
            TexMobject("{{A^2}} = {{C^2}} - {{B^2}}"),
            # Alternatively, you can pass in the keyword argument
            # substrings_to_isolate with a list of strings that
            # should be broken out as their own submobject.  So
            # both lines below are equivalent to what you'd get
            # by wrapping every instance of "B", "C" and "=" with
            # double braces
            TexMobject("{{A^2}} = (C + B)(C - B)", **kw),
            TexMobject("A = \\sqrt{(C + B)(C - B)}", **kw)
        )
        lines.arrange(DOWN, buff=LARGE_BUFF)
        for line in lines:
            line.set_color_by_tex_to_color_map({
                "A": BLUE,
                "B": TEAL,
                "C": GREEN,
            })

        self.add(lines[0])
        # The animation TransformMatchingTex will line up parts
        # of the source and target which have matching tex strings.
        # Here, giving it a little path_arc makes each part sort of
        # rotate into their final positions, which feels appropriate
        # for the idea of rearranging an equation
        self.play(
            TransformMatchingTex(
                lines[0].copy(), lines[1],
                path_arc=90 * DEGREES,
            ),
        )
        self.wait()

        # Now, we could try this again on the next line...
        self.play(
            TransformMatchingTex(lines[1].copy(), lines[2]),
        )
        self.wait()
        # ...and this looks nice enough, but since there's no tex
        # in lines[2] which matches "C^2" or "B^2", those terms fade
        # out to nothing while the C and B terms fade in from nothing.
        # If, however, we want the C to go to C, and B to go to B, but
        # we don't want to think about breaking up the tex string
        # differently, we could instead try TransformMatchingShapes,
        # which will line up parts of the source and target which
        # have matching shapes, regardless of where they fall in the
        # mobject family heirarchies.
        self.play(FadeOut(lines[2]))
        self.play(
            TransformMatchingShapes(lines[1].copy(), lines[2]),
        )
        # That's almost what we want, but if you were finicky you
        # might complain that all the exponents from lines[1] got
        # to the 2 in A^2, since that's the only part of lines[2]
        # which matches the shape of a 2.  In this case, one option
        # would be to use TransformMatchingTex on the left-hand-side,
        # but TransformMatchingShapes on the right-hand-side
        eq_index = lines[1].index_of_part_by_tex("=")
        self.play(FadeOut(lines[2]))
        self.play(
            TransformMatchingTex(
                lines[1][:eq_index].copy(),
                lines[2][:eq_index],
            ),
            TransformMatchingShapes(
                lines[1][eq_index:].copy(),
                lines[2][eq_index:],
            ),
        )
        self.wait()

        # And to finish off, a simple TransformMatchingShapes will do,
        # though maybe we really want that exponent from A^2 to turn
        # into the square root, so we set fade_transform_mismatches to
        # True so that parts with mis-matching shapes transform into
        # each other.
        self.play(
            TransformMatchingShapes(
                lines[2].copy(), lines[3],
                fade_transform_mismatches=True,
            ),
        )
        self.wait()


class UpdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square()
        square.to_edge(UP)

        # This ensures that the method deicmal.next_to(square)
        # is called on every frame
        always(decimal.next_to, square)
        # This ensures thst decimal.set_value(square.get_y()) is
        # called every frame
        f_always(decimal.set_value, square.get_y)

        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            run_time=3,
        )
        self.play(square.center)
        self.wait()

        # You can also add any function generally to a Mobject's
        # list of 'updaters'.
        now = self.time
        square.add_updater(
            lambda m: m.set_y(math.sin(self.time - now))
        )
        self.wait(10)


class SurfaceExample(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
    }

    def construct(self):
        torus1 = Torus(r1=1, r2=1)
        torus2 = Torus(r1=3, r2=1)
        sphere = Sphere(radius=3, resolution=torus1.resolution)
        # You can texture a surface with up to two images, which will
        # be interpreted as the side towards the light, and away from
        # the light.  These can be either urls, or paths to a local file
        # in whatever you've set as the iamge directory in
        # the custom_defaults.yml file
        day_texture = "https://upload.wikimedia.org/wikipedia/commons/4/4d/Whole_world_-_land_and_oceans.jpg"
        night_texture = "https://upload.wikimedia.org/wikipedia/commons/b/ba/The_earth_at_night.jpg"
        surfaces = [
            TexturedSurface(surface, day_texture, night_texture)
            for surface in [sphere, torus1, torus2]
        ]

        for mob in surfaces:
            mob.mesh = SurfaceMesh(mob)
            mob.mesh.set_stroke(BLUE, 1, opacity=0.5)

        # Set perspective
        frame = self.camera.frame
        frame.set_rotation(
            theta=-30 * DEGREES,
            phi=70 * DEGREES,
        )

        surface = surfaces[0]

        self.play(
            FadeIn(surface),
            ShowCreation(surface.mesh, lag_ratio=0.01, run_time=3),
        )
        for mob in surfaces:
            mob.add(mob.mesh)
        surface.save_state()
        self.play(Rotate(surface, PI / 2), run_time=2)
        for mob in surfaces[1:]:
            mob.rotate(PI / 2)

        self.play(
            Transform(surface, surfaces[1]),
            run_time=3
        )

        self.play(
            Transform(surface, surfaces[2]),
            # Move camera frame during the transition
            frame.increment_phi, -10 * DEGREES,
            frame.increment_theta, -20 * DEGREES,
            run_time=3
        )
        # Add ambient rotation
        frame.add_updater(lambda m, dt: m.increment_theta(-0.1 * dt))

        # Play around with where the light is
        light = self.camera.light_source
        self.add(light)
        light.save_state()
        self.play(light.move_to, 3 * IN, run_time=5)
        self.play(light.shift, 10 * OUT, run_time=5)
        self.wait(4)


# See https://github.com/3b1b/videos for many, many more
