import { Code2, Cpu, Database, Globe, BookOpen, AlertTriangle } from 'lucide-react'

function TechBadge({ name, type }) {
  const colors = {
    frontend:  'bg-sky-900/40 text-sky-300 border-sky-700/50',
    backend:   'bg-purple-900/40 text-purple-300 border-purple-700/50',
    ml:        'bg-green-900/40 text-green-300 border-green-700/50',
    database:  'bg-orange-900/40 text-orange-300 border-orange-700/50',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium border ${colors[type] || colors.frontend}`}>
      {name}
    </span>
  )
}

export default function About() {
  return (
    <div className="max-w-3xl space-y-5">
      {/* Hero */}
      <div className="card bg-gradient-to-br from-sky-900/40 to-slate-800 border-sky-700/50">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-sky-500/20 flex items-center justify-center">
            <Globe className="w-6 h-6 text-sky-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">AirGuard</h1>
            <p className="text-sky-300 text-sm font-medium">AI-Based Air Pollution Event Detection and Early Warning System</p>
            <p className="text-slate-400 text-sm mt-2">
              A full-stack AI sustainability project built for the <strong className="text-slate-300">1M1B AI for Sustainability Virtual Internship</strong>
              {' '}in collaboration with <strong className="text-slate-300">IBM SkillsBuild</strong> and <strong className="text-slate-300">AICTE</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Objective */}
      <div className="card space-y-2">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-sky-400" /> Project Objective
        </h2>
        <p className="text-sm text-slate-300">
          AirGuard analyses time-series air-quality sensor data using an unsupervised Isolation Forest
          anomaly detection model to identify unusual pollution patterns, group them into pollution events,
          classify their severity, generate AI-based explanations, and present everything through an
          interactive web dashboard.
        </p>
        <p className="text-sm text-slate-300">
          The goal is to help students, citizens, and communities understand air-quality changes in their
          environment through accessible, transparent AI tools.
        </p>
      </div>

      {/* SDG Alignment */}
      <div className="card space-y-3">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <Globe className="w-4 h-4 text-green-400" /> SDG Alignment
        </h2>
        <div className="grid md:grid-cols-3 gap-3">
          {[
            { sdg: 'SDG 11', name: 'Sustainable Cities', color: 'border-orange-500 bg-orange-950/30', text: 'text-orange-300', desc: 'Supports evidence-based urban environmental monitoring and awareness.' },
            { sdg: 'SDG 3',  name: 'Good Health',        color: 'border-blue-500 bg-blue-950/30',   text: 'text-blue-300',   desc: 'Raises awareness about air pollution impacts on respiratory health.' },
            { sdg: 'SDG 13', name: 'Climate Action',     color: 'border-green-500 bg-green-950/30', text: 'text-green-300',  desc: 'Air pollutants like black carbon are also short-lived climate forcers.' },
          ].map((s) => (
            <div key={s.sdg} className={`rounded-xl border p-3 ${s.color}`}>
              <p className={`text-xs font-bold ${s.text}`}>{s.sdg}</p>
              <p className="text-slate-200 text-sm font-medium">{s.name}</p>
              <p className="text-slate-400 text-xs mt-1">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Stack */}
      <div className="card space-y-3">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <Code2 className="w-4 h-4 text-sky-400" /> Technology Stack
        </h2>
        <div className="space-y-3">
          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Frontend</p>
            <div className="flex flex-wrap gap-2">
              {['React.js', 'Vite', 'JavaScript', 'Tailwind CSS', 'Recharts', 'Axios', 'React Router'].map((t) => (
                <TechBadge key={t} name={t} type="frontend" />
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Backend</p>
            <div className="flex flex-wrap gap-2">
              {['Python 3.11', 'FastAPI', 'Uvicorn', 'Pydantic', 'Pandas', 'NumPy'].map((t) => (
                <TechBadge key={t} name={t} type="backend" />
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Machine Learning</p>
            <div className="flex flex-wrap gap-2">
              {['Scikit-learn', 'Isolation Forest', 'StandardScaler', 'Unsupervised Learning'].map((t) => (
                <TechBadge key={t} name={t} type="ml" />
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Database</p>
            <div className="flex flex-wrap gap-2">
              {['SQLite', 'SQLAlchemy ORM'].map((t) => (
                <TechBadge key={t} name={t} type="database" />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI Methodology */}
      <div className="card space-y-2">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-purple-400" /> AI Methodology
        </h2>
        <div className="space-y-2 text-sm text-slate-300">
          <p><strong className="text-purple-300">Algorithm:</strong> Isolation Forest (scikit-learn)</p>
          <p><strong className="text-purple-300">Type:</strong> Unsupervised anomaly detection</p>
          <p><strong className="text-purple-300">Why Isolation Forest?</strong> Air-quality datasets rarely have labelled anomalies, making supervised models impractical. Isolation Forest is efficient, handles multi-dimensional pollutant data well, produces a continuous anomaly score, and requires no distributional assumptions.</p>
          <p><strong className="text-purple-300">Features:</strong> PM2.5, PM10, NO₂, CO, SO₂, O₃ (using whichever are present in the uploaded data)</p>
          <p><strong className="text-purple-300">Anomaly score:</strong> Normalised to [0, 1] where 1 = most anomalous. These are relative scores, not official AQI values.</p>
          <p><strong className="text-purple-300">Event grouping:</strong> Consecutive anomalous records within a configurable time gap are merged into a single pollution event.</p>
        </div>
      </div>

      {/* Limitations */}
      <div className="card space-y-2">
        <h2 className="text-sm font-semibold text-white flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-yellow-400" /> Limitations
        </h2>
        <ul className="text-sm text-slate-300 space-y-1">
          {[
            'Cannot identify the exact source of a pollution event from sensor data alone.',
            'Results depend on data quality — faulty sensors produce incorrect detections.',
            'Anomaly detection is relative to the uploaded dataset, not a universal baseline.',
            'No real-time data feed — requires manual CSV upload.',
            'Single-location analysis only (multi-location support is a future enhancement).',
            'Severity categories are custom and should not be compared to official AQI classifications.',
            'Not validated against official monitoring station data in this student implementation.',
          ].map((l, i) => (
            <li key={i} className="flex gap-2">
              <span className="text-yellow-400 shrink-0 mt-0.5">•</span> {l}
            </li>
          ))}
        </ul>
      </div>

      {/* Footer */}
      <div className="card text-xs text-slate-500">
        <p>Version 1.0.0 · Built for 1M1B AI for Sustainability Virtual Internship</p>
        <p className="mt-1">This is a student educational project. Not intended for regulatory or clinical use.</p>
      </div>
    </div>
  )
}
