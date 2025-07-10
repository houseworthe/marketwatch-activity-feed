const admin = require('firebase-admin');
const serviceAccount = require('./firebase-credentials.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://martketwatch-activity-feed-default-rtdb.firebaseio.com/'
});

const db = admin.database();

db.ref('/').once('value', (snapshot) => {
  const data = snapshot.val();
  console.log('Firebase data structure:', JSON.stringify(data, null, 2).substring(0, 500));
  
  if (data && data.latest_data) {
    console.log('\nFound latest_data with', data.latest_data.competitors ? data.latest_data.competitors.length : 0, 'competitors');
  } else {
    console.log('\nNo latest_data found in Firebase');
  }
  
  process.exit(0);
});