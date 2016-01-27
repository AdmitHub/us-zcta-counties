# US ZCTA Counties

List of all US ZipCode Tabulation Areas and the counties that correspond to them.

Data sources:

 * http://www2.census.gov/geo/docs/maps-data/data/rel/zcta_county_rel_10.txt
 * http://www2.census.gov/geo/docs/maps-data/data/gazetteer/Gaz_counties_national.zip

## What are ZCTA's?

ZipCode Tabulation Areas are mostly sorta similar to zip codes, but they're
different.  See http://www.census.gov/geo/reference/zctas.html for full
details.  For the purposes of doing rough-and-ready associations between
zipcodes and counties, ZCTAs are mostly sort-of correct but not entirely.  This
dataset will *not* include all valid zip codes, and addresses with a given zip
code may actually reside in a different county from the one named by their
ZCTA.  There *is no simple mapping between zipcodes and counties*, you need a
full address to do that.

Other zip-code related data: 
 - http://federalgovernmentzipcodes.us/free-zipcode-database-Primary.csv 
 - http://www2.census.gov/geo/docs/reference/codes/files/national_county.txt 

Other relevant NPM modules:
 - https://www.npmjs.com/package/zipcodes
 - https://www.npmjs.com/package/us-regions

## Usage

Install:

    npm install us-zcta-counties

### `zcta.find(opts)`: Search by state, county, or zip.

    var zcta = require("us-zcta-counties");
    zcta.find({state: "HI"});

    // returns:

    {
        "Hawaii County": ["96704" "96710" "96719" "96720" "96725" "96726" "96727" "96728" "96737" "96738" "96740" "96743" "96749" "96750" "96755" "96760" "96764" "96771" "96772" "96773" "96774" "96776" "96777" "96778" "96780" "96781" "96783" "96785"],
        "Honolulu County": [ "96701" "96706" "96707" "96712" "96717" "96730" "96731" "96734" "96744" "96759" "96762" "96782" "96786" "96789" "96791" "96792" "96795" "96797" "96813" "96814" "96815" "96816" "96817" "96818" "96819" "96821" "96822" "96825" "96826" "96850" "96853" "96857" "96859" "96860" "96863" ]
        "Kalawao County": [ "96742" ]
        "Kauai County": [ "96703" "96705" "96714" "96716" "96722" "96741" "96746" "96747" "96751" "96752" "96754" "96756" "96765" "96766" "96769" "96796" ]
        "Maui County": [ "96708" "96713" "96729" "96732" "96748" "96753" "96757" "96761" "96763" "96768" "96770" "96779" "96790" "96793" ]
    }

    zcta.find({zip: "96742"})
    // {state: "HI", county: "Kalawao County"}

### `zcta.getStates()`: List states

    var zcta = require("us-zcta-counties");
    zcta.getStates();

    // returns:
    ['AK', 'AL', 'AR', 'AZ' ... ]

### `zcta.getCountiesByState(state)`: List counties by state

    var zcta = require("us-zcta-counties");
    zcta.getCountiesByState("HI")

    // returns
    ['Hawaii County', 'Honolulu County', 'Kalawao County' ... ]

