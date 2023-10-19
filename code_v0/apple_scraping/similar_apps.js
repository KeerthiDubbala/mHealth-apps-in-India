var store = require('app-store-scraper');
var app_id = process.argv[2];

// try {
//   promise1 = store.similar({appId: app_id, country: 'in', lang: 'en', fullDetail: true});
// } catch {
//   console.log("None")
//   return
// }

// promise1.then((value) => {
//   console.log(JSON.stringify(value));
// });

store.similar({ appId: app_id, country: 'in', lang: 'en', fullDetail: true })
  .then((value) => {
    console.log(JSON.stringify(value));
  })
  .catch((error) => {
    // console.log('Hello');
    console.log(JSON.stringify(error));
    // return error
  });

