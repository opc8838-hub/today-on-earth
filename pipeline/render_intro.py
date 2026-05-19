"""
Today on Earth — Intro Animation Renderer
==========================================
Blender bpy script: renders 3-second Earth intro (1920×1080@30fps).

Usage:
    blender.exe --background --python render_intro.py

Output:
    C:\tmp\earth-render\intro.mp4
"""
import bpy
import os
import math
from pathlib import Path

# === CONFIG ============================================================
OUTPUT_DIR = Path("C:/tmp/earth-render")
TEXTURE_PATH = OUTPUT_DIR / "earth_texture.jpg"
OUTPUT_PATH = OUTPUT_DIR / "intro.mp4"

FPS = 30
DURATION_SEC = 3  # 3 seconds
TOTAL_FRAMES = FPS * DURATION_SEC
RES_X, RES_Y = 1920, 1080

# === CLEANUP ===========================================================

# Remove default cube, light, camera
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# === SCENE SETUP =======================================================

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

# Output settings — render as PNG sequence, then convert to MP4
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.image_settings.compression = 15

# Output path for frame sequence
frames_dir = OUTPUT_DIR / "frames"
frames_dir.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(frames_dir / "frame_")

# World — deep space background
world = bpy.data.worlds.new("SpaceWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.005, 0.008, 0.018, 1.0)  # deep space blue-black
bg.inputs[1].default_value = 0.1  # subtle glow

# === EARTH SPHERE ======================================================

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.8,
    location=(0, 0, 0),
    segments=128,
    ring_count=64
)
earth = bpy.context.active_object
earth.name = "Earth"

# Smooth shading
bpy.ops.object.shade_smooth()

# Create material with Earth texture
mat = bpy.data.materials.new("EarthMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Output
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)

# Principled BSDF
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Roughness'].default_value = 0.35
bsdf.inputs['Specular IOR Level'].default_value = 0.05
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Image texture
tex_node = nodes.new('ShaderNodeTexImage')
tex_node.location = (-300, 0)
img = bpy.data.images.load(str(TEXTURE_PATH))
tex_node.image = img
links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

# Assign material
earth.data.materials.append(mat)

# === LIGHTING ==========================================================

# Key light (sun-like, from upper-left)
key = bpy.data.lights.new("KeyLight", 'SUN')
key.energy = 5.0
key.angle = 0.5  # soft shadows
key_obj = bpy.data.objects.new("KeyLight", key)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (-8, -4, 6)
key_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(30))

# Fill light (subtle ambient from right)
fill = bpy.data.lights.new("FillLight", 'AREA')
fill.energy = 80
fill.size = 10
fill_obj = bpy.data.objects.new("FillLight", fill)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (6, 2, -1)
fill_obj.rotation_euler = (math.radians(90), 0, 0)

# Rim light (subtle backlight for depth)
rim = bpy.data.lights.new("RimLight", 'SUN')
rim.energy = 1.5
rim_obj = bpy.data.objects.new("RimLight", rim)
bpy.context.collection.objects.link(rim_obj)
rim_obj.location = (0, -6, -2)
rim_obj.rotation_euler = (math.radians(-30), 0, math.radians(-90))

# === STARS (particle system) ===========================================

# Create a large sphere for star background
bpy.ops.mesh.primitive_uv_sphere_add(radius=50, location=(0, 0, 0), segments=32, ring_count=16)
star_sphere = bpy.context.active_object
star_sphere.name = "StarSphere"

# Star material — emissive dots
star_mat = bpy.data.materials.new("StarMaterial")
star_mat.use_nodes = True
snodes = star_mat.node_tree.nodes
slinks = star_mat.node_tree.links
snodes.clear()

s_output = snodes.new('ShaderNodeOutputMaterial')
s_output.location = (400, 0)

# Voronoi texture for star-like dots
voronoi = snodes.new('ShaderNodeTexVoronoi')
voronoi.location = (-400, 0)
voronoi.feature = 'DISTANCE_TO_EDGE'
voronoi.inputs['Scale'].default_value = 300.0

# Color ramp to make dots small and bright
ramp = snodes.new('ShaderNodeValToRGB')
ramp.location = (-100, 0)
ramp.color_ramp.elements[0].position = 0.95
ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp.color_ramp.elements[1].position = 1.0
ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

s_emit = snodes.new('ShaderNodeEmission')
s_emit.location = (100, 0)
s_emit.inputs['Strength'].default_value = 1.5

slinks.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
slinks.new(ramp.outputs['Color'], s_emit.inputs['Color'])
slinks.new(s_emit.outputs['Emission'], s_output.inputs['Surface'])

star_sphere.data.materials.append(star_mat)

# === CAMERA ============================================================

bpy.ops.object.camera_add(location=(0, -5.5, 0.8))
camera = bpy.context.active_object
camera.name = "MainCamera"
camera.rotation_euler = (math.radians(80), 0, 0)
scene.camera = camera

# Camera: subtle push-in (z moves closer, slight tilt)
camera.keyframe_insert(data_path="location", frame=1)
camera.keyframe_insert(data_path="rotation_euler", frame=1)

# End position — gently push in
camera.location = (0, -4.8, 0.6)
camera.rotation_euler = (math.radians(82), 0, 0)
camera.keyframe_insert(data_path="location", frame=TOTAL_FRAMES)
camera.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)

# === EARTH ROTATION ====================================================

# Rotate ~50 degrees over 3 seconds (slow, elegant)
earth.rotation_euler = (0, 0, math.radians(5))  # slight initial tilt
earth.keyframe_insert(data_path="rotation_euler", frame=1)

earth.rotation_euler = (0, 0, math.radians(55))
earth.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)

# === 3D TEXT "今日地球" ================================================

# We'll render text as a separate pass using a plane with text texture
# Alternative: Use a text object in front of the camera

# Create text object
bpy.ops.object.text_add(location=(0, -1.5, 1.6))
text_obj = bpy.context.active_object
text_obj.name = "TitleText"
text_obj.data.body = "今日地球"
text_obj.data.extrude = 0.02
text_obj.data.size = 0.55
text_obj.rotation_euler = (math.radians(90), 0, 0)

# Text material — gold with emission
text_mat = bpy.data.materials.new("TextMaterial")
text_mat.use_nodes = True
tnodes = text_mat.node_tree.nodes
tlinks = text_mat.node_tree.links
tnodes.clear()

t_output = tnodes.new('ShaderNodeOutputMaterial')
t_output.location = (400, 0)

t_emit = tnodes.new('ShaderNodeEmission')
t_emit.location = (100, 0)
t_emit.inputs['Color'].default_value = (0.83, 0.71, 0.45, 1.0)  # gold #d4b872
t_emit.inputs['Strength'].default_value = 2.5

tlinks.new(t_emit.outputs['Emission'], t_output.inputs['Surface'])
text_obj.data.materials.append(text_mat)

# Animate text: fade in (scale and emission strength)
# Start invisible
text_obj.scale = (0.8, 0.8, 0.8)
t_emit.inputs['Strength'].default_value = 0.0
text_obj.keyframe_insert(data_path="scale", frame=1)
text_obj.data.materials[0].node_tree.nodes['Emission'].inputs['Strength'].keyframe_insert(
    data_path="default_value", frame=1)

# Fade in between frames 20-50 (0.67s - 1.67s)
text_obj.scale = (1.0, 1.0, 1.0)
t_emit.inputs['Strength'].default_value = 0.0
text_obj.keyframe_insert(data_path="scale", frame=20)
text_obj.data.materials[0].node_tree.nodes['Emission'].inputs['Strength'].keyframe_insert(
    data_path="default_value", frame=20)

t_emit.inputs['Strength'].default_value = 2.5
text_obj.data.materials[0].node_tree.nodes['Emission'].inputs['Strength'].keyframe_insert(
    data_path="default_value", frame=50)

# Hold for rest
text_obj.keyframe_insert(data_path="scale", frame=TOTAL_FRAMES)

# Subtitle "Today on Earth" below
bpy.ops.object.text_add(location=(0, -1.5, 1.2))
sub_text = bpy.context.active_object
sub_text.name = "SubtitleText"
sub_text.data.body = "Today on Earth"
sub_text.data.size = 0.15
sub_text.rotation_euler = (math.radians(90), 0, 0)

sub_mat = bpy.data.materials.new("SubTextMaterial")
sub_mat.use_nodes = True
subnodes = sub_mat.node_tree.nodes
sublinks = sub_mat.node_tree.links
subnodes.clear()

s_output = subnodes.new('ShaderNodeOutputMaterial')
s_output.location = (400, 0)

s_emit = subnodes.new('ShaderNodeEmission')
s_emit.location = (100, 0)
s_emit.inputs['Color'].default_value = (0.7, 0.7, 0.8, 1.0)
s_emit.inputs['Strength'].default_value = 1.0

sublinks.new(s_emit.outputs['Emission'], s_output.inputs['Surface'])
sub_text.data.materials.append(sub_mat)

# Fade in slightly later
s_emit.inputs['Strength'].default_value = 0.0
sub_text.data.materials[0].node_tree.nodes['Emission'].inputs['Strength'].keyframe_insert(
    data_path="default_value", frame=1)

s_emit.inputs['Strength'].default_value = 0.0
sub_text.data.materials[0].node_tree.nodes['Emission'].inputs['Strength'].keyframe_insert(
    data_path="default_value", frame=40)

s_emit.inputs['Strength'].default_value = 1.0
sub_text.data.materials[0].node_tree.nodes['Emission'].inputs['Strength'].keyframe_insert(
    data_path="default_value", frame=70)

# === ATMOSPHERE GLOW (volumetric rim) ===================================

# Add a subtle glow sphere around Earth
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.88, location=(0, 0, 0), segments=64, ring_count=32)
atmo = bpy.context.active_object
atmo.name = "Atmosphere"

atmo_mat = bpy.data.materials.new("AtmoMaterial")
atmo_mat.use_nodes = True
anodes = atmo_mat.node_tree.nodes
alinks = atmo_mat.node_tree.links
anodes.clear()

a_output = anodes.new('ShaderNodeOutputMaterial')
a_output.location = (400, 0)

# Fresnel for edge glow
fresnel = anodes.new('ShaderNodeFresnel')
fresnel.location = (-300, 0)
fresnel.inputs['IOR'].default_value = 1.01

# Color ramp for atmosphere
aramp = anodes.new('ShaderNodeValToRGB')
aramp.location = (-100, 0)
aramp.color_ramp.elements[0].position = 0.0
aramp.color_ramp.elements[0].color = (0, 0, 0, 0)  # transparent center
aramp.color_ramp.elements[1].position = 1.0
aramp.color_ramp.elements[1].color = (0.3, 0.6, 1.0, 0.3)  # blue rim

a_emit = anodes.new('ShaderNodeEmission')
a_emit.location = (100, 0)
a_emit.inputs['Strength'].default_value = 0.8

# Mix with transparency
mix = anodes.new('ShaderNodeMixShader')
mix.location = (200, 0)

transparent = anodes.new('ShaderNodeBsdfTransparent')
transparent.location = (0, 200)

alinks.new(fresnel.outputs['Fac'], aramp.inputs['Fac'])
alinks.new(aramp.outputs['Color'], a_emit.inputs['Color'])
alinks.new(a_emit.outputs['Emission'], mix.inputs[1])
alinks.new(transparent.outputs['BSDF'], mix.inputs[2])
alinks.new(fresnel.outputs['Fac'], mix.inputs['Fac'])
alinks.new(mix.outputs['Shader'], a_output.inputs['Surface'])

atmo.data.materials.append(atmo_mat)

# === RENDER SETTINGS ====================================================

# Eevee settings for quality (Blender 5.x compatible)
try:
    scene.eevee.taa_render_samples = 64
    scene.eevee.use_ssr = True
    scene.eevee.ssr_quality = 0.5
    scene.eevee.use_gtao = True
    scene.eevee.gtao_distance = 0.5
except AttributeError:
    pass  # API changed in Blender 5.x, use defaults

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Render animation as PNG sequence
print(f"Rendering {TOTAL_FRAMES} frames ({DURATION_SEC}s @ {FPS}fps)...")
print(f"Resolution: {RES_X}×{RES_Y} | Engine: Eevee")
print(f"Texture: {TEXTURE_PATH}")
print(f"Frames: {frames_dir}")

bpy.ops.render.render(animation=True, write_still=False)

# Convert PNG sequence to MP4 using Blender's built-in FFmpeg
print("\nConverting frames to MP4...")
import subprocess
import glob

frame_files = sorted(glob.glob(str(frames_dir / "frame_*.png")))
print(f"  Frames rendered: {len(frame_files)}")

if frame_files:
    # Use ffmpeg from Blender's bundled shared libraries
    ffmpeg_bin = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.shared") / "ffmpeg"
    # Try system ffmpeg first, then Blender's
    ffmpeg_paths = [
        str(ffmpeg_bin.with_suffix(".exe")),
        "ffmpeg"
    ]

    ffmpeg_cmd = None
    for p in ffmpeg_paths:
        try:
            subprocess.run([p, "-version"], capture_output=True, timeout=5)
            ffmpeg_cmd = p
            break
        except:
            continue

    if ffmpeg_cmd:
        cmd = [
            ffmpeg_cmd, "-y",
            "-framerate", str(FPS),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(OUTPUT_PATH)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and OUTPUT_PATH.exists():
            print(f"\nDone! Output: {OUTPUT_PATH}")
            print(f"File size: {OUTPUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print(f"FFmpeg error: {result.stderr[:200]}")
    else:
        print("FFmpeg not found. PNG frames available in:", frames_dir)
else:
    print("\nERROR: No frames rendered!")
