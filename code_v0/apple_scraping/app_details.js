var store = require('app-store-scraper');
var app_id = process.argv[2];

// try {
//   promise1 = store.app({appId: app_id, country: 'in', lang: 'en', ratings: true});
// } catch {
//   console.log("None")
//   return
// }

// promise1.then((value) => {
//   console.log(JSON.stringify(value));
// });

store.app({ appId: app_id, country: 'in', lang: 'en', ratings: true })
  .then((value) => {
    console.log(JSON.stringify(value));
  })
  .catch((error) => {
    // console.log('Hello');
    console.log(JSON.stringify(error));
    // return error
  });
