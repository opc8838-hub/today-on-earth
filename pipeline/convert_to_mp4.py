"""
Convert PNG sequence to MP4 using Blender's built-in FFmpeg.
"""
import bpy
from pathlib import Path

FRAMES_DIR = Path("C:/tmp/earth-render/frames")
OUTPUT_PATH = Path("C:/tmp/earth-render/intro.mp4")
FPS = 30
RES_X, RES_Y = 1920, 1080
TOTAL_FRAMES = 90

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

# Set up video output via FFmpeg
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.audio_codec = 'NONE'
scene.render.filepath = str(OUTPUT_PATH)

# Open VSE workspace
if 'Video Editing' not in bpy.data.workspaces:
    bpy.ops.workspace.append_activate(
        idname='VideoEditing',
        filepath=str(FRAMES_DIR / "frame_0001.png")
    )

# Import image sequence via VSE
scene.sequence_editor_clear()
scene.sequence_editor_create()

# Add image sequence strip
bpy.ops.sequencer.image_strip_add(
    directory=str(FRAMES_DIR),
    files=[{"name": f"frame_{i:04d}.png"} for i in range(1, TOTAL_FRAMES + 1)],
    frame_start=1,
    channel=1,
    fit_method='FIT'
)

# Set render region
scene.use_preview_range = False

print(f"Rendering {TOTAL_FRAMES} frames to {OUTPUT_PATH}...")
bpy.ops.render.render(animation=True, write_still=False)

if OUTPUT_PATH.exists():
    print(f"Done! {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size / 1024 / 1024:.1f} MB)")
else:
    print("FAILED: Output not found")
