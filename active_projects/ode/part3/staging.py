from manimlib.imports import *

from active_projects.ode.part2.fourier_series import FourierOfTrebleClef


class FourierNameIntro(Scene):
    def construct(self):
        self.show_two_titles()
        self.transition_to_image()
        self.show_paper()

    def show_two_titles(self):
        lt = TextMobject("Fourier", "Series")
        rt = TextMobject("Fourier", "Transform")
        lt_variants = VGroup(
            TextMobject("Complex", "Fourier Series"),
            TextMobject("Discrete", "Fourier Series"),
        )
        rt_variants = VGroup(
            TextMobject("Discrete", "Fourier Transform"),
            TextMobject("Fast", "Fourier Transform"),
            TextMobject("Quantum", "Fourier Transform"),
        )

        titles = VGroup(lt, rt)
        titles.scale(1.5)
        for title, vect in (lt, LEFT), (rt, RIGHT):
            title.move_to(vect * FRAME_WIDTH / 4)
            title.to_edge(UP)

        for title, variants in (lt, lt_variants), (rt, rt_variants):
            title.save_state()
            title.target = title.copy()
            title.target.scale(1 / 1.5, about_edge=RIGHT)
            for variant in variants:
                variant.move_to(title.target, UR)
                variant[0].set_color(YELLOW)

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.set_stroke(WHITE, 2)

        self.play(
            FadeInFrom(lt, RIGHT),
            ShowCreation(v_line)
        )
        self.play(
            FadeInFrom(rt, LEFT),
        )
        # Edit in images of circle animations
        # and clips from FT video

        # for title, variants in (rt, rt_variants), (lt, lt_variants):
        for title, variants in [(rt, rt_variants)]:
            # Maybe do it for left variant, maybe not...
            self.play(
                MoveToTarget(title),
                FadeInFrom(variants[0][0], LEFT)
            )
            for v1, v2 in zip(variants, variants[1:]):
                self.play(
                    FadeOutAndShift(v1[0], UP),
                    FadeInFrom(v2[0], DOWN),
                    run_time=0.5,
                )
                self.wait(0.5)
            self.play(
                Restore(title),
                FadeOut(variants[-1][0])
            )
        self.wait()

        self.titles = titles
        self.v_line = v_line

    def transition_to_image(self):
        titles = self.titles
        v_line = self.v_line

        image = ImageMobject("Joseph Fourier")
        image.set_height(5)
        image.to_edge(LEFT)

        frame = Rectangle()
        frame.replace(image, stretch=True)

        name = TextMobject("Joseph", "Fourier")
        fourier_part = name.get_part_by_tex("Fourier")
        fourier_part.set_color(YELLOW)
        F_sym = fourier_part[0]
        name.match_width(image)
        name.next_to(image, DOWN)

        self.play(
            ReplacementTransform(v_line, frame),
            FadeIn(image),
            FadeIn(name[0]),
            *[
                ReplacementTransform(
                    title[0].deepcopy(),
                    name[1]
                )
                for title in titles
            ],
            titles.scale, 0.65,
            titles.arrange, DOWN,
            titles.next_to, image, UP,
        )
        self.wait()

        big_F = F_sym.copy()
        big_F.set_fill(opacity=0)
        big_F.set_stroke(WHITE, 2)
        big_F.set_height(3)
        big_F.move_to(midpoint(
            image.get_right(),
            RIGHT_SIDE,
        ))
        big_F.shift(DOWN)
        equivalence = VGroup(
            fourier_part.copy().scale(1.25),
            TexMobject("\\Leftrightarrow").scale(1.5),
            TextMobject("Break down into\\\\pure frequencies"),
        )
        equivalence.arrange(RIGHT)
        equivalence.move_to(big_F)
        equivalence.to_edge(UP)

        self.play(
            FadeIn(big_F),
            TransformFromCopy(fourier_part, equivalence[0]),
            Write(equivalence[1:]),
        )
        self.wait(3)
        self.play(FadeOut(VGroup(big_F, equivalence)))

        self.image = image
        self.name = name

    def show_paper(self):
        image = self.image
        paper = ImageMobject("Fourier paper")
        paper.match_height(image)
        paper.next_to(image, RIGHT, MED_LARGE_BUFF)

        date = TexMobject("1822")
        date.next_to(paper, DOWN)
        date_rect = SurroundingRectangle(date)
        date_rect.scale(0.3)
        date_rect.set_color(RED)
        date_rect.shift(1.37 * UP + 0.08 * LEFT)
        date_arrow = Arrow(
            date_rect.get_bottom(),
            date.get_top(),
            buff=SMALL_BUFF,
            color=date_rect.get_color(),
        )

        heat_rect = SurroundingRectangle(
            TextMobject("CHALEUR")
        )
        heat_rect.set_color(RED)
        heat_rect.scale(0.6)
        heat_rect.move_to(
            paper.get_top() +
            1.22 * DOWN + 0.37 * RIGHT
        )
        heat_word = TextMobject("Heat")
        heat_word.scale(1.5)
        heat_word.next_to(paper, UP)
        heat_word.shift(paper.get_width() * RIGHT)
        heat_arrow = Arrow(
            heat_rect.get_top(),
            heat_word.get_left(),
            buff=0.1,
            path_arc=-60 * DEGREES,
            color=heat_rect.get_color(),
        )

        self.play(FadeInFrom(paper, LEFT))
        self.play(
            ShowCreation(date_rect),
        )
        self.play(
            GrowFromPoint(date, date_arrow.get_start()),
            ShowCreation(date_arrow),
        )
        self.wait(3)

        # Insert animation of circles/sine waves
        # approximating a square wave

        self.play(
            ShowCreation(heat_rect),
        )
        self.play(
            GrowFromPoint(heat_word, heat_arrow.get_start()),
            ShowCreation(heat_arrow),
        )
        self.wait(3)


class FourierSeriesIllustraiton(Scene):
    CONFIG = {
        "n_range": range(1, 31, 2),
    }

    def construct(self):
        n_range = self.n_range

        axes1 = Axes(
            number_line_config={
                "include_tip": False,
            },
            x_axis_config={
                "tick_frequency": 1 / 4,
                "unit_size": 4,
            },
            x_min=0,
            x_max=1,
            y_min=-1,
            y_max=1,
        )
        axes1.x_axis.add_numbers(
            0.5, 1,
            number_config={"num_decimal_places": 1}
        )
        axes2 = axes1.copy()
        target_func_graph = self.get_target_func_graph(axes2)
        axes2.add(target_func_graph)

        arrow = Arrow(LEFT, RIGHT, color=WHITE)
        group = VGroup(axes1, arrow, axes2)
        group.arrange(RIGHT, buff=LARGE_BUFF)
        group.shift(2 * UP)

        sine_graphs = VGroup(*[
            axes1.get_graph(self.generate_nth_func(n))
            for n in n_range
        ])
        sine_graphs.set_stroke(width=3)
        sine_graphs.set_color_by_gradient(
            BLUE, GREEN, RED, YELLOW, PINK,
            BLUE, GREEN, RED, YELLOW, PINK,
        )

        partial_sums = VGroup(*[
            axes1.get_graph(self.generate_kth_partial_sum_func(k + 1))
            for k in range(len(n_range))
        ])
        partial_sums.match_style(sine_graphs)

        sum_tex = self.get_sum_tex()
        sum_tex.next_to(axes1, DOWN, LARGE_BUFF)
        sum_tex.shift(RIGHT)
        eq = TexMobject("=")
        target_func_tex = self.get_target_func_tex()
        target_func_tex.next_to(axes2, DOWN)
        target_func_tex.match_y(sum_tex)
        eq.move_to(midpoint(
            target_func_tex.get_left(),
            sum_tex.get_right()
        ))

        range_words = TextMobject(
            "For $0 \\le x \\le 1$"
        )
        range_words.next_to(
            VGroup(sum_tex, target_func_tex),
            DOWN,
        )

        rects = it.chain(
            [
                SurroundingRectangle(piece)
                for piece in self.get_sum_tex_pieces(sum_tex)
            ],
            it.cycle([None])
        )

        self.add(axes1, arrow, axes2)
        self.add(target_func_graph)
        self.add(sum_tex, eq, target_func_tex)
        self.add(range_words)

        curr_partial_sum = axes1.get_graph(lambda x: 0)
        curr_partial_sum.set_stroke(width=1)
        for sine_graph, partial_sum, rect in zip(sine_graphs, partial_sums, rects):
            anims1 = [
                ShowCreation(sine_graph)
            ]
            partial_sum.set_stroke(BLACK, 4, background=True)
            anims2 = [
                curr_partial_sum.set_stroke,
                {"width": 1, "opacity": 0.5},
                curr_partial_sum.set_stroke,
                {"width": 0, "background": True},
                ReplacementTransform(
                    sine_graph, partial_sum,
                    remover=True
                ),
            ]
            if rect:
                rect.match_style(sine_graph)
                anims1.append(ShowCreation(rect))
                anims2.append(FadeOut(rect))
            self.play(*anims1)
            self.play(*anims2)
            curr_partial_sum = partial_sum

    def get_sum_tex(self):
        return TexMobject(
            "\\frac{4}{\\pi} \\left(",
            "\\frac{\\cos(\\pi x)}{1}",
            "-\\frac{\\cos(3\\pi x)}{3}",
            "+\\frac{\\cos(5\\pi x)}{5}",
            "- \\cdots \\right)"
        ).scale(0.75)

    def get_sum_tex_pieces(self, sum_tex):
        return sum_tex[1:4]

    def get_target_func_tex(self):
        step_tex = TexMobject(
            """
            1 \\quad \\text{if $x < 0.5$} \\\\
            0 \\quad \\text{if $x = 0.5$} \\\\
            -1 \\quad \\text{if $x > 0.5$} \\\\
            """
        )
        lb = Brace(step_tex, LEFT, buff=SMALL_BUFF)
        step_tex.add(lb)
        return step_tex

    def get_target_func_graph(self, axes):
        step_func = axes.get_graph(
            lambda x: (1 if x < 0.5 else -1),
            discontinuities=[0.5],
            color=YELLOW,
            stroke_width=3,
        )
        dot = Dot(axes.c2p(0.5, 0), color=step_func.get_color())
        dot.scale(0.5)
        step_func.add(dot)
        return step_func

    # def generate_nth_func(self, n):
    #     return lambda x: (4 / n / PI) * np.sin(TAU * n * x)

    def generate_nth_func(self, n):
        return lambda x: np.prod([
            (4 / PI),
            (1 / n) * (-1)**((n - 1) / 2),
            np.cos(PI * n * x)
        ])

    def generate_kth_partial_sum_func(self, k):
        return lambda x: np.sum([
            self.generate_nth_func(n)(x)
            for n in self.n_range[:k]
        ])


class FourierSeriesOfLineIllustration(FourierSeriesIllustraiton):
    CONFIG = {
        "n_range": range(1, 31, 2)
    }

    def get_sum_tex(self):
        return TexMobject(
            "\\frac{8}{\\pi^2} \\left(",
            "\\frac{\\cos(\\pi x)}{1^2}",
            "+\\frac{\\cos(3\\pi x)}{3^2}",
            "+\\frac{\\cos(5\\pi x)}{5^2}",
            "+ \\cdots \\right)"
        ).scale(0.75)

    # def get_sum_tex_pieces(self, sum_tex):
    #     return sum_tex[1:4]

    def get_target_func_tex(self):
        result = TexMobject("1 - 2x")
        result.scale(1.5)
        point = VectorizedPoint()
        point.next_to(result, RIGHT, 1.5 * LARGE_BUFF)
        # result.add(point)
        return result

    def get_target_func_graph(self, axes):
        return axes.get_graph(
            lambda x: 1 - 2 * x,
            color=YELLOW,
            stroke_width=3,
        )

    # def generate_nth_func(self, n):
    #     return lambda x: (4 / n / PI) * np.sin(TAU * n * x)

    def generate_nth_func(self, n):
        return lambda x: np.prod([
            (8 / PI**2),
            (1 / n**2),
            np.cos(PI * n * x)
        ])


class CircleAnimationOfF(FourierOfTrebleClef):
    CONFIG = {
        "height": 3,
        "n_circles": 200,
        "run_time": 10,
        "arrow_config": {
            "tip_length": 0.1,
            "stroke_width": 2,
        }
    }

    def get_shape(self):
        path = VMobject()
        shape = TexMobject("F")
        for sp in shape.family_members_with_points():
            path.append_points(sp.points)
        return path


class NewSceneName(Scene):
    def construct(self):
        pass
