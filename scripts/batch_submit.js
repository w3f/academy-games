// Import the API & Provider and some utility functions
const { ApiPromise } = require('@polkadot/api');

const { Keyring } = require('@polkadot/keyring');

// Utility function for random values
const { randomAsU8a } = require('@polkadot/util-crypto');

// Some constants we are using in this sample

const Papa = require('papaparse');
const fs = require('fs');

function createTransaction(api, record) {
    const recipient = record.address;
    const AMOUNT = record.balance;

    console.log('Creating transaction of', AMOUNT, 'to', recipient);

    return api.tx.balances.transfer(recipient, AMOUNT);
}

async function main() {
    const api = await ApiPromise.create();
    console.log(Object.keys(api.tx));
    const keyring = new Keyring({ type: 'sr25519', ss58Format: 42 });
    const alice = keyring.addFromUri('//Alice');

    // Read CSV file
    const csvFile = fs.readFileSync('test_batch.csv', 'utf8');

    // Parse CSV file
    Papa.parse(csvFile, {
        header: true,
        skipEmptyLines: true,
        complete: async function(results) {
            // Create transactions based on CSV records
            const transactions = results.data.map(record => createTransaction(api, record));

            // Batch transactions and send
            api.tx.utility
                .batch(transactions)
                .signAndSend(alice, ({ status, events }) => {
                    if (status.isInBlock) {
                        console.log(`included in ${status.asInBlock}`);
                        console.log('Events:');
                        events.forEach(({ event: { data, method, section }, phase }) => {
                            console.log('\t', phase.toString(), `: ${section}.${method}`, data.toString());
                        });
                    } else if (status.isFinalized) {
                        console.log('Finalized block hash', status.asFinalized.toHex());
                        process.exit(0);
                    }
                });
        }
    });
}

main().catch(console.error);
