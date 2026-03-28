export interface DetectedClause {
  clause:      string
  text:        string
  confidence:  number
  risk_weight: number
}

export interface ScoreResult {
  score:    number
  triage:   'AUTO-CLEAR' | 'FLAG FOR REVIEW' | 'URGENT REVIEW'
  clauses:  DetectedClause[]
  word_count:         number
  n_clauses_detected: number
  model:     string
  threshold: number
}

export const RISK_COLORS: Record<number, string> = {
  10: '#C0392B',
  9:  '#C0392B',
  8:  '#D35400',
  7:  '#E67E22',
  6:  '#E8943A',
  5:  '#C9933A',
  4:  '#8CA0BB',
  3:  '#8CA0BB',
  2:  '#5D7A9A',
  1:  '#3D5A7A',
}

export const RISK_LABELS: Record<number, string> = {
  10: 'Critical',
  9:  'Critical',
  8:  'High',
  7:  'High',
  6:  'Elevated',
  5:  'Moderate',
  4:  'Low',
  3:  'Low',
  2:  'Minimal',
  1:  'Minimal',
}

// Mock result for demo/development
export const MOCK_RESULT: ScoreResult = {
  score: 82,
  triage: 'URGENT REVIEW',
  word_count: 847,
  n_clauses_detected: 9,
  model: 'RoBERTa-base fine-tuned on CUAD',
  threshold: 0.1,
  clauses: [
    {
      clause:      'Uncapped Liability',
      text:        "Vendor's liability shall not be limited or capped under any circumstances whatsoever.",
      confidence:  0.8821,
      risk_weight: 10,
    },
    {
      clause:      'Ip Ownership Assignment',
      text:        'All intellectual property created under this Agreement shall be assigned to Vendor, including any derivative works.',
      confidence:  0.9143,
      risk_weight: 9,
    },
    {
      clause:      'Change Of Control',
      text:        'Any acquisition or change of control of Customer requires prior written consent from Vendor.',
      confidence:  0.8456,
      risk_weight: 8,
    },
    {
      clause:      'Liquidated Damages',
      text:        'Customer shall pay $500,000 as liquidated damages for any breach of the exclusivity provisions.',
      confidence:  0.7932,
      risk_weight: 7,
    },
    {
      clause:      'Anti-Assignment',
      text:        'This Agreement may not be assigned by either party without the prior written consent of the other party.',
      confidence:  0.8671,
      risk_weight: 7,
    },
    {
      clause:      'Source Code Escrow',
      text:        'Vendor shall deposit the source code into an escrow account maintained by a mutually agreed escrow agent.',
      confidence:  0.7234,
      risk_weight: 7,
    },
    {
      clause:      'Non-Compete',
      text:        'Customer agrees not to engage with competing vendors for 24 months following termination of this Agreement.',
      confidence:  0.8102,
      risk_weight: 6,
    },
    {
      clause:      'Renewal Term',
      text:        'This Agreement shall auto-renew annually unless terminated with 90 days prior written notice.',
      confidence:  0.9312,
      risk_weight: 5,
    },
    {
      clause:      'Governing Law',
      text:        'This Agreement shall be governed by the laws of the State of Delaware.',
      confidence:  0.9781,
      risk_weight: 5,
    },
  ],
}
