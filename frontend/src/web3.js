import { ethers } from 'ethers'

const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS
const ABI = [
  'function createJob(uint256 jobId, address freelancer) payable',
]

export async function lockPayment(jobId, freelancerAddr, amountMon) {
  if (!window.ethereum) {
    throw new Error('MetaMask not found')
  }
  if (!CONTRACT_ADDRESS) {
    throw new Error('Missing VITE_CONTRACT_ADDRESS')
  }

  const provider = new ethers.BrowserProvider(window.ethereum)
  await provider.send('eth_requestAccounts', [])
  const signer = await provider.getSigner()
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, signer)

  const tx = await contract.createJob(jobId, freelancerAddr, {
    value: ethers.parseEther(String(amountMon || 0)),
  })
  const receipt = await tx.wait()
  return receipt.hash
}
