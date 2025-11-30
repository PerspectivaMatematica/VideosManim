# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 22:28:38 2025

@author: brand
"""

from manim import *
import numpy as np
altura_actual = config.pixel_height
config.pixel_height = config.pixel_width
config.pixel_width = altura_actual

config.frame_width = config.frame_height * 9 /16


class IntroPerspectivaMatematica(Scene):
    def construct(self):
        # Colores
        rejilla=NumberPlane()
        self.add(rejilla)
        
        BACKGROUND_COLOR = "#05060A"
        LINE_WHITE = "#FFFFFF"
        LINE_BLUE = "#3DF5FF"
        TEXT_COLOR = "#FFFFFF"
        ACCENT_COLOR = "#3DF5FF"

        #self.camera.background_color = BACKGROUND_COLOR

        # --------------------------------------------------------
        # 1) Construir la figura tipo pursuit (espiral poligonal)
        # --------------------------------------------------------
        n_sides = 7      # lados del polígono
        steps = 100      # iteraciones (más = más denso)
        alpha = 0.92     # qué tanto persigue cada vértice al siguiente

        base_polygon = RegularPolygon(n_sides, radius=1.75)
        base_polygon.set_stroke(color=LINE_WHITE, width=1)

        current_vertices = list(base_polygon.get_vertices())
        polygons = []
        white_polys = []
        blue_polys = []

        for k in range(steps):
            next_vertices = []
            for i in range(n_sides):
                p = current_vertices[i]
                q = current_vertices[(i + 1) % n_sides]
                new_point = (1 - alpha) * p + alpha * q
                next_vertices.append(new_point)

            poly = Polygon(*next_vertices)
            opacity = 1.0 - 0.7 * (k / steps)
            color = LINE_WHITE if k % 2 == 0 else LINE_BLUE
            poly.set_stroke(color=color, width=1.2, opacity=opacity)

            polygons.append(poly)
            if k % 2 == 0:
                white_polys.append(poly)
            else:
                blue_polys.append(poly)

            current_vertices = next_vertices

        # Grupo completo de la espiral
        pursuit_group = VGroup(*polygons).move_to(ORIGIN)

        # Rotación SOLO mientras se dibuja
        rotation_speed = 0.3  # radianes por segundo aprox.

        def rotate_updater(mob, dt):
            mob.rotate(rotation_speed * dt, about_point=ORIGIN)

        pursuit_group.add_updater(rotate_updater)
        #self.add(pursuit_group)

        # --------------------------------------------------------
        # 2) Dibujar líneas rápido mientras rota
        # --------------------------------------------------------
        self.play(
            LaggedStart(
                *[Create(p) for p in polygons],
                lag_ratio=0.012,
                run_time=2.0,
            )
        )

        # Paramos el giro inmediatamente después de terminar
        #pursuit_group.clear_updaters()
        self.wait(0.1)

        # --------------------------------------------------------
        # 3) Texto final
        # --------------------------------------------------------
        title_top = Text(
            "Perspectiva",
            color=TEXT_COLOR,
            weight=BOLD
        )
        title_bottom = Text(
            "Matemática", 
            color=ACCENT_COLOR,
            weight=BOLD
        )

        title = VGroup(title_top, title_bottom).arrange(DOWN, buff=0.15)
        title.scale(0.65)
        title.move_to(ORIGIN)

        # Grupos separados: blancos → top, azules → bottom
        white_group = VGroup(*white_polys)
        blue_group = VGroup(*blue_polys)

        # --------------------------------------------------------
        # 4) TRANSFORMACIÓN: líneas blancas → "Perspectiva"
        #                     líneas azules → "Matemática"
        # --------------------------------------------------------
        self.play(
            Transform(white_group, title_top),
            Transform(blue_group, title_bottom),
            run_time=1.5,
        )

        # Subrayado de "Matemática"
        underline = Line(
            start=title_bottom.get_left() + 0.1 * LEFT,
            end=title_bottom.get_right() + 0.1 * RIGHT,
            stroke_color=ACCENT_COLOR,
            stroke_width=3,
        ).next_to(title_bottom, DOWN, buff=0.1)

        self.play(Create(underline), run_time=0.4)

        self.wait(0.8)
