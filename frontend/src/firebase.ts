import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue } from 'firebase/database';
import { CompetitionData } from './types';

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDKUP0sLXoNzRW3VnzKFcJ_pClqn0UmRlg",
  authDomain: "martketwatch-activity-feed.firebaseapp.com",
  databaseURL: "https://martketwatch-activity-feed-default-rtdb.firebaseio.com",
  projectId: "martketwatch-activity-feed",
  storageBucket: "martketwatch-activity-feed.firebasestorage.app",
  messagingSenderId: "299097685936",
  appId: "1:299097685936:web:2695b2fc3e582c13bb2e32"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// Subscribe to latest data
export const subscribeToLatestData = (callback: (data: CompetitionData | null) => void) => {
  const dataRef = ref(database, 'latest_data');
  
  return onValue(dataRef, (snapshot) => {
    const data = snapshot.val();
    callback(data as CompetitionData);
  }, (error) => {
    console.error('Firebase read error:', error);
    callback(null);
  });
};

export { database };