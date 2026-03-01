# -*- coding: utf-8 -*-
"""
Cube 3D/4D Integration — Real mesh generation for Roblox
=========================================================
Uses Roblox's Cube 3D API (GenerateModelAsync) to create
real 3D meshes from text descriptions instead of Parts.

Status: Roblox Cube 4D Open Beta — February 2026
API: GenerateModelAsync (Beta, requires Studio Beta features)

When enabled, this replaces Part-based generation with real meshes:
  "Build a dragon" → real 3D mesh, not cubes!
"""

# Hebrew to English prompt mapping for Cube 3D
CUBE3D_PROMPTS = {
    # Animals
    "כלב": "a cute cartoon dog, low poly game asset",
    "חתול": "a cute cartoon cat, low poly game asset",
    "סוס": "a horse, low poly game asset",
    "דג": "a colorful cartoon fish, low poly game asset",
    "ציפור": "a small bird, low poly game asset",
    "דרקון": "a friendly cartoon dragon with wings, low poly game asset",
    "ארנב": "a cute rabbit, low poly game asset",
    "פרפר": "a colorful butterfly, low poly game asset",
    "דינוזאור": "a friendly cartoon dinosaur, low poly game asset",

    # Vehicles (complex)
    "ספינה": "a pirate ship with sails, low poly game asset",
    "רכבת": "a steam train locomotive, low poly game asset",
    "טנק": "a cartoon military tank, low poly game asset",
    "אופנוע": "a motorcycle, low poly game asset",
    "אופניים": "a bicycle, low poly game asset",

    # Nature
    "הר": "a mountain with snow peak, low poly terrain",
    "אי": "a tropical island with palm tree, low poly game asset",
    "מערה": "a cave entrance in rock, low poly game asset",

    # Buildings (complex)
    "טירה": "a medieval castle with towers, low poly game asset",
    "ארמון": "a royal palace, low poly game asset",
    "מגדלור": "a lighthouse on rocks, low poly game asset",
    "תחנת חלל": "a space station, low poly game asset",
    "פירמידה": "an egyptian pyramid, low poly game asset",

    # Objects
    "חרב": "a fantasy sword, low poly game asset",
    "כתר": "a golden crown with gems, low poly game asset",
    "מגן": "a knight's shield, low poly game asset",
    "שלט": "a wooden sign post, low poly game asset",
    "ארגז אוצר": "a treasure chest, low poly game asset",
}


def get_cube3d_prompt(hebrew_text: str) -> str:
    """
    Convert Hebrew text to English prompt for Cube 3D.
    Returns None if no matching prompt found.
    """
    hebrew_text = hebrew_text.strip()

    # Direct match
    for heb, eng in CUBE3D_PROMPTS.items():
        if heb in hebrew_text:
            return eng

    return None


def generate_cube3d_lua(description_en: str, position: tuple = (0, 5, 0)) -> str:
    """
    Generate Lua code that uses Cube 3D API to create a mesh.

    Args:
        description_en: English text prompt for Cube 3D
        position: (x, y, z) position in world

    Returns:
        Lua code string that generates a mesh in Roblox Studio
    """
    x, y, z = position
    return f'''-- Cube 3D Generation (Beta API)
local parts = {{}}
local AssetService = game:GetService("AssetService")

local success, result = pcall(function()
    return AssetService:GenerateModelAsync("{description_en}")
end)

if success and result then
    -- Cube 3D returned a mesh!
    local mesh = Instance.new("MeshPart")
    mesh.MeshId = result
    mesh.Anchored = true
    mesh.Position = Vector3.new({x}, {y}, {z})
    mesh.Parent = workspace
    table.insert(parts, mesh)
else
    -- Fallback: create a placeholder Part
    local p = Instance.new("Part")
    p.Size = Vector3.new(8, 8, 8)
    p.Position = Vector3.new({x}, {y}, {z})
    p.BrickColor = BrickColor.new("Medium stone grey")
    p.Material = Enum.Material.Plastic
    p.Anchored = true
    p.Parent = workspace
    table.insert(parts, p)
    warn("Cube 3D not available, using placeholder")
end

game.Selection:Set(parts)'''


def generate_cube4d_lua(description_en: str, schema: str = "Body-1",
                         position: tuple = (0, 5, 0)) -> str:
    """
    Generate Lua code that uses Cube 4D API for interactive objects.

    Schemas:
        - "Car-5": 5-part car (body + 4 wheels) with driving behavior
        - "Body-1": single-mesh object

    Args:
        description_en: English text prompt
        schema: 4D schema type
        position: (x, y, z) position

    Returns:
        Lua code string
    """
    x, y, z = position
    return f'''-- Cube 4D Generation (Beta API)
local parts = {{}}
local AssetService = game:GetService("AssetService")

local success, model = pcall(function()
    return AssetService:Generate4DModelAsync("{description_en}", "{schema}")
end)

if success and model then
    model:PivotTo(CFrame.new({x}, {y}, {z}))
    model.Parent = workspace
    for _, part in ipairs(model:GetDescendants()) do
        if part:IsA("BasePart") then
            table.insert(parts, part)
        end
    end
else
    -- Fallback
    local p = Instance.new("Part")
    p.Size = Vector3.new(8, 8, 8)
    p.Position = Vector3.new({x}, {y}, {z})
    p.BrickColor = BrickColor.new("Medium stone grey")
    p.Anchored = true
    p.Parent = workspace
    table.insert(parts, p)
    warn("Cube 4D not available, using placeholder")
end

game.Selection:Set(parts)'''


# Vehicle detection for Car-5 schema
VEHICLE_WORDS = {"מכונית", "אוטו", "רכב", "ג'יפ", "מונית", "אוטובוס", "משאית"}


def should_use_cube3d(hebrew_text: str) -> bool:
    """Check if this request would benefit from Cube 3D (complex/organic shapes)."""
    return get_cube3d_prompt(hebrew_text) is not None


def try_cube3d(hebrew_text: str, position: tuple = (0, 5, 0)) -> dict:
    """
    Try to generate using Cube 3D/4D.

    Returns:
        dict with success, lua_code, method
        or None if Cube 3D not applicable
    """
    prompt = get_cube3d_prompt(hebrew_text)
    if not prompt:
        return None

    # Check if it's a vehicle → use Car-5 schema
    is_vehicle = any(word in hebrew_text for word in VEHICLE_WORDS)

    if is_vehicle:
        lua = generate_cube4d_lua(prompt, schema="Car-5", position=position)
        method = "cube4d_car"
    else:
        lua = generate_cube3d_lua(prompt, position=position)
        method = "cube3d_mesh"

    return {
        "success": True,
        "lua_code": lua,
        "method": method,
        "prompt_en": prompt,
    }
