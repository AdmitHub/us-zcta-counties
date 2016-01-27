var expect = require("chai").expect;
var zcta = require("../index");

describe("fetch", function() {
  it("Gets a list of US states", function() {
    var res = zcta.getStates();
    expect(res).to.be.an('array');
    expect(res.length).to.equal(52); // states + territories
  });

  it("Gets a list of counties by state", function() {
    var res = zcta.getCountiesByState('UT');
    expect(res).to.be.an('array');
    expect(res).to.contain("Salt Lake County");
    expect(res.length).to.equal(29);
  });

  it("Gets a county and state by zip", function() {
    var res = zcta.getCountyByZip(59715);
    expect(res).to.deep.equal({state: 'MT', county: 'Park County'});
  });

  it("Finds arbitrary relations", function() {
    var res = zcta.find({county: 'Gallatin County', state: 'MT'});
    expect(res).to.deep.equal([
      '59714', '59718', '59730', '59741', '59758', '59760'
    ]);
    var res = zcta.find({state: 'HI'});
    var keys = Object.keys(res);
    keys.sort();
    expect(keys).to.deep.equal(['Hawaii County', 'Honolulu County',
                               'Kalawao County', 'Kauai County', 'Maui County']);
    var res = zcta.find({state: 'RI'});
    expect(res['Bristol County']).to.deep.equal(['02806', '02809', '02885']);
  });

  it("Returns true/false for valid mapping", function() {
    var res = zcta.find({county: "fooey", state: "MT", zip: "59715"});
    expect(res).to.be.false;
    var res = zcta.find({county: "Park County", state: "MT", zip: "59715"});
    expect(res).to.be.true;
  });

  it("Returns undefined for bad params", function() {
    var res = zcta.find({foo: "bar"});
    expect(res).to.be.undefined;
    var res = zcta.find({state: "MAMA"});
    expect(res).to.be.undefined;
    var res = zcta.find({zip: "fooey"});
    expect(res).to.be.undefined;
    var res = zcta.find({county: "fooey", state: "mama"});
    expect(res).to.be.undefined;
  });

});
