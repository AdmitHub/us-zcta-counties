var zipStateCounty = require("./zip_state_county.json");

var stateToCounties = {};
var zipToCounties = {};

zipStateCounty.zip_state_county.forEach(function(list) {
  var zip = list[0];
  var state = list[1];
  var county = list[2];
  stateToCounties[state] = stateToCounties[state] || {};
  stateToCounties[state][county] = stateToCounties[state][county] || [];
  stateToCounties[state][county].push(zip);
  zipToCounties[zip] = {state: state, county: county}
});

// free this reference so it can be GC'ed.
zipStateCounty = null;

module.exports = {
  getStates: function() {
    return Object.keys(stateToCounties);
  },
  getCountiesByState: function(state) {
    return Object.keys(stateToCounties[state]);
  },
  getCountyByZip: function(zip) {
    return zipToCounties[zip];
  },
  find: function(obj) {
    if (obj.state && obj.county && obj.zip) {
      var zips = (stateToCounties[obj.state] || {})[obj.county] || [];
      for (var i = 0; i < zips.length; i++) {
        if (zips[i] === obj.zip) {
          return true;
        }
      }
      return false;
    }
    if (obj.state && obj.county) {
      return (stateToCounties[obj.state] || {})[obj.county];
    }
    if (obj.state) {
      return stateToCounties[obj.state];
    }
    if (obj.zip) {
      return zipToCounties[obj.zip];
    }
    return undefined;
  }
}
