import ollama
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging

app = FastAPI(title="LLM Service API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "gemma3:4b"

class ParseRequest(BaseModel):
    section_text: str
    section_type: str
    model: str = "gemma3:4b"

class IntroductionQuestionRequest(BaseModel):
    candidate_name: str
    role: str
    model: str = "gemma3:4b"

class ProjectQuestionRequest(BaseModel):
    resume_data: Dict[str, Any]
    model: str = "gemma3:4b"

class TechnicalQuestionRequest(BaseModel):
    resume_data: Dict[str, Any]
    tech_stack: List[str]
    role: str
    model: str = "gemma3:4b"

class FollowupQuestionRequest(BaseModel):
    previous_question: str
    answer: str
    model: str = "gemma3:4b"

class CSFundamentalsQuestionRequest(BaseModel):
    role: str
    tech_stack: List[str]
    model: str = "gemma3:4b"

class DSAQuestionRequest(BaseModel):
    model: str = "gemma3:4b"

class AnswerEvaluationRequest(BaseModel):
    question: str
    answer: str
    question_type: str
    role: str
    tech_stack: List[str]
    model: str = "gemma3:4b"

class SummaryReportRequest(BaseModel):
    candidate_name: str
    role: str
    tech_stack: List[str]
    scores: Dict[str, int]
    interview_log: List[Dict[str, Any]]
    model: str = "gemma3:4b"

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat")
def chat_with_llm(request: ChatRequest):
    try:
        logger.info(f"Chat request received for model: {request.model}")
        response = ollama.chat(
            model=request.model,
            messages=request.messages
        )
        return response
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse_resume_section")
def parse_resume_section(request: ParseRequest):
    try:
        logger.info(f"Parse request received for section: {request.section_type}")
        
        # Output templates for different section types
        output_templates = {
            'education': '''[{"institution": "...", "degree": "...", "year": "...", "gpa": "..."}]''',
            'projects': '''[{"name": "...", "description": "...", "technologies": ["..."]}]''',
            'work_experience': '''[{"company": "...", "year": "...", "description": "..."}]''',
        }

        prompt = f'''
        You are a resume parsing expert. ONLY extract structured information from the following {request.section_type} section.
        Return a valid JSON array with no explanation.
        Strictly use only the information provided.
        Use double quotes for all keys and string values.

        Text: 
        """
        {request.section_text}
        """

        Return JSON Format:
        {output_templates.get(request.section_type, '[]')}
        Only return JSON, no extra text.
        '''
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content']
        
        return {"result": content}
    except Exception as e:
        logger.error(f"Error in parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_introduction_question")
def generate_introduction_question(request: IntroductionQuestionRequest):
    try:
        prompt = f"""
        Generate an introduction question for {request.candidate_name} who is interviewing for a {request.role} role.
        The question should help understand their background, skills, and general technical experience.
        Return only the question text without any additional explanation.
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        question = response['message']['content'].strip()
        
        return {"question": question, "type": "introduction"}
    except Exception as e:
        logger.error(f"Error generating introduction question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_project_question")
def generate_project_question(request: ProjectQuestionRequest):
    try:
        resume_json = json.dumps(request.resume_data, indent=2)
        
        prompt = f"""
        Based on the following resume data:
        ```
        {resume_json}
        ```

        Generate a specific question about one of the candidate's projects. The question should:
        1. Be specific to a project detail mentioned in the resume
        2. Explore technical decisions, challenges, or technologies used
        3. Help assess their depth of knowledge and problem-solving abilities

        Return only the question text without any additional explanation.
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        question = response['message']['content'].strip()
        
        return {"question": question, "type": "projects"}
    except Exception as e:
        logger.error(f"Error generating project question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_technical_question")
def generate_technical_question(request: TechnicalQuestionRequest):
    try:
        resume_json = json.dumps(request.resume_data, indent=2)
        tech_stack_str = ", ".join(request.tech_stack)
        
        prompt = f"""
        Generate a specific technical question for a candidate interviewing for a {request.role} role.
        The required tech stack is: {tech_stack_str}

        Consider the candidate's experience from their resume:
        ```
        {resume_json}
        ```

        The question should:
        1. Test their knowledge of one of the required technologies
        2. Be relevant to their past experience if possible
        3. Be appropriate for the {request.role} role

        Return only the question text without any additional explanation.
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        question = response['message']['content'].strip()
        
        return {"question": question, "type": "technical"}
    except Exception as e:
        logger.error(f"Error generating technical question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_followup_question")
def generate_followup_question(request: FollowupQuestionRequest):
    try:
        prompt = f"""
        The candidate was asked: "{request.previous_question}"

        Their response was:
        "{request.answer}"

        Generate a relevant follow-up question that:
        1. Digs deeper into their response
        2. Asks for clarification on any unclear points
        3. Explores their understanding of the topic further

        Return only the question text without any additional explanation.
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        question = response['message']['content'].strip()
        
        return {"question": question, "type": "followup"}
    except Exception as e:
        logger.error(f"Error generating followup question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_cs_fundamentals_question")
def generate_cs_fundamentals_question(request: CSFundamentalsQuestionRequest):
    try:
        tech_stack_str = ", ".join(request.tech_stack)
        
        prompt = f"""
        Generate a computer science fundamentals question relevant for a {request.role} developer who works with {tech_stack_str}.

        Focus on one of these areas:
        - Data structures and their applications
        - Algorithms concepts and complexity
        - Operating systems principles
        - Database concepts
        - Networking fundamentals
        - Computer architecture

        The question should test core CS knowledge that any {request.role} developer should understand.
        Return only the question text without any additional explanation.
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        question = response['message']['content'].strip()
        
        return {"question": question, "type": "cs_fundamentals"}
    except Exception as e:
        logger.error(f"Error generating CS fundamentals question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_dsa_question")
def generate_dsa_question(request: DSAQuestionRequest):
    try:
        prompt = f"""
        Generate a easy-difficulty data structure and algorithm question similar to ones found on LeetCode, appropriate for testing problem-solving skills.

        Return a only JSON object with the following format:
        {{
        "question": "The full question text including all requirements and constraints",
        "example": "At least one example with input and expected output",
        "topic": "The DSA topic (e.g., Arrays, Trees, Binary Search)",
        "difficulty": "Easy"
        }}

        Return only the json object without any additional explanations.
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content'].strip()
        
        # Extract JSON object
        try:
            # Remove any markdown code block syntax if present
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)
            if content.startswith("```"):
                content = content.replace("```", "", 1)
            if content.endswith("```"):
                content = content[:-3].strip()
                
            result = json.loads(content)
            
            # Format the result as a complete question
            question_text = f"{result.get('question', 'DSA Problem')}\n\nExample: {result.get('example', '')}\n\nTopic: {result.get('topic', 'Algorithm')}"
            return {"question": question_text, "type": "dsa", "raw_data": result}
        except json.JSONDecodeError:
            return {"question": content, "type": "dsa"}
    except Exception as e:
        logger.error(f"Error generating DSA question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate_answer")
def evaluate_answer(request: AnswerEvaluationRequest):
    try:
        tech_context = ", ".join(request.tech_stack)
        
        prompt = f"""
        Evaluate this {request.role} candidate's answer for a {request.question_type} question.

        Question: "{request.question}"

        Answer: "{request.answer}"

        Relevant context:
        - Role: {request.role}
        - Required tech stack: {tech_context}

        Score the answer from 1-10, where:
        1-3: Poor understanding, incorrect or vague response
        4-6: Basic understanding with some gaps
        7-8: Good understanding with minor issues
        9-10: Excellent, comprehensive and accurate

        Return a JSON object with this format:
        {{
        "score": 7,
        "feedback": "Brief explanation of strengths and weaknesses",
        "areas_to_probe": "Suggestion for a follow-up area if needed"
        }}
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content'].strip()
        
        # Extract JSON object
        try:
            # Remove any markdown code block syntax if present
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)
            if content.startswith("```"):
                content = content.replace("```", "", 1)
            if content.endswith("```"):
                content = content[:-3].strip()
                
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            return {"score": 5, "feedback": "Unable to provide specific feedback", "areas_to_probe": ""}
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_summary_report")
def generate_summary_report(request: SummaryReportRequest):
    try:
        total_score = sum(request.scores.values())
        max_possible = len([s for s in request.scores.values() if s > 0]) * 10
        percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
        
        log_summary = json.dumps(request.interview_log, indent=2)
        
        prompt = f"""
        Review this technical interview for {request.candidate_name} who applied for a {request.role} role.

        Interview log summary:
        ```
        {log_summary}
        ```

        The candidate scored {total_score}/{max_possible} ({percentage:.1f}%).

        Provide a comprehensive assessment including:
        1. Overall impression
        2. Technical strengths demonstrated
        3. Areas for improvement
        4. Hiring recommendation (Reject, Consider, Recommended, Highly Recommended)

        Return a JSON object with this format:
        {{
        "overall_impression": "...",
        "technical_strengths": ["...", "..."],
        "areas_for_improvement": ["...", "..."],
        "recommendation": "..."
        }}
        """
        
        response = ollama.chat(
            model=request.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content'].strip()
        
        # Extract JSON object
        try:
            # Remove any markdown code block syntax if present
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)
            if content.startswith("```"):
                content = content.replace("```", "", 1)
            if content.endswith("```"):
                content = content[:-3].strip()
                
            assessment = json.loads(content)
            
            return {
                "candidate_name": request.candidate_name,
                "role": request.role,
                "tech_stack": request.tech_stack,
                "scores": request.scores,
                "total_score": total_score,
                "max_possible": max_possible,
                "percentage": percentage,
                "assessment": assessment
            }
        except json.JSONDecodeError:
            return {
                "candidate_name": request.candidate_name,
                "role": request.role,
                "tech_stack": request.tech_stack,
                "scores": request.scores,
                "total_score": total_score,
                "max_possible": max_possible,
                "percentage": percentage,
                "assessment": {
                    "overall_impression": "Assessment could not be generated",
                    "technical_strengths": [],
                    "areas_for_improvement": [],
                    "recommendation": "Consider"
                }
            }
    except Exception as e:
        logger.error(f"Error generating summary report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("llm_service:app", host="0.0.0.0", port=8000, reload=True)