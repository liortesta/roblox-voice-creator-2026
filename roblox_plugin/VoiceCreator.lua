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

-- מודלים מוכנים - ספרייה מורחבת
VoiceCreator.MODELS = {
    -- טבע
    tree = 4631364747,
    rock = 5765284230,
    bush = 6899673073,
    flower = 6432066505,
    grass = 6432055451,

    -- בניינים
    house = 7075284869,
    building = 7074712850,
    shop = 6432140591,
    castle = 6899526583,
    tower = 6432154321,

    -- רכבים
    car = 7086281035,
    truck = 6899547632,
    plane = 6432189012,
    boat = 6899612345,
    bike = 6432201234,

    -- רהיטים
    chair = 8667289978,
    table_model = 7086407632,
    bed = 6899678901,
    sofa = 6432215678,
    desk = 6899689012,

    -- תאורה ונוי
    lamp = 7086431294,
    streetlight = 6432228901,
    torch = 6899701234,
    sign = 6432241567,

    -- גדרות ומבנים
    fence = 7074904498,
    wall = 6899712345,
    gate = 6432254890,
    bridge = 6899723456,

    -- דמויות (NPC)
    person = 6432267123,
    soldier = 6899734567,
    zombie = 6432279890,
    animal = 6899745678,

    -- ספורט ומשחק
    goal = 6432292345,
    basketball = 6899756789,
    slide = 6432304567,
    swing = 6899767890,
    trampoline = 6432316789,

    -- אפקטים
    fire = 6899778901,
    water = 6432328901,
    smoke = 6899789012,
    sparkle = 6432341234,
}

-- פונקציות קיצור למודלים
function VoiceCreator.tree(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.tree, x, y, z) end
function VoiceCreator.house(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.house, x, y, z) end
function VoiceCreator.car(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.car, x, y, z) end
function VoiceCreator.chair(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.chair, x, y, z) end
function VoiceCreator.lamp(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.lamp, x, y, z) end
function VoiceCreator.fence(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.fence, x, y, z) end
function VoiceCreator.rock(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.rock, x, y, z) end
function VoiceCreator.soldier(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.soldier, x, y, z) end
function VoiceCreator.castle(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.castle, x, y, z) end
function VoiceCreator.truck(x, y, z) return VoiceCreator.loadModel(VoiceCreator.MODELS.truck, x, y, z) end

-- פונקציה גנרית לטעינת מודל לפי שם
function VoiceCreator.spawn(modelName, x, y, z)
    local assetId = VoiceCreator.MODELS[modelName]
    if assetId then
        return VoiceCreator.loadModel(assetId, x, y, z)
    else
        warn("מודל לא נמצא: " .. modelName)
        print("מודלים זמינים: tree, house, car, chair, lamp, fence, rock, soldier, castle, truck...")
        return nil
    end
end

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
        buildEffect = VoiceCreator.buildEffect,
        flyTo = VoiceCreator.flyTo,
        playBuildSound = VoiceCreator.playBuildSound,
        playSuccessSound = VoiceCreator.playSuccessSound,
        addFire = VoiceCreator.addFire,
        addSparkles = VoiceCreator.addSparkles,
        addSmoke = VoiceCreator.addSmoke,
        addParticles = VoiceCreator.addParticles,
        addLight = VoiceCreator.addLight,
        makeNeon = VoiceCreator.makeNeon,
        rainbow = VoiceCreator.rainbow,
        float = VoiceCreator.float,
        spin = VoiceCreator.spin,
        setLighting = VoiceCreator.setLighting,
        dayNightCycle = VoiceCreator.dayNightCycle,
        clearWeather = VoiceCreator.clearWeather,
        scanWorkspace = VoiceCreator.scanWorkspace,
        sendScan = VoiceCreator.sendScan,
        -- v8.0 Script Injection & Behaviors
        addScript = VoiceCreator.addScript,
        removeScript = VoiceCreator.removeScript,
        listScripts = VoiceCreator.listScripts,
        createNPC = VoiceCreator.createNPC,
        addHumanoid = VoiceCreator.addHumanoid,
        makeVehicle = VoiceCreator.makeVehicle,
        addClickDetector = VoiceCreator.addClickDetector,
        addProximityPrompt = VoiceCreator.addProximityPrompt,
        HttpService = HttpService,
        tostring = tostring,
        ipairs = ipairs,
        pairs = pairs,
        string = string,
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
        spawn = spawn,
        delay = delay,
        InsertService = InsertService,
        wait = wait,
        Color3 = Color3,
        ColorSequence = ColorSequence,
        ColorSequenceKeypoint = ColorSequenceKeypoint,
        NumberSequence = NumberSequence,
        NumberSequenceKeypoint = NumberSequenceKeypoint,
        NumberRange = NumberRange,
        Vector2 = Vector2,
        Debris = game:GetService("Debris"),
        Lighting = game:GetService("Lighting"),
        Players = game:GetService("Players"),
        TweenService = game:GetService("TweenService"),
        TweenInfo = TweenInfo,
        UDim2 = UDim2,
        Selection = Selection,
        task = task,
        warn = warn,
        loadstring = loadstring,
        setfenv = setfenv,
        setmetatable = setmetatable,
        getmetatable = getmetatable,
        type = type,
        tick = tick,
        unpack = unpack,
        select = select,
        rawset = rawset,
        rawget = rawget,
        tonumber = tonumber,
        error = error,
        require = require,
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

-- ========================================
-- אנימציות ואפקטים v4.1
-- ========================================

-- אפקט בנייה - ניצוצות וזוהר
function VoiceCreator.buildEffect(x, y, z)
    local pos = Vector3.new(x or 0, y or 10, z or 0)
    local effect = Instance.new("Part")
    effect.Name = "BuildEffect"
    effect.Anchored = true
    effect.CanCollide = false
    effect.Transparency = 0.5
    effect.Size = Vector3.new(3, 3, 3)
    effect.Position = pos
    effect.BrickColor = BrickColor.new("Bright yellow")
    effect.Shape = Enum.PartType.Ball
    effect.Material = Enum.Material.Neon
    effect.Parent = workspace

    -- ניצוצות
    local sparkle = Instance.new("Sparkles")
    sparkle.SparkleColor = Color3.fromRGB(255, 215, 0)
    sparkle.Parent = effect

    -- אור
    local light = Instance.new("PointLight")
    light.Brightness = 3
    light.Color = Color3.fromRGB(255, 215, 0)
    light.Range = 40
    light.Parent = effect

    -- היעלמות אחרי 2 שניות
    spawn(function()
        wait(1.5)
        for i = 1, 10 do
            effect.Transparency = 0.5 + (i * 0.05)
            light.Brightness = 3 - (i * 0.3)
            effect.Size = effect.Size * 0.9
            wait(0.05)
        end
        effect:Destroy()
    end)

    return effect
end

-- מצלמה עפה לאובייקט שנבנה
function VoiceCreator.flyTo(x, y, z)
    local camera = workspace.CurrentCamera
    if not camera then return end

    local targetPos = Vector3.new(x or 0, (y or 5) + 25, (z or 0) + 35)
    local lookAt = Vector3.new(x or 0, y or 5, z or 0)

    local startCF = camera.CFrame
    local endCF = CFrame.new(targetPos, lookAt)

    -- מעבר חלק
    spawn(function()
        for i = 0, 1, 0.04 do
            camera.CFrame = startCF:Lerp(endCF, i)
            wait()
        end
        camera.CFrame = endCF
    end)
end

-- צליל בנייה
function VoiceCreator.playBuildSound()
    pcall(function()
        local sound = Instance.new("Sound")
        sound.SoundId = "rbxassetid://9125402735"
        sound.Volume = 0.6
        sound.PlaybackSpeed = 1.2
        sound.Parent = workspace
        sound:Play()
        spawn(function()
            wait(3)
            sound:Destroy()
        end)
    end)
end

-- צליל הצלחה
function VoiceCreator.playSuccessSound()
    pcall(function()
        local sound = Instance.new("Sound")
        sound.SoundId = "rbxassetid://9125402735"
        sound.Volume = 0.5
        sound.PlaybackSpeed = 1.5
        sound.Parent = workspace
        sound:Play()
        wait(0.15)
        local sound2 = Instance.new("Sound")
        sound2.SoundId = "rbxassetid://9125402735"
        sound2.Volume = 0.5
        sound2.PlaybackSpeed = 2.0
        sound2.Parent = workspace
        sound2:Play()
        spawn(function()
            wait(3)
            sound:Destroy()
            sound2:Destroy()
        end)
    end)
end

-- ========================================
-- אפקטים ויזואליים v5.0
-- ========================================

-- אש
function VoiceCreator.addFire(part, size, heat)
    if not part then return end
    local fire = Instance.new("Fire")
    fire.Size = size or 10
    fire.Heat = heat or 15
    fire.Color = Color3.fromRGB(255, 100, 0)
    fire.SecondaryColor = Color3.fromRGB(255, 200, 0)
    fire.Parent = part
    return fire
end

-- ניצוצות
function VoiceCreator.addSparkles(part, color)
    if not part then return end
    local sparkles = Instance.new("Sparkles")
    sparkles.SparkleColor = color or Color3.fromRGB(255, 215, 0)
    sparkles.Parent = part
    return sparkles
end

-- עשן
function VoiceCreator.addSmoke(part, size, opacity, color)
    if not part then return end
    local smoke = Instance.new("Smoke")
    smoke.Size = size or 5
    smoke.Opacity = opacity or 0.5
    smoke.Color = color or Color3.fromRGB(150, 150, 150)
    smoke.RiseVelocity = 3
    smoke.Parent = part
    return smoke
end

-- חלקיקים צבעוניים
function VoiceCreator.addParticles(part, color1, color2, rate, lifetime)
    if not part then return end
    local emitter = Instance.new("ParticleEmitter")
    local c1 = color1 or Color3.fromRGB(255, 200, 50)
    local c2 = color2 or Color3.fromRGB(255, 100, 0)
    emitter.Color = ColorSequence.new({
        ColorSequenceKeypoint.new(0, c1),
        ColorSequenceKeypoint.new(1, c2)
    })
    emitter.Size = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 1),
        NumberSequenceKeypoint.new(1, 0)
    })
    emitter.Lifetime = NumberRange.new(lifetime or 1, (lifetime or 1) + 1)
    emitter.Rate = rate or 30
    emitter.Speed = NumberRange.new(3, 8)
    emitter.SpreadAngle = Vector2.new(30, 30)
    emitter.Parent = part
    return emitter
end

-- אור נקודתי
function VoiceCreator.addLight(part, color, brightness, range)
    if not part then return end
    local light = Instance.new("PointLight")
    light.Color = color or Color3.fromRGB(255, 255, 200)
    light.Brightness = brightness or 2
    light.Range = range or 30
    light.Parent = part
    return light
end

-- זוהר ניאון (הפוך חלק לנאון זוהר)
function VoiceCreator.makeNeon(part, color)
    if not part then return end
    part.Material = Enum.Material.Neon
    if color then
        part.BrickColor = BrickColor.new(color)
    end
    -- הוסף אור אוטומטי
    VoiceCreator.addLight(part, part.Color, 1.5, 20)
end

-- אפקט קשת בענן - צבעים משתנים
function VoiceCreator.rainbow(part)
    if not part then return end
    spawn(function()
        local colors = {"Bright red", "Bright orange", "Bright yellow", "Bright green", "Bright blue", "Bright violet"}
        local i = 1
        while part and part.Parent do
            part.BrickColor = BrickColor.new(colors[i])
            i = (i % #colors) + 1
            wait(0.3)
        end
    end)
end

-- אפקט ריחוף
function VoiceCreator.float(part, height, speed)
    if not part then return end
    local originY = part.Position.Y
    height = height or 3
    speed = speed or 2
    spawn(function()
        local t = 0
        while part and part.Parent do
            t = t + 0.03
            local newY = originY + math.sin(t * speed) * height
            part.Position = Vector3.new(part.Position.X, newY, part.Position.Z)
            wait(0.03)
        end
    end)
end

-- סיבוב אוטומטי
function VoiceCreator.spin(part, speed)
    if not part then return end
    speed = speed or 2
    spawn(function()
        while part and part.Parent do
            part.CFrame = part.CFrame * CFrame.Angles(0, math.rad(speed), 0)
            wait(0.03)
        end
    end)
end

-- ========================================
-- SCRIPT INJECTION v8.0 - Logic & Behaviors
-- ========================================

-- יצירת Script בתוך אובייקט (Plugin יכול לכתוב .Source!)
function VoiceCreator.addScript(target, scriptName, sourceCode, scriptType)
    if not target then
        -- Use selection if no target
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then
        warn("❌ No target for script! Select an object first.")
        return nil
    end

    scriptType = scriptType or "Script"
    local newScript = Instance.new(scriptType)
    newScript.Name = scriptName or ("Behavior_" .. tick())
    newScript.Source = sourceCode
    newScript.Parent = target

    ChangeHistoryService:SetWaypoint("הוספת סקריפט: " .. newScript.Name)
    print("✅ סקריפט '" .. newScript.Name .. "' נוסף ל-" .. target.Name)
    return newScript
end

-- הסרת סקריפט מאובייקט
function VoiceCreator.removeScript(target, scriptName)
    if not target then
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then return end

    for _, child in ipairs(target:GetDescendants()) do
        if (child:IsA("Script") or child:IsA("LocalScript")) then
            if scriptName == nil or child.Name == scriptName then
                child:Destroy()
                print("✅ סקריפט '" .. child.Name .. "' הוסר מ-" .. target.Name)
            end
        end
    end
    ChangeHistoryService:SetWaypoint("הסרת סקריפט")
end

-- רשימת סקריפטים באובייקט
function VoiceCreator.listScripts(target)
    if not target then
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then return {} end

    local scripts = {}
    for _, child in ipairs(target:GetDescendants()) do
        if child:IsA("Script") or child:IsA("LocalScript") then
            table.insert(scripts, {
                name = child.Name,
                type = child.ClassName,
                source = string.sub(child.Source or "", 1, 200),
                disabled = child.Disabled
            })
            print("  📜 " .. child.ClassName .. ": " .. child.Name)
        end
    end
    print("סה\"כ: " .. #scripts .. " סקריפטים")
    return scripts
end

-- יצירת NPC עם Humanoid (בסיס לכל ההתנהגויות)
function VoiceCreator.createNPC(x, y, z, name, color)
    local npc = Instance.new("Model")
    npc.Name = name or "NPC"

    -- גוף
    local torso = Instance.new("Part")
    torso.Name = "HumanoidRootPart"
    torso.Size = Vector3.new(2, 2, 1)
    torso.Position = Vector3.new(x or 0, (y or 0) + 3, z or 0)
    torso.BrickColor = BrickColor.new(color or "Bright blue")
    torso.Anchored = false
    torso.Parent = npc

    -- ראש
    local head = Instance.new("Part")
    head.Name = "Head"
    head.Shape = Enum.PartType.Ball
    head.Size = Vector3.new(1.5, 1.5, 1.5)
    head.Position = torso.Position + Vector3.new(0, 1.75, 0)
    head.BrickColor = BrickColor.new("Light orange")
    head.Anchored = false
    head.Parent = npc

    local headWeld = Instance.new("WeldConstraint")
    headWeld.Part0 = torso
    headWeld.Part1 = head
    headWeld.Parent = head

    -- רגליים
    local leftLeg = Instance.new("Part")
    leftLeg.Name = "LeftLeg"
    leftLeg.Size = Vector3.new(0.8, 2, 0.8)
    leftLeg.Position = torso.Position + Vector3.new(-0.5, -2, 0)
    leftLeg.BrickColor = BrickColor.new("Dark blue")
    leftLeg.Anchored = false
    leftLeg.Parent = npc

    local llWeld = Instance.new("WeldConstraint")
    llWeld.Part0 = torso
    llWeld.Part1 = leftLeg
    llWeld.Parent = leftLeg

    local rightLeg = Instance.new("Part")
    rightLeg.Name = "RightLeg"
    rightLeg.Size = Vector3.new(0.8, 2, 0.8)
    rightLeg.Position = torso.Position + Vector3.new(0.5, -2, 0)
    rightLeg.BrickColor = BrickColor.new("Dark blue")
    rightLeg.Anchored = false
    rightLeg.Parent = npc

    local rlWeld = Instance.new("WeldConstraint")
    rlWeld.Part0 = torso
    rlWeld.Part1 = rightLeg
    rlWeld.Parent = rightLeg

    -- Humanoid
    local humanoid = Instance.new("Humanoid")
    humanoid.WalkSpeed = 16
    humanoid.MaxHealth = 100
    humanoid.Health = 100
    humanoid.Parent = npc

    npc.PrimaryPart = torso
    npc.Parent = workspace

    Selection:Set({npc})
    ChangeHistoryService:SetWaypoint("יצירת NPC: " .. npc.Name)
    print("✅ NPC '" .. npc.Name .. "' נוצר!")
    return npc
end

-- יצירת Humanoid לאובייקט קיים
function VoiceCreator.addHumanoid(target, walkSpeed, jumpPower)
    if not target then
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then return end

    -- If it's a single part, wrap in model
    if target:IsA("BasePart") then
        local model = Instance.new("Model")
        model.Name = target.Name
        model.Parent = target.Parent
        target.Parent = model
        target.Name = "HumanoidRootPart"
        model.PrimaryPart = target
        target = model
    end

    if not target:FindFirstChildOfClass("Humanoid") then
        local humanoid = Instance.new("Humanoid")
        humanoid.WalkSpeed = walkSpeed or 16
        humanoid.JumpPower = jumpPower or 50
        humanoid.Parent = target
    end

    -- Ensure PrimaryPart & HumanoidRootPart
    if not target.PrimaryPart then
        local root = target:FindFirstChild("HumanoidRootPart")
        if not root then
            root = target:FindFirstChildOfClass("BasePart")
            if root then
                root.Name = "HumanoidRootPart"
            end
        end
        if root then
            target.PrimaryPart = root
        end
    end

    ChangeHistoryService:SetWaypoint("הוספת Humanoid")
    print("✅ Humanoid נוסף ל-" .. target.Name)
end

-- יצירת VehicleSeat לרכב
function VoiceCreator.makeVehicle(target, maxSpeed, torque)
    if not target then
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then return end

    local primary = target
    if target:IsA("Model") then
        primary = target.PrimaryPart or target:FindFirstChildOfClass("BasePart")
    end
    if not primary then return end

    local seat = Instance.new("VehicleSeat")
    seat.Name = "DriverSeat"
    seat.Size = Vector3.new(2, 1, 2)
    seat.Position = primary.Position + Vector3.new(0, 2, 0)
    seat.MaxSpeed = maxSpeed or 60
    seat.Torque = torque or 20
    seat.TurnSpeed = 1
    seat.Anchored = false

    if target:IsA("Model") then
        seat.Parent = target
        local weld = Instance.new("WeldConstraint")
        weld.Part0 = seat
        weld.Part1 = primary
        weld.Parent = seat

        -- Unanchor all parts
        for _, part in pairs(target:GetDescendants()) do
            if part:IsA("BasePart") then
                part.Anchored = false
            end
        end
    else
        seat.Parent = workspace
    end

    ChangeHistoryService:SetWaypoint("יצירת רכב")
    print("✅ רכב ניתן לנהיגה! מהירות: " .. (maxSpeed or 60))
end

-- הוספת ClickDetector
function VoiceCreator.addClickDetector(target, maxDistance)
    if not target then
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then return end

    local clickPart = target
    if target:IsA("Model") then
        clickPart = target.PrimaryPart or target:FindFirstChildOfClass("BasePart")
    end

    if clickPart then
        local cd = Instance.new("ClickDetector")
        cd.MaxActivationDistance = maxDistance or 15
        cd.Parent = clickPart
        print("✅ ClickDetector נוסף!")
    end
end

-- הוספת ProximityPrompt
function VoiceCreator.addProximityPrompt(target, actionText, objectText, distance)
    if not target then
        local selected = Selection:Get()
        target = selected[1]
    end
    if not target then return end

    local promptPart = target
    if target:IsA("Model") then
        promptPart = target.PrimaryPart or target:FindFirstChildOfClass("BasePart")
    end

    if promptPart then
        local prompt = Instance.new("ProximityPrompt")
        prompt.ActionText = actionText or "Interact"
        prompt.ObjectText = objectText or ""
        prompt.MaxActivationDistance = distance or 10
        prompt.Parent = promptPart
        print("✅ ProximityPrompt נוסף!")
    end
end

-- ========================================
-- מזג אוויר ותאורה v6.0
-- ========================================

-- שליטה בתאורה
function VoiceCreator.setLighting(clockTime, brightness, ambient)
    local Lighting = game:GetService("Lighting")
    if clockTime then Lighting.ClockTime = clockTime end
    if brightness then Lighting.Brightness = brightness end
    if ambient then Lighting.Ambient = ambient end
end

-- מעבר יום/לילה חלק
function VoiceCreator.dayNightCycle(speed)
    speed = speed or 1
    local Lighting = game:GetService("Lighting")
    spawn(function()
        while true do
            Lighting.ClockTime = (Lighting.ClockTime + 0.01 * speed) % 24
            wait(0.1)
        end
    end)
end

-- ביטול כל אפקטי מזג אוויר
function VoiceCreator.clearWeather()
    local Lighting = game:GetService("Lighting")
    Lighting.ClockTime = 14
    Lighting.Brightness = 2
    Lighting.FogEnd = 100000
    Lighting.FogStart = 0
    Lighting.Ambient = Color3.fromRGB(128, 128, 128)
    Lighting.OutdoorAmbient = Color3.fromRGB(128, 128, 128)
    -- Remove atmosphere, sky, bloom
    for _, child in ipairs(Lighting:GetChildren()) do
        if child:IsA("Atmosphere") or child:IsA("Sky") or child:IsA("BloomEffect") then
            child:Destroy()
        end
    end
    print("Weather cleared!")
end

-- הוספה ל-env
_G.VC.clearWorld = VoiceCreator.clearWorld
_G.VC.listObjects = VoiceCreator.listObjects
_G.VC.duplicate = VoiceCreator.duplicate
_G.VC.rotate = VoiceCreator.rotate
_G.VC.buildEffect = VoiceCreator.buildEffect
_G.VC.flyTo = VoiceCreator.flyTo
_G.VC.playBuildSound = VoiceCreator.playBuildSound
_G.VC.playSuccessSound = VoiceCreator.playSuccessSound
_G.VC.addFire = VoiceCreator.addFire
_G.VC.addSparkles = VoiceCreator.addSparkles
_G.VC.addSmoke = VoiceCreator.addSmoke
_G.VC.addParticles = VoiceCreator.addParticles
_G.VC.addLight = VoiceCreator.addLight
_G.VC.makeNeon = VoiceCreator.makeNeon
_G.VC.rainbow = VoiceCreator.rainbow
_G.VC.float = VoiceCreator.float
_G.VC.spin = VoiceCreator.spin
_G.VC.setLighting = VoiceCreator.setLighting
_G.VC.dayNightCycle = VoiceCreator.dayNightCycle
_G.VC.clearWeather = VoiceCreator.clearWeather

-- ========================================
-- סריקת Workspace v7.0 - AI Chat
-- ========================================

function VoiceCreator.scanWorkspace()
    local objects = {}
    for _, child in ipairs(workspace:GetChildren()) do
        if child.Name ~= "Baseplate" and child.Name ~= "Terrain" and child.Name ~= "Camera" then
            local info = {
                name = child.Name,
                class = child.ClassName,
            }

            if child:IsA("BasePart") then
                info.position = {math.floor(child.Position.X), math.floor(child.Position.Y), math.floor(child.Position.Z)}
                info.size = {math.floor(child.Size.X), math.floor(child.Size.Y), math.floor(child.Size.Z)}
                info.color = tostring(child.BrickColor)
                info.material = tostring(child.Material)
                info.anchored = child.Anchored
            end

            if child:IsA("Model") then
                info.children = {}
                for _, part in ipairs(child:GetChildren()) do
                    if part:IsA("BasePart") then
                        table.insert(info.children, {
                            name = part.Name,
                            class = part.ClassName,
                            position = {math.floor(part.Position.X), math.floor(part.Position.Y), math.floor(part.Position.Z)},
                            size = {math.floor(part.Size.X), math.floor(part.Size.Y), math.floor(part.Size.Z)},
                            color = tostring(part.BrickColor),
                            material = tostring(part.Material),
                        })
                    end
                end
                info.childCount = #info.children
            end

            -- Check for scripts
            local scripts = {}
            for _, desc in ipairs(child:GetDescendants()) do
                if desc:IsA("Script") or desc:IsA("LocalScript") then
                    table.insert(scripts, {
                        name = desc.Name,
                        class = desc.ClassName,
                        source = string.sub(desc.Source or "", 1, 500),
                    })
                end
            end
            if #scripts > 0 then
                info.scripts = scripts
            end

            table.insert(objects, info)
        end
    end
    return objects
end

-- Send scan data to Python server
function VoiceCreator.sendScan()
    local objects = VoiceCreator.scanWorkspace()
    local jsonData = HttpService:JSONEncode({objects = objects})

    local success, result = pcall(function()
        return HttpService:PostAsync(
            SERVER_URL .. "/scan",
            jsonData,
            Enum.HttpContentType.ApplicationJson,
            false
        )
    end)

    if success then
        print("📡 Workspace scan sent: " .. #objects .. " objects")
    else
        warn("Scan send failed: " .. tostring(result))
    end
    return objects
end

_G.VC.scanWorkspace = VoiceCreator.scanWorkspace
_G.VC.sendScan = VoiceCreator.sendScan
-- v8.0 Script Injection
_G.VC.addScript = VoiceCreator.addScript
_G.VC.removeScript = VoiceCreator.removeScript
_G.VC.listScripts = VoiceCreator.listScripts
_G.VC.createNPC = VoiceCreator.createNPC
_G.VC.addHumanoid = VoiceCreator.addHumanoid
_G.VC.makeVehicle = VoiceCreator.makeVehicle
_G.VC.addClickDetector = VoiceCreator.addClickDetector
_G.VC.addProximityPrompt = VoiceCreator.addProximityPrompt

-- Auto-scan every 10 seconds when active
local scanConnection = nil
local function startAutoScan()
    if scanConnection then scanConnection:Disconnect() end
    local lastScan = 0
    scanConnection = RunService.Heartbeat:Connect(function()
        local now = tick()
        if now - lastScan >= 10 then
            lastScan = now
            spawn(function()
                pcall(VoiceCreator.sendScan)
            end)
        end
    end)
end

local function stopAutoScan()
    if scanConnection then
        scanConnection:Disconnect()
        scanConnection = nil
    end
end

-- Hook auto-scan to button activation
button.Click:Connect(function()
    if isActive then
        startAutoScan()
    else
        stopAutoScan()
    end
end)

-- הודעת טעינה
print("=" .. string.rep("=", 50))
print("🎤 Voice Creator Plugin v8.0 - Logic & Behaviors Edition נטען!")
print("כולל: Script Injection, NPC, Behaviors, Interactions, AI Chat")
print("לחץ על הכפתור ב-Toolbar להפעלה")
print("=" .. string.rep("=", 50))
