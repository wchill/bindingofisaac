importScripts(`crafting.js`);

function combRep(arr, l) {
  if(l === void 0) l = arr.length; // Length of the combinations
  var data = Array(l),             // Used to store state
      results = [];                // Array of results
  (function f(pos, start) {        // Recursive function
    if(pos === l) {                // End reached
      results.push(data.slice());  // Add a copy of data to results
      return;
    }
    for(var i=start; i<arr.length; ++i) {
      data[pos] = arr[i];          // Update data
      f(pos+1, i);                 // Call f recursively
    }
  })(0, 0);                        // Start at index 0
  return results;                  // Return results
}

self.addEventListener('message', async function (MessageEvent) {
  //let itemId = get_result(MessageEvent.data.charArr, str2seed(MessageEvent.data.seed))

  let t0 = this.performance.now();

  // let quality1 = [1, 7, 8]
  // let quality2 = [12, 15, 18, 21, 22, 25]
  // let quality3 = [9]
  // let quality4 = [2, 19, 23, 24]

  let result = combRep(MessageEvent.data.components, 8)
  console.log(`permutations: ${result.length}`);
  const seed = str2seed(MessageEvent.data.seed)

  var i = 0, len = result.length;
  var recipeArr = [];

  // do the magic
  while (i < len) {
    let id = await get_result(result[i], seed);
    let itemIndex = recipeArr.findIndex(e => e.x === id);

    if (itemIndex > -1) {
      if (recipeArr[itemIndex].y.length < 20) recipeArr[itemIndex].y.push(result[i]);
    } else {
      recipeArr.push({
        x: id,
        y: [
          result[i]
        ],
      })
    }


    i++
  }

  let t1 = this.performance.now();

  self.postMessage({
    result: recipeArr,
    total: result.length,
    time: t1 - t0,
  })



}, false);
