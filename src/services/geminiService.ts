import { GoogleGenAI, Type } from "@google/genai";

const API_KEY = process.env.GEMINI_API_KEY || "";

export interface AnalysisResult {
  matchScore: number;
  decision: "APPLY" | "SKIP" | "APPLY WITH CUSTOMIZATION";
  decisionReason: string;
  resumeImprovements: string[];
  coverLetter: string;
  recruiterMessage: string;
  autoFillAnswers: {
    yearsOfExperience: string;
    skillsSummary: string;
    expectedSalary: string;
    noticePeriod: string;
  };
}

export async function analyzeJob(
  jobDescription: string,
  companyName: string,
  userProfile: string
): Promise<AnalysisResult> {
  const ai = new GoogleGenAI({ apiKey: API_KEY });
  
  const prompt = `
    You are an expert job application assistant specialized in helping candidates land software engineering roles.
    
    User Profile:
    ${userProfile}
    
    Company Name: ${companyName}
    Job Description:
    ${jobDescription}
    
    Your tasks:
    1. JOB FILTERING: Decide if it is a strong match (>= 70% match). Reject irrelevant or low-quality jobs.
    2. RESUME OPTIMIZATION: Modify resume points to match the job description using ATS-friendly keywords. Keep it natural and human.
    3. COVER LETTER: Write a short, sharp, human-sounding message (5-7 lines max). Avoid generic phrases like "I am passionate".
    4. RECRUITER OUTREACH: Write a short message for a recruiter. Polite, direct, and slightly personalized.
    5. APPLICATION DECISION: APPLY NOW / SKIP / APPLY WITH CUSTOMIZATION. Give a 1-line reason.
    6. AUTO-FILL DATA: Extract key answers: Years of experience, Skills summary (2-3 lines), Expected salary (reasonable range), Notice period (assume standard fresher/early role).
    
    Rules:
    - Be brutally honest.
    - Optimize for interview calls, not number of applications.
    - Avoid robotic or AI-sounding outputs.
  `;

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          matchScore: { type: Type.NUMBER, description: "Percentage match score (0-100)" },
          decision: { type: Type.STRING, enum: ["APPLY", "SKIP", "APPLY WITH CUSTOMIZATION"] },
          decisionReason: { type: Type.STRING, description: "1-line reason for the decision" },
          resumeImprovements: { 
            type: Type.ARRAY, 
            items: { type: Type.STRING },
            description: "List of specific resume point improvements"
          },
          coverLetter: { type: Type.STRING, description: "Short, sharp cover letter message" },
          recruiterMessage: { type: Type.STRING, description: "LinkedIn-style recruiter outreach message" },
          autoFillAnswers: {
            type: Type.OBJECT,
            properties: {
              yearsOfExperience: { type: Type.STRING },
              skillsSummary: { type: Type.STRING },
              expectedSalary: { type: Type.STRING },
              noticePeriod: { type: Type.STRING }
            },
            required: ["yearsOfExperience", "skillsSummary", "expectedSalary", "noticePeriod"]
          }
        },
        required: [
          "matchScore", 
          "decision", 
          "decisionReason", 
          "resumeImprovements", 
          "coverLetter", 
          "recruiterMessage", 
          "autoFillAnswers"
        ]
      }
    }
  });

  return JSON.parse(response.text || "{}");
}
