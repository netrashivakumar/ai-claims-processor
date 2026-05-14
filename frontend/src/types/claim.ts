export interface Claim {
  id: number;
  policy_number: string;
  claim_amount: number;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  embedding?: number[]; // Your 384-dimension vector
  created_at: string;
  metadata?: Record<string, any>;
}
