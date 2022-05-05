"use strict"

//disassembly from Game

function str2seed(seed) {
    if (seed.length != 9)
        return 0
    //"xxxx xxxx"
    if (seed[4] != ' ') {
        return 0
    }

    let dict = []
    for (let i = 0; i < 255; i++) {
        dict[i] = 0xFF
    }
    for (let i = 0; i < 32; i++) {
        dict["ABCDEFGHJKLMNPQRSTWXYZ01234V6789".charCodeAt(i)] = i
    }

    let num_seed = []
    for (let i = 0; i < 9; i++) {
        if (i == 4)
            continue
        let j = i
        if (i > 4) {
            j = i - 1
        }
        num_seed[j] = dict[seed.charCodeAt(i)]
        if (num_seed[j] == 0xFF)
            return 0
    }

    let v8 = 0;
    let v10

    //num_seed[x] j is unsigned int8
    for (let j = ((num_seed[6] >>> 3) | (4
        * (num_seed[5] | (32
            * (num_seed[4] | (32
                * (num_seed[3] | (32
                    * (num_seed[2] | (32 * (num_seed[1] | (32 * num_seed[0])))))))))))) ^ 0xFEF7FFD;
         j != 0;
         v8 = ((v10 >>> 7) + 2 * v10) & 0xFF) {
        v10 = ((j & 0xFF) + v8) & 0xFF;
        j >>>= 5;
    }
    if (v8 == (num_seed[7] | (0xFF & (32 * num_seed[6])))) {
        return ((num_seed[6] >> 3) | (4
            * (num_seed[5] | (32
                * (num_seed[4] | (32
                    * (num_seed[3] | (32
                        * (num_seed[2] | (32 * (num_seed[1] | (32 * num_seed[0])))))))))))) ^ 0xFEF7FFD;
    }
    return 0
}


function bucket_sort_list_toint64(item_array) {
    //å¯¹item_arrayè¿›è¡Œæ¡¶æŽ’åº
    console.assert(item_array.length == 8)

    let item_count = []

    //initial value
    for (let i = 0; i < 0x1F; i++) {
        item_count[i] = 0
    }

    item_count[item_array[0]]++
    item_count[item_array[1]]++
    item_count[item_array[2]]++
    item_count[item_array[3]]++
    item_count[item_array[4]]++
    item_count[item_array[5]]++
    item_count[item_array[6]]++
    item_count[item_array[7]]++

    let offset = 0n


    let v12 = 0n // v12 is 64 bit
    for (let i = 0n; i < 0x1Fn; i++) {
        for (let j = 0; j < item_count[i]; j++) {
            //æ­¤ä»£ç ä¸€å®šä¼šæ‰§è¡Œ8é
            v12 |= i << offset
            offset += 8n
        }
    }
    //v12 = 0x08 07 06 05 04 03 02 01
    return v12
}

console.assert(bucket_sort_list_toint64([0x16, 0x2, 0x16, 0x16, 0x16, 0x16, 0x16, 0x16]) == 0x1616161616161602n)


//========== test a combine ===========

let rng_offsets = [
    0x00000001, 0x00000005, 0x00000010, 0x00000001, 0x00000005, 0x00000013, 0x00000001, 0x00000009,
    0x0000001D, 0x00000001, 0x0000000B, 0x00000006, 0x00000001, 0x0000000B, 0x00000010, 0x00000001,
    0x00000013, 0x00000003, 0x00000001, 0x00000015, 0x00000014, 0x00000001, 0x0000001B, 0x0000001B,
    0x00000002, 0x00000005, 0x0000000F, 0x00000002, 0x00000005, 0x00000015, 0x00000002, 0x00000007,
    0x00000007, 0x00000002, 0x00000007, 0x00000009, 0x00000002, 0x00000007, 0x00000019, 0x00000002,
    0x00000009, 0x0000000F, 0x00000002, 0x0000000F, 0x00000011, 0x00000002, 0x0000000F, 0x00000019,
    0x00000002, 0x00000015, 0x00000009, 0x00000003, 0x00000001, 0x0000000E, 0x00000003, 0x00000003,
    0x0000001A, 0x00000003, 0x00000003, 0x0000001C, 0x00000003, 0x00000003, 0x0000001D, 0x00000003,
    0x00000005, 0x00000014, 0x00000003, 0x00000005, 0x00000016, 0x00000003, 0x00000005, 0x00000019,
    0x00000003, 0x00000007, 0x0000001D, 0x00000003, 0x0000000D, 0x00000007, 0x00000003, 0x00000017,
    0x00000019, 0x00000003, 0x00000019, 0x00000018, 0x00000003, 0x0000001B, 0x0000000B, 0x00000004,
    0x00000003, 0x00000011, 0x00000004, 0x00000003, 0x0000001B, 0x00000004, 0x00000005, 0x0000000F,
    0x00000005, 0x00000003, 0x00000015, 0x00000005, 0x00000007, 0x00000016, 0x00000005, 0x00000009,
    0x00000007, 0x00000005, 0x00000009, 0x0000001C, 0x00000005, 0x00000009, 0x0000001F, 0x00000005,
    0x0000000D, 0x00000006, 0x00000005, 0x0000000F, 0x00000011, 0x00000005, 0x00000011, 0x0000000D,
    0x00000005, 0x00000015, 0x0000000C, 0x00000005, 0x0000001B, 0x00000008, 0x00000005, 0x0000001B,
    0x00000015, 0x00000005, 0x0000001B, 0x00000019, 0x00000005, 0x0000001B, 0x0000001C, 0x00000006,
    0x00000001, 0x0000000B, 0x00000006, 0x00000003, 0x00000011, 0x00000006, 0x00000011, 0x00000009,
    0x00000006, 0x00000015, 0x00000007, 0x00000006, 0x00000015, 0x0000000D, 0x00000007, 0x00000001,
    0x00000009, 0x00000007, 0x00000001, 0x00000012, 0x00000007, 0x00000001, 0x00000019, 0x00000007,
    0x0000000D, 0x00000019, 0x00000007, 0x00000011, 0x00000015, 0x00000007, 0x00000019, 0x0000000C,
    0x00000007, 0x00000019, 0x00000014, 0x00000008, 0x00000007, 0x00000017, 0x00000008, 0x00000009,
    0x00000017, 0x00000009, 0x00000005, 0x0000000E, 0x00000009, 0x00000005, 0x00000019, 0x00000009,
    0x0000000B, 0x00000013, 0x00000009, 0x00000015, 0x00000010, 0x0000000A, 0x00000009, 0x00000015,
    0x0000000A, 0x00000009, 0x00000019, 0x0000000B, 0x00000007, 0x0000000C, 0x0000000B, 0x00000007,
    0x00000010, 0x0000000B, 0x00000011, 0x0000000D, 0x0000000B, 0x00000015, 0x0000000D, 0x0000000C,
    0x00000009, 0x00000017, 0x0000000D, 0x00000003, 0x00000011, 0x0000000D, 0x00000003, 0x0000001B,
    0x0000000D, 0x00000005, 0x00000013, 0x0000000D, 0x00000011, 0x0000000F, 0x0000000E, 0x00000001,
    0x0000000F, 0x0000000E, 0x0000000D, 0x0000000F, 0x0000000F, 0x00000001, 0x0000001D, 0x00000011,
    0x0000000F, 0x00000014, 0x00000011, 0x0000000F, 0x00000017, 0x00000011, 0x0000000F, 0x0000001A]

function RNG_Next(num, offset_id) {
    let offset_a = rng_offsets[offset_id * 3]
    let offset_b = rng_offsets[offset_id * 3 + 1]
    let offset_c = rng_offsets[offset_id * 3 + 2]
    num = num ^ ((num >>> offset_a) & 0xFFFFFFFF)
    num = num ^ ((num << offset_b) & 0xFFFFFFFF)
    num = num ^ ((num >>> offset_c) & 0xFFFFFFFF)
    return num >>> 0 /* to unsigned */
}
let _item_data = {}
let _version_data = undefined;


async function GetItemData() {
    let version_data = await GetVersionData();
    let default_version = "#" + version_data.default;

    let version = (location.hash || default_version).substr(1);
    if (_item_data[version] === undefined) {
        console.log(`Fetching game data for ${version}`);
        let versioned_data = await fetch(`gamedata/${version}/data.json`);
        _item_data[version] = await versioned_data.json();
    }
    return _item_data[version];
}


async function GetVersionData() {
    if (_version_data === undefined) {
        console.log(`Fetching version data`);
        let versioned_data = await fetch(`gamedata/versions.json`);
        _version_data = await versioned_data.json();
    }
    return _version_data;
}


function GetCalculatorVersion(version_data) {
    let default_version = "#" + version_data.default;
    let version_str = (location.hash || default_version).substr(1);
    let version_components = version_str.split("/");
    let platform = version_components[0];
    let version = version_components[1];

    return version_data["platforms"][platform]["versions"][version];
}


function GetItemPoolData(itemdata, item_pool_id) {
    let item_pool_data = itemdata.itempools;

    console.assert(item_pool_data["items"][item_pool_id] !== undefined)
    return item_pool_data["items"][item_pool_id]
}

function GetItemConfig(itemdata, item_id) {
    let item_config_data = itemdata.metadata;

    console.assert(item_config_data[item_id] !== undefined)
    return item_config_data[item_id]
}

function GetHardcodedRecipe(itemdata, pickup_int) {
    let recipe_data = itemdata.recipes;
    return recipe_data[pickup_int]
}

function GetAchievementUnlocked(achievement_id) {
    if (achievement_id >= 0x27E)
        return false
    if (achievement_id === 0)
        return true

    return true
}

function GetMinMaxQualityOld(score) {
    // repentance.nro 1.5, 1.6
    let quality_max, quality_min;
    if (score > 34) {
        quality_max = 4;
        quality_min = 4;
    } else if (score > 30) {
        quality_max = 4;
        quality_min = 3;
    } else if (score > 26) {
        quality_max = 4;
        quality_min = 2;
    } else if (score > 22) {
        quality_max = 4;
        quality_min = 1;
    } else if (score > 18) {
        quality_max = 3;
        quality_min = 1;
    } else if (score > 14) {
        quality_max = 2;
        quality_min = 1;
    } else if (score > 8) {
        quality_max = 2;
        quality_min = 0;
    } else {
        quality_max = 1;
        quality_min = 0;
    }
    return {min: quality_min, max: quality_max}
}

function GetMinMaxQualityNew(score) {
    // isaac-ng.exe 1.7.7a, Repentance.nro 1.7
    let quality_max, quality_min;
    if (score > 34) {
        quality_max = 4;
        quality_min = 4;
    } else if (score > 30) {
        quality_max = 4;
        quality_min = 3;
    } else if (score > 26) {
        quality_max = 4;
        quality_min = 3;
    } else if (score > 22) {
        quality_max = 4;
        quality_min = 2;
    } else if (score > 18) {
        quality_max = 3;
        quality_min = 2;
    } else if (score > 14) {
        quality_max = 2;
        quality_min = 1;
    } else if (score > 8) {
        quality_max = 2;
        quality_min = 0;
    } else {
        quality_max = 1;
        quality_min = 0;
    }
    return {min: quality_min, max: quality_max}
}

function GetMinMaxQualityImpl(calculator_version) {
    if (calculator_version === 1) {
        return GetMinMaxQualityOld;
    }
    return GetMinMaxQualityNew;
}

function IsItemUnlocked(itemdata, item_id) {
    let item_config = GetItemConfig(itemdata, item_id);
    return (item_config.achievement_id === undefined || GetAchievementUnlocked(item_config["achievement_id"]));
}

function ShouldUseHardcodedRecipe(calculator_version, itemdata, item_id) {
    if (item_id === undefined) return false;
    if (calculator_version < 3) return true;
    return IsItemUnlocked(itemdata, item_id);
}

async function get_result(input_array, currentSeed) {
    let itemdata = await GetItemData();
    let versiondata = await GetVersionData();
    let calculatorVersion = GetCalculatorVersion(versiondata);

    let sorted_items = bucket_sort_list_toint64(input_array);
    let hardcoded_recipe_id = GetHardcodedRecipe(itemdata, sorted_items);

    if (ShouldUseHardcodedRecipe(calculatorVersion, itemdata, hardcoded_recipe_id)) {
        return hardcoded_recipe_id
    }

    let getMinMaxQuality = GetMinMaxQualityImpl(calculatorVersion);

    let item_count = [];
    for (let i = 0; i < 0x1F; i++) {
        item_count[i] = 0
    }
    item_count[input_array[0]]++
    item_count[input_array[1]]++
    item_count[input_array[2]]++
    item_count[input_array[3]]++
    item_count[input_array[4]]++
    item_count[input_array[5]]++
    item_count[input_array[6]]++
    item_count[input_array[7]]++

    let score_matrix = [
        0x00000000, 0x00000001, 0x00000004, 0x00000005, 0x00000005, 0x00000005, 0x00000005,
        0x00000001, 0x00000001, 0x00000003, 0x00000005, 0x00000008, 0x00000002, 0x00000007,
        0x00000005, 0x00000002, 0x00000007, 0x0000000A, 0x00000002, 0x00000004, 0x00000008,
        0x00000002, 0x00000002, 0x00000004, 0x00000004, 0x00000002, 0x00000007, 0x00000007,
        0x00000007, 0x00000000, 0x00000001]

    let item_score_sum =
        score_matrix[input_array[0]] +
        score_matrix[input_array[1]] +
        score_matrix[input_array[2]] +
        score_matrix[input_array[3]] +
        score_matrix[input_array[4]] +
        score_matrix[input_array[5]] +
        score_matrix[input_array[6]] +
        score_matrix[input_array[7]]

    // console.log("item score sum = " + item_score_sum)
    let weight_list = [
        {id: 0, weight: 1.0},
        {id: 1, weight: 2.0},
        {id: 2, weight: 2.0},
        {id: 3, weight: item_count[3] * 10.0},
        {id: 4, weight: item_count[4] * 10.0},
        {id: 5, weight: item_count[6] * 5.0},
        {id: 7, weight: item_count[29] * 10.0},
        {id: 8, weight: item_count[5] * 10.0},
        {id: 9, weight: item_count[25] * 10.0},
        {id: 12, weight: item_count[7] * 10.0},
    ]
    if (item_count[15] + item_count[12] + item_count[8] + item_count[1] === 0) {
        weight_list.push(
            {id: 26, weight: item_count[23] * 10.0}
        )
    }
    if (currentSeed === 0) {
        throw "Invalid seed"
    }

    for (let item_i = 0; item_i < 0x1F; item_i++) {
        for (let j = 0; j < item_count[item_i]; j++) {
            currentSeed = RNG_Next(currentSeed, item_i)
        }
    }
    // console.log(currentSeed)
    let collectible_count = 733 // it equals to some_variable_a - some_variable_b

    let collectible_list = []
    for (let i = 0; i < collectible_count; i++) {
        collectible_list[i] = 0.0
    }

    let all_weight = 0.0
    // console.log(weight_list)
    if (weight_list.length > 0) {
        for (let weight_select_i = 0; weight_select_i < weight_list.length; weight_select_i++) {
            if (weight_list[weight_select_i].weight <= 0.0) {
                continue
            }
            let score = item_score_sum
            if (weight_list[weight_select_i].id == 4 || weight_list[weight_select_i].id == 3 || weight_list[weight_select_i].id == 5) {
                score -= 5
            }

            let quality_bounds = getMinMaxQuality(score);
            let quality_min = quality_bounds.min;
            let quality_max = quality_bounds.max;

            let item_pools = GetItemPoolData(itemdata, weight_list[weight_select_i].id)
            for (let item_pool_i = 0; item_pool_i < item_pools.length; item_pool_i++) {
                // if(some_address == 0){//v53, dword_1779AEC
                //     //not handled
                //     //i dont know
                // }
                let item_config = undefined
                if (item_pools[item_pool_i].id >= 0) {
                    if (item_pools[item_pool_i].id >= collectible_count) {
                        item_config = undefined
                    } else {
                        item_config = GetItemConfig(itemdata, item_pools[item_pool_i].id)
                    }
                    //goto label 86
                } else {
                    //what's wrong with item ID?
                    //i dont know if it is right...
                    console.assert(false, "Unknown condition")
                    let tempid = ~item_pools[item_pool_i].id
                    if (tempid < 0 || tempid > collectible_count /* it is not collectible_count, i dont know what it is */) {
                        item_config = undefined
                    } else {
                        item_config = GetItemConfig(itemdata, tempid) /* it is not ItemConfig, i dont know what it is */
                    }
                }

                let item_quality = 0 + item_config.quality /* there is not a zero, but a var from item_config, which is always zero when i'm testing */
                if (item_quality >= quality_min && item_quality <= quality_max) {
                    //be careful:the game use float instead of double, so js in not accurate!!!
                    let item_weight = item_pools[item_pool_i].weight * weight_list[weight_select_i].weight
                    all_weight += item_weight
                    // console.log(all_weight)
                    collectible_list[item_pools[item_pool_i].id] += item_weight
                }
            }
        }
        //label 92
        //for break condition, nothing to do here
    }
    //all weight is not accurate
    // console.log("all weight = " + all_weight)

    // console.log("current seed = " + currentSeed)

    for (let retry_count = 0; retry_count < 20; retry_count++) {
        currentSeed = RNG_Next(currentSeed, 6)
        //use float instead!!!
        let remains = Number(currentSeed) * 2.3283062e-10 * all_weight
        let selected = 25;

        for (let current_select = 0; current_select < collectible_count; current_select++) {
            // console.log(collectible_list[current_select])
            if (collectible_list[current_select] > remains) {
                selected = current_select
                break
            }
            remains -= collectible_list[current_select]
        }

        if (IsItemUnlocked(itemdata, selected)) {
            return selected;
        }
    }
    return 25;
}
