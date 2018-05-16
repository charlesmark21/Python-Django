from big_ol_pile_of_manim_imports import *


class NumberlineTransformationScene(Scene):
    CONFIG = {
        "input_line_center": 2 * UP,
        "output_line_center": 2 * DOWN,
        "number_line_config": {
            "include_numbers": True,
            "x_min": -3.5,
            "x_max": 3.5,
            "unit_size": 2,
        },
        # These would override number_line_config
        "input_line_config": {
            "color": BLUE,
        },
        "output_line_config": {},
        "num_inserted_number_line_anchors": 20,
<<<<<<< HEAD
        "default_delta_x": 0.1,
        "default_sample_dot_radius": 0.07,
        "default_sample_dot_colors": [RED, YELLOW],
        "default_mapping_animation_config": {
            "run_time": 3,
            # "path_arc": 30 * DEGREES,
        },
        "local_coordinate_num_decimal_places": 2,
        "zoom_factor": 0.1,
        "zoomed_display_height": 2.5,
        "zoomed_display_corner_buff": MED_SMALL_BUFF,
        "mini_line_scale_factor": 2,
        "default_coordinate_value_dx": 0.05,
        "zoomed_camera_background_rectangle_fill_opacity": 1.0,
=======
>>>>>>> parent of b9f4b8b... Merge pull request #235 from 3b1b/alt-calc
    }

    def setup(self):
        self.setup_number_lines()
        self.setup_titles()

    def setup_number_lines(self):
        number_lines = self.number_lines = VGroup()
        added_configs = (self.input_line_config, self.output_line_config)
        centers = (self.input_line_center, self.output_line_center)
        for added_config, center in zip(added_configs, centers):
            full_config = dict(self.number_line_config)
            full_config.update(added_config)
            number_line = NumberLine(**full_config)
            number_line.main_line.insert_n_anchor_points(
                self.num_inserted_number_line_anchors
            )
            number_line.move_to(center)
            number_lines.add(number_line)
        self.input_line, self.output_line = number_lines

        self.add(number_lines)

    def setup_titles(self):
        input_title, output_title = self.titles = VGroup(*[
            TextMobject()
            for word in "Inputs", "Outputs"
        ])
        for title, line in zip(self.titles, self.number_lines):
            title.next_to(line, UP)
            title.shift_onto_screen()

        self.add(self.titles)

<<<<<<< HEAD
    def setup_zoomed_camera_background_rectangle(self):
        frame = self.zoomed_camera.frame
        frame.next_to(self.camera.frame, UL)
        self.zoomed_camera_background_rectangle = BackgroundRectangle(
            frame, fill_opacity=self.zoomed_camera_background_rectangle_fill_opacity
        )
        self.zoomed_camera_background_rectangle_anim = UpdateFromFunc(
            self.zoomed_camera_background_rectangle,
            lambda m: m.replace(frame, stretch=True)
        )
        self.zoomed_camera_background_rectangle_group = VGroup(
            self.zoomed_camera_background_rectangle,
        )

    def get_sample_input_points(self, x_min=None, x_max=None, delta_x=None):
        x_min = x_min or self.input_line.x_min
        x_max = x_max or self.input_line.x_max
        delta_x = delta_x or self.default_delta_x
        return [
            self.get_input_point(x)
            for x in np.arange(x_min, x_max + delta_x, delta_x)
        ]

    def get_sample_dots(self, x_min=None, x_max=None,
                        delta_x=None, dot_radius=None, colors=None):
        dot_radius = dot_radius or self.default_sample_dot_radius
        colors = colors or self.default_sample_dot_colors

        dots = VGroup(*[
            Dot(point, radius=dot_radius)
            for point in self.get_sample_input_points(x_min, x_max, delta_x)
        ])
        dots.set_color_by_gradient(*colors)
        return dots

    def get_local_sample_dots(self, x, sample_radius=None, **kwargs):
        zoom_factor = self.get_zoom_factor()
        delta_x = kwargs.get("delta_x", self.default_delta_x * zoom_factor)
        dot_radius = kwargs.get("dot_radius", self.default_sample_dot_radius * zoom_factor)

        if sample_radius is None:
            unrounded_radius = self.zoomed_camera.frame.get_width() / 2
            sample_radius = int(unrounded_radius / delta_x) * delta_x
        config = {
            "x_min": x - sample_radius,
            "x_max": x + sample_radius,
            "delta_x": delta_x,
            "dot_radius": dot_radius,
        }
        config.update(kwargs)
        return self.get_sample_dots(**config)

    def add_sample_dot_ghosts(self, sample_dots, fade_factor=0.5):
        self.sample_dot_ghosts = sample_dots.copy()
        self.sample_dot_ghosts.fade(fade_factor)
        self.add(self.sample_dot_ghosts, sample_dots)

    def get_local_coordinate_values(self, x, dx=None, n_neighbors=1):
        dx = dx or self.default_coordinate_value_dx
        return [
            x + n * dx
            for n in range(-n_neighbors, n_neighbors + 1)
        ]

    # Mapping animations
    def get_mapping_animation(self, func, mobject,
                              how_to_apply_func=apply_function_to_center,
                              **kwargs):
        anim_config = dict(self.default_mapping_animation_config)
        anim_config.update(kwargs)

        point_func = self.number_func_to_point_func(func)

        mobject.generate_target(use_deepcopy=True)
        how_to_apply_func(point_func, mobject.target)
        return MoveToTarget(mobject, **anim_config)

    def get_line_mapping_animation(self, func, **kwargs):
        input_line_copy = self.input_line.deepcopy()
        self.moving_input_line = input_line_copy
        input_line_copy.remove(input_line_copy.numbers)
        # input_line_copy.set_stroke(width=2)
        input_line_copy.main_line.insert_n_anchor_points(
            self.num_inserted_number_line_anchors
        )
        return AnimationGroup(
            self.get_mapping_animation(
                func, input_line_copy.main_line,
                apply_function_to_points
            ),
            self.get_mapping_animation(
                func, input_line_copy.tick_marks,
                apply_function_to_submobjects
            ),
        )

    def get_sample_dots_mapping_animation(self, func, dots, **kwargs):
        return self.get_mapping_animation(
            func, dots, how_to_apply_func=apply_function_to_submobjects
        )

    def get_zoomed_camera_frame_mapping_animation(self, func, x=None, **kwargs):
        frame = self.zoomed_camera.frame
        if x is None:
            point = frame.get_center()
        else:
            point = self.get_input_point(x)
        point_mob = VectorizedPoint(point)
        return AnimationGroup(
            self.get_mapping_animation(func, point_mob),
            UpdateFromFunc(frame, lambda m: m.move_to(point_mob)),
        )

    def apply_function(self, func,
                       apply_function_to_number_line=True,
                       sample_dots=None,
                       local_sample_dots=None,
                       target_coordinate_values=None,
                       added_anims=None
                       ):
        zcbr_group = self.zoomed_camera_background_rectangle_group
        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        frame = self.zoomed_camera.frame

        anims = []
        if apply_function_to_number_line:
            anims.append(self.get_line_mapping_animation(func))
        if hasattr(self, "mini_line"):  # Test for if mini_line is in self?
            anims.append(self.get_mapping_animation(
                func, self.mini_line,
                how_to_apply_func=apply_function_to_center
            ))
        if sample_dots:
            anims.append(
                self.get_sample_dots_mapping_animation(func, sample_dots)
            )
        if self.zoom_activated:
            zoom_anim = self.get_zoomed_camera_frame_mapping_animation(func)
            anims.append(zoom_anim)
            anims.append(zcbr_anim)

            zoom_anim.update(1)
            target_mini_line = Line(frame.get_left(), frame.get_right())
            target_mini_line.scale(self.mini_line_scale_factor)
            target_mini_line.match_style(self.output_line.main_line)
            zoom_anim.update(0)
            zcbr_group.submobjects.insert(1, target_mini_line)
        if target_coordinate_values:
            coordinates = self.get_local_coordinates(
                self.output_line,
                *target_coordinate_values
            )
            anims.append(FadeIn(coordinates))
            zcbr_group.add(coordinates)
            self.local_target_coordinates = coordinates
        if local_sample_dots:
            anims.append(
                self.get_sample_dots_mapping_animation(func, local_sample_dots)
            )
            zcbr_group.add(local_sample_dots)
        if added_anims:
            anims += added_anims
        anims.append(Animation(zcbr_group))

        self.play(*anims)

    # Zooming
    def zoom_in_on_input(self, x,
                         local_sample_dots=None,
                         local_coordinate_values=None,
                         pop_out=True,
                         first_added_anims=[],
                         second_added_anims=[],
                         ):
        input_point = self.get_input_point(x)

        # Decide how to move camera frame into place
        frame = self.zoomed_camera.frame
        movement = ApplyMethod(frame.move_to, input_point)
        zcbr = self.zoomed_camera_background_rectangle
        zcbr_group = self.zoomed_camera_background_rectangle_group
        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        anims = []
        if self.zoom_activated:
            anims.append(movement)
            anims.append(zcbr_anim)
        else:
            movement.update(1)
            zcbr_anim.update(1)
            anims.append(self.get_zoom_in_animation())
            anims.append(FadeIn(zcbr))

        # Make sure frame is in final place
        for anim in anims:
            anim.update(1)

        # Add miniature number_line
        mini_line = self.mini_line = Line(frame.get_left(), frame.get_right())
        mini_line.scale(self.mini_line_scale_factor)
        mini_line.insert_n_anchor_points(self.num_inserted_number_line_anchors)
        mini_line.match_style(self.input_line.main_line)
        mini_line_copy = mini_line.copy()
        zcbr_group.add(mini_line_copy, mini_line)
        anims += [FadeIn(mini_line), FadeIn(mini_line_copy)]

        # Add tiny coordiantes
        if local_coordinate_values is None:
            local_coordinate_values = [x]
        local_coordinates = self.get_local_coordinates(
            self.input_line,
            *local_coordinate_values
        )
        anims.append(FadeIn(local_coordinates))
        zcbr_group.add(local_coordinates)
        self.local_coordinates = local_coordinates

        # Add tiny dots
        if local_sample_dots is not None:
            anims.append(LaggedStart(GrowFromCenter, local_sample_dots))
            zcbr_group.add(local_sample_dots)

        if first_added_anims:
            anims += first_added_anims

        anims.append(Animation(zcbr_group))
        if not pop_out:
            self.activate_zooming(animate=False)
        self.play(*anims)

        if not self.zoom_activated and pop_out:
            self.activate_zooming(animate=False)
            added_anims = second_added_anims or []
            self.play(
                self.get_zoomed_display_pop_out_animation(),
                *added_anims
            )

    def get_local_coordinates(self, line, *x_values, **kwargs):
        num_decimal_places = kwargs.get(
            "num_decimal_places", self.local_coordinate_num_decimal_places
        )
        result = VGroup()
        result.tick_marks = VGroup()
        result.numbers = VGroup()
        result.add(result.tick_marks, result.numbers)
        for x in x_values:
            tick_mark = Line(UP, DOWN)
            tick_mark.scale_to_fit_height(
                0.15 * self.zoomed_camera.frame.get_height()
            )
            tick_mark.move_to(line.number_to_point(x))
            result.tick_marks.add(tick_mark)

            number = DecimalNumber(x, num_decimal_places=num_decimal_places)
            number.scale(self.get_zoom_factor())
            number.scale(0.5)  # To make it seem small
            number.next_to(tick_mark, DOWN, buff=0.5 * number.get_height())
            result.numbers.add(number)
        return result

    def get_mobjects_in_zoomed_camera(self, mobjects):
        frame = self.zoomed_camera.frame
        x_min = frame.get_left()[0]
        x_max = frame.get_right()[0]
        y_min = frame.get_bottom()[1]
        y_max = frame.get_top()[1]
        result = VGroup()
        for mob in mobjects:
            for point in mob.get_all_points():
                if (x_min < point[0] < x_max) and (y_min < point[1] < y_max):
                    result.add(mob)
                    break
        return result

    # Helpers
    def get_input_point(self, x):
        return self.input_line.number_to_point(x)

    def get_output_point(self, fx):
        return self.output_line.number_to_point(fx)

    def number_func_to_point_func(self, number_func):
=======
    def get_line_mapping_animation(self, func, run_time=3, path_arc=30 * DEGREES):
>>>>>>> parent of b9f4b8b... Merge pull request #235 from 3b1b/alt-calc
        input_line, output_line = self.number_lines
        input_line_copy = input_line.deepcopy()
        input_line_copy.remove(input_line_copy.numbers)
        input_line_copy.set_stroke(width=2)

        def point_func(point):
            input_number = input_line.point_to_number(point)
            output_number = func(input_number)
            return output_line.number_to_point(output_number)

        return ApplyPointwiseFunction(
            point_func, input_line_copy,
            run_time=run_time,
            path_arc=path_arc,
        )


class ExampleNumberlineTransformationScene(NumberlineTransformationScene):
    def construct(self):
        func = lambda x: x**2
        anim = self.get_line_mapping_animation(func)
        self.play(anim)
        self.wait()

# Scenes


class WriteOpeningWords(Scene):
    def construct(self):
        raw_string1 = "Dear calculus student,"
        raw_string2 = "You're about to go through your first course. Like " + \
                      "any new topic, it will take some hard work to understand,"
        words1, words2 = [
            TextMobject("\\Large", *rs.split(" "))
            for rs in raw_string1, raw_string2
        ]
        words1.next_to(words2, UP, aligned_edge=LEFT, buff=LARGE_BUFF)
        words = VGroup(*it.chain(words1, words2))
        words.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        words.to_edge(UP)

        letter_wait = 0.05
        word_wait = 2 * letter_wait
        comma_wait = 5 * letter_wait
        for word in words:
            self.play(LaggedStart(
                FadeIn, word,
                run_time=len(word) * letter_wait,
                lag_ratio=1.5 / len(word)
            ))
            self.wait(word_wait)
            if word.get_tex_string()[-1] == ",":
                self.wait(comma_wait)


class StartingCalc101(PiCreatureScene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "image_frame_width": 3.5,
        "image_frame_height": 2.5,
    }

    def construct(self):
        self.show_you()
        self.show_images()
        self.show_mystery_topic()

    def show_you(self):
        randy = self.pi_creature
        title = self.title = Title("Calculus 101")
        you = TextMobject("You")
        arrow = Vector(DL, color=WHITE)
        arrow.next_to(randy, UR)
        you.next_to(arrow.get_start(), UP)

        self.play(
            Write(you),
            GrowArrow(arrow),
            randy.change, "erm", title
        )
        self.wait()
        self.play(Write(title, run_time=1))
        self.play(FadeOut(VGroup(arrow, you)))

    def show_images(self):
        randy = self.pi_creature
        images = self.get_all_images()
        modes = [
            "pondering",  # hard_work_image
            "pondering",  # neat_example_image
            "hesitant",  # not_so_neat_example_image
            "hesitant",  # physics_image
            "horrified",  # piles_of_formulas_image
            "horrified",  # getting_stuck_image
            "thinking",  # aha_image
            "thinking",  # graphical_intuition_image
        ]

        for i, image, mode in zip(it.count(), images, modes):
            anims = []
            if hasattr(image, "fade_in_anim"):
                anims.append(image.fade_in_anim)
                anims.append(FadeIn(image.frame))
            else:
                anims.append(FadeIn(image))

            if i >= 3:
                image_to_fade_out = images[i - 3]
                if hasattr(image_to_fade_out, "fade_out_anim"):
                    anims.append(image_to_fade_out.fade_out_anim)
                else:
                    anims.append(FadeOut(image_to_fade_out))

            if hasattr(image, "continual_animations"):
                self.add(*image.continual_animations)

            anims.append(ApplyMethod(randy.change, mode))
            self.play(*anims)
            self.wait()
            if i >= 3:
                if hasattr(image_to_fade_out, "continual_animations"):
                    self.remove(*image_to_fade_out.continual_animations)
                self.remove(image_to_fade_out.frame)
        self.wait(3)

        self.remaining_images = images[-3:]

    def show_mystery_topic(self):
        images = self.remaining_images
        randy = self.pi_creature

        mystery_box = Rectangle(
            width=self.image_frame_width,
            height=self.image_frame_height,
            stroke_color=YELLOW,
            fill_color=DARK_GREY,
            fill_opacity=0.5,
        )
        mystery_box.scale(1.5)
        mystery_box.next_to(self.title, DOWN, MED_LARGE_BUFF)

        rects = images[-1].rects.copy()
        rects.center()
        rects.scale_to_fit_height(FRAME_HEIGHT - 1)
        # image = rects.get_image()
        open_cv_image = cv2.imread(get_full_raster_image_path("alt_calc_hidden_image"))
        blurry_iamge = cv2.blur(open_cv_image, (50, 50))
        array = np.array(blurry_iamge)[:, :, ::-1]
        im_mob = ImageMobject(array)
        im_mob.replace(mystery_box, stretch=True)
        mystery_box.add(im_mob)

        q_marks = TexMobject("???").scale(3)
        q_marks.space_out_submobjects(1.5)
        q_marks.set_stroke(BLACK, 1)
        q_marks.move_to(mystery_box)
        mystery_box.add(q_marks)

        for image in images:
            if hasattr(image, "continual_animations"):
                self.remove(*image.continual_animations)
            self.play(
                image.shift, DOWN,
                image.fade, 1,
                randy.change, "erm",
                run_time=1.5
            )
            self.remove(image)
        self.wait()
        self.play(
            FadeInFromDown(mystery_box),
            randy.change, "confused"
        )
        self.wait(5)

    # Helpers

    def get_all_images(self):
        # Images matched to narration's introductory list
        images = VGroup(
            self.get_hard_work_image(),
            self.get_neat_example_image(),
            self.get_not_so_neat_example_image(),
            self.get_physics_image(),
            self.get_piles_of_formulas_image(),
            self.get_getting_stuck_image(),
            self.get_aha_image(),
            self.get_graphical_intuition_image(),
        )
        colors = color_gradient([BLUE, YELLOW], len(images))
        for i, image, color in zip(it.count(), images, colors):
            self.adjust_size(image)
            frame = Rectangle(
                width=self.image_frame_width,
                height=self.image_frame_height,
                color=color,
                stroke_width=2,
            )
            frame.move_to(image)
            image.frame = frame
            image.add(frame)
            image.next_to(self.title, DOWN)
            alt_i = (i % 3) - 1
            vect = (self.image_frame_width + LARGE_BUFF) * RIGHT
            image.shift(alt_i * vect)
        return images

    def adjust_size(self, group):
        group.scale_to_fit_width(min(
            group.get_width(),
            self.image_frame_width - 2 * MED_SMALL_BUFF
        ))
        group.scale_to_fit_height(min(
            group.get_height(),
            self.image_frame_height - 2 * MED_SMALL_BUFF
        ))
        return group

    def get_hard_work_image(self):
        new_randy = self.pi_creature.copy()
        new_randy.change_mode("telepath")
        bubble = new_randy.get_bubble(height=3.5, width=4)
        bubble.add_content(TexMobject("\\frac{d}{dx}(\\sin(\\sqrt{x}))"))
        bubble.add(bubble.content)  # Remove?

        return VGroup(new_randy, bubble)

    def get_neat_example_image(self):
        filled_circle = Circle(
            stroke_width=0,
            fill_color=BLUE_E,
            fill_opacity=1
        )
        area = TexMobject("\\pi r^2")
        area.move_to(filled_circle)
        unfilled_circle = Circle(
            stroke_width=3,
            stroke_color=YELLOW,
            fill_opacity=0,
        )
        unfilled_circle.next_to(filled_circle, RIGHT)
        circles = VGroup(filled_circle, unfilled_circle)
        circumference = TexMobject("2\\pi r")
        circumference.move_to(unfilled_circle)
        equation = TexMobject(
            "{d (\\pi r^2) \\over dx}  = 2\\pi r",
            tex_to_color_map={
                "\\pi r^2": BLUE_D,
                "2\\pi r": YELLOW,
            }
        )
        equation.next_to(circles, UP)

        return VGroup(
            filled_circle, area,
            unfilled_circle, circumference,
            equation
        )

    def get_not_so_neat_example_image(self):
        return TexMobject("\\int x \\cos(x) \\, dx")

    def get_physics_image(self):
        t_max = 6.5
        r = 0.2
        spring = ParametricFunction(
            lambda t: op.add(
                r * (np.sin(TAU * t) * RIGHT + np.cos(TAU * t) * UP),
                t * DOWN,
            ),
            t_min=0, t_max=t_max,
            color=WHITE,
            stroke_width=2,
        )
        spring.color_using_background_image("grey_gradient")

        weight = Square()
        weight.set_stroke(width=0)
        weight.set_fill(opacity=1)
        weight.color_using_background_image("grey_gradient")
        weight.scale_to_fit_height(0.4)

        t_tracker = ValueTracker(0)
        group = VGroup(spring, weight)
        group.continual_animations = [
            ContinualUpdateFromTimeFunc(
                t_tracker,
                lambda tracker, dt: tracker.set_value(
                    tracker.get_value() + dt
                )
            ),
            ContinualUpdateFromFunc(
                spring,
                lambda s: s.stretch_to_fit_height(
                    1.5 + 0.5 * np.cos(3 * t_tracker.get_value()),
                    about_edge=UP
                )
            ),
            ContinualUpdateFromFunc(
                weight,
                lambda w: w.move_to(spring.points[-1])
            )
        ]

        def update_group_style(alpha):
            spring.set_stroke(width=2 * alpha)
            weight.set_fill(opacity=alpha)

        group.fade_in_anim = UpdateFromAlphaFunc(
            group,
            lambda g, a: update_group_style(a)
        )
        group.fade_out_anim = UpdateFromAlphaFunc(
            group,
            lambda g, a: update_group_style(1 - a)
        )
        return group

    def get_piles_of_formulas_image(self):
        return TexMobject("(f/g)' = \\frac{gf' - fg'}{g^2}")

    def get_getting_stuck_image(self):
        creature = self.pi_creature.copy()
        creature.change_mode("angry")
        equation = TexMobject("\\frac{d}{dx}(x^x)")
        equation.scale_to_fit_height(creature.get_height() / 2)
        equation.next_to(creature, RIGHT, aligned_edge=UP)
        creature.look_at(equation)
        return VGroup(creature, equation)

    def get_aha_image(self):
        creature = self.pi_creature.copy()
        creature.change_mode("hooray")
        from old_projects.eoc.chapter3 import NudgeSideLengthOfCube
        scene = NudgeSideLengthOfCube(
            end_at_animation_number=7,
            skip_animations=True
        )
        group = VGroup(
            scene.cube, scene.faces,
            scene.bars, scene.corner_cube,
        )
        group.scale_to_fit_height(0.75 * creature.get_height())
        group.next_to(creature, RIGHT)
        creature.look_at(group)
        return VGroup(creature, group)

    def get_graphical_intuition_image(self):
        gs = GraphScene()
        gs.setup_axes()
        graph = gs.get_graph(
            lambda x: 0.2 * (x - 3) * (x - 5) * (x - 6) + 4,
            x_min=2, x_max=8,
        )
        rects = gs.get_riemann_rectangles(
            graph, x_min=2, x_max=8,
            stroke_width=0.5,
            dx=0.25
        )
        gs.add(graph, rects, gs.axes)
        group = VGroup(*gs.mobjects)
        self.adjust_size(group)
        group.next_to(self.title, DOWN, MED_LARGE_BUFF)
        group.rects = rects
        group.continual_animations = [
            NormalAnimationAsContinualAnimation(Write(rects)),
            NormalAnimationAsContinualAnimation(ShowCreation(graph)),
            NormalAnimationAsContinualAnimation(FadeIn(gs.axes)),
        ]
        self.adjust_size(group)
        return group


class GraphicalIntuitions(GraphScene):
    CONFIG = {
        "func": lambda x: 0.1 * (x - 2) * (x - 5) * (x - 7) + 4,
        "x_labeled_nums": range(1, 10),
    }

    def construct(self):
        self.setup_axes()
        axes = self.axes
        graph = self.get_graph(self.func)

        ss_group = self.get_secant_slope_group(
            x=2, graph=graph, dx=0.01,
            secant_line_length=6,
            secant_line_color=RED,
        )
        rects = self.get_riemann_rectangles(
            graph, x_min=2, x_max=8, dx=0.01, stroke_width=0
        )

        deriv_text = TextMobject(
            "Derivative $\\rightarrow$ slope",
            tex_to_color_map={"slope": ss_group.secant_line.get_color()}
        )
        deriv_text.to_edge(UP)
        integral_text = TextMobject(
            "Integral $\\rightarrow$ area",
            tex_to_color_map={"area": rects[0].get_color()}
        )
        integral_text.next_to(deriv_text, DOWN)

        self.play(
            Succession(Write(axes), ShowCreation(graph, run_time=2)),
            self.get_graph_words_anim(),
        )
        self.animate_secant_slope_group_change(
            ss_group,
            target_x=8,
            rate_func=there_and_back,
            run_time=5,
            added_anims=[
                Write(deriv_text),
                VFadeIn(ss_group, run_time=2),
            ]
        )
        self.play(FadeIn(integral_text))
        self.play(
            LaggedStart(
                GrowFromEdge, rects,
                lambda r: (r, DOWN)
            ),
            Animation(axes),
            Animation(graph),
        )
        self.wait()

    def get_graph_words_anim(self):
        words = VGroup(
            TextMobject("Graphs,"),
            TextMobject("graphs,"),
            TextMobject("non-stop graphs"),
            TextMobject("all day"),
            TextMobject("every day"),
            TextMobject("as if to visualize is to graph"),
        )
        for word in words:
            word.add_background_rectangle()
        words.arrange_submobjects(DOWN)
        words.to_edge(UP)
        return LaggedStart(
            FadeIn, words,
            rate_func=there_and_back,
            run_time=len(words) - 1,
            lag_ratio=0.6,
            remover=True
        )


class Wrapper(Scene):
    CONFIG = {
        "title": "",
        "title_kwargs": {},
        "screen_height": 6,
        "wait_time": 2,
    }

    def construct(self):
        rect = ScreenRectangle(height=self.screen_height)
        title = TextMobject(self.title, **self.title_kwargs)
        title.to_edge(UP)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait(self.wait_time)


class DomainColoringWrapper(Wrapper):
    CONFIG = {
        "title": "Complex $\\rightarrow$ Complex",
    }


class ChangingVectorFieldWrapper(Wrapper):
    CONFIG = {"title": "$(x, y, t) \\rightarrow (x', y')$"}


class ChangingVectorField(Scene):
    def construct(self):
        plane = self.plane = NumberPlane()
        plane.set_stroke(width=2)
        plane.add_coordinates()
        self.add(plane)

        time_tracker = self.time_tracker = ValueTracker(0)
        self.add(ContinualGrowValue(time_tracker))

        vectors = self.get_vectors()
        self.add(ContinualUpdateFromFunc(
            vectors,
            lambda vs: self.update_vectors(vs)
        ))
        self.wait(15)

    def get_vectors(self):
        vectors = VGroup()
        x_max = int(np.ceil(FRAME_WIDTH))
        y_max = int(np.ceil(FRAME_HEIGHT))
        step = 0.5
        for x in np.arange(-x_max, x_max + 1, step):
            for y in np.arange(-y_max, y_max + 1, step):
                point = x * RIGHT + y * UP
                vectors.add(Vector(RIGHT).shift(point))
        vectors.set_color_by_gradient(YELLOW, RED)
        return vectors

    def update_vectors(self, vectors):
        time = self.time_tracker.get_value()
        for vector in vectors:
            point = vector.get_start()
            out_point = self.func(point, time)
            norm = np.linalg.norm(out_point)
            if norm == 0:
                out_point = RIGHT  # Fake it
                vector.set_fill(opacity=0)
            else:
                alpha = sigmoid(2 * norm - 1)
                out_point *= 0.4 / norm
                color = interpolate_color(BLUE, RED, alpha)
                vector.set_fill(color, opacity=1)
                vector.set_stroke(BLACK, width=1)
            new_x, new_y = out_point[:2]
            vector.put_start_and_end_on(
                point, point + new_x * RIGHT + new_y * UP
            )

    def func(self, point, time):
        x, y, z = point
        time += 5
        return np.array([
            np.sin(time) * np.sin((y * x**2 + 0.9 * x + 0.8 * y) / 10) + 0.1,
            np.cos(time) * np.sin((y / (0.8 * x + 1)) / 10) + 0.1,
            0
        ])


class StandardDerivativeVisual(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        self.show_slope_of_graph()
        self.encourage_not_to_think_of_slope_as_definition()
        self.show_sensitivity()

    def add_title(self):
        title = self.title = TextMobject("Standard derivative visual")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)

    def show_function_graph(self):
        self.setup_axes()

        def func(x):
            x -= 5
            return 0.1 * (x + 3) * (x - 3) * x + 3
        graph = self.get_graph(func)
        graph_label = self.get_graph_label(graph, x_val=9.5)

        input_tracker = ValueTracker(4)

        def get_x_value():
            return input_tracker.get_value()

        def get_y_value():
            return graph.underlying_function(get_x_value())

        def get_x_point():
            return self.coords_to_point(get_x_value(), 0)

        def get_y_point():
            return self.coords_to_point(0, get_y_value())

        def get_graph_point():
            return self.coords_to_point(get_x_value(), get_y_value())

        def get_v_line():
            return DashedLine(get_x_point(), get_graph_point(), stroke_width=2)

        def get_h_line():
            return DashedLine(get_graph_point(), get_y_point(), stroke_width=2)

        input_triangle = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle, output_triangle:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)

        input_triangle_update = ContinualUpdateFromFunc(
            input_triangle, lambda m: m.move_to(get_x_point(), UP)
        )
        output_triangle_update = ContinualUpdateFromFunc(
            output_triangle, lambda m: m.move_to(get_y_point(), RIGHT)
        )

        x_label = TexMobject("x")
        x_label_update = ContinualUpdateFromFunc(
            x_label, lambda m: m.next_to(input_triangle, DOWN, SMALL_BUFF)
        )

        output_label = TexMobject("f(x)")
        output_label_update = ContinualUpdateFromFunc(
            output_label, lambda m: m.next_to(
                output_triangle, LEFT, SMALL_BUFF)
        )

        v_line = get_v_line()
        v_line_update = ContinualUpdateFromFunc(
            v_line, lambda vl: Transform(vl, get_v_line()).update(1)
        )

        h_line = get_h_line()
        h_line_update = ContinualUpdateFromFunc(
            h_line, lambda hl: Transform(hl, get_h_line()).update(1)
        )

        graph_dot = Dot(color=YELLOW)
        graph_dot_update = ContinualUpdateFromFunc(
            graph_dot, lambda m: m.move_to(get_graph_point())
        )

        self.play(
            ShowCreation(graph),
            Write(graph_label),
        )
        self.play(
            DrawBorderThenFill(input_triangle, run_time=1),
            Write(x_label),
            ShowCreation(v_line),
            GrowFromCenter(graph_dot),
        )
        self.add_foreground_mobject(graph_dot)
        self.play(
            ShowCreation(h_line),
            Write(output_label),
            DrawBorderThenFill(output_triangle, run_time=1)
        )
        self.add(
            input_triangle_update,
            x_label_update,
            graph_dot_update,
            v_line_update,
            h_line_update,
            output_triangle_update,
            output_label_update,
        )
        self.play(
            input_tracker.set_value, 8,
            run_time=6,
            rate_func=there_and_back
        )

        self.input_tracker = input_tracker
        self.graph = graph

    def show_slope_of_graph(self):
        input_tracker = self.input_tracker
        deriv_input_tracker = ValueTracker(input_tracker.get_value())

        # Slope line
        def get_slope_line():
            return self.get_secant_slope_group(
                x=deriv_input_tracker.get_value(),
                graph=self.graph,
                dx=0.01,
                secant_line_length=4
            ).secant_line

        slope_line = get_slope_line()
        slope_line_update = ContinualUpdateFromFunc(
            slope_line, lambda sg: Transform(sg, get_slope_line()).update(1)
        )

        def position_deriv_label(deriv_label):
            deriv_label.next_to(slope_line, UP)
            return deriv_label
        deriv_label = TexMobject(
            "\\frac{df}{dx}(x) =", "\\text{Slope}", "="
        )
        deriv_label.get_part_by_tex("Slope").match_color(slope_line)
        deriv_label_update = ContinualUpdateFromFunc(
            deriv_label, position_deriv_label
        )

        slope_decimal = DecimalNumber(slope_line.get_slope())
        slope_decimal.match_color(slope_line)
        slope_decimal_update = ContinualChangingDecimal(
            slope_decimal, lambda dt: slope_line.get_slope(),
            position_update_func=lambda m: m.next_to(
                deriv_label, RIGHT, SMALL_BUFF
            ).shift(0.2 * SMALL_BUFF * DOWN)
        )

        self.play(
            ShowCreation(slope_line),
            Write(deriv_label),
            Write(slope_decimal),
            run_time=1
        )
        self.wait()
        self.add(
            slope_line_update,
            # deriv_label_update,
            slope_decimal_update,
        )
        for x in 9, 2, 4:
            self.play(
                input_tracker.set_value, x,
                deriv_input_tracker.set_value, x,
                run_time=3
            )
            self.wait()

        self.deriv_input_tracker = deriv_input_tracker

    def encourage_not_to_think_of_slope_as_definition(self):
        morty = Mortimer(height=2)
        morty.to_corner(DR)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "Don't think of \\\\ this as the definition",
            bubble_kwargs={"height": 2, "width": 4}
        ))
        self.play(Blink(morty))
        self.wait()
        self.play(
            RemovePiCreatureBubble(morty),
            UpdateFromAlphaFunc(
                morty, lambda m, a: m.set_fill(opacity=1 - a),
                remover=True
            )
        )

    def show_sensitivity(self):
        input_tracker = self.input_tracker
        deriv_input_tracker = self.deriv_input_tracker

        self.wiggle_input()
        for x in 9, 7, 2:
            self.play(
                input_tracker.set_value, x,
                deriv_input_tracker.set_value, x,
                run_time=3
            )
            self.wiggle_input()

    ###
    def wiggle_input(self, dx=0.5, run_time=3):
        input_tracker = self.input_tracker

        x = input_tracker.get_value()
        x_min = x - dx
        x_max = x + dx
        y, y_min, y_max = map(
            self.graph.underlying_function,
            [x, x_min, x_max]
        )
        x_line = Line(
            self.coords_to_point(x_min, 0),
            self.coords_to_point(x_max, 0),
        )
        y_line = Line(
            self.coords_to_point(0, y_min),
            self.coords_to_point(0, y_max),
        )

        x_rect, y_rect = rects = VGroup(Rectangle(), Rectangle())
        rects.set_stroke(width=0)
        rects.set_fill(YELLOW, 0.5)
        x_rect.match_width(x_line)
        x_rect.stretch_to_fit_height(0.25)
        x_rect.move_to(x_line)
        y_rect.match_height(y_line)
        y_rect.stretch_to_fit_width(0.25)
        y_rect.move_to(y_line)

        self.play(
            ApplyMethod(
                input_tracker.set_value, input_tracker.get_value() + dx,
                rate_func=lambda t: wiggle(t, 6)
            ),
            FadeIn(
                rects,
                rate_func=squish_rate_func(smooth, 0, 0.33),
                remover=True,
            ),
            run_time=run_time,
        )
        self.play(FadeOut(rects))


class EoCWrapper(Scene):
    def construct(self):
        title = Title("Essence of calculus")
        self.play(Write(title))
        self.wait()
<<<<<<< HEAD


class IntroduceTransformationView(NumberlineTransformationScene):
    CONFIG = {
        "func": lambda x: 0.5 * np.sin(2 * x) + x,
        "number_line_config": {
            "x_min": 0,
            "x_max": 6,
            "unit_size": 2.0
        },
    }

    def construct(self):
        self.add_title()
        self.show_animation_preview()
        self.indicate_indicate_point_densities()
        self.show_zoomed_transformation()

    def add_title(self):
        title = self.title = TextMobject("$f(x)$ as a transformation")
        title.to_edge(UP)
        self.add(title)

    def show_animation_preview(self):
        input_points = self.get_sample_input_points()
        output_points = map(
            self.number_func_to_point_func(self.func),
            input_points
        )
        sample_dots = self.get_sample_dots()
        sample_dot_ghosts = sample_dots.copy().fade(0.5)
        arrows = VGroup(*[
            Arrow(ip, op, buff=MED_SMALL_BUFF)
            for ip, op in zip(input_points, output_points)
        ])
        arrows = arrows[1::3]
        arrows.set_stroke(BLACK, 1)

        self.play(
            LaggedStart(GrowFromCenter, sample_dots, run_time=1),
            LaggedStart(GrowArrow, arrows)
        )
        self.add(sample_dot_ghosts)
        self.apply_function(
            self.func, sample_dots=sample_dots
        )
        self.wait()
        self.play(LaggedStart(FadeOut, arrows, run_time=1))

        self.sample_dots = sample_dots
        self.sample_dot_ghosts = sample_dot_ghosts

    def indicate_indicate_point_densities(self):
        lower_brace = Brace(Line(LEFT, RIGHT), UP)
        upper_brace = lower_brace.copy()
        input_tracker = ValueTracker(0.5)
        dx = 0.5

        def update_upper_brace(brace):
            x = input_tracker.get_value()
            line = Line(
                self.get_input_point(x),
                self.get_input_point(x + dx),
            )
            brace.match_width(line, stretch=True)
            brace.next_to(line, UP, buff=SMALL_BUFF)
            return brace

        def update_lower_brace(brace):
            x = input_tracker.get_value()
            line = Line(
                self.get_output_point(self.func(x)),
                self.get_output_point(self.func(x + dx)),
            )
            brace.match_width(line, stretch=True)
            brace.next_to(line, UP, buff=SMALL_BUFF)
            return brace

        lower_brace_anim = UpdateFromFunc(lower_brace, update_lower_brace)
        upper_brace_anim = UpdateFromFunc(upper_brace, update_upper_brace)

        new_title = TextMobject(
            "$\\frac{df}{dx}(x)$ measures stretch/squishing"
        )
        new_title.move_to(self.title, UP)

        stretch_factor = DecimalNumber(0, color=YELLOW)
        stretch_factor_anim = ChangingDecimal(
            stretch_factor, lambda a: lower_brace.get_width() / upper_brace.get_width(),
            position_update_func=lambda m: m.next_to(lower_brace, UP, SMALL_BUFF)
        )

        self.play(
            GrowFromCenter(upper_brace),
            FadeOut(self.title),
            # FadeIn(new_title)
            Write(new_title, run_time=2)
        )
        self.title = new_title
        self.play(
            ReplacementTransform(upper_brace.copy(), lower_brace),
            GrowFromPoint(stretch_factor, upper_brace.get_center())
        )
        self.play(
            input_tracker.set_value, self.input_line.x_max - dx,
            lower_brace_anim,
            upper_brace_anim,
            stretch_factor_anim,
            run_time=8,
            rate_func=bezier([0, 0, 1, 1])
        )
        self.wait()

        new_sample_dots = self.get_sample_dots()
        self.play(
            FadeOut(VGroup(
                upper_brace, lower_brace, stretch_factor,
                self.sample_dots, self.moving_input_line,
            )),
            FadeIn(new_sample_dots),
        )
        self.sample_dots = new_sample_dots

    def show_zoomed_transformation(self):
        x = 2.75
        local_sample_dots = self.get_local_sample_dots(x)

        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=self.get_local_coordinate_values(x),
        )
        self.wait()
        self.apply_function(
            self.func,
            sample_dots=self.sample_dots,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=self.get_local_coordinate_values(self.func(x))
        )
        self.wait()


class TalkThroughXSquaredExample(IntroduceTransformationView):
    CONFIG = {
        "func": lambda x: x**2,
        "number_line_config": {
            "x_min": 0,
            "x_max": 5,
            "unit_size": 1.25,
        },
        "output_line_config": {
            "x_max": 25,
        },
        "default_delta_x": 0.2
    }

    def construct(self):
        self.add_title()
        self.show_specific_points_mapping()

    def add_title(self):
        title = self.title = TextMobject("$f(x) = x^2$")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.add(title)

    def show_specific_points_mapping(self):
        # First, just show integers as examples
        int_dots = self.get_sample_dots(1, 6, 1)
        int_dot_ghosts = int_dots.copy().fade(0.5)
        int_arrows = VGroup(*[
            Arrow(
                # num.get_bottom(),
                self.get_input_point(x),
                self.get_output_point(self.func(x)),
                buff=MED_SMALL_BUFF
            )
            for x, num in zip(range(1, 6), self.input_line.numbers[1:])
        ])
        point_func = self.number_func_to_point_func(self.func)

        numbers = self.input_line.numbers
        numbers.next_to(self.input_line, UP, SMALL_BUFF)
        self.titles[0].next_to(numbers, UP, MED_SMALL_BUFF, LEFT)
        # map(TexMobject.add_background_rectangle, numbers)
        # self.add_foreground_mobject(numbers)

        for dot, dot_ghost, arrow in zip(int_dots, int_dot_ghosts, int_arrows):
            arrow.match_color(dot)
            self.play(DrawBorderThenFill(dot, run_time=1))
            self.add(dot_ghost)
            self.play(
                GrowArrow(arrow),
                dot.apply_function_to_position, point_func
            )
        self.wait()

        # Show more sample_dots
        sample_dots = self.get_sample_dots()
        sample_dot_ghosts = sample_dots.copy().fade(0.5)

        self.play(
            LaggedStart(DrawBorderThenFill, sample_dots),
            LaggedStart(FadeOut, int_arrows),
        )
        self.remove(int_dot_ghosts)
        self.add(sample_dot_ghosts)
        self.apply_function(self.func, sample_dots=sample_dots)
        self.remove(int_dots)
        self.wait()

        self.sample_dots = sample_dots
        self.sample_dot_ghosts = sample_dot_ghosts

    def get_stretch_words(self, factor, color=RED, less_than_one=False):
        factor_str = "$%s$" % str(factor)
        result = TextMobject(
            "Scale \\\\ by", factor_str,
            tex_to_color_map={factor_str: color}
        )
        result.scale(0.7)
        la, ra = TexMobject("\\leftarrow \\rightarrow")
        if less_than_one:
            la, ra = ra, la
        if factor < 0:
            kwargs = {
                "path_arc": -np.pi,
                "use_rectangular_stem": False,
            }
            la = Arrow(DOWN, UP, **kwargs)
            ra = Arrow(UP, DOWN, **kwargs)
            for arrow in la, ra:
                arrow.pointwise_become_partial(arrow, 0, 0.9)
                arrow.tip.scale(2)
            VGroup(la, ra).match_height(result)
        la.next_to(result, LEFT)
        ra.next_to(result, RIGHT)
        result.add(la, ra)
        result.next_to(
            self.zoomed_display.get_top(), DOWN, SMALL_BUFF
        )
        return result

    def get_deriv_equation(self, x, rhs, color=RED):
        deriv_equation = self.deriv_equation = TexMobject(
            "\\frac{df}{dx}(", str(x), ")", "=", str(rhs),
            tex_to_color_map={str(x): color, str(rhs): color}
        )
        deriv_equation.next_to(self.title, DOWN, MED_LARGE_BUFF)
        return deriv_equation


class ZoomInOnXSquaredNearOne(TalkThroughXSquaredExample):
    def setup(self):
        TalkThroughXSquaredExample.setup(self)
        self.force_skipping()
        self.add_title()
        self.show_specific_points_mapping()
        self.revert_to_original_skipping_status()

    def construct(self):
        zoom_words = TextMobject("Zoomed view \\\\ near 1")
        zoom_words.next_to(self.zoomed_display, DOWN)
        # zoom_words.shift_onto_screen()

        x = 1
        local_sample_dots = self.get_local_sample_dots(x)
        local_coords = self.get_local_coordinate_values(x, dx=0.1)

        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        zcbr_group = self.zoomed_camera_background_rectangle_group
        frame = self.zoomed_camera.frame

        self.zoom_in_on_input(x, local_sample_dots, local_coords)
        self.play(FadeIn(zoom_words))
        self.wait()
        local_sample_dots.save_state()
        frame.save_state()
        self.mini_line.save_state()
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=local_coords
        )
        self.remove(sample_dot_ghost_copies)
        self.wait()

        # Go back
        self.play(
            frame.restore,
            self.mini_line.restore,
            local_sample_dots.restore,
            zcbr_anim,
            Animation(zcbr_group)
        )
        self.wait()

        # Zoom in even more
        extra_zoom_factor = 0.3
        one_group = VGroup(
            self.local_coordinates.tick_marks[1],
            self.local_coordinates.numbers[1],
        )
        all_other_coordinates = VGroup(
            self.local_coordinates.tick_marks[::2],
            self.local_coordinates.numbers[::2],
            self.local_target_coordinates,
        )
        self.play(frame.scale, extra_zoom_factor)
        new_local_sample_dots = self.get_local_sample_dots(x, delta_x=0.005)
        new_coordinate_values = self.get_local_coordinate_values(x, dx=0.02)
        new_local_coordinates = self.get_local_coordinates(
            self.input_line, *new_coordinate_values
        )

        self.play(
            Write(new_local_coordinates),
            Write(new_local_sample_dots),
            one_group.scale, extra_zoom_factor, {"about_point": self.get_input_point(1)},
            FadeOut(all_other_coordinates),
            *[
                ApplyMethod(dot.scale, extra_zoom_factor)
                for dot in local_sample_dots
            ]
        )
        self.remove(one_group, local_sample_dots)
        zcbr_group.remove(
            self.local_coordinates, self.local_target_coordinates,
            local_sample_dots
        )

        # Transform new zoomed view
        stretch_by_two_words = self.get_stretch_words(2)
        self.add_foreground_mobject(stretch_by_two_words)
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=new_local_sample_dots,
            target_coordinate_values=new_coordinate_values,
            added_anims=[FadeIn(stretch_by_two_words)]
        )
        self.remove(sample_dot_ghost_copies)
        self.wait()

        # Write derivative
        deriv_equation = self.get_deriv_equation(1, 2, color=RED)
        self.play(Write(deriv_equation))
        self.wait()


class ZoomInOnXSquaredNearThree(ZoomInOnXSquaredNearOne):
    CONFIG = {
        "zoomed_display_width": 4,
    }

    def construct(self):
        zoom_words = TextMobject("Zoomed view \\\\ near 3")
        zoom_words.next_to(self.zoomed_display, DOWN)

        x = 3
        local_sample_dots = self.get_local_sample_dots(x)
        local_coordinate_values = self.get_local_coordinate_values(x, dx=0.1)
        target_coordinate_values = self.get_local_coordinate_values(self.func(x), dx=0.1)

        color = self.sample_dots[len(self.sample_dots) / 2].get_color()
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        stretch_words = self.get_stretch_words(2 * x, color)
        deriv_equation = self.get_deriv_equation(x, 2 * x, color)

        self.add(deriv_equation)
        self.zoom_in_on_input(
            x,
            pop_out=False,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values
        )
        self.play(Write(zoom_words, run_time=1))
        self.wait()
        self.add_foreground_mobject(stretch_words)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=target_coordinate_values,
            added_anims=[Write(stretch_words)]
        )
        self.wait(2)


class ZoomInOnXSquaredNearOneFourth(ZoomInOnXSquaredNearOne):
    CONFIG = {
        "zoom_factor": 0.01,
        "local_coordinate_num_decimal_places": 4,
        "zoomed_display_width": 4,
        "default_delta_x": 0.25,
    }

    def construct(self):
        # Much copy-pasting from previous scenes.  Not great, but
        # the fastest way to get the ease-of-tweaking I'd like.
        zoom_words = TextMobject("Zoomed view \\\\ near $1/4$")
        zoom_words.next_to(self.zoomed_display, DOWN)

        x = 0.25
        local_sample_dots = self.get_local_sample_dots(
            x, sample_radius=2.5 * self.zoomed_camera.frame.get_width(),
        )
        local_coordinate_values = self.get_local_coordinate_values(
            x, dx=0.01,
        )
        target_coordinate_values = self.get_local_coordinate_values(
            self.func(x), dx=0.01,
        )

        color = RED
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        stretch_words = self.get_stretch_words("1/2", color, less_than_one=True)
        deriv_equation = self.get_deriv_equation("1/4", "1/2", color)

        one_fourth_point = self.get_input_point(x)
        one_fourth_arrow = Vector(0.5 * UP, color=WHITE)
        one_fourth_arrow.stem.stretch(0.75, 0)
        one_fourth_arrow.tip.scale(0.75, about_edge=DOWN)
        one_fourth_arrow.next_to(one_fourth_point, DOWN, SMALL_BUFF)
        one_fourth_label = TexMobject("0.25")
        one_fourth_label.match_height(self.input_line.numbers)
        one_fourth_label.next_to(one_fourth_arrow, DOWN, SMALL_BUFF)

        self.add(deriv_equation)
        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values,
            pop_out=False,
            first_added_anims=[
                FadeIn(one_fourth_label),
                GrowArrow(one_fourth_arrow),
            ]
        )
        self.play(Write(zoom_words, run_time=1))
        self.wait()
        self.add_foreground_mobject(stretch_words)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=target_coordinate_values,
            added_anims=[Write(stretch_words)]
        )
        self.wait(2)


class ZoomInOnXSquaredNearZero(ZoomInOnXSquaredNearOne):
    CONFIG = {
        "zoom_factor": 0.1,
        "zoomed_display_width": 4,
        "scale_by_term": "???",
    }

    def construct(self):
        zoom_words = TextMobject(
            "Zoomed %sx \\\\ near 0" % "{:,}".format(int(1.0 / self.zoom_factor))
        )
        zoom_words.next_to(self.zoomed_display, DOWN)

        x = 0
        local_sample_dots = self.get_local_sample_dots(
            x, sample_radius=2 * self.zoomed_camera.frame.get_width()
        )
        local_coordinate_values = self.get_local_coordinate_values(
            x, dx=self.zoom_factor
        )
        # target_coordinate_values = self.get_local_coordinate_values(
        #     self.func(x), dx=self.zoom_factor
        # )

        color = self.sample_dots[len(self.sample_dots) / 2].get_color()
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        stretch_words = self.get_stretch_words(
            self.scale_by_term, color, less_than_one=True
        )
        deriv_equation = self.get_deriv_equation(x, 2 * x, color)

        self.add(deriv_equation)
        self.zoom_in_on_input(
            x,
            pop_out=False,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values
        )
        self.play(Write(zoom_words, run_time=1))
        self.wait()
        self.add_foreground_mobject(stretch_words)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            # target_coordinate_values=target_coordinate_values,
            added_anims=[
                Write(stretch_words),
                MaintainPositionRelativeTo(
                    self.local_coordinates,
                    self.zoomed_camera.frame
                )
            ]
        )
        self.wait(2)


class ZoomInOnXSquared100xZero(ZoomInOnXSquaredNearZero):
    CONFIG = {
        "zoom_factor": 0.01
    }


class ZoomInOnXSquared1000xZero(ZoomInOnXSquaredNearZero):
    CONFIG = {
        "zoom_factor": 0.001,
        "local_coordinate_num_decimal_places": 3,
    }


class ZoomInOnXSquared10000xZero(ZoomInOnXSquaredNearZero):
    CONFIG = {
        "zoom_factor": 0.0001,
        "local_coordinate_num_decimal_places": 4,
        "scale_by_term": "0",
    }


class XSquaredForNegativeInput(TalkThroughXSquaredExample):
    CONFIG = {
        "input_line_config": {
            "x_min": -4,
            "x_max": 4,
        },
        "input_line_zero_point": 0.5 * UP + 0 * LEFT,
        "output_line_config": {},
        "default_mapping_animation_config": {
            "path_arc": 30 * DEGREES
        },
        "zoomed_display_width": 4,
    }

    def construct(self):
        self.add_title()
        self.show_full_transformation()
        self.zoom_in_on_example()

    def show_full_transformation(self):
        sample_dots = self.get_sample_dots()

        self.play(LaggedStart(DrawBorderThenFill, sample_dots))
        self.add_sample_dot_ghosts(sample_dots)
        self.apply_function(self.func, sample_dots=sample_dots)
        self.wait()

    def zoom_in_on_example(self):
        x = -2

        local_sample_dots = self.get_local_sample_dots(x)
        local_coordinate_values = self.get_local_coordinate_values(
            x, dx=0.1
        )
        target_coordinate_values = self.get_local_coordinate_values(
            self.func(x), dx=0.1
        )
        deriv_equation = self.get_deriv_equation(x, 2 * x, color=BLUE)
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        scale_words = self.get_stretch_words(-4, color=BLUE)

        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values,
        )
        self.wait()
        self.play(Write(deriv_equation))
        self.add_foreground_mobject(scale_words)
        self.play(Write(scale_words))
        self.apply_function(
            self.func,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=target_coordinate_values
        )
        self.wait()
=======
>>>>>>> parent of b9f4b8b... Merge pull request #235 from 3b1b/alt-calc
