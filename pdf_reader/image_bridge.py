from image_processor import load_image, detect_qr_code, get_html_content, get_text
from text_processor import text_to_json, create_ics
from pypdf_test import analyze_club_data
import json

def main():
    try:
        # Process image and create club.json
        img = load_image('/Users/sam/Desktop/HackGT12-main/Project Website/IMG_0708.jpg')
        link = detect_qr_code(img)
        html_content = get_html_content(link)
        raw_text = get_text(html_content)
        json_output = text_to_json(raw_text, link)
        
        with open("club.json", "w") as f:
            json.dump(json_output, f, indent=2)
        
        create_ics(json_output, 1)
        print("Files created: club.json and event1.ics")
        
        # Resume analysis
        resume_path = input("Enter resume path (or press Enter to skip): ").strip("'")
        if resume_path:
            analyze_club_data(resume_path)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()