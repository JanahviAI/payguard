async function main() {
  const Escrow = await ethers.getContractFactory('PayGuardEscrow');
  const escrow = await Escrow.deploy();
  await escrow.waitForDeployment();
  console.log('PayGuardEscrow deployed to:', await escrow.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
