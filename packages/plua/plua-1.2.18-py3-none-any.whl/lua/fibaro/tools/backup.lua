local Emu,path = ...
local fmt = string.format

local lfs = require("lfs")

local hasSetup = false
local function setup()
  if hasSetup then return end
  hasSetup = true
  local now = os.time()
  
  path = tostring(path)
  path = path:gsub("\\","/") -- Normalize path separators
  path = path:sub(#path) == "/" and path or path.."/"
  if not lfs.attributes(path) then
    error("Backup directory don't exist")
  end
  
  lfs.mkdir(path.."quickApps")
  lfs.mkdir(path.."scenes")
  lfs.mkdir(path.."globalVars")
  lfs.mkdir(path.."climate")
  lfs.mkdir(path.."sprinklers")
  -- lfs.mkdir(path.."humidity")
  lfs.mkdir(path.."profiles")
  lfs.mkdir(path.."alarmPartitions")
  lfs.mkdir(path.."location")
end

local function backup(path,filename,modification) -- backup a backup file
end

local function backupQuickApps()
  setup()
  Emu:INFO("======== Quick Apps ================")
  local n = 0
  local fqas = Emu.api.hc3.get("/devices?interface=quickApp")
  for _,d in ipairs(fqas) do
    local name = fmt("%s_%d.fqa",d.name,d.id)
    local fpath = path.."quickApps/"..name
    local attr = lfs.attributes(fpath)
    if attr == nil or attr.modification < d.modified then
      n = n+1
      if attr then backup("quickApps",fpath, attr.modification) end
      local fqa,err = Emu.api.get("/quickApp/export/"..d.id)
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encodeFast(fqa))
      lfs.touch(fpath, d.modified, d.modified) -- Use lfs to set the timestamps
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d quickApps", n))
end

local function backupScenes()
  setup()
  Emu:INFO("======== Scenes ====================")
  local n = 0
  local scenes = Emu.api.hc3.get("/scenes")
  for _,d in ipairs(scenes) do
    local name = fmt("%s_%d.scene",d.name,d.id)
    local fpath = path.."scenes/"..name
    local attr = lfs.attributes(fpath)
    if attr == nil or attr.modification < d.updated then
      n = n+1
      if attr then backup("scenes",fpath, attr.modification) end
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
      lfs.touch(fpath, d.updated, d.updated) -- Use lfs to set the timestamps
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d scenes", n))
end

local function backupGlobalVars()
  setup()
  Emu:INFO("======== Global Vars ===============")
  local n = 0
  local gvars = Emu.api.hc3.get("/globalVariables")
  for _,d in ipairs(gvars) do
    local name = fmt("%s.var",d.name)
    local fpath = path.."globalVars/"..name
    local attr = lfs.attributes(fpath)
    if attr == nil or attr.modification < d.modified then
      n = n+1
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
      lfs.touch(fpath, d.modified, d.modified) -- Use lfs to set the timestamps
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d global vars", n))
end

local function equalContent(tab,filename)
  local stat,c = pcall(Emu.lib.readFile,filename)
  if not stat then return false end
  if not c then return false end
  local stat,t2 = pcall(json.decode,c)
  if not stat then return false end
  return table.equal(tab,t2)
end

local function backupClimate()
  setup()
  Emu:INFO("======== Climate ===================")
  local n = 0
  local climates = Emu.api.hc3.get("/panels/climate")
  for _,d in ipairs(climates) do
    local name = fmt("%s_%d.clim",d.name,d.id)
    local fpath = path.."climate/"..name
    if not equalContent(d,fpath) then
      n = n+1
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d climates", n))
end

local function backupSprinklers()
  setup()
  Emu:INFO("======== Sprinklers ================")
  local n = 0
  local sprinklers = Emu.api.hc3.get("/panels/sprinklers")
  for _,d in ipairs(sprinklers) do
    local name = fmt("%s_%d.sprinkler",d.name,d.id)
    local fpath = path.."sprinklers/"..name
    if not equalContent(d,fpath) then
      n = n+1
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d sprinkers", n))
end

-- local function backupHumidity()
--   Emu:INFO("======== Humidity ===============")
--   local n = 0
--   local humidity = Emu.api.get("/panels/humidity")
--   for _,d in ipairs(humidity) do
--     local name = fmt("%s_%d.humidity",d.name,d.id)
--     local fpath = path.."humidity/"..name
--     local attr = nil
--     if attr == nil then
--       n = n+1
--       Emu:INFO("🗄️ Backing up",fpath)
--       Emu.lib.writeFile(fpath,json.encode(d))
--     end
--   end
--   Emu:INFO(fmt("🗄️ Backed up %d humidity", n))
-- end

local function backupLocation()
  setup()
  Emu:INFO("======== Location ==================")
  local n = 0
  local locations = Emu.api.hc3.get("/panels/location")
  for _,d in ipairs(locations) do
    local name = fmt("%s_%d.location",d.name,d.id)
    local fpath = path.."location/"..name
    local attr = lfs.attributes(fpath)
    if attr == nil or attr.modification < d.modified then
      n = n+1
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
      lfs.touch(fpath, d.modified, d.modified) -- Use lfs to set the timestamps
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d locations", n))
end

local function backupProfiles()
  setup()
  Emu:INFO("======== Profiles ==================")
  local n = 0
  local profiles = Emu.api.hc3.get("/profiles")
  for _,d in ipairs(profiles.profiles) do
    local name = fmt("%s_%d.prof",d.name,d.id)
    local fpath = path.."profiles/"..name
    if not equalContent(d,fpath) then
      n = n+1
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
      lfs.touch(fpath, d.modified, d.modified) -- Use lfs to set the timestamps
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d profiles", n))
end

local function backupAlarmPartitions()
  setup()
  Emu:INFO("======== Alarm Partitions ==========")
  local n = 0
  local partitions = Emu.api.hc3.get("/alarms/v1/partitions")
  for _,d in ipairs(partitions) do
    local name = fmt("%s_%d.alarm",d.name,d.id)
    local fpath = path.."alarmPartitions/"..name
    if not equalContent(d,fpath) then
      n = n+1
      Emu:INFO("🗄️ Backing up",fpath)
      Emu.lib.writeFile(fpath,json.encode(d))
      lfs.touch(fpath, d.modified, d.modified) -- Use lfs to set the timestamps
    end
  end
  Emu:INFO(fmt("🗄️ Backed up %d alarm partitions", n))
end

return {
  sort = -1,
  doc = "Backup tool for HC3. Backs up QuickApps, Scenes, Global Variables, Climate, Sprinklers, Profiles, Alarms, and Location.",
  usage = ">plua -t backup <backup dir>",
  fun = function()
    backupQuickApps()
    backupScenes()
    backupGlobalVars()
    backupClimate()
    backupSprinklers()
    -- backupHumidity()
    backupLocation()
    backupProfiles()
    backupAlarmPartitions()
  end
}