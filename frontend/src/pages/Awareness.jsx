import { Wind, Activity, Globe, Heart, Leaf, AlertTriangle } from 'lucide-react'

function Section({ icon: Icon, color, title, children }) {
  return (
    <div className="card space-y-3">
      <div className="flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <h2 className="text-base font-semibold text-white">{title}</h2>
      </div>
      <div className="text-sm text-slate-300 leading-relaxed space-y-2">{children}</div>
    </div>
  )
}

function AQITable() {
  const rows = [
    { cat: 'Good',        pm25: '0 – 12',   color: 'text-green-400',  bg: 'bg-green-900/30' },
    { cat: 'Moderate',    pm25: '12.1 – 35.4', color: 'text-yellow-400', bg: 'bg-yellow-900/30' },
    { cat: 'Unhealthy for Sensitive Groups', pm25: '35.5 – 55.4', color: 'text-orange-400', bg: 'bg-orange-900/30' },
    { cat: 'Unhealthy',   pm25: '55.5 – 150.4', color: 'text-red-400',  bg: 'bg-red-900/30' },
    { cat: 'Very Unhealthy', pm25: '150.5 – 250.4', color: 'text-purple-400', bg: 'bg-purple-900/30' },
    { cat: 'Hazardous',   pm25: '> 250.4',  color: 'text-rose-400',   bg: 'bg-rose-900/30' },
  ]
  return (
    <div>
      <p className="text-xs text-slate-400 mb-2">US EPA AQI categories for PM2.5 (µg/m³, 24-hr average) — for reference only</p>
      <div className="overflow-x-auto rounded border border-slate-700">
        <table className="text-xs w-full">
          <thead className="bg-slate-800">
            <tr>
              <th className="text-left px-3 py-2 text-slate-400">Category</th>
              <th className="text-left px-3 py-2 text-slate-400">PM2.5 Range</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.cat} className={`border-t border-slate-700/50 ${r.bg}`}>
                <td className={`px-3 py-2 font-medium ${r.color}`}>{r.cat}</td>
                <td className="px-3 py-2 text-slate-300">{r.pm25}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-500 mt-1">
        Source: US EPA AirNow. These are official US EPA thresholds and are separate from AirGuard's custom AI severity categories.
      </p>
    </div>
  )
}

export default function Awareness() {
  return (
    <div className="max-w-3xl space-y-5">
      <div className="card bg-gradient-to-r from-sky-900/40 to-slate-800 border-sky-700/50">
        <h1 className="text-xl font-bold text-white mb-1">Environmental Awareness</h1>
        <p className="text-sm text-slate-300">
          Understanding air pollution is the first step toward cleaner, healthier communities.
          AirGuard supports <strong>SDG 11 – Sustainable Cities</strong>, <strong>SDG 3 – Good Health</strong>,
          and <strong>SDG 13 – Climate Action</strong>.
        </p>
      </div>

      <Section icon={Wind} color="bg-sky-500/20 text-sky-400" title="What is Air Pollution?">
        <p>
          Air pollution is the presence of harmful substances in the atmosphere at concentrations that can
          negatively affect human health, ecosystems, and climate. It can originate from natural sources
          (dust storms, wildfires) or human activities (vehicles, industry, agriculture, waste burning).
        </p>
        <p>
          Long-term exposure to polluted air is linked to respiratory disease, cardiovascular problems, and
          other health effects. The World Health Organization estimates that 99% of the world's population
          breathes air that exceeds WHO guideline limits.
        </p>
      </Section>

      <Section icon={Activity} color="bg-red-500/20 text-red-400" title="What is PM2.5?">
        <p>
          PM2.5 refers to fine particulate matter with an aerodynamic diameter of 2.5 micrometres or less —
          about 30 times smaller than the width of a human hair. Because of their tiny size, these particles
          can penetrate deep into the lungs and enter the bloodstream.
        </p>
        <p>
          Sources include combustion (vehicles, power plants, cooking fires), industrial processes,
          and secondary formation from gaseous pollutants.
        </p>
        <p>
          The WHO 24-hour mean guideline for PM2.5 is <strong className="text-red-300">15 µg/m³</strong> (2021 guidelines).
        </p>
      </Section>

      <Section icon={Wind} color="bg-orange-500/20 text-orange-400" title="What is PM10?">
        <p>
          PM10 refers to coarse particles with diameters of 10 micrometres or less. They are produced by
          road dust, construction, agriculture, pollen, and mould spores. While they are filtered more
          effectively by the upper respiratory tract than PM2.5, elevated PM10 can still cause respiratory
          irritation and aggravate existing conditions.
        </p>
        <p>
          The WHO 24-hour mean guideline for PM10 is <strong className="text-orange-300">45 µg/m³</strong> (2021 guidelines).
        </p>
        <AQITable />
      </Section>

      <Section icon={Activity} color="bg-purple-500/20 text-purple-400" title="What is Anomaly Detection?">
        <p>
          Anomaly detection is a branch of machine learning that identifies observations that deviate
          significantly from an expected pattern. In AirGuard, it is used to find pollution readings
          that are unusual compared to the recent historical baseline.
        </p>
        <p>
          AirGuard uses the <strong className="text-purple-300">Isolation Forest</strong> algorithm. It works by
          randomly partitioning the data: anomalies, being rare and different, are isolated in fewer
          partitioning steps than normal observations. This makes it efficient and well-suited to
          unlabelled air-quality datasets.
        </p>
      </Section>

      <Section icon={AlertTriangle} color="bg-yellow-500/20 text-yellow-400" title="Why Do Pollution Events Matter?">
        <p>
          Short-term pollution spikes can be more harmful than moderate chronic exposure, especially for
          vulnerable populations (children, elderly, people with respiratory or cardiovascular conditions).
        </p>
        <p>
          Early detection of pollution events allows communities, schools, and individuals to take
          protective actions — such as staying indoors, reducing outdoor activity, or investigating
          possible sources — before exposure accumulates.
        </p>
      </Section>

      <Section icon={Globe} color="bg-green-500/20 text-green-400" title="Sustainability Connection">
        <div className="space-y-2">
          <div className="bg-slate-700/40 rounded-lg p-3">
            <p className="font-medium text-green-300">SDG 11 – Sustainable Cities and Communities</p>
            <p className="text-slate-400 text-xs mt-1">
              Target 11.6 focuses on reducing the per capita environmental impact of cities, including air quality.
              Monitoring pollution patterns supports evidence-based urban planning.
            </p>
          </div>
          <div className="bg-slate-700/40 rounded-lg p-3">
            <p className="font-medium text-blue-300">SDG 3 – Good Health and Well-being</p>
            <p className="text-slate-400 text-xs mt-1">
              Target 3.9 aims to substantially reduce deaths and illnesses from hazardous chemicals and air pollution by 2030.
            </p>
          </div>
          <div className="bg-slate-700/40 rounded-lg p-3">
            <p className="font-medium text-sky-300">SDG 13 – Climate Action</p>
            <p className="text-slate-400 text-xs mt-1">
              Many air pollutants (such as black carbon and methane) are also short-lived climate forcers.
              Reducing air pollution and addressing climate change are complementary goals.
            </p>
          </div>
        </div>
      </Section>

      <Section icon={Leaf} color="bg-emerald-500/20 text-emerald-400" title="Practical Environmental Actions">
        <ul className="list-none space-y-2">
          {[
            'Use public transport, cycling, or walking instead of private vehicles.',
            'Avoid burning waste, dry leaves, or agricultural residue.',
            'Support local clean energy and green space initiatives.',
            'Plant trees and maintain green cover in urban areas.',
            'Report visible pollution sources (industrial smoke, illegal burning) to local authorities.',
            'Use air purifiers with HEPA filters indoors during high-pollution days.',
            'Monitor local AQI through official government portals before outdoor activities.',
            'Advocate for stricter emission standards in your community.',
          ].map((action, i) => (
            <li key={i} className="flex gap-2 text-slate-300">
              <span className="text-emerald-400 mt-0.5">→</span> {action}
            </li>
          ))}
        </ul>
      </Section>

      <div className="card text-xs text-slate-500 border-slate-700">
        <p>
          <strong className="text-slate-400">Sources:</strong> WHO Global Air Quality Guidelines (2021) ·
          US EPA AirNow · UN SDG Knowledge Platform · IPCC Reports.
          AirGuard is a student educational project and does not provide medical or regulatory advice.
        </p>
      </div>
    </div>
  )
}
