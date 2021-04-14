/*
 * ****************************************************************************
 *
 *  CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
 *  (C) Cloudera, Inc. 2021
 *  All rights reserved.
 *
 *  Applicable Open Source License: Apache 2.0
 *
 *  NOTE: Cloudera open source products are modular software products
 *  made up of hundreds of individual components, each of which was
 *  individually copyrighted.  Each Cloudera open source product is a
 *  collective work under U.S. Copyright Law. Your license to use the
 *  collective work is as provided in your written agreement with
 *  Cloudera.  Used apart from the collective work, this file is
 *  licensed for your use pursuant to the open source license
 *  identified above.
 *
 *  This code is provided to you pursuant a written agreement with
 *  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
 *  this code. If you do not have a written agreement with Cloudera nor
 *  with an authorized and properly licensed third party, you do not
 *  have any rights to access nor to use this code.
 *
 *  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
 *  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
 *  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
 *  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
 *  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
 *  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
 *  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
 *  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
 *  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
 *  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
 *  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
 *  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
 *  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
 *  DATA.
 *
 * ***************************************************************************
 */


$(document).ready(function () {
    $('.js-example-basic-single').select2();
});


// Sequence generator function
const range = (start, stop, step) => Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + (i * step));

// Create dropdown option arrays
var departureHours = range(0, 23, 1);
var weeks = range(0, 51, 1);

// carrier and airport data from: https://www.bts.gov/topics/airlines-and-airports/world-airport-codes
var carriers = {
    'ATA Airlines d/b/a ATA': 'TZ',
    'AirTran Airways Corporation': 'FL',
    'Alaska Airlines Inc.': 'AS',
    'Aloha Airlines Inc.': 'AQ',
    'America West Airlines Inc.': 'HP',
    'American Airlines Inc.': 'AA',
    'Continental Air Lines Inc.': 'CO',
    'Delta Air Lines Inc.': 'DL',
    'Endeavor Air Inc.': '9E',
    'Envoy Air': 'MQ',
    'ExpressJet Airlines Inc.': 'EV',
    'Frontier Airlines Inc.': 'F9',
    'Hawaiian Airlines Inc.': 'HA',
    'Independence Air': 'DH',
    'JetBlue Airways': 'B6',
    'Mesa Airlines Inc.': 'YV',
    'Northwest Airlines Inc.': 'NW',
    'PSA Airlines Inc.': 'OH',
    'SkyWest Airlines Inc.': 'OO',
    'Southwest Airlines Co.': 'WN',
    'Trans World Airways LLC': 'TW',
    'US Airways Inc.': 'US',
    'United Air Lines Inc.': 'UA'
};
var airports = {
    'Abilene, TX: Abilene Regional': 'ABI',
    'Adak Island, AK: Adak': 'ADK',
    'Aguadilla, PR: Rafael Hernandez': 'BQN',
    'Akron, OH: Akron-Canton Regional': 'CAK',
    'Albany, GA: Southwest Georgia Regional': 'ABY',
    'Albany, NY: Albany International': 'ALB',
    'Albuquerque, NM: Albuquerque International Sunport': 'ABQ',
    'Alexandria, LA: Alexandria International': 'AEX',
    'Allentown/Bethlehem/Easton, PA: Lehigh Valley International': 'ABE',
    'Amarillo, TX: Rick Husband Amarillo International': 'AMA',
    'Anchorage, AK: Ted Stevens Anchorage International': 'ANC',
    'Aniak, AK: Aniak Airport': 'ANI',
    'Appleton, WI: Appleton International': 'ATW',
    'Arcata/Eureka, CA: California Redwood Coast Humboldt County': 'ACV',
    'Asheville, NC: Asheville Regional': 'AVL',
    'Ashland, WV: Tri-State/Milton J. Ferguson Field': 'HTS',
    'Aspen, CO: Aspen Pitkin County Sardy Field': 'ASE',
    'Atlanta, GA: Hartsfield-Jackson Atlanta International': 'ATL',
    'Atlantic City, NJ: Atlantic City International': 'ACY',
    'Augusta, GA: Augusta Regional at Bush Field': 'AGS',
    'Austin, TX: Austin - Bergstrom International': 'AUS',
    'Bakersfield, CA: Meadows Field': 'BFL',
    'Baltimore, MD: Baltimore/Washington International Thurgood Marshall': 'BWI',
    'Bangor, ME: Bangor International': 'BGR',
    'Barrow, AK: Wiley Post/Will Rogers Memorial': 'BRW',
    'Baton Rouge, LA: Baton Rouge Metropolitan/Ryan Field': 'BTR',
    'Beaumont/Port Arthur, TX: Jack Brooks Regional': 'BPT',
    'Bellingham, WA: Bellingham International': 'BLI',
    'Bemidji, MN: Bemidji Regional': 'BJI',
    'Bend/Redmond, OR: Roberts Field': 'RDM',
    'Bethel, AK: Bethel Airport': 'BET',
    'Billings, MT: Billings Logan International': 'BIL',
    'Binghamton, NY: Greater Binghamton/Edwin A. Link Field': 'BGM',
    'Birmingham, AL: Birmingham-Shuttlesworth International': 'BHM',
    'Bismarck/Mandan, ND: Bismarck Municipal': 'BIS',
    'Bloomington/Normal, IL: Central Illinois Regional': 'BMI',
    'Boise, ID: Boise Air Terminal': 'BOI',
    'Boston, MA: Logan International': 'BOS',
    'Bozeman, MT: Bozeman Yellowstone International': 'BZN',
    'Bristol/Johnson City/Kingsport, TN: Tri Cities': 'TRI',
    'Brownsville, TX: Brownsville South Padre Island International': 'BRO',
    'Brunswick, GA: Brunswick Golden Isles': 'BQK',
    'Buffalo, NY: Buffalo Niagara International': 'BUF',
    'Burbank, CA: Bob Hope': 'BUR',
    'Burlington, VT: Burlington International': 'BTV',
    'Butte, MT: Bert Mooney': 'BTM',
    'Carlsbad, CA: McClellan-Palomar': 'CLD',
    'Casper, WY: Casper/Natrona County International': 'CPR',
    'Cedar City, UT: Cedar City Regional': 'CDC',
    'Cedar Rapids/Iowa City, IA: The Eastern Iowa': 'CID',
    'Champaign/Urbana, IL: University of Illinois/Willard': 'CMI',
    'Charleston, SC: Charleston AFB/International': 'CHS',
    'Charleston/Dunbar, WV: Yeager': 'CRW',
    'Charlotte Amalie, VI: Cyril E King': 'STT',
    'Charlotte, NC: Charlotte Douglas International': 'CLT',
    'Charlottesville, VA: Charlottesville Albemarle': 'CHO',
    'Chattanooga, TN: Lovell Field': 'CHA',
    'Chicago, IL: Chicago Midway International': 'MDW',
    "Chicago, IL: Chicago O'Hare International": 'ORD',
    'Chico, CA: Chico Municipal': 'CIC',
    'Christiansted, VI: Henry E. Rohlsen': 'STX',
    'Cincinnati, OH: Cincinnati/Northern Kentucky International': 'CVG',
    'Cleveland, OH: Cleveland-Hopkins International': 'CLE',
    'Cody, WY: Yellowstone Regional': 'COD',
    'College Station/Bryan, TX: Easterwood Field': 'CLL',
    'Colorado Springs, CO: City of Colorado Springs Municipal': 'COS',
    'Columbia, SC: Columbia Metropolitan': 'CAE',
    'Columbus, GA: Columbus Airport': 'CSG',
    'Columbus, MS: Golden Triangle Regional': 'GTR',
    'Columbus, OH: John Glenn Columbus International': 'CMH',
    'Cordova, AK: Merle K Mudhole Smith': 'CDV',
    'Corpus Christi, TX: Corpus Christi International': 'CRP',
    'Crescent City, CA: Jack McNamara Field': 'CEC',
    'Dallas, TX: Dallas Love Field': 'DAL',
    'Dallas/Fort Worth, TX: Dallas/Fort Worth International': 'DFW',
    'Dayton, OH: James M Cox/Dayton International': 'DAY',
    'Daytona Beach, FL: Daytona Beach International': 'DAB',
    'Deadhorse, AK: Deadhorse Airport': 'SCC',
    'Denver, CO: Denver International': 'DEN',
    'Des Moines, IA: Des Moines International': 'DSM',
    'Detroit, MI: Detroit Metro Wayne County': 'DTW',
    'Dillingham, AK: Dillingham Airport': 'DLG',
    'Dothan, AL: Dothan Regional': 'DHN',
    'Dubuque, IA: Dubuque Regional': 'DBQ',
    'Duluth, MN: Duluth International': 'DLH',
    'Durango, CO: Durango La Plata County': 'DRO',
    'Eagle, CO: Eagle County Regional': 'EGE',
    'Eau Claire, WI: Chippewa Valley Regional': 'EAU',
    'El Centro, CA: Imperial County': 'IPL',
    'El Paso, TX: El Paso International': 'ELP',
    'Elko, NV: Elko Regional': 'EKO',
    'Elmira/Corning, NY: Elmira/Corning Regional': 'ELM',
    'Erie, PA: Erie International/Tom Ridge Field': 'ERI',
    'Eugene, OR: Mahlon Sweet Field': 'EUG',
    'Evansville, IN: Evansville Regional': 'EVV',
    'Fairbanks, AK: Fairbanks International': 'FAI',
    'Fargo, ND: Hector International': 'FAR',
    'Fayetteville, AR: Northwest Arkansas Regional': 'XNA',
    'Fayetteville, NC: Fayetteville Regional/Grannis Field': 'FAY',
    'Flagstaff, AZ: Flagstaff Pulliam': 'FLG',
    'Flint, MI: Bishop International': 'FNT',
    'Florence, SC: Florence Regional': 'FLO',
    'Fort Lauderdale, FL: Fort Lauderdale-Hollywood International': 'FLL',
    'Fort Myers, FL: Southwest Florida International': 'RSW',
    'Fort Smith, AR: Fort Smith Regional': 'FSM',
    'Fort Wayne, IN: Fort Wayne International': 'FWA',
    'Fresno, CA: Fresno Yosemite International': 'FAT',
    'Gainesville, FL: Gainesville Regional': 'GNV',
    'Gillette, WY: Gillette Campbell County': 'GCC',
    'Grand Forks, ND: Grand Forks International': 'GFK',
    'Grand Junction, CO: Grand Junction Regional': 'GJT',
    'Grand Rapids, MI: Gerald R. Ford International': 'GRR',
    'Great Falls, MT: Great Falls International': 'GTF',
    'Green Bay, WI: Green Bay Austin Straubel International': 'GRB',
    'Greensboro/High Point, NC: Piedmont Triad International': 'GSO',
    'Greer, SC: Greenville-Spartanburg International': 'GSP',
    'Gulfport/Biloxi, MS: Gulfport-Biloxi International': 'GPT',
    'Gunnison, CO: Gunnison-Crested Butte Regional': 'GUC',
    'Gustavus, AK: Gustavus Airport': 'GST',
    'Hancock/Houghton, MI: Houghton County Memorial': 'CMX',
    'Harlingen/San Benito, TX: Valley International': 'HRL',
    'Harrisburg, PA: Harrisburg International': 'MDT',
    'Hartford, CT: Bradley International': 'BDL',
    'Hayden, CO: Yampa Valley': 'HDN',
    'Helena, MT: Helena Regional': 'HLN',
    'Hickory, NC: Hickory Regional': 'HKY',
    'Hilo, HI: Hilo International': 'ITO',
    'Hilton Head, SC: Hilton Head Airport': 'HHH',
    'Honolulu, HI: Daniel K Inouye International': 'HNL',
    'Hoolehua, HI: Molokai': 'MKK',
    'Houston, TX: Ellington': 'EFD',
    'Houston, TX: George Bush Intercontinental/Houston': 'IAH',
    'Houston, TX: William P Hobby': 'HOU',
    'Huntsville, AL: Huntsville International-Carl T Jones Field': 'HSV',
    'Idaho Falls, ID: Idaho Falls Regional': 'IDA',
    'Indianapolis, IN: Indianapolis International': 'IND',
    'International Falls, MN: Falls International Einarson Field': 'INL',
    'Inyokern, CA: Inyokern Airport': 'IYK',
    'Islip, NY: Long Island MacArthur': 'ISP',
    'Ithaca/Cortland, NY: Ithaca Tompkins Regional': 'ITH',
    'Jackson, WY: Jackson Hole': 'JAC',
    'Jackson/Vicksburg, MS: Jackson Medgar Wiley Evers International': 'JAN',
    'Jacksonville, FL: Jacksonville International': 'JAX',
    'Jacksonville/Camp Lejeune, NC: Albert J Ellis': 'OAJ',
    'Juneau, AK: Juneau International': 'JNU',
    'Kahului, HI: Kahului Airport': 'OGG',
    'Kalamazoo, MI: Kalamazoo/Battle Creek International': 'AZO',
    'Kalispell, MT: Glacier Park International': 'FCA',
    'Kansas City, MO: Kansas City International': 'MCI',
    'Ketchikan, AK: Ketchikan International': 'KTN',
    'Key West, FL: Key West International': 'EYW',
    'Killeen, TX: Robert Gray AAF': 'GRK',
    'Killeen, TX: Skylark Field': 'ILE',
    'King Salmon, AK: King Salmon Airport': 'AKN',
    'Kinston, NC: Kinston Regional Jetport at Stallings Field': 'ISO',
    'Klamath Falls, OR: Crater Lake Klamath Regional': 'LMT',
    'Knoxville, TN: McGhee Tyson': 'TYS',
    'Kodiak, AK: Kodiak Airport': 'ADQ',
    'Kona, HI: Ellison Onizuka Kona International at Keahole': 'KOA',
    'Kotzebue, AK: Ralph Wien Memorial': 'OTZ',
    'La Crosse, WI: La Crosse Regional': 'LSE',
    'Lafayette, LA: Lafayette Regional Paul Fournet Field': 'LFT',
    'Lake Charles, LA: Lake Charles Regional': 'LCH',
    'Lanai, HI: Lanai Airport': 'LNY',
    'Lansing, MI: Capital Region International': 'LAN',
    'Laredo, TX: Laredo International': 'LRD',
    'Las Vegas, NV: McCarran International': 'LAS',
    'Lawton/Fort Sill, OK: Lawton-Fort Sill Regional': 'LAW',
    'Lewisburg, WV: Greenbrier Valley': 'LWB',
    'Lewiston, ID: Lewiston Nez Perce County': 'LWS',
    'Lexington, KY: Blue Grass': 'LEX',
    'Lihue, HI: Lihue Airport': 'LIH',
    'Lincoln, NE: Lincoln Airport': 'LNK',
    'Little Rock, AR: Bill and Hillary Clinton Nat Adams Field': 'LIT',
    'Long Beach, CA: Long Beach Airport': 'LGB',
    'Longview, TX: East Texas Regional': 'GGG',
    'Los Angeles, CA: Los Angeles International': 'LAX',
    'Louisville, KY: Louisville International-Standiford Field': 'SDF',
    'Lubbock, TX: Lubbock Preston Smith International': 'LBB',
    'Lynchburg, VA: Lynchburg Regional/Preston Glenn Field': 'LYH',
    'Macon, GA: Middle Georgia Regional': 'MCN',
    'Madison, WI: Dane County Regional-Truax Field': 'MSN',
    'Manchester, NH: Manchester-Boston Regional': 'MHT',
    'Marathon, FL: The Florida Keys Marathon International': 'MTH',
    'Marquette, MI: Sawyer International': 'MQT',
    'Mayaguez, PR: Eugenio Maria de Hostos': 'MAZ',
    'Medford, OR: Rogue Valley International - Medford': 'MFR',
    'Melbourne, FL: Melbourne International': 'MLB',
    'Memphis, TN: Memphis International': 'MEM',
    'Meridian, MS: Key Field': 'MEI',
    'Miami, FL: Miami International': 'MIA',
    'Midland/Odessa, TX: Midland International Air and Space Port': 'MAF',
    'Milwaukee, WI: General Mitchell International': 'MKE',
    'Minneapolis, MN: Minneapolis-St Paul International': 'MSP',
    'Minot, ND: Minot AFB': 'MIB',
    'Minot, ND: Minot International': 'MOT',
    'Mission/McAllen/Edinburg, TX: McAllen Miller International': 'MFE',
    'Missoula, MT: Missoula International': 'MSO',
    'Mobile, AL: Mobile Regional': 'MOB',
    'Modesto, CA: Modesto City-County-Harry Sham Field': 'MOD',
    'Moline, IL: Quad City International': 'MLI',
    'Monroe, LA: Monroe Regional': 'MLU',
    'Monterey, CA: Monterey Regional': 'MRY',
    'Montgomery, AL: Montgomery Regional': 'MGM',
    'Montrose/Delta, CO: Montrose Regional': 'MTJ',
    'Mosinee, WI: Central Wisconsin': 'CWA',
    'Muskegon, MI: Muskegon County': 'MKG',
    'Myrtle Beach, SC: Myrtle Beach International': 'MYR',
    'Nantucket, MA: Nantucket Memorial': 'ACK',
    'Naples, FL: Naples Municipal': 'APF',
    'Nashville, TN: Nashville International': 'BNA',
    'New Bern/Morehead/Beaufort, NC: Coastal Carolina Regional': 'EWN',
    'New Haven, CT: Tweed New Haven': 'HVN',
    'New Orleans, LA: Louis Armstrong New Orleans International': 'MSY',
    'New York, NY: John F. Kennedy International': 'JFK',
    'New York, NY: LaGuardia': 'LGA',
    'Newark, NJ: Newark Liberty International': 'EWR',
    'Newburgh/Poughkeepsie, NY: Stewart International': 'SWF',
    'Newport News/Williamsburg, VA: Newport News/Williamsburg International': 'PHF',
    'Nome, AK: Nome Airport': 'OME',
    'Norfolk, VA: Norfolk International': 'ORF',
    'North Bend/Coos Bay, OR: Southwest Oregon Regional': 'OTH',
    'Oakland, CA: Metropolitan Oakland International': 'OAK',
    'Oklahoma City, OK: Will Rogers World': 'OKC',
    'Omaha, NE: Eppley Airfield': 'OMA',
    'Ontario, CA: Ontario International': 'ONT',
    'Orlando, FL: Orlando International': 'MCO',
    'Oxnard/Ventura, CA: Oxnard': 'OXR',
    'Palm Springs, CA: Palm Springs International': 'PSP',
    'Palmdale, CA: Palmdale USAF Plant 42': 'PMD',
    'Panama City, FL: Bay County': 'PFN',
    'Pasco/Kennewick/Richland, WA: Tri Cities': 'PSC',
    'Pellston, MI: Pellston Regional Airport of Emmet County': 'PLN',
    'Pensacola, FL: Pensacola International': 'PNS',
    'Peoria, IL: General Downing - Peoria International': 'PIA',
    'Petersburg, AK: Petersburg James A Johnson': 'PSG',
    'Philadelphia, PA: Philadelphia International': 'PHL',
    'Phoenix, AZ: Phoenix Sky Harbor International': 'PHX',
    'Pierre, SD: Pierre Regional': 'PIR',
    'Pinehurst/Southern Pines, NC: Moore County': 'SOP',
    'Pittsburgh, PA: Pittsburgh International': 'PIT',
    'Pocatello, ID: Pocatello Regional': 'PIH',
    'Ponce, PR: Mercedita': 'PSE',
    'Portland, ME: Portland International Jetport': 'PWM',
    'Portland, OR: Portland International': 'PDX',
    'Providence, RI: Theodore Francis Green State': 'PVD',
    'Provo, UT: Provo Municipal': 'PVU',
    'Pueblo, CO: Pueblo Memorial': 'PUB',
    'Raleigh/Durham, NC: Raleigh-Durham International': 'RDU',
    'Rapid City, SD: Rapid City Regional': 'RAP',
    'Red River, ND: Grand Forks AFB': 'RDR',
    'Redding, CA: Redding Municipal': 'RDD',
    'Reno, NV: Reno/Tahoe International': 'RNO',
    'Rhinelander, WI: Rhinelander/Oneida County': 'RHI',
    'Richmond, VA: Richmond International': 'RIC',
    'Roanoke, VA: Roanoke Blacksburg Regional Woodrum Field': 'ROA',
    'Rochester, MN: Rochester International': 'RST',
    'Rochester, NY: Greater Rochester International': 'ROC',
    'Rock Springs, WY: Rock Springs Sweetwater County': 'RKS',
    'Rockford, IL: Chicago/Rockford International': 'RFD',
    'Roswell, NM: Roswell International Air Center': 'ROW',
    'Sacramento, CA: Sacramento International': 'SMF',
    'Saginaw/Bay City/Midland, MI: MBS International': 'MBS',
    'Saipan, TT: Francisco C. Ada Saipan International': 'SPN',
    'Salem, OR: McNary Field': 'SLE',
    'Salt Lake City, UT: Salt Lake City International': 'SLC',
    'San Angelo, TX: San Angelo Regional/Mathis Field': 'SJT',
    'San Antonio, TX: San Antonio International': 'SAT',
    'San Diego, CA: San Diego International': 'SAN',
    'San Francisco, CA: San Francisco International': 'SFO',
    'San Jose, CA: Norman Y. Mineta San Jose International': 'SJC',
    'San Juan, PR: Luis Munoz Marin International': 'SJU',
    'San Luis Obispo, CA: San Luis County Regional': 'SBP',
    'Santa Ana, CA: John Wayne Airport-Orange County': 'SNA',
    'Santa Barbara, CA: Santa Barbara Municipal': 'SBA',
    'Santa Maria, CA: Santa Maria Public/Capt. G. Allan Hancock Field': 'SMX',
    'Sarasota/Bradenton, FL: Sarasota/Bradenton International': 'SRQ',
    'Savannah, GA: Savannah/Hilton Head International': 'SAV',
    'Scranton/Wilkes-Barre, PA: Wilkes Barre Scranton International': 'AVP',
    'Seattle, WA: Seattle/Tacoma International': 'SEA',
    'Shreveport, LA: Shreveport Regional': 'SHV',
    'Sioux City, IA: Sioux Gateway/Col. Bud Day Field': 'SUX',
    'Sioux Falls, SD: Joe Foss Field': 'FSD',
    'Sitka, AK: Sitka Rocky Gutierrez': 'SIT',
    'South Bend, IN: South Bend International': 'SBN',
    'Spokane, WA: Spokane International': 'GEG',
    'Springfield, IL: Abraham Lincoln Capital': 'SPI',
    'Springfield, MO: Springfield-Branson National': 'SGF',
    'St. George, UT: St George Regional': 'SGU',
    'St. Louis, MO: St Louis Lambert International': 'STL',
    "St. Mary's, AK: St. Mary's Airport": 'KSM',
    'St. Petersburg, FL: St Pete Clearwater International': 'PIE',
    'State College, PA: University Park': 'SCE',
    'Sun Valley/Hailey/Ketchum, ID: Friedman Memorial': 'SUN',
    'Syracuse, NY: Syracuse Hancock International': 'SYR',
    'Tallahassee, FL: Tallahassee International': 'TLH',
    'Tampa, FL: Tampa International': 'TPA',
    'Telluride, CO: Telluride Regional': 'TEX',
    'Texarkana, AR: Texarkana Regional-Webb Field': 'TXK',
    'Toledo, OH: Toledo Express': 'TOL',
    'Traverse City, MI: Cherry Capital': 'TVC',
    'Trenton, NJ: Trenton Mercer': 'TTN',
    'Tucson, AZ: Tucson International': 'TUS',
    'Tulsa, OK: Tulsa International': 'TUL',
    'Tupelo, MS: Tupelo Regional': 'TUP',
    'Twin Falls, ID: Joslin Field - Magic Valley Regional': 'TWF',
    'Tyler, TX: Tyler Pounds Regional': 'TYR',
    'Unalaska, AK: Unalaska Airport': 'DUT',
    'Valdosta, GA: Valdosta Regional': 'VLD',
    'Valparaiso, FL: Eglin AFB Destin Fort Walton Beach': 'VPS',
    'Victoria, TX: Victoria Regional': 'VCT',
    'Visalia, CA: Visalia Municipal': 'VIS',
    'Waco, TX: Waco Regional': 'ACT',
    'Washington, DC: Ronald Reagan Washington National': 'DCA',
    'Washington, DC: Washington Dulles International': 'IAD',
    'Waterloo, IA: Waterloo Regional': 'ALO',
    'West Palm Beach/Palm Beach, FL: Palm Beach International': 'PBI',
    'West Yellowstone, MT: Yellowstone': 'WYS',
    'White Plains, NY: Westchester County': 'HPN',
    'Wichita Falls, TX: Sheppard AFB/Wichita Falls Municipal': 'SPS',
    'Wichita, KS: Wichita Dwight D Eisenhower National': 'ICT',
    'Wilmington, DE: New Castle': 'ILG',
    'Wilmington, NC: Wilmington International': 'ILM',
    'Worcester, MA: Worcester Regional': 'ORH',
    'Wrangell, AK: Wrangell Airport': 'WRG',
    'Yakima, WA: Yakima Air Terminal/McAllister Field': 'YKM',
    'Yakutat, AK: Yakutat Airport': 'YAK',
    'Yuma, AZ: Yuma MCAS/Yuma International': 'YUM'
};

// Set dropdown options and initialize each
populateSelect(carriers, "carrier");
$('#carrier').val('US')

populateSelect(airports, "origin");
$('#origin').val('DCA');

populateSelect(airports, "destination");
$('#destination').val('DFW');

populateSelect(weeks, "week");
$('#week').val('16');

populateSelect(departureHours, "departure");
$('#departure').val('12');


function populateSelect(option_dict, id) {

    var select = document.getElementById(id);
    var keys = Object.keys(option_dict)

    for (var i = 0; i < keys.length; i++) {
        var opt = keys[i];
        var el = document.createElement("option");
        el.classList.add("selectrow")
        el.textContent = opt;
        el.value = option_dict[opt];
        select.appendChild(el);
    };
}

// Get prediction from model API endpoint
function get_key() {
    fetch('/getkey')
        .then(
            function (response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                        response.status);
                    return;
                }

                // Examine the text in the response
                response.json().then(function (data) {
                    console.log("api key. is", data)
                    api_key = data.api_key

                });
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}
get_key()

var url = window.location.origin.substr(0, window.location.origin.indexOf(":") + 1) + "//" + "modelservice." + window.location.origin.substr(window.location.origin.indexOf(".") + 1) + '/model'

function go_fetch() {
    var post_data = {
        accessKey: api_key,
        request: {
            feature: d3.select('#carrier').property("value") + "," +
                d3.select('#origin').property("value") + "," +
                d3.select('#destination').property("value") + "," +
                d3.select('#week').property("value") + "," +
                d3.select('#departure').property("value")
        }
    };

    fetch(url, {
        method: 'POST', // or 'PUT'
        body: JSON.stringify(post_data), // data can be `string` or {object}!
        headers: {
            'Content-Type': 'application/json',
            //'Authorization' : 'Bearer ' + model_api_key
        }
    })
        .then(response => response.json())
        .then(data => d3.select("#pred_value").text("Predicted Value: " + (data.response.prediction.prediction == 0 ? "Not Canceled" : "Canceled")) &
            d3.select("#proba_value").text("Probability: " + (data.response.prediction.proba)))
        .catch(error => console.error('Error:', error));
}