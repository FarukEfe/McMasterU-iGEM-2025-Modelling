
from manim import *
from matplotlib import axes

config.format = "webm"
# config.format = "gif"

class ThreeDAxesScene(ThreeDScene):

    def construct(self):

        # Create 3D axes with range -8 to +8 for each axis
        axes = ThreeDAxes(
        	x_range=[-8, 8, 1],
        	y_range=[-8, 8, 1],
        	z_range=[-8, 8, 1]
        )
		
		# Define vertices for a slightly irregular octahedron (8-faced polyhedron)
        # Base vertices (bottom square, slightly irregular)
        v0 = [0, 0, 0]       # front-left
        v1 = [2.1, 0, 0]     # front-right (slightly wider)
        v2 = [2, 1.9, 0]     # back-right (slightly shorter)
        v3 = [0, 1.75, 0]       # back-left
        
        # Top vertices (upper square, slightly offset and irregular)
        v4 = [0, 0, 2.3]   # front-left top (slightly offset)
        v5 = [1.9, 0, 2.9] # front-right top (slightly higher)
        v6 = [2.1, 1.8, 2.6] # back-right top (slightly lower)
        v7 = [0, 2.1, 2.45]   # back-left top (slightly offset)

        # Create faces as polygons (slightly irregular octahedron)
        baby_blue = "#87CEEB"
        
        # Bottom face
        bottom = Polygon(v0, v1, v2, v3, fill_opacity=0.45, color=baby_blue, stroke_color=WHITE, stroke_width=2)
        bottom.set_shade_in_3d(True)
        
        # Top face
        top = Polygon(v4, v5, v6, v7, fill_opacity=0.45, color=baby_blue, stroke_color=WHITE, stroke_width=2)
        top.set_shade_in_3d(True)

        # Side faces (connecting bottom to top)
        side1 = Polygon(v0, v1, v5, v4, fill_opacity=0.45, color=baby_blue, stroke_color=WHITE, stroke_width=2)  # front
        side2 = Polygon(v1, v2, v6, v5, fill_opacity=0.45, color=baby_blue, stroke_color=WHITE, stroke_width=2)  # right
        side3 = Polygon(v2, v3, v7, v6, fill_opacity=0.45, color=baby_blue, stroke_color=WHITE, stroke_width=2)  # back
        side4 = Polygon(v3, v0, v4, v7, fill_opacity=0.45, color=baby_blue, stroke_color=WHITE, stroke_width=2)  # left
        side1.set_shade_in_3d(True)
        side2.set_shade_in_3d(True)
        side3.set_shade_in_3d(True)
        side4.set_shade_in_3d(True)

        # Group all faces into a single VGroup for animation
        polyhedron = VGroup(bottom, top, side1, side2, side3, side4)

        # Create a point for linear optimization animation (simplex method)
        optimization_point = Dot3D(radius=0.08, color=color.manim_colors.ORANGE)
        # optimization_point.set_shade_in_3d(False)
        optimization_point.move_to([0, 0, 0])  # Start at origin (vertex v0)
        
        # Define actual edge traversal path for simplex method
        # Move step-by-step along actual edges of the polyhedron
        edge_path = [
            [0, 0, 0],         # v0 - starting vertex (origin)
            [0, 1.75, 0],
            [2, 1.9, 0],         # v1 - move along bottom edge (v0 to v1)
            [2.1, 1.8, 2.6],
            [1.9, 0, 2.9]        # v5 - move up vertical edge (v1 to v5) - optimal point
        ]

        # Add axis labels as simple text (no LaTeX required)
        label_v1 = Text("v1", font_size=24).next_to(axes.x_axis.get_end(), RIGHT)
        label_v2 = Text("v2", font_size=24).next_to(axes.y_axis.get_end(), UP)
        label_v3 = Text("v3", font_size=24).next_to(axes.z_axis.get_end(), OUT)
        
        # Orient labels to face specific directions
        # v1 faces in direction of v2 (y-axis direction)
        label_v1.rotate(90 * DEGREES, axis=RIGHT)
        label_v1.rotate(180 * DEGREES, axis=IN)

        # v2 faces in direction of v1 (x-axis direction)
        label_v2.rotate(90 * DEGREES, axis=OUT)
        label_v2.rotate(90 * DEGREES, axis=UP)
        
        # v3 faces in-between v1 and v2 at 45 degree angle
        label_v3.rotate(90 * DEGREES, axis=OUT)
        label_v3.rotate(-45 * DEGREES, axis=RIGHT)
        label_v3.rotate(90 * DEGREES, axis=UP)

        # Group the axes, labels, polyhedron, and optimization point together
        everything = VGroup(axes, polyhedron, label_v1, label_v2, label_v3, optimization_point)
        self.add(everything)

        # Add axes and labels to the scene
        # (Note: axes and labels are now part of the 'everything' group)

        # Set camera orientation so all axes are visible
        self.set_camera_orientation(phi=60 * DEGREES, theta=35 * DEGREES)

        # Start camera rotation (60 degrees counter-clockwise about v3/z-axis over 4 seconds)
        # From theta=45° to theta=105° (45 + 60 = 105 degrees)
        self.begin_ambient_camera_rotation(rate=3 * DEGREES)  # 60° ÷ 4s = 15°/s

        # Point animation for optimization
        self.play(
            optimization_point.animate.move_to(edge_path[1]),
            run_time=1.25
        )
        
        self.play(
            optimization_point.animate.move_to(edge_path[2]),
            run_time=1.25
        )

        self.play(
            optimization_point.animate.move_to(edge_path[3]),
            run_time=1.25
        )

        self.play(
            optimization_point.animate.move_to(edge_path[4]),
            run_time=1.25
        )

        # Stop camera rotation
        self.stop_ambient_camera_rotation()