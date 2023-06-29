const path = require('path');

module.exports = {
    entry: './_static/wallet/wallet_select.js',
    output: {
        path: path.resolve(__dirname, '_static/wallet'),
        filename: 'wallet_select_bundle.js'
    }
};
