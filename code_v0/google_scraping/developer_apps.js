var gplay = require('google-play-scraper');
var dev_id = process.argv[2];

try {
  promise1 = gplay.developer({devId: dev_id, country: 'in', lang: 'en', num: 200, fullDetail: true});
} catch {
  console.log("None")
  return
}

promise1.then((value) => {
  console.log(JSON.stringify(value));
});


