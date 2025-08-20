global.window = {};
// rsa_encrypt.js
const JSEncrypt = require('D:\\Environment\\nodejs\\node_modules\\npm\\node_modules\\jsencrypt');
const Key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBBWMLcNnyiRZdRFmaZGUBxearvgnTQGyCgvnfrvHHzKJrIYuvVsbElqO5MG5lSom3JQr/OJnkgVAEZSN0x6hyinjRwdfdiUlKviUhX7tyHpC6+As60IupL1Wo1s+gco25+RteQRC/ZDh0Ca74IZfFBX180vec1oMbcMQtE5sRMQIDAQAB";


function u(e) {
    for (var t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", n = "", i = 0; i < e; i++) {
        var a = Math.floor(Math.random() * t.length);
        n += t.substring(a, a + 1)
    }
    return n
}

function encryptLong(data) {
  const publicKeyPem = Key;
  const encryptor = new JSEncrypt();
  encryptor.setPublicKey(publicKeyPem);

  const chunkSize = 1024; // RSA 1024 位的分段大小
  const encryptedChunks = [];
  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.substring(i, i + chunkSize);
    encryptedChunks.push(encryptor.encrypt(chunk));
  }
  return encryptedChunks.join('|'); // 用分隔符拼接
}