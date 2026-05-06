// Pathfinder custom scripting API template.
//
// Enable scripting with -Dex_enable_scripting, then open Model > Edit Custom
// Scripts. This script runs inside Pathfinder's JavaScript environment, not in
// Python. Rename all object names before use.

var pfSkill = pfSkill || {};

pfSkill.regionDoorControl = (function () {
  var sim = api.simctl.v1;
  var geom = api.geometry.v1;
  var agents = api.agents.v1;
  var io = api.io.v1;
  var triggers = api.triggers.v1;

  var config = {
    regionName: "Region A",
    doorName: "Station Entrance",
    triggerName: "Fire alarm trigger",
    closeAtCount: 30,
    reopenAtCount: 10,
    sampleSeconds: 1.0,
    logFile: "custom_region_door_log.tsv"
  };

  var region = geom.find(config.regionName);
  var door = geom.find(config.doorName);
  var trigger = triggers.find(config.triggerName);
  var out = io.openPrintStream(config.logFile);
  var lastSample = -1.0;
  var closed = false;

  function countAgentsInRegion() {
    return agents.findAll(region).size();
  }

  function setDoorClosed(shouldClose) {
    if (shouldClose && !closed) {
      geom.close(door);
      closed = true;
    } else if (!shouldClose && closed) {
      geom.open(door);
      closed = false;
    }
  }

  sim.onUpdate(function (t) {
    if (lastSample >= 0 && t - lastSample < config.sampleSeconds) {
      return;
    }
    lastSample = t;

    var count = countAgentsInRegion();
    if (count >= config.closeAtCount) {
      setDoorClosed(true);
      triggers.setInfluenceChance(trigger, 1.0);
    } else if (count <= config.reopenAtCount) {
      setDoorClosed(false);
      triggers.setInfluenceChance(trigger, 0.0);
    }

    out.println(t + "\t" + count + "\t" + closed);
  });

  sim.onExit(function () {
    out.close();
  });

  return {
    countAgentsInRegion: countAgentsInRegion,
    setDoorClosed: setDoorClosed
  };
})();
