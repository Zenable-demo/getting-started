-- Finding decisions table for tracking user approvals/rejections

CREATE TABLE IF NOT EXISTS finding_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    finding_id UUID NOT NULL REFERENCES guardrail_findings(id) ON DELETE CASCADE,
    decision VARCHAR(50) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    note TEXT,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_finding_decisions_finding_id ON finding_decisions(finding_id);
CREATE INDEX IF NOT EXISTS idx_finding_decisions_decision ON finding_decisions(decision);
