require('@nomicfoundation/hardhat-toolbox');
require('dotenv').config();

module.exports = {
  solidity: '0.8.20',
  networks: {
    monadTestnet: {
      url: process.env.MONAD_RPC || 'https://testnet-rpc.monad.xyz',
      accounts: process.env.DEPLOYER_PRIVATE_KEY ? [process.env.DEPLOYER_PRIVATE_KEY] : [],
      chainId: Number(process.env.MONAD_CHAIN_ID || 10143),
    },
  },
};
