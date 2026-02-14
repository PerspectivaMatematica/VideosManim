from manim import *
import numpy as np


class RollingWindowRiskScoreScene(Scene):
    """Run with: manim -pqh IntroVideo4.py RollingWindowRiskScoreScene"""

    def construct(self):
        # -----------------------------
        # Configuration
        # -----------------------------
        N_TOTAL = 170
        N_INITIAL = 80
        L = 60
        W = 0.65

        np.random.seed(7)
        t = np.arange(N_TOTAL)
        base = 1.8 * np.sin(t / 10.0) + 0.9 * np.sin(t / 23.0 + 1.4)
        trend = 0.015 * t
        noise = np.random.normal(scale=0.32, size=N_TOTAL)
        x_vals = base + trend + noise

        # Precompute RS components for performance and stable animation
        trend_vals = np.zeros(N_TOTAL)
        mom_vals = np.zeros(N_TOTAL)
        rs_vals = np.zeros(N_TOTAL)

        for i in range(N_TOTAL):
            start = max(0, i - L + 1)
            window = x_vals[start : i + 1]
            x_min = window.min()
            x_max = window.max()
            span = max(x_max - x_min, 1e-8)

            t_i = (x_vals[i] - x_min) / span
            if i == 0:
                mom_i = 0.5
            else:
                mom_i = 0.5 * (1 + (x_vals[i] - x_vals[i - 1]) / span)

            t_i = float(np.clip(t_i, 0, 1))
            mom_i = float(np.clip(mom_i, 0, 1))
            rs_i = float(np.clip(W * t_i + (1 - W) * mom_i, 0, 1))

            trend_vals[i] = t_i
            mom_vals[i] = mom_i
            rs_vals[i] = rs_i

        # -----------------------------
        # Layout
        # -----------------------------
        title = Text("Rolling-Window Risk Score", font_size=38, weight=BOLD).to_edge(UP)

        top_axes = Axes(
            x_range=[1, N_TOTAL, 20],
            y_range=[float(x_vals.min() - 0.8), float(x_vals.max() + 0.8), 1],
            x_length=11.0,
            y_length=2.6,
            axis_config={"stroke_width": 2, "include_ticks": False},
            tips=False,
        )
        top_axes.to_edge(LEFT, buff=0.5).shift(UP * 1.2)
        top_lbl = Text("Raw series  $x_t$", font_size=24).next_to(top_axes, UP, buff=0.15)

        bottom_axes = Axes(
            x_range=[1, N_TOTAL, 20],
            y_range=[0, 1, 0.2],
            x_length=11.0,
            y_length=2.6,
            axis_config={"stroke_width": 2, "include_ticks": False},
            tips=False,
        )
        bottom_axes.next_to(top_axes, DOWN, buff=1.0)
        bottom_lbl = Tex(r"Risk score  $RS_t \in [0,1]$").scale(0.7).next_to(bottom_axes, UP, buff=0.15)

        x_coords = [top_axes.c2p(i + 1, x_vals[i]) for i in range(N_TOTAL)]
        rs_coords = [bottom_axes.c2p(i + 1, rs_vals[i]) for i in range(N_TOTAL)]

        index_tracker = ValueTracker(2)

        def idx_now() -> int:
            return int(np.clip(np.floor(index_tracker.get_value()), 2, N_TOTAL))

        # -----------------------------
        # Dynamic visuals
        # -----------------------------
        x_line = VMobject(color=BLUE_D, stroke_width=3)
        rs_line = VMobject(color=ORANGE, stroke_width=3)

        def update_x_line(mob):
            i = idx_now()
            mob.set_points_as_corners(x_coords[:i])
            return mob

        def update_rs_line(mob):
            i = idx_now()
            mob.set_points_as_corners(rs_coords[:i])
            return mob

        x_line.add_updater(update_x_line)
        rs_line.add_updater(update_rs_line)

        x_dot = always_redraw(lambda: Dot(x_coords[idx_now() - 1], radius=0.05, color=BLUE_D))
        rs_dot = always_redraw(lambda: Dot(rs_coords[idx_now() - 1], radius=0.05, color=ORANGE))

        window_box = always_redraw(
            lambda: Polygon(
                top_axes.c2p(max(1, idx_now() - L + 1), top_axes.y_range[0]),
                top_axes.c2p(idx_now(), top_axes.y_range[0]),
                top_axes.c2p(idx_now(), top_axes.y_range[1]),
                top_axes.c2p(max(1, idx_now() - L + 1), top_axes.y_range[1]),
                stroke_width=0,
                fill_color=GREY_B,
                fill_opacity=0.3,
            )
        )

        window_label = always_redraw(
            lambda: Text("L=60 rolling window", font_size=18, color=GREY_D).next_to(window_box, UP, buff=0.08)
        )

        def minmax_points():
            i = idx_now() - 1
            start = max(0, i - L + 1)
            win = x_vals[start : i + 1]
            min_rel = int(np.argmin(win))
            max_rel = int(np.argmax(win))
            min_idx = start + min_rel
            max_idx = start + max_rel
            return min_idx, max_idx

        min_dot = always_redraw(lambda: Dot(x_coords[minmax_points()[0]], color=TEAL_C, radius=0.055))
        max_dot = always_redraw(lambda: Dot(x_coords[minmax_points()[1]], color=RED_C, radius=0.055))

        min_tag = always_redraw(lambda: Text("min", font_size=16, color=TEAL_C).next_to(min_dot, DOWN, buff=0.05))
        max_tag = always_redraw(lambda: Text("max", font_size=16, color=RED_C).next_to(max_dot, UP, buff=0.05))

        # Equation and live values panel
        eq_trend = MathTex(r"T_t = \frac{x_t-\min}{\max-\min}").scale(0.62)
        eq_mom = MathTex(r"\mathrm{Mom}_t = 0.5\left(1+\frac{x_t-x_{t-1}}{\max-\min}\right)").scale(0.62)
        eq_rs = MathTex(r"RS_t = w\,T_t + (1-w)\,\mathrm{Mom}_t", r",\; w=0.65").scale(0.62)

        val_t_num = DecimalNumber(0.0, num_decimal_places=3, font_size=28, color=BLUE_D)
        val_m_num = DecimalNumber(0.0, num_decimal_places=3, font_size=28, color=GREEN_D)
        val_rs_num = DecimalNumber(0.0, num_decimal_places=3, font_size=28, color=ORANGE)

        val_t_num.add_updater(lambda m: m.set_value(trend_vals[idx_now() - 1]))
        val_m_num.add_updater(lambda m: m.set_value(mom_vals[idx_now() - 1]))
        val_rs_num.add_updater(lambda m: m.set_value(rs_vals[idx_now() - 1]))

        live_vals = VGroup(
            VGroup(Text("T_t:", font_size=24), val_t_num).arrange(RIGHT, buff=0.15),
            VGroup(Text("Mom_t:", font_size=24), val_m_num).arrange(RIGHT, buff=0.15),
            VGroup(Text("RS_t:", font_size=24), val_rs_num).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        eq_panel = VGroup(eq_trend, eq_mom, eq_rs, live_vals).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22
        )
        eq_panel.to_edge(RIGHT, buff=0.4).shift(DOWN * 0.05)

        # -----------------------------
        # Animation sequence
        # -----------------------------
        self.play(FadeIn(title, shift=UP * 0.2))
        self.play(Create(top_axes), FadeIn(top_lbl, shift=UP * 0.1), run_time=1.0)
        self.play(Create(bottom_axes), FadeIn(bottom_lbl, shift=UP * 0.1), run_time=1.0)

        self.play(Write(eq_trend), run_time=0.8)
        self.play(Write(eq_mom), run_time=0.8)
        self.play(Write(eq_rs), run_time=0.8)
        self.play(FadeIn(live_vals, shift=RIGHT * 0.15), run_time=0.7)

        self.add(window_box, window_label)
        self.add(x_line, rs_line, x_dot, rs_dot, min_dot, max_dot, min_tag, max_tag)

        # Build first ~80 points
        self.play(index_tracker.animate.set_value(N_INITIAL), run_time=4.5, rate_func=smooth)

        # Conceptual bridge: emphasize RS equation -> bottom plot
        rs_focus = SurroundingRectangle(eq_rs[0], color=ORANGE, buff=0.08)
        arrow = Arrow(
            rs_focus.get_left() + LEFT * 0.15,
            bottom_axes.c2p(N_INITIAL - 6, 0.82),
            color=ORANGE,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.08,
        )
        self.play(Create(rs_focus), GrowArrow(arrow), run_time=0.8)
        self.play(Indicate(rs_dot, color=ORANGE, scale_factor=1.5), run_time=0.6)
        self.play(FadeOut(rs_focus), FadeOut(arrow), run_time=0.5)

        # New data arrivals until N_TOTAL
        self.play(index_tracker.animate.set_value(N_TOTAL), run_time=6.5, rate_func=linear)

        self.wait(1.2)
