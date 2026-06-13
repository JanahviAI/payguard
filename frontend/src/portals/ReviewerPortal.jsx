import { useEffect, useState } from 'react'
import { decide, getJobs } from '../api'

export default function ReviewerPortal() {
  const [jobs, setJobs] = useState([])
  const [error, setError] = useState('')

  const loadJobs = async () => {
    const pending = await getJobs('human_review')
    setJobs(pending)
  }

  useEffect(() => {
    loadJobs().catch((err) => setError(err.message))
  }, [])

  const makeDecision = async (id, decision) => {
    setError('')
    try {
      await decide(id, decision)
      await loadJobs()
    } catch (err) {
      setError(err.response?.data?.error || err.message)
    }
  }

  return (
    <section>
      <h2>Reviewer Portal</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <h3>{job.title}</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <h4>Requirements</h4>
                <p>{job.requirements}</p>
              </div>
              <div>
                <h4>Submission</h4>
                <p>{job.submission}</p>
              </div>
            </div>
            <p>AI confidence: {Math.round((job.ai_confidence || 0) * 100)}%</p>
            <p>{job.ai_reasoning}</p>
            <button style={{ background: 'green', color: 'white' }} onClick={() => makeDecision(job.id, 'approve')}>Approve</button>
            <button style={{ background: 'red', color: 'white', marginLeft: 8 }} onClick={() => makeDecision(job.id, 'reject')}>Reject</button>
          </li>
        ))}
      </ul>
    </section>
  )
}
