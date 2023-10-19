var gplay = require('google-play-scraper');
var app_id = process.argv[2];

try {
  promise1 = gplay.similar({appId: app_id, country: 'in', lang: 'en', fullDetail: true});
} catch {
  console.log("None")
  return
}

promise1.then((value) => {
  console.log(JSON.stringify(value));
});


