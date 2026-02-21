#!/usr/bin/env python3
"""
Demo Video Creator for Gemini Screen Navigator
Creates a demo video showcasing the project features
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

def create_demo_video():
    """Create a demo video for the project"""
    
    project_dir = Path(__file__).parent
    output_dir = project_dir / "demo_assets"
    output_dir.mkdir(exist_ok=True)
    
    # Create a JSON file with demo video metadata
    demo_metadata = {
        "project": "Gemini Screen Navigator",
        "title": "AI-Powered Desktop Automation Agent",
        "duration": "3-4 minutes",
        "created": datetime.now().isoformat(),
        "features_demonstrated": [
            "Task input form with Brutalist design",
            "Real-time execution dashboard",
            "Live progress monitoring",
            "Screenshot gallery (before/after)",
            "Execution logs and timestamps",
            "Final report generation",
            "Safety approval system"
        ],
        "recording_instructions": {
            "resolution": "1920x1080",
            "frame_rate": "30 FPS",
            "audio": "Professional voiceover + background music",
            "tools": [
                "OBS Studio (free)",
                "ScreenFlow (Mac)",
                "DaVinci Resolve (free editing)"
            ]
        },
        "script": {
            "scene_1": {
                "duration": "0:00-0:30",
                "title": "Introduction",
                "description": "Show the Gemini Navigator homepage with Brutalist design"
            },
            "scene_2": {
                "duration": "0:30-1:00",
                "title": "Task Input",
                "description": "Demonstrate entering a task goal"
            },
            "scene_3": {
                "duration": "1:00-2:30",
                "title": "Task Execution",
                "description": "Show the Perceive-Plan-Act-Verify loop in action"
            },
            "scene_4": {
                "duration": "2:30-3:15",
                "title": "Screenshot Gallery",
                "description": "Display before/after screenshots"
            },
            "scene_5": {
                "duration": "3:15-3:50",
                "title": "Final Report",
                "description": "Show the generated Markdown report"
            },
            "scene_6": {
                "duration": "3:50-4:00",
                "title": "Closing",
                "description": "Return to homepage and closing remarks"
            }
        }
    }
    
    # Save metadata
    metadata_file = output_dir / "demo_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(demo_metadata, f, indent=2)
    
    print("✅ Demo video metadata created")
    print(f"   File: {metadata_file}")
    
    # Create a detailed recording guide
    recording_guide = """# Gemini Screen Navigator - Demo Video Recording Guide

## Equipment Needed
- Computer with screen recording capability
- Microphone (USB microphone recommended)
- Headphones (to monitor audio)

## Software Setup
1. **Recording**: OBS Studio (free)
   - Download: https://obsproject.com/
   - Setup guide: https://obsproject.com/wiki/OBS-Studio-Quickstart

2. **Editing**: DaVinci Resolve (free)
   - Download: https://www.blackmagicdesign.com/products/davinciresolve/
   - Tutorials: https://www.youtube.com/c/DaVinciResolveOfficial

3. **Audio**: Audacity (free)
   - Download: https://www.audacityteam.org/

## Recording Steps

### Step 1: Prepare Your Environment
- Close unnecessary applications
- Clear desktop of distracting elements
- Ensure good lighting
- Test microphone levels

### Step 2: Configure OBS Studio
1. Set output resolution to 1920x1080
2. Set frame rate to 30 FPS
3. Add display capture source
4. Add audio input (microphone)
5. Create a new scene for recording

### Step 3: Record Each Scene
Follow the DEMO_SCRIPT.md for each scene:
- Scene 1: Introduction (30 seconds)
- Scene 2: Task Input (30 seconds)
- Scene 3: Execution (90 seconds)
- Scene 4: Gallery (45 seconds)
- Scene 5: Report (35 seconds)
- Scene 6: Closing (10 seconds)

### Step 4: Record Voiceover
- Write script (see DEMO_SCRIPT.md)
- Practice pronunciation
- Record in quiet environment
- Aim for clear, professional delivery
- Speak at 120-150 words per minute

### Step 5: Edit Video
1. Import screen recording into DaVinci Resolve
2. Add title card (2 seconds)
3. Add transitions between scenes
4. Import voiceover audio
5. Adjust audio levels
6. Add background music (royalty-free)
7. Add text overlays for key points
8. Add captions/subtitles
9. Color correction if needed
10. Export as MP4

## Video Specifications

| Aspect | Specification |
|--------|---------------|
| Resolution | 1920x1080 (Full HD) |
| Frame Rate | 30 FPS |
| Bitrate | 5000 kbps |
| Format | MP4 or WebM |
| Audio | 128 kbps, 48 kHz |
| Duration | < 4 minutes |
| File Size | < 500 MB |

## Royalty-Free Resources

### Music
- YouTube Audio Library: https://www.youtube.com/audiolibrary
- Epidemic Sound: https://www.epidemicsound.com/
- Artlist: https://artlist.io/

### Sound Effects
- Freesound: https://freesound.org/
- Zapsplat: https://www.zapsplat.com/

### Fonts
- Google Fonts: https://fonts.google.com/
- DaFont: https://www.dafont.com/

## Tips for Professional Video

1. **Audio Quality**
   - Use a good microphone
   - Record in a quiet room
   - Normalize audio levels
   - Add subtle background music

2. **Visual Quality**
   - Use high contrast (Brutalist design helps!)
   - Zoom in on text-heavy areas
   - Use smooth transitions
   - Add subtle animations

3. **Pacing**
   - Don't rush through content
   - Pause between major sections
   - Allow time for viewers to absorb information
   - Keep total duration under 4 minutes

4. **Engagement**
   - Use mouse cursor highlights
   - Add text overlays for key points
   - Include captions for accessibility
   - Show enthusiasm in voiceover

## Submission

1. Export video as MP4 (H.264 codec)
2. Upload to YouTube (unlisted if not public)
3. Get shareable link
4. Add to Devpost submission
5. Share on social media with #GeminiLiveAgentChallenge

## Troubleshooting

### Video is too large
- Reduce bitrate to 3000-4000 kbps
- Use H.265 codec instead of H.264
- Reduce resolution to 1280x720

### Audio is out of sync
- Ensure audio track is properly aligned
- Use DaVinci Resolve's sync tools
- Re-export if needed

### Video is blurry
- Ensure source is 1920x1080
- Check scaling settings
- Use high-quality source footage

---

**Good luck with your recording!** 🎬
"""
    
    guide_file = output_dir / "RECORDING_GUIDE.md"
    with open(guide_file, "w") as f:
        f.write(recording_guide)
    
    print("✅ Recording guide created")
    print(f"   File: {guide_file}")
    
    # Create a checklist for video submission
    submission_checklist = """# Demo Video Submission Checklist

## Before Recording
- [ ] Read DEMO_SCRIPT.md
- [ ] Read RECORDING_GUIDE.md
- [ ] Test microphone and audio levels
- [ ] Prepare recording environment
- [ ] Close unnecessary applications
- [ ] Ensure stable internet connection

## During Recording
- [ ] Record at 1920x1080 resolution
- [ ] Maintain 30 FPS frame rate
- [ ] Speak clearly and professionally
- [ ] Follow the script timing
- [ ] Pause between major sections
- [ ] Record backup takes if needed

## During Editing
- [ ] Add title card (2 seconds)
- [ ] Add transitions between scenes
- [ ] Sync voiceover with video
- [ ] Adjust audio levels
- [ ] Add background music (royalty-free)
- [ ] Add text overlays for key points
- [ ] Add captions/subtitles
- [ ] Color correction if needed
- [ ] Verify video is under 4 minutes
- [ ] Export as MP4 (< 500 MB)

## Before Submission
- [ ] Watch entire video
- [ ] Check audio quality
- [ ] Verify all features are shown
- [ ] Confirm video duration (< 4 minutes)
- [ ] Check file format and size
- [ ] Upload to YouTube or storage
- [ ] Get shareable link

## Submission
- [ ] Add video link to Devpost
- [ ] Include video description
- [ ] Add video thumbnail
- [ ] Share on social media
- [ ] Include #GeminiLiveAgentChallenge hashtag

---

**Deadline**: March 16, 2026
"""
    
    checklist_file = output_dir / "VIDEO_CHECKLIST.md"
    with open(checklist_file, "w") as f:
        f.write(submission_checklist)
    
    print("✅ Video submission checklist created")
    print(f"   File: {checklist_file}")
    
    print("\n" + "="*60)
    print("📹 DEMO VIDEO ASSETS CREATED")
    print("="*60)
    print("\nFiles created:")
    print(f"1. {metadata_file}")
    print(f"2. {guide_file}")
    print(f"3. {checklist_file}")
    print("\nNext steps:")
    print("1. Read RECORDING_GUIDE.md for detailed instructions")
    print("2. Set up OBS Studio and DaVinci Resolve")
    print("3. Follow DEMO_SCRIPT.md while recording")
    print("4. Edit video and export as MP4")
    print("5. Upload to YouTube")
    print("6. Add link to Devpost submission")

if __name__ == "__main__":
    create_demo_video()
