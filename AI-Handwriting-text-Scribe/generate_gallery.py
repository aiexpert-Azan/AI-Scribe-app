import os
import shutil
from demo import Hand

def main():
    print("⏳ Loading Model for Gallery Generation...")
    hand = Hand()
    
    # Reset gallery folder
    gallery_dir = "style_gallery"
    if os.path.exists(gallery_dir):
        shutil.rmtree(gallery_dir)
    os.makedirs(gallery_dir)
    
    print("📸 Generating 13 CENTERED Style Previews...")
    
    for i in range(13):
        text = "Handwriting Sample"
        temp_filename = f"temp_style_{i}.svg"
        
        # === CENTERING CONFIGURATION ===
        # Canvas Width: 1000px
        # Canvas Height: 100px
        
        custom_margins = {
            "left": 350,  # <--- HORIZONTAL CENTER: Pushes start point to the middle
            "right": 50,
            "top": 35,    # <--- VERTICAL CENTER: Pushes text down to the middle
            "bottom": 10
        }

        hand.write(
            filename=temp_filename,
            lines=text,
            biases=[0.9],
            styles=[i],
            page_width=1000, 
            page_height=100,  
            margins=custom_margins,
            ruled=False
        )
        
        # Rename logic
        generated_file = temp_filename.replace(".svg", "_p1.svg")
        final_path = os.path.join(gallery_dir, f"style_{i}.svg")
        
        if os.path.exists(generated_file):
            os.rename(generated_file, final_path)
            print(f"   ✅ Saved Style {i}")
            if os.path.exists(temp_filename): os.remove(temp_filename)
        else:
            print(f"   ❌ Error generating style {i}")

    print("\n🎉 Gallery Updated! Text should be dead center now.")

if __name__ == "__main__":
    main()