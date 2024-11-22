const admin = require('firebase-admin');

const fs = require('fs');
const csv = require('csv-parser');

var serviceAccount = require('./serviceAccount.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

// CSV file path
const filePath = './user-passwords.csv';

// users collection
const collectionName = 'users';

async function loadCsvToFirestore() {
  const batch = db.batch();
  let count = 0;

  fs.createReadStream(filePath)
    .pipe(csv())
    .on('data', (row) => {
      const email = row.email;
      if (!email || email.includes('/')) {
        console.error(`Skipping invalid email: ${email}`);
        return;
      }

      const docRef = db.collection(collectionName).doc(email);
      batch.set(docRef, row);
      count++;
    })
    .on('end', async () => {
      await batch.commit();
      console.log(`Successfully uploaded ${count} records to Firestore.`);
    })
    .on('error', (error) => {
      console.error('Error reading the CSV file:', error);
    });
}

loadCsvToFirestore();
