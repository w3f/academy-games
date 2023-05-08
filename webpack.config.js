const path = require('path');

module.exports = {
    entry: './_static/wallet/sign_in.js',
    output: {
        path: path.resolve(__dirname, '_static/wallet'),
        filename: 'bundle.js'
    }
};