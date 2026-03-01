"""
Template Builder - Two-Phase Generation System
==============================================
Converts JSON blueprints to deterministic Lua code.
No LLM randomness, no Hebrew text, always valid output.
"""

from typing import Dict, List, Any, Optional

# Handle both package and direct imports
try:
    from .blueprint_schema import BlueprintSpec, PRESET_BLUEPRINTS
except ImportError:
    from blueprint_schema import BlueprintSpec, PRESET_BLUEPRINTS


class TemplateBuilder:
    """
    Converts BlueprintSpec (JSON) to valid Lua code for Roblox Studio.
    Deterministic output - same input always produces same output.
    """

    def __init__(self):
        self.indent = "    "  # 4 spaces

    def build_lua(self, blueprint: BlueprintSpec, base_x: float = 0, base_z: float = 0) -> str:
        """
        Convert a blueprint to Lua code.

        Args:
            blueprint: The BlueprintSpec to convert
            base_x: X offset for positioning (prevents overlap)
            base_z: Z offset for positioning

        Returns:
            Valid Lua code string
        """
        lines = []

        # Header
        lines.append("local parts = {}")
        lines.append("")

        # Optional: Create a model to group parts
        if len(blueprint.parts) > 3:
            lines.append(f'local model = Instance.new("Model")')
            lines.append(f'model.Name = "{self._safe_string(blueprint.name)}"')
            lines.append("model.Parent = workspace")
            lines.append("")
            parent = "model"
        else:
            parent = "workspace"

        # Build each part
        for i, part_spec in enumerate(blueprint.parts):
            part_lines = self._build_part(part_spec, i, parent, base_x, base_z)
            lines.extend(part_lines)
            lines.append("")

        # Footer
        lines.append("game.Selection:Set(parts)")

        # Generate embedded scripts (for interactive objects)
        if hasattr(blueprint, 'scripts') and blueprint.scripts:
            lines.append("")
            lines.append("-- Interactive Scripts")
            for script_spec in blueprint.scripts:
                script_name = script_spec.get("name", "Script")
                parent_part = script_spec.get("parent", "")
                source = script_spec.get("source", "")
                # Find the variable name for the parent part
                parent_var = self._to_var_name(parent_part) if parent_part else parent
                lines.append(f'local {self._to_var_name(script_name)}_{parent_var} = Instance.new("Script")')
                lines.append(f'{self._to_var_name(script_name)}_{parent_var}.Name = "{script_name}"')
                # Use double brackets for multi-line source
                source_lua = source.replace("\\n", "\n")
                lines.append(f'{self._to_var_name(script_name)}_{parent_var}.Source = [[\n{source_lua}\n]]')
                lines.append(f'{self._to_var_name(script_name)}_{parent_var}.Parent = {parent_var}')
                lines.append("")

        return "\n".join(lines)

    def _build_part(self, part: Dict, index: int, parent: str, base_x: float, base_z: float) -> List[str]:
        """Build Lua code for a single part."""
        lines = []

        # Get part properties with defaults
        name = part.get("name", f"part{index}")
        part_type = part.get("type", "Part")
        size = part.get("size", [4, 1, 2])
        position = part.get("position", [0, 0, 0])
        color = part.get("color", "Medium stone grey")
        material = part.get("material", "Plastic")
        anchored = part.get("anchored", True)
        rotation = part.get("rotation")
        transparency = part.get("transparency", 0)
        shape = part.get("shape")

        # Variable name
        var_name = self._to_var_name(name)

        # Create instance
        lines.append(f'local {var_name} = Instance.new("{part_type}")')
        lines.append(f'{var_name}.Name = "{self._safe_string(name)}"')

        # Size
        lines.append(f'{var_name}.Size = Vector3.new({size[0]}, {size[1]}, {size[2]})')

        # Position (with offset)
        pos_x = position[0] + base_x
        pos_y = position[1]
        pos_z = position[2] + base_z

        # If rotation specified, use CFrame
        if rotation and any(r != 0 for r in rotation):
            rx, ry, rz = rotation
            rx_rad = f"math.rad({rx})" if rx != 0 else "0"
            ry_rad = f"math.rad({ry})" if ry != 0 else "0"
            rz_rad = f"math.rad({rz})" if rz != 0 else "0"
            lines.append(f'{var_name}.CFrame = CFrame.new({pos_x}, {pos_y}, {pos_z}) * CFrame.Angles({rx_rad}, {ry_rad}, {rz_rad})')
        else:
            lines.append(f'{var_name}.Position = Vector3.new({pos_x}, {pos_y}, {pos_z})')

        # Color
        lines.append(f'{var_name}.BrickColor = BrickColor.new("{color}")')

        # Material
        lines.append(f'{var_name}.Material = Enum.Material.{material}')

        # Shape (for Part type only)
        if shape and part_type == "Part":
            lines.append(f'{var_name}.Shape = Enum.PartType.{shape}')

        # Transparency
        if transparency > 0:
            lines.append(f'{var_name}.Transparency = {transparency}')

        # Anchored
        if anchored:
            lines.append(f'{var_name}.Anchored = true')

        # Parent
        lines.append(f'{var_name}.Parent = {parent}')

        # Add to parts table
        lines.append(f'table.insert(parts, {var_name})')

        return lines

    def _to_var_name(self, name: str) -> str:
        """Convert a name to a valid Lua variable name."""
        # Replace spaces and special chars with underscores
        var = name.lower().replace(" ", "_").replace("-", "_")
        # Remove any remaining invalid characters
        var = "".join(c for c in var if c.isalnum() or c == "_")
        # Ensure it starts with a letter
        if var and not var[0].isalpha():
            var = "part_" + var
        return var or "part"

    def _safe_string(self, s: str) -> str:
        """Make a string safe for Lua string literals."""
        return s.replace('"', '\\"').replace("\n", "\\n")


class CityBuilder(TemplateBuilder):
    """
    Specialized builder for creating cities with multiple buildings.
    """

    def build_city(self, num_houses: int = 3, include_trees: bool = True) -> str:
        """
        Build a city with houses and optional trees.

        Args:
            num_houses: Number of houses to create
            include_trees: Whether to add trees

        Returns:
            Lua code for the city
        """
        lines = []
        lines.append("local parts = {}")
        lines.append("")
        lines.append('local cityModel = Instance.new("Model")')
        lines.append('cityModel.Name = "City"')
        lines.append("cityModel.Parent = workspace")
        lines.append("")

        # Grid layout
        grid_spacing = 40  # Space between buildings
        buildings_per_row = 3

        house_blueprint = PRESET_BLUEPRINTS["house"]
        tree_blueprint = PRESET_BLUEPRINTS["tree"]

        for i in range(num_houses):
            row = i // buildings_per_row
            col = i % buildings_per_row

            x_offset = col * grid_spacing
            z_offset = row * grid_spacing

            lines.append(f"-- House {i + 1}")
            lines.append(f'local house{i + 1} = Instance.new("Model")')
            lines.append(f'house{i + 1}.Name = "House{i + 1}"')
            lines.append(f"house{i + 1}.Parent = cityModel")
            lines.append("")

            for j, part in enumerate(house_blueprint.parts):
                var_name = f"house{i + 1}_{self._to_var_name(part['name'])}"
                part_lines = self._build_part_with_parent(
                    part, var_name, f"house{i + 1}", x_offset, z_offset
                )
                lines.extend(part_lines)
                lines.append("")

            # Add a tree next to each house
            if include_trees:
                tree_x = x_offset + 18
                tree_z = z_offset + 5

                lines.append(f"-- Tree near House {i + 1}")
                for j, part in enumerate(tree_blueprint.parts):
                    var_name = f"tree{i + 1}_{self._to_var_name(part['name'])}"
                    part_lines = self._build_part_with_parent(
                        part, var_name, "cityModel", tree_x, tree_z
                    )
                    lines.extend(part_lines)
                    lines.append("")

        # Add road
        lines.append("-- Main Road")
        lines.append('local road = Instance.new("Part")')
        lines.append('road.Name = "Road"')
        total_length = (num_houses // buildings_per_row + 1) * grid_spacing + 20
        lines.append(f"road.Size = Vector3.new(10, 0.5, {total_length})")
        lines.append(f"road.Position = Vector3.new(-15, 0.25, {total_length / 2 - 10})")
        lines.append('road.BrickColor = BrickColor.new("Dark stone grey")')
        lines.append("road.Material = Enum.Material.Concrete")
        lines.append("road.Anchored = true")
        lines.append("road.Parent = cityModel")
        lines.append("table.insert(parts, road)")
        lines.append("")

        lines.append("game.Selection:Set(parts)")

        return "\n".join(lines)

    def _build_part_with_parent(self, part: Dict, var_name: str, parent: str,
                                 base_x: float, base_z: float) -> List[str]:
        """Build a part with specified variable name and parent."""
        lines = []

        part_type = part.get("type", "Part")
        size = part.get("size", [4, 1, 2])
        position = part.get("position", [0, 0, 0])
        color = part.get("color", "Medium stone grey")
        material = part.get("material", "Plastic")
        rotation = part.get("rotation")
        transparency = part.get("transparency", 0)
        shape = part.get("shape")

        lines.append(f'local {var_name} = Instance.new("{part_type}")')
        lines.append(f'{var_name}.Name = "{part.get("name", var_name)}"')
        lines.append(f'{var_name}.Size = Vector3.new({size[0]}, {size[1]}, {size[2]})')

        pos_x = position[0] + base_x
        pos_y = position[1]
        pos_z = position[2] + base_z

        if rotation and any(r != 0 for r in rotation):
            rx, ry, rz = rotation
            rx_rad = f"math.rad({rx})" if rx != 0 else "0"
            ry_rad = f"math.rad({ry})" if ry != 0 else "0"
            rz_rad = f"math.rad({rz})" if rz != 0 else "0"
            lines.append(f'{var_name}.CFrame = CFrame.new({pos_x}, {pos_y}, {pos_z}) * CFrame.Angles({rx_rad}, {ry_rad}, {rz_rad})')
        else:
            lines.append(f'{var_name}.Position = Vector3.new({pos_x}, {pos_y}, {pos_z})')

        lines.append(f'{var_name}.BrickColor = BrickColor.new("{color}")')
        lines.append(f'{var_name}.Material = Enum.Material.{material}')

        if shape and part_type == "Part":
            lines.append(f'{var_name}.Shape = Enum.PartType.{shape}')

        if transparency > 0:
            lines.append(f'{var_name}.Transparency = {transparency}')

        lines.append(f'{var_name}.Anchored = true')
        lines.append(f'{var_name}.Parent = {parent}')
        lines.append(f'table.insert(parts, {var_name})')

        return lines


class ObbyBuilder(TemplateBuilder):
    """
    Specialized builder for obstacle courses (obby).
    """

    def build_obby(self, num_platforms: int = 10, difficulty: str = "easy") -> str:
        """
        Build an obstacle course.

        Args:
            num_platforms: Number of platforms
            difficulty: "easy", "medium", or "hard" (affects spacing)

        Returns:
            Lua code for the obby
        """
        lines = []
        lines.append("local parts = {}")
        lines.append("")
        lines.append('local obbyModel = Instance.new("Model")')
        lines.append('obbyModel.Name = "Obby"')
        lines.append("obbyModel.Parent = workspace")
        lines.append("")

        # Difficulty settings
        spacing = {"easy": 8, "medium": 12, "hard": 16}.get(difficulty, 10)
        height_var = {"easy": 2, "medium": 4, "hard": 6}.get(difficulty, 3)

        # Start platform
        lines.append("-- Start Platform")
        lines.append('local startPlatform = Instance.new("SpawnLocation")')
        lines.append('startPlatform.Name = "Start"')
        lines.append("startPlatform.Size = Vector3.new(15, 3, 15)")
        lines.append("startPlatform.Position = Vector3.new(0, 1.5, 0)")
        lines.append('startPlatform.BrickColor = BrickColor.new("Bright green")')
        lines.append("startPlatform.Material = Enum.Material.Grass")
        lines.append("startPlatform.Anchored = true")
        lines.append("startPlatform.Parent = obbyModel")
        lines.append("table.insert(parts, startPlatform)")
        lines.append("")

        current_x = 0
        current_y = 3
        current_z = 15

        colors = ["Bright red", "Bright blue", "Bright yellow", "Bright green", "Bright orange"]

        for i in range(num_platforms):
            current_z += spacing
            current_y += (i % 3 - 1) * height_var  # Vary height
            if current_y < 3:
                current_y = 3

            color = colors[i % len(colors)]

            lines.append(f"-- Platform {i + 1}")
            lines.append(f'local platform{i + 1} = Instance.new("Part")')
            lines.append(f'platform{i + 1}.Name = "Platform{i + 1}"')
            lines.append(f"platform{i + 1}.Size = Vector3.new(6, 1, 6)")
            lines.append(f"platform{i + 1}.Position = Vector3.new({current_x}, {current_y}, {current_z})")
            lines.append(f'platform{i + 1}.BrickColor = BrickColor.new("{color}")')
            lines.append(f"platform{i + 1}.Material = Enum.Material.Neon")
            lines.append(f"platform{i + 1}.Anchored = true")
            lines.append(f"platform{i + 1}.Parent = obbyModel")
            lines.append(f"table.insert(parts, platform{i + 1})")
            lines.append("")

        # End platform
        lines.append("-- End Platform (Victory)")
        lines.append('local endPlatform = Instance.new("Part")')
        lines.append('endPlatform.Name = "Victory"')
        lines.append("endPlatform.Size = Vector3.new(15, 3, 15)")
        lines.append(f"endPlatform.Position = Vector3.new(0, {current_y + 5}, {current_z + spacing})")
        lines.append('endPlatform.BrickColor = BrickColor.new("Gold")')
        lines.append("endPlatform.Material = Enum.Material.Neon")
        lines.append("endPlatform.Anchored = true")
        lines.append("endPlatform.Parent = obbyModel")
        lines.append("table.insert(parts, endPlatform)")
        lines.append("")

        lines.append("game.Selection:Set(parts)")

        return "\n".join(lines)


# Factory function
def create_builder(build_type: str = "default") -> TemplateBuilder:
    """
    Create the appropriate builder for the task.

    Args:
        build_type: "default", "city", or "obby"

    Returns:
        Appropriate TemplateBuilder instance
    """
    builders = {
        "default": TemplateBuilder,
        "city": CityBuilder,
        "obby": ObbyBuilder,
    }
    return builders.get(build_type, TemplateBuilder)()


# Quick test
if __name__ == "__main__":
    from blueprint_schema import PRESET_BLUEPRINTS, get_blueprint_for_command

    print("Testing Template Builder")
    print("=" * 50)

    # Test basic building
    builder = TemplateBuilder()

    print("\n1. Building a house from preset:")
    house_blueprint = PRESET_BLUEPRINTS["house"]
    lua_code = builder.build_lua(house_blueprint)
    print(lua_code[:500])
    print("...")

    # Test city builder
    print("\n" + "=" * 50)
    print("2. Building a city with 3 houses:")
    city_builder = CityBuilder()
    city_code = city_builder.build_city(num_houses=3)
    print(f"Generated {len(city_code)} characters of Lua code")
    print(city_code[:500])
    print("...")

    # Test obby builder
    print("\n" + "=" * 50)
    print("3. Building an obby with 5 platforms:")
    obby_builder = ObbyBuilder()
    obby_code = obby_builder.build_obby(num_platforms=5, difficulty="medium")
    print(f"Generated {len(obby_code)} characters of Lua code")
    print(obby_code[:500])
    print("...")
