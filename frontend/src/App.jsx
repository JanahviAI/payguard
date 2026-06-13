import { useState } from 'react'
import ClientPortal from './portals/ClientPortal'
import FreelancerPortal from './portals/FreelancerPortal'
import ReviewerPortal from './portals/ReviewerPortal'

const tabs = ['client', 'freelancer', 'reviewer']

export default function App() {
  const [role, setRole] = useState('client')

  return (
    <main style={{ maxWidth: 900, margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>PayGuard</h1>
      <p>AI escrow agent for freelancers</p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setRole(tab)}
            style={{
              textTransform: 'capitalize',
              background: role === tab ? '#222' : '#ddd',
              color: role === tab ? '#fff' : '#000',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {role === 'client' && <ClientPortal />}
      {role === 'freelancer' && <FreelancerPortal />}
      {role === 'reviewer' && <ReviewerPortal />}
    </main>
  )
}
