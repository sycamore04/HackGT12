from pypdf import PdfReader
import spacy
import json

nlp = spacy.load("en_core_web_md")

def extract_resume_text(resume_path):
    """Extract text from PDF resume"""
    try:
        reader = PdfReader(resume_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading resume: {e}")
        return ""

def calculate_similarity(resume_text, club_description):
    """Calculate similarity between resume and club description"""
    if not resume_text or not club_description:
        return 0.0
    
    resume_doc = nlp(resume_text)
    club_doc = nlp(club_description)
    return resume_doc.similarity(club_doc)

def analyze_club_data(resume_path):
    """Analyze club.json against resume (works with server-processed data)"""
    try:
        # Load club data (potentially altered by server)
        with open("club.json", "r") as f:
            club_data = json.load(f)
        
        # Extract resume text
        resume_text = extract_resume_text(resume_path)
        if not resume_text:
            return 0.0
        
        # Get description (works with both original and server-processed data)
        description = club_data.get("description", "")
        if not description:
            print("No description found in club data")
            return 0.0
        
        # Calculate similarity
        similarity = calculate_similarity(resume_text, description)
        
        # Display results
        print(f"Club: {club_data.get('title', 'Unknown Club')}")
        print(f"Similarity with your resume: {similarity:.3f}")
        
        if similarity >= 0.8:
            print("You should join this club!")
        elif similarity >= 0.6:
            print("This club might be a good fit for you.")
        else:
            print("Consider other options or look for clubs more aligned with your background.")
        
        # Display additional server-processed info if available
        if club_data.get("status") == "processed":
            print("Note: This data was processed by the server")
            if "result" in club_data:
                print("Server provided additional processing")
        
        return similarity
        
    except FileNotFoundError:
        print("club.json not found. Run the club processing script first.")
        return 0.0
    except Exception as e:
        print(f"Error analyzing club data: {e}")
        return 0.0

if __name__ == "__main__":
    resume_path = input("Enter your resume file path: ").strip("'")
    analyze_club_data(resume_path)