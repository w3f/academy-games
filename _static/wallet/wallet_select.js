import { web3Accounts, web3Enable, web3FromSource } from '@polkadot/extension-dapp';

async function get_accounts() {
    console.log("getting all accounts from keystore");

    const allInjected = await web3Enable('Academy games');
    const allAccounts = await web3Accounts();

    populateDropdown(allAccounts);
}

function populateDropdown(accounts) {
    console.log('Accounts:', accounts); // log the accounts

    const dropdownContent = document.getElementById('accounts');
    if (!dropdownContent) {
        console.log('Could not find dropdown-content element');
        return;
    }
    accounts.forEach(account => {
        var opt = document.createElement("option");
        opt.value = JSON.stringify(account);
        opt.textContent = account.meta.name;
        dropdownContent.appendChild(opt);
    });
}

window.onload = get_accounts;