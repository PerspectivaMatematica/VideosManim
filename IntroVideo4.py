from manim import *
import numpy as np


class RiskScoreDefinitions(Scene):
    def construct(self):
        title = Text("Risk Score Indicator", weight=BOLD).to_edge(UP)

        trend_eq = MathTex(
            r"T_t = \frac{x_t - \min(x)}{\max(x) - \min(x)}"
        ).scale(0.9)
        momentum_eq = MathTex(
            r"\mathrm{Mom}_t = \frac{1 + \frac{x_t - x_{t-1}}{\max(x)-\min(x)}}{2}"
        ).scale(0.9)
        combined_eq = MathTex(
            r"RS_t = w\,T_t + (1-w)\,\mathrm{Mom}_t"
        ).scale(0.9)

        w_label = Tex(r"$w$: weight of trend component", color=YELLOW).scale(0.7)

        equations = VGroup(trend_eq, momentum_eq, combined_eq, w_label).arrange(
            DOWN, aligned_edge=LEFT, buff=0.45
        )
        equations.next_to(title, DOWN, buff=0.7)

        intuition = VGroup(
            Text("Trend: position within range", font_size=28, color=BLUE_C),
            Text("Momentum: recent change", font_size=28, color=GREEN_C),
            Text("Combined: 1=high risk, 0=low risk", font_size=28, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        intuition.to_edge(DOWN).shift(UP * 0.3)

        self.play(Write(title))
        self.play(FadeIn(trend_eq, shift=UP * 0.2))
        self.play(FadeIn(momentum_eq, shift=UP * 0.2))
        self.play(FadeIn(combined_eq, shift=UP * 0.2), FadeIn(w_label, shift=UP * 0.2))

        for line in intuition:
            self.play(Write(line), run_time=0.7)

        self.wait(1)
        self.play(FadeOut(VGroup(title, equations, intuition)))


class RiskScoreSeriesExample(Scene):
    def _risk_series(self, values, w=0.65):
        arr = np.array(values, dtype=float)
        min_v, max_v = arr.min(), arr.max()
        span = max(max_v - min_v, 1e-8)

        trend = (arr - min_v) / span

        momentum = np.zeros_like(arr)
        momentum[0] = 0.5
        momentum[1:] = (1 + (arr[1:] - arr[:-1]) / span) / 2

        rs = w * trend + (1 - w) * momentum
        return trend, momentum, rs

    def _plot_series_group(self, title_text, raw_values, color, anchor):
        trend, momentum, rs = self._risk_series(raw_values)
        n = len(raw_values)

        title = Text(title_text, font_size=30, color=color)
        axes = Axes(
            x_range=[1, n, 1],
            y_range=[0, 1, 0.2],
            x_length=5.2,
            y_length=2.8,
            axis_config={"include_numbers": False},
        )
        labels = axes.get_axis_labels(
            Tex("t").scale(0.7), Tex("score").scale(0.7)
        )

        trend_line = axes.plot_line_graph(
            x_values=list(range(1, n + 1)), y_values=trend, line_color=BLUE_C, add_vertex_dots=False
        )
        mom_line = axes.plot_line_graph(
            x_values=list(range(1, n + 1)), y_values=momentum, line_color=GREEN_C, add_vertex_dots=False
        )
        rs_line = axes.plot_line_graph(
            x_values=list(range(1, n + 1)), y_values=rs, line_color=ORANGE, add_vertex_dots=False
        )

        tracker = ValueTracker(1)
        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(
                    tracker.get_value(),
                    np.interp(tracker.get_value(), np.arange(1, n + 1), rs),
                ),
                color=ORANGE,
                radius=0.06,
            )
        )

        legend = VGroup(
            Dot(color=BLUE_C, radius=0.05), Tex("Trend").scale(0.55),
            Dot(color=GREEN_C, radius=0.05), Tex("Momentum").scale(0.55),
            Dot(color=ORANGE, radius=0.05), Tex("RS").scale(0.55),
        ).arrange(RIGHT, buff=0.15)

        panel = VGroup(title, VGroup(axes, labels), legend)
        panel.arrange(DOWN, buff=0.15)
        panel.move_to(anchor)

        graph_group = VGroup(axes, labels, trend_line, mom_line, rs_line, moving_dot)
        graph_group.move_to(panel[1].get_center())
        legend.next_to(graph_group, DOWN, buff=0.15)
        title.next_to(graph_group, UP, buff=0.2)

        return VGroup(title, graph_group, legend), tracker, n

    def construct(self):
        intro = Text("Example: Inflation and Growth Risk Scores", font_size=34, weight=BOLD).to_edge(UP)
        self.play(Write(intro))

        inflation_values = [2.0, 2.4, 2.8, 3.4, 3.0, 3.8, 4.2]
        growth_values = [3.6, 3.3, 3.0, 2.9, 2.5, 2.8, 2.2]

        left_panel, left_tracker, left_n = self._plot_series_group(
            "Inflation Risk", inflation_values, RED_C, LEFT * 3.2 + DOWN * 0.3
        )
        right_panel, right_tracker, right_n = self._plot_series_group(
            "Growth Risk", growth_values, PURPLE_C, RIGHT * 3.2 + DOWN * 0.3
        )

        self.play(FadeIn(left_panel), FadeIn(right_panel), run_time=1.2)

        step_text = Text("RS moves as trend and momentum evolve over time", font_size=26).to_edge(DOWN)
        self.play(Write(step_text))

        self.play(
            left_tracker.animate.set_value(left_n),
            right_tracker.animate.set_value(right_n),
            run_time=5,
            rate_func=linear,
        )

        outro = Text("Higher RS means higher perceived risk.", font_size=30, color=ORANGE)
        outro.next_to(intro, DOWN, buff=0.35)
        self.play(ReplacementTransform(step_text, outro))
        self.wait(1.5)


class RiskScoreExplainer(Scene):
    def construct(self):
        definition_card = RoundedRectangle(width=7.4, height=1.4, corner_radius=0.15, color=BLUE_E)
        definition_text = Text("Step 1: Define components", font_size=30).move_to(definition_card)
        card1 = VGroup(definition_card, definition_text)

        formula_card = RoundedRectangle(width=7.4, height=1.4, corner_radius=0.15, color=GREEN_E)
        formula_text = Text("Step 2: Combine with weight w", font_size=30).move_to(formula_card)
        card2 = VGroup(formula_card, formula_text)

        visualize_card = RoundedRectangle(width=7.4, height=1.4, corner_radius=0.15, color=ORANGE)
        visualize_text = Text("Step 3: Track RS through time", font_size=30).move_to(visualize_card)
        card3 = VGroup(visualize_card, visualize_text)

        self.play(FadeIn(card1, shift=UP * 0.3))
        self.wait(0.4)
        self.play(ReplacementTransform(card1, card2))
        self.wait(0.4)
        self.play(ReplacementTransform(card2, card3))
        self.wait(0.6)

        self.play(FadeOut(card3))

        next_scene_text = Text("Render: RiskScoreDefinitions and RiskScoreSeriesExample", font_size=28)
        self.play(Write(next_scene_text))
        self.wait(1)
