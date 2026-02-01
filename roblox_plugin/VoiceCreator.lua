--[[
    Voice Creator Plugin for Roblox Studio
    ========================================
    שליטה קולית דרך HTTP Server!

    התקנה:
    1. שמור בתיקיית Plugins: %LOCALAPPDATA%\Roblox\Plugins\
    2. הפעל מחדש Roblox Studio
    3. לחץ על כפתור "Voice Creator" ב-Toolbar

    איך זה עובד:
    1. Python מריץ שרת HTTP על localhost:8080
    2. ה-Plugin שואל כל שנייה "יש פקודה חדשה?"
    3. אם יש - מריץ את קוד ה-Lua!
]]

local HttpService = game:GetService("HttpService")
local Selection = game:GetService("Selection")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local RunService = game:GetService("RunService")
local InsertService = game:GetService("InsertService")

-- הגדרות
local SERVER_URL = "http://127.0.0.1:8080"
local POLL_INTERVAL = 0.5  -- שניות

-- יצירת Toolbar
local toolbar = plugin:CreateToolbar("Voice Creator")
local button = toolbar:CreateButton(
    "Voice Creator",
    "הפעל שליטה קולית",
    "rbxassetid://6031075938"
)

-- ========================================
-- פקודות זמינות
-- ========================================

local VoiceCreator = {}

-- יצירת קוביה
function VoiceCreator.cube(color, size)
    local part = Instance.new("Part")
    part.Shape = Enum.PartType.Block
    part.Size = size or Vector3.new(4, 4, 4)
    part.Position = Vector3.new(0, 10, 0)
    part.Anchored = true
    if color then
        part.BrickColor = BrickColor.new(color)
    end
    part.Parent = workspace
    Selection:Set({part})
    ChangeHistoryService:SetWaypoint("יצירת קוביה")
    print("✅ נוצרה קוביה " .. (color or ""))
    return part
end

-- יצירת כדור
function VoiceCreator.ball(color, size)
    local part = Instance.new("Part")
    part.Shape = Enum.PartType.Ball
    part.Size = size or Vector3.new(4, 4, 4)
    part.Position = Vector3.new(0, 10, 0)
    part.Anchored = true
    if color then
        part.BrickColor = BrickColor.new(color)
    end
    part.Parent = workspace
    Selection:Set({part})
    ChangeHistoryService:SetWaypoint("יצירת כדור")
    print("✅ נוצר כדור " .. (color or ""))
    return part
end

-- יצירת גליל
function VoiceCreator.cylinder(color, size)
    local part = Instance.new("Part")
    part.Shape = Enum.PartType.Cylinder
    part.Size = size or Vector3.new(4, 4, 4)
    part.Position = Vector3.new(0, 10, 0)
    part.Anchored = true
    if color then
        part.BrickColor = BrickColor.new(color)
    end
    part.Parent = workspace
    Selection:Set({part})
    ChangeHistoryService:SetWaypoint("יצירת גליל")
    print("✅ נוצר גליל " .. (color or ""))
    return part
end

-- שינוי צבע
function VoiceCreator.color(newColor)
    local selected = Selection:Get()
    local count = 0
    for _, obj in ipairs(selected) do
        if obj:IsA("BasePart") then
            obj.BrickColor = BrickColor.new(newColor)
            count = count + 1
        end
    end
    ChangeHistoryService:SetWaypoint("שינוי צבע")
    print("✅ צבעתי " .. count .. " אובייקטים ב-" .. newColor)
end

-- הגדלה
function VoiceCreator.bigger(mult)
    mult = mult or 2
    local selected = Selection:Get()
    for _, obj in ipairs(selected) do
        if obj:IsA("BasePart") then
            obj.Size = obj.Size * mult
        end
    end
    ChangeHistoryService:SetWaypoint("הגדלה")
    print("✅ הגדלתי פי " .. mult)
end

-- הקטנה
function VoiceCreator.smaller(mult)
    mult = mult or 0.5
    local selected = Selection:Get()
    for _, obj in ipairs(selected) do
        if obj:IsA("BasePart") then
            obj.Size = obj.Size * mult
        end
    end
    ChangeHistoryService:SetWaypoint("הקטנה")
    print("✅ הקטנתי")
end

-- מחיקה
function VoiceCreator.delete()
    local selected = Selection:Get()
    local count = #selected
    for _, obj in ipairs(selected) do
        obj:Destroy()
    end
    ChangeHistoryService:SetWaypoint("מחיקה")
    print("✅ מחקתי " .. count .. " אובייקטים")
end

-- בחירת האחרון
function VoiceCreator.selectLast()
    local children = workspace:GetChildren()
    for i = #children, 1, -1 do
        if children[i]:IsA("BasePart") then
            Selection:Set({children[i]})
            print("✅ בחרתי: " .. children[i].Name)
            return children[i]
        end
    end
end

-- הזזה
function VoiceCreator.move(x, y, z)
    local selected = Selection:Get()
    for _, obj in ipairs(selected) do
        if obj:IsA("BasePart") then
            obj.Position = obj.Position + Vector3.new(x or 0, y or 0, z or 0)
        end
    end
    ChangeHistoryService:SetWaypoint("הזזה")
    print("✅ הזזתי")
end

-- טעינת מודל מוכן מ-Toolbox
function VoiceCreator.loadModel(assetId, x, y, z)
    local success, model = pcall(function()
        return InsertService:LoadAsset(assetId):GetChildren()[1]
    end)
    if success and model then
        model.Parent = workspace
        if model:IsA("Model") then
            model:MoveTo(Vector3.new(x or 0, y or 5, z or 0))
        elseif model:IsA("BasePart") then
            model.Position = Vector3.new(x or 0, y or 5, z or 0)
            model.Anchored = true
        end
        Selection:Set({model})
        ChangeHistoryService:SetWaypoint("טעינת מודל")
        print("✅ נטען מודל: " .. assetId)
        return model
    else
        warn("❌ נכשל בטעינת מודל: " .. assetId)
        return nil
    end
end

-- מודלים מוכנים
VoiceCreator.MODELS = {
    tree = 4631364747,
    house = 7075284869,
    car = 7086281035,
    chair = 8667289978,
    table = 7086407632,
    lamp = 7086431294,
    fence = 7074904498,
    rock = 5765284230,
}

-- פונקציות קיצור למודלים
function VoiceCreator.tree(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.tree, x, y, z) end
function VoiceCreator.house(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.house, x, y, z) end
function VoiceCreator.car(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.car, x, y, z) end
function VoiceCreator.chair(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.chair, x, y, z) end
function VoiceCreator.lamp(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.lamp, x, y, z) end
function VoiceCreator.fence(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.fence, x, y, z) end
function VoiceCreator.rock(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.rock, x, y, z) end

-- ========================================
-- חשיפה גלובלית (לשימוש מ-Command Bar)
-- ========================================

_G.VC = VoiceCreator
_G.VoiceCreator = VoiceCreator
_G.cube = VoiceCreator.cube
_G.ball = VoiceCreator.ball
_G.color = VoiceCreator.color

-- ========================================
-- HTTP Polling
-- ========================================

local isActive = false
local pollConnection = nil

local function executeCommand(luaCode)
    -- הרץ את הקוד ב-environment עם גישה ל-VoiceCreator
    local env = setmetatable({
        VC = VoiceCreator,
        VoiceCreator = VoiceCreator,
        cube = VoiceCreator.cube,
        ball = VoiceCreator.ball,
        cylinder = VoiceCreator.cylinder,
        color = VoiceCreator.color,
        bigger = VoiceCreator.bigger,
        smaller = VoiceCreator.smaller,
        delete = VoiceCreator.delete,
        selectLast = VoiceCreator.selectLast,
        move = VoiceCreator.move,
        loadModel = VoiceCreator.loadModel,
        tree = VoiceCreator.tree,
        house = VoiceCreator.house,
        car = VoiceCreator.car,
        chair = VoiceCreator.chair,
        lamp = VoiceCreator.lamp,
        fence = VoiceCreator.fence,
        rock = VoiceCreator.rock,
        workspace = workspace,
        game = game,
        Instance = Instance,
        Vector3 = Vector3,
        CFrame = CFrame,
        BrickColor = BrickColor,
        Enum = Enum,
        print = print,
        math = math,
        table = table,
        pcall = pcall,
        InsertService = InsertService,
        wait = wait,
    }, {__index = _G})

    local func, err = loadstring(luaCode)
    if not func then
        warn("❌ שגיאת קומפילציה: " .. tostring(err))
        return false
    end

    setfenv(func, env)

    local success, result = pcall(func)
    if not success then
        warn("❌ שגיאת הרצה: " .. tostring(result))
        return false
    end

    return true
end

local function pollServer()
    local success, response = pcall(function()
        return HttpService:GetAsync(SERVER_URL .. "/command")
    end)

    if success then
        local data = HttpService:JSONDecode(response)
        if data.hasCommand and data.command then
            print("🎤 מריץ פקודה: " .. data.command)
            executeCommand(data.command)
        end
    end
    -- אם נכשל - פשוט ממשיכים (השרת אולי לא פעיל)
end

local function startPolling()
    if pollConnection then
        pollConnection:Disconnect()
    end

    local lastPoll = 0
    pollConnection = RunService.Heartbeat:Connect(function()
        local now = tick()
        if now - lastPoll >= POLL_INTERVAL then
            lastPoll = now
            spawn(pollServer)
        end
    end)

    print("🔄 מתחיל לשאול את השרת...")
end

local function stopPolling()
    if pollConnection then
        pollConnection:Disconnect()
        pollConnection = nil
    end
    print("⏹️ הפסקתי לשאול")
end

-- ========================================
-- UI
-- ========================================

button.Click:Connect(function()
    isActive = not isActive
    button:SetActive(isActive)

    if isActive then
        print("=" .. string.rep("=", 50))
        print("🎤 Voice Creator מופעל!")
        print("=" .. string.rep("=", 50))
        print("")
        print("מחכה לפקודות מ-" .. SERVER_URL)
        print("")
        print("פקודות זמינות:")
        print("  VC.cube('Bright blue')  - קוביה כחולה")
        print("  VC.ball('Bright red')   - כדור אדום")
        print("  VC.color('Bright green') - צבע ירוק")
        print("  VC.bigger()             - הגדל פי 2")
        print("  VC.smaller()            - הקטן לחצי")
        print("  VC.delete()             - מחק נבחרים")
        print("")

        startPolling()
    else
        print("🔴 Voice Creator כבוי")
        stopPolling()
    end
end)

-- ========================================
-- פונקציות נוספות למערכת החכמה
-- ========================================

-- ניקוי העולם
function VoiceCreator.clearWorld()
    for _, child in ipairs(workspace:GetChildren()) do
        if child:IsA("BasePart") or child:IsA("Model") then
            if child.Name ~= "Baseplate" and child.Name ~= "Terrain" then
                child:Destroy()
            end
        end
    end
    print("🧹 העולם נוקה!")
end

-- רשימת כל האובייקטים
function VoiceCreator.listObjects()
    local count = 0
    print("📋 אובייקטים בעולם:")
    for _, child in ipairs(workspace:GetChildren()) do
        if child:IsA("BasePart") then
            print("  - " .. child.Name .. " @ " .. tostring(child.Position))
            count = count + 1
        elseif child:IsA("Model") then
            print("  - [Model] " .. child.Name)
            count = count + 1
        end
    end
    print("סה״כ: " .. count .. " אובייקטים")
end

-- שכפול נבחר
function VoiceCreator.duplicate(offsetX, offsetY, offsetZ)
    local selected = Selection:Get()
    local newParts = {}
    for _, obj in ipairs(selected) do
        if obj:IsA("BasePart") then
            local clone = obj:Clone()
            clone.Position = obj.Position + Vector3.new(offsetX or 5, offsetY or 0, offsetZ or 0)
            clone.Parent = workspace
            table.insert(newParts, clone)
        end
    end
    Selection:Set(newParts)
    ChangeHistoryService:SetWaypoint("שכפול")
    print("✅ שכפלתי " .. #newParts .. " אובייקטים")
end

-- סיבוב
function VoiceCreator.rotate(degrees)
    local selected = Selection:Get()
    for _, obj in ipairs(selected) do
        if obj:IsA("BasePart") then
            obj.CFrame = obj.CFrame * CFrame.Angles(0, math.rad(degrees or 45), 0)
        end
    end
    ChangeHistoryService:SetWaypoint("סיבוב")
    print("✅ סובבתי " .. (degrees or 45) .. " מעלות")
end

-- הוספה ל-env
_G.VC.clearWorld = VoiceCreator.clearWorld
_G.VC.listObjects = VoiceCreator.listObjects
_G.VC.duplicate = VoiceCreator.duplicate
_G.VC.rotate = VoiceCreator.rotate

-- הודעת טעינה
print("=" .. string.rep("=", 50))
print("🎤 Voice Creator Plugin v2.0 - Smart Edition נטען!")
print("לחץ על הכפתור ב-Toolbar להפעלה")
print("=" .. string.rep("=", 50))
