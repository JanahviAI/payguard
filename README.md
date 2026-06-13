# PayGuard - AI Escrow Agent for Freelancers

PayGuard combines Monad escrow smart contracts, a Flask backend, and a React frontend with Claude-powered evaluation for freelancer submissions.

## Prerequisites

- Node.js 18+
- Python 3.10+
- MetaMask
- MON test tokens from Monad testnet faucet

## Folder Structure

- `/contract`: Solidity escrow contract + Hardhat deployment config
- `/backend`: Flask API, SQLAlchemy model, Claude evaluator, blockchain transaction bridge
- `/frontend`: React role-based portal UI (Client, Freelancer, Reviewer)

## Bootstrap

```bash
git clone https://github.com/JanahviAI/payguard.git
cd payguard
```

### 1) Contract

```bash
cd contract
cp .env.example .env # create this file manually if missing
npm install
npm run compile
npm run deploy:monad
```

Set env vars:

- `MONAD_RPC`
- `DEPLOYER_PRIVATE_KEY`
- `MONAD_CHAIN_ID` (default `10143`)

### 2) Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Backend env vars:

- `ANTHROPIC_API_KEY`
- `AGENT_PRIVATE_KEY`
- `CONTRACT_ADDRESS`
- `MONAD_RPC`
- `SECRET_KEY`

API endpoints:

- `POST /api/jobs` - create job
- `GET /api/jobs?status=` - list/filter jobs
- `POST /api/jobs/:id/submit` - freelancer submission + AI evaluation
- `POST /api/jobs/:id/decide` - reviewer approve/reject

### 3) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend env vars:

- `VITE_API_URL`
- `VITE_CONTRACT_ADDRESS`

## Workflow

1. Client creates a job and locks MON in escrow (`createJob` contract call).
2. Freelancer submits work.
3. Claude AI evaluates requirement compliance.
4. High-confidence `approved` => automatic payment release.
5. High-confidence `rejected` => refund to client.
6. Uncertain verdict => reviewer portal for manual decision.

## Testing

- Contract: `cd contract && npm run compile && npm run test`
- Backend syntax check: `cd backend && python -m py_compile app.py models.py agent.py blockchain.py`
- Frontend build: `cd frontend && npm run build`

## Deployment

- Backend: deploy Flask app to Render.
- Frontend: deploy Vite build to Vercel.
- Contract: deploy to Monad testnet and configure addresses in backend/frontend `.env`.

## Key Features

- Job creation with escrow payment lock
- AI-powered submission evaluation using Claude
- Automatic payment release on approval
- Human reviewer fallback for uncertain verdicts
- Monad blockchain transaction hash tracking
- Role-specific portals for client, freelancer, and reviewer
