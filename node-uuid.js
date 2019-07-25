const UuidEncoder = require('uuid-encoder');
 
// Create Base 36 encoder
const encoder = new UuidEncoder('base36');
 
// Encode an UUID
//const encodedUuid = encoder.encode('38b9823d-fa1a-48e7-91fc-ee16ad091cf2');
//console.log(encodedUuid);
 
// Decode an encoded UUID
//const decodedUuid = encoder.decode(encodedUuid);
//console.log(decodedUuid);

console.log(encoder.decode('2YeecYwqAodIpe4FO2FbOX'));
