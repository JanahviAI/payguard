import { useEffect, useState } from 'react'
import { getJobs, submitWork } from '../api'

const verdictColor = {
  approved: 'green',
  rejected: 'red',
  uncertain: 'goldenrod',
}

export default function FreelancerPortal() {
  const [jobs, setJobs] = useState([])
  const [submissions, setSubmissions] = useState({})
  const [error, setError] = useState('')

  const loadJobs = async () => {
    const allJobs = await getJobs()
    setJobs(allJobs.filter((job) => ['open', 'submitted', 'human_review'].includes(job.status)))
  }

  useEffect(() => {
    loadJobs().catch((err) => setError(err.message))
  }, [])

  const handleSubmit = async (jobId) => {
    setError('')
    try {
      await submitWork(jobId, submissions[jobId] || '')
      await loadJobs()
    } catch (err) {
      setError(err.response?.data?.error || err.message)
    }
  }

  return (
    <section>
      <h2>Freelancer Portal</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <h3>{job.title}</h3>
            <p>{job.requirements}</p>
            <textarea
              placeholder="Submit your work"
              value={submissions[job.id] || ''}
              onChange={(event) => setSubmissions((prev) => ({ ...prev, [job.id]: event.target.value }))}
            />
            <button onClick={() => handleSubmit(job.id)}>Submit work</button>

            {job.ai_verdict && (
              <div>
                <span style={{ color: verdictColor[job.ai_verdict] || 'black', fontWeight: 700 }}>
                  {job.ai_verdict.toUpperCase()}
                </span>
                <div>Confidence: {Math.round((job.ai_confidence || 0) * 100)}%</div>
                <div>{job.ai_reasoning}</div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}
