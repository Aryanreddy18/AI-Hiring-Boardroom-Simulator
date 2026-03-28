const agentTitles = {
  hr: "HR agent",
  tech: "Technical reviewer",
  manager: "Hiring manager",
};

export function normalizeHiringResult(result) {
  const reviews = result.agent_reviews || [];
  const similarity = result.pipeline?.similarity || {};
  const supervisor = result.supervisor_review || {};
  const debate = result.debate || {};

  return {
    chartData: reviews.map((review) => ({
      name: agentTitles[review.agent] || review.agent,
      score: Number(review.score || 0),
    })),
    agentCards: reviews.map((review) => ({
      title: agentTitles[review.agent] || review.agent,
      agent: review.agent,
      score: Number(review.score || 0),
      vote: review.vote || "hold",
      confidence: Number(review.confidence || 0),
      rationale: review.rationale || review.feedback || "No rationale was returned.",
      strengths: review.strengths || [],
      concerns: review.concerns || [],
    })),
    finalDecision: {
      decision: result.final_decision?.decision || "hold",
      score: Number(result.final_decision?.score || 0),
      explanation: result.final_decision?.explanation || "No explanation returned.",
    },
    supervisor: {
      confidence: Number(supervisor.confidence || 0),
      rationale: supervisor.rationale || "",
    },
    debate: {
      weightedScore: Number(debate.weighted_score || 0),
      rawAverage: Number(debate.raw_average_score || 0),
      votes: debate.votes || { hire: 0, hold: 0, reject: 0 },
      conflicts: debate.conflicts || [],
      resolutionNotes: debate.resolution_notes || [],
    },
    metrics: {
      requiredSkillMatch: Number(similarity.required_score || similarity.skill_match?.required_score || 0),
      experienceMatch: Number(similarity.experience_match || 0),
      textSimilarity: Number(similarity.text_similarity || 0),
    },
  };
}
