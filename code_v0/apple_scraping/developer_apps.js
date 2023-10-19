var store = require('app-store-scraper');
var dev_id = process.argv[2];

// try {
//   promise1 = store.developer({devId: dev_id, country: 'in', lang: 'en', num: 200, fullDetail: true});
// } catch {
//   console.log("None")
//   return
// }

// promise1.then((value) => {
//   console.log(JSON.stringify(value));
// });

store.developer({ devId: dev_id, country: 'in', lang: 'en', num: 200, fullDetail: true})
  .then((value) => {
    console.log(JSON.stringify(value));
  })
  .catch((error) => {
    // console.log('Hello');
    console.log(JSON.stringify(error));
    // return error
  });
