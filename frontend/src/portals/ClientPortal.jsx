import { useEffect, useState } from 'react'
import { createJob, getJobs } from '../api'
import { lockPayment } from '../web3'

const initialForm = {
  title: '',
  requirements: '',
  amount_inr: '',
  amount_mon: '',
  client_addr: '',
  freelancer_addr: '',
}

export default function ClientPortal() {
  const [form, setForm] = useState(initialForm)
  const [jobs, setJobs] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const loadJobs = async () => {
    const allJobs = await getJobs()
    setJobs(allJobs.filter((job) => job.client_addr === form.client_addr || !form.client_addr))
  }

  useEffect(() => {
    loadJobs().catch((err) => setError(err.message))
  }, [form.client_addr])

  const onChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }))
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const tempId = Date.now()
      const tx_hash = await lockPayment(tempId, form.freelancer_addr, form.amount_mon)
      await createJob({
        id: tempId,
        ...form,
        amount_inr: Number(form.amount_inr),
        amount_mon: Number(form.amount_mon),
        tx_hash,
      })
      setForm(initialForm)
      await loadJobs()
    } catch (err) {
      setError(err.response?.data?.error || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Client Portal</h2>
      <form onSubmit={onSubmit}>
        <input name="client_addr" placeholder="Your wallet address" value={form.client_addr} onChange={onChange} required />
        <input name="freelancer_addr" placeholder="Freelancer wallet address" value={form.freelancer_addr} onChange={onChange} required />
        <input name="title" placeholder="Job title" value={form.title} onChange={onChange} required />
        <textarea name="requirements" placeholder="Requirements" value={form.requirements} onChange={onChange} required />
        <input name="amount_inr" type="number" min="1" placeholder="Amount INR" value={form.amount_inr} onChange={onChange} required />
        <input name="amount_mon" type="number" min="0" step="0.0001" placeholder="Amount MON" value={form.amount_mon} onChange={onChange} required />
        <button disabled={loading} type="submit">Lock payment in escrow</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <strong>{job.title}</strong> · {job.status} · INR {job.amount_inr}
            <div>Escrow TX: {job.tx_hash || 'Pending'}</div>
            {job.ai_reasoning && <div>AI: {job.ai_reasoning}</div>}
          </li>
        ))}
      </ul>
    </section>
  )
}
