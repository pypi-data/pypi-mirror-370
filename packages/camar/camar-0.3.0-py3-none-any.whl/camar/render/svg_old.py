import math
from .const import LANDMARK_COLOR, COLORS
from .utils import hex_to_hsl


class Visualizer:
    def __init__(
        self,
        env,
        state_seq,
        animate_agents=True,
        animate_goals=True,
        animate_landmarks=True,
        fps=None,
        color_step=None,
        use_all_colors=False,
        agent_transparancy=0.8,
    ):
        self.env = env
        self.state_seq = state_seq

        if isinstance(self.state_seq, list) and len(self.state_seq) > 1:
            self.animate_agents = animate_agents
            self.animate_goals = animate_goals
            self.animate_landmarks = animate_landmarks
        else:
            self.animate_agents = False
            self.animate_goals = False
            self.animate_landmarks = False

        if fps is None:
            self.fps = 8 / env.step_dt
        else:
            self.fps = fps

        if isinstance(self.state_seq, list):
            self.keytimes = [round(tmp / len(self.state_seq), 8) for tmp in range(len(self.state_seq) - 1)]
            self.keytimes.append(1.0)
            self.keytimes = ";".join(map(str, self.keytimes))
            self.dur = round(len(self.state_seq) / self.fps, 3)
        else:
            self.keytimes = None
            self.dur = None

        self.width = self.env.width
        self.height = self.env.height
        self.scale = max(self.width, self.height) / 512

        self.use_all_colors = use_all_colors
        self.agent_transparancy = str(agent_transparancy)
        if color_step is not None:
            self.color_step = color_step
        else:
            self.color_step = max(360 // self.env.num_agents, 25)

    def render_landmarks(self):
        if isinstance(self.state_seq, list) and len(self.state_seq) > 1 and self.animate_landmarks:
            landmark_dict = {}
            for state in self.state_seq:
                landmark_pos = state.landmark_pos.tolist()  # convert to list in one call
                if not self.env.homogeneous_landmarks:
                    landmark_rad = state.sizes.landmark_rad.tolist()

                for landmark_i, (landmark_x, landmark_y) in enumerate(landmark_pos):
                    if landmark_i not in landmark_dict:
                        landmark_dict[landmark_i] = {"cx": [], "cy": []}

                        if not self.env.homogeneous_landmarks:
                            landmark_dict[landmark_i]["r"] = []

                    landmark_dict[landmark_i]["cx"].append(landmark_x / self.scale)
                    landmark_dict[landmark_i]["cy"].append(landmark_y / self.scale)

                    if not self.env.homogeneous_landmarks:
                        landmark_dict[landmark_i]["r"].append(landmark_rad[landmark_i] / self.scale)

            state_seq_svg = []
            for i, landmark in enumerate(landmark_dict):
                hex_color = LANDMARK_COLOR
                hue, saturation, lightness = hex_to_hsl(hex_color)
                color = f"hsl({hue}, {saturation}%, {lightness}%)"

                if self.env.homogeneous_landmarks:
                    state_seq_svg.append(
                        f'<circle class="landmark" r="{self.env.map_generator.landmark_rad / self.scale}" fill="{color}">'
                    )
                else:
                    state_seq_svg.append(f'<circle class="landmark" fill="{color}">')

                for attribute_name in landmark_dict[landmark]:
                    values = ";".join(
                        map(
                            lambda x: f"{x:.3f}",
                            landmark_dict[landmark][attribute_name],
                        )
                    )
                    state_seq_svg.append(f'<animate attributeName="{attribute_name}" dur="{self.dur}s"')
                    state_seq_svg.append(f'\tkeyTimes="{self.keytimes}" repeatCount="indefinite"')
                    state_seq_svg.append(f'\tvalues="{values}"/>')

                state_seq_svg.append("</circle>")
                state_seq_svg.append("\n")

            return "\n".join(state_seq_svg)
        else:
            if isinstance(self.state_seq, list):
                state = self.state_seq[0]
            else:
                state = self.state_seq

            landmark_pos = state.landmark_pos.tolist()
            landmark_svg = []
            for landmark_x, landmark_y in landmark_pos:
                hex_color = LANDMARK_COLOR
                hue, saturation, lightness = hex_to_hsl(hex_color)
                color = f"hsl({hue}, {saturation}%, {lightness}%)"

                landmark_x = landmark_x / self.scale
                landmark_y = landmark_y / self.scale
                landmark_r = (
                    self.env.map_generator.landmark_rad
                    if self.env.homogeneous_landmarks
                    else state.sizes.landmark_rad
                ) / self.scale
                landmark_svg.append(
                    f'<circle class="landmark" cx="{landmark_x:.3f}" cy="{landmark_y:.3f}" r="{landmark_r:.3f}" fill="{color}">  </circle>'
                )

            return "\n".join(landmark_svg)

    def render_goals(self):
        if isinstance(self.state_seq, list) and len(self.state_seq) > 1 and self.animate_goals:
            goal_dict = {}
            for state in self.state_seq:
                goal_pos = state.goal_pos.tolist()
                if not self.env.homogeneous_goals:
                    goal_rad = state.sizes.goal_rad.tolist()

                for goal_i, (goal_x, goal_y) in enumerate(goal_pos):
                    if goal_i not in goal_dict:
                        goal_dict[goal_i] = {"cx": [], "cy": []}

                        if not self.env.homogeneous_goals:
                            goal_dict[goal_i]["r"] = []

                    goal_dict[goal_i]["cx"].append(goal_x / self.scale)
                    goal_dict[goal_i]["cy"].append(goal_y / self.scale)

                    if not self.env.homogeneous_goals:
                        goal_dict[goal_i]["r"].append(goal_rad[goal_i] / self.scale)

            state_seq_svg = []
            for i, goal in enumerate(goal_dict):
                if self.use_all_colors:
                    color = (i * self.color_step) % 360
                    color = f"hsl({color}, 100%, 50%)"
                else:
                    hex_color = COLORS[i % len(COLORS)]
                    hue, saturation, lightness = hex_to_hsl(hex_color)
                    color = f"hsl({hue}, {saturation}%, {lightness}%)"

                if self.env.homogeneous_goals:
                    state_seq_svg.append(
                        f'<circle class="goal" r="{self.env.map_generator.goal_rad / self.scale}" fill="{color}">'
                    )
                else:
                    state_seq_svg.append(f'<circle class="goal" fill="{color}">')

                for attribute_name in goal_dict[goal]:
                    values = ";".join(map(lambda x: f"{x:.3f}", goal_dict[goal][attribute_name]))
                    state_seq_svg.append(f'<animate attributeName="{attribute_name}" dur="{self.dur}s"')
                    state_seq_svg.append(f'\tkeyTimes="{self.keytimes}" repeatCount="indefinite"')
                    state_seq_svg.append(f'\tvalues="{values}"/>')

                state_seq_svg.append("</circle>")
                state_seq_svg.append("\n")

            return "\n".join(state_seq_svg)
        else:
            if isinstance(self.state_seq, list):
                state = self.state_seq[0]
            else:
                state = self.state_seq

            goal_pos = state.goal_pos.tolist()
            goal_svg = []
            for i, (goal_x, goal_y) in enumerate(goal_pos):
                if self.use_all_colors:
                    color = (i * self.color_step) % 360
                    color = f"hsl({color}, 100%, 50%)"
                else:
                    hex_color = COLORS[i % len(COLORS)]
                    hue, saturation, lightness = hex_to_hsl(hex_color)
                    color = f"hsl({hue}, {saturation}%, {lightness}%)"

                goal_x = float(goal_x) / self.scale
                goal_y = float(goal_y) / self.scale
                goal_r = (
                    self.env.map_generator.goal_rad if self.env.homogeneous_goals else state.sizes.goal_rad
                ) / self.scale
                goal_svg.append(
                    f'<circle class="goal" cx="{goal_x:.3f}" cy="{goal_y:.3f}" r="{goal_r:.3f}" fill="{color}">  </circle>'
                )

            return "\n".join(goal_svg)

    def render_agents(self):
        if isinstance(self.state_seq, list) and len(self.state_seq) > 1 and self.animate_agents:
            agent_dict = {}
            for state in self.state_seq:
                agent_pos = state.physical_state.agent_pos.tolist()
                if not self.env.homogeneous_agents:
                    agent_rad = state.sizes.agent_rad.tolist()

                for agent_i, (agent_x, agent_y) in enumerate(agent_pos):
                    if agent_i not in agent_dict:
                        agent_dict[agent_i] = {"cx": [], "cy": []}

                        if not self.env.homogeneous_agents:
                            agent_dict[agent_i]["r"] = []

                    agent_dict[agent_i]["cx"].append(agent_x / self.scale)
                    agent_dict[agent_i]["cy"].append(agent_y / self.scale)

                    if not self.env.homogeneous_agents:
                        agent_dict[agent_i]["r"].append(agent_rad[agent_i] / self.scale)

            state_seq_svg = []
            for i, agent in enumerate(agent_dict):
                if self.use_all_colors:
                    color = (i * self.color_step) % 360
                    color = f"hsl({color}, 100%, 50%)"
                else:
                    hex_color = COLORS[i % len(COLORS)]
                    hue, saturation, lightness = hex_to_hsl(hex_color)
                    color = f"hsla({hue}, {saturation}%, {lightness}%, {self.agent_transparancy})"

                if self.env.homogeneous_agents:
                    state_seq_svg.append(
                        f'<circle class="agent" r="{self.env.map_generator.agent_rad / self.scale}" fill="{color}">'
                    )
                else:
                    state_seq_svg.append(f'<circle class="agent" fill="{color}">')

                for attribute_name in agent_dict[agent]:
                    values = ";".join(map(lambda x: f"{x:.3f}", agent_dict[agent][attribute_name]))
                    state_seq_svg.append(f'<animate attributeName="{attribute_name}" dur="{self.dur}s"')
                    state_seq_svg.append(f'\tkeyTimes="{self.keytimes}" repeatCount="indefinite"')
                    state_seq_svg.append(f'\tvalues="{values}"/>')

                state_seq_svg.append("</circle>")
                state_seq_svg.append("\n")

            return "\n".join(state_seq_svg)
        else:
            if isinstance(self.state_seq, list):
                state = self.state_seq[0]
            else:
                state = self.state_seq

            agent_pos = state.physical_state.agent_pos.tolist()
            agent_svg = []
            for i, (agent_x, agent_y) in enumerate(agent_pos):
                if self.use_all_colors:
                    color = (i * self.color_step) % 360
                    color = f"hsl({color}, 100%, 50%)"
                else:
                    hex_color = COLORS[i % len(COLORS)]
                    hue, saturation, lightness = hex_to_hsl(hex_color)
                    color = f"hsla({hue}, {saturation}%, {lightness}%, {self.agent_transparancy})"

                agent_x = agent_x / self.scale
                agent_y = agent_y / self.scale
                agent_r = (
                    self.env.map_generator.agent_rad if self.env.homogeneous_agents else state.sizes.agent_rad
                ) / self.scale
                agent_svg.append(
                    f'<circle class="agent" cx="{agent_x:.3f}" cy="{agent_y:.3f}" r="{agent_r:.3f}" fill="{color}">  </circle>'
                )

            return "\n".join(agent_svg)

    def render(self):
        scaled_width = math.ceil(self.width / self.scale)
        scaled_height = math.ceil(self.height / self.scale)

        view_box = (
            -self.width / 2 / self.scale,
            -self.height / 2 / self.scale,
            self.width / self.scale,
            self.height / self.scale,
        )

        svg_header = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"',
            f'\twidth="{scaled_width}" height="{scaled_height}" viewBox="{" ".join(map(str, view_box))}">',
        ]
        svg_header = "\n".join(svg_header)

        definitions = [
            "<style>",
            "\t.landmark {{ }}",
            "\t.agent {{ }}",
            f"\t.goal {{stroke: {LANDMARK_COLOR}; stroke-width: {self.env.map_generator.goal_rad / 2 / self.scale};}}"
            if self.env.homogeneous_goals
            else f"\t.goal {{stroke: {LANDMARK_COLOR};}}",
            "</style>",
        ]
        definitions = "\n".join(definitions)

        svg_header = [svg_header, "\n", "<defs>", definitions, "</defs>"]
        svg_header = "\n".join(svg_header)

        svg_landmark = self.render_landmarks()
        svg_goal = self.render_goals()
        svg_agent = self.render_agents()

        return "\n".join([svg_header, "\n", svg_landmark, "\n", svg_goal, "\n", svg_agent, "</svg>"])

    def save_svg(self, filename="test.svg"):
        with open(filename, "w") as svg_file:
            svg_file.write(self.render())
