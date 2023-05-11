import { web3Accounts, web3Enable, web3FromSource } from '@polkadot/extension-dapp';
import { cryptoWaitReady, decodeAddress, signatureVerify, blake2AsHex } from '@polkadot/util-crypto'
import { u8aToHex, stringToHex } from '@polkadot/util'


const storePubkeyBtn = document.getElementById('sign-in-btn');
const storePubkeyThing = document.getElementById('sign-in');
storePubkeyBtn.addEventListener('click', storePubkey);

async function storePubkey(event) {
    event.preventDefault();
    console.log("requesting a signin..");

    const {result: signInSuccess, id: userId} = await signIn();

    storePubkeyThing.value = userId;
    this.form.submit();
};

async function signIn() {
    // returns an array of all the injected sources
    // (this needs to be called first, before other requests)
    const allInjected = await web3Enable('Academy games');

    // returns an array of { address, meta: { name, source } }
    // meta.source contains the name of the extension that provides this account
    const allAccounts = await web3Accounts();
    console.log('Web3 accounts:', allAccounts);

    // Extract first account
    // TODO: How to handle if there are no accounts can return an error??
    const sender = allAccounts[0];
    console.log('First sender: ', sender.address);

    const injector = await web3FromSource(sender.meta.source);

    // this injector object has a signer and a signRaw method
    // to be able to sign raw bytes
    const signRaw = injector?.signer?.signRaw;

    let signature;
    if (!!signRaw) {
        // after making sure that signRaw is defined
        // we can use it to sign our message
        const { signature: sig } = await signRaw({
            address: sender.address,
            data: stringToHex('Sign in message'),
            type: 'bytes'
        });
        signature = sig;
        console.log('signature produced', signature);
    }

    // Now verify signature.
    const verification = await verifySignature(
        'Sign in message',
        signature,
        sender.address
    );
    console.log('Signature verification result: ', verification);

    // returning the Hash of the address..
    const hashedAddress = blake2AsHex(sender.address);
    return {
        result: verification,
        id: hashedAddress
    }
}

const verifySignature = async (signedMessage, signature, address) => {
    await cryptoWaitReady();
    const publicKey = decodeAddress(address);
    const hexPublicKey = u8aToHex(publicKey);
    return signatureVerify(signedMessage, signature, hexPublicKey).isValid
}



