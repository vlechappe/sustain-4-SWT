import FreeCAD as App
import Part
import csv
import os
import sys


turbine_diameter = 4200
    

# === CONFIGURATION ===
FCSTD_PATH = f"WT_3D_Files/{turbine_diameter}/WindTurbine.FCStd"     # Change this
CSV_PATH = f"Volume_csv/volumes_{turbine_diameter}.csv"             # Change this

# === Ensure CSV file is ready ===
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)  # Create directory if needed
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Component", "Volume (cm³)"])  # Write headers immediately
    
# === LOAD MODEL ===
doc = App.openDocument(FCSTD_PATH)
App.setActiveDocument(doc.Name)

# === INIT ===
processed_shapes = set()
visited_objects = set()
rows = []

SKIP_TYPES = {
    'Sketcher::SketchObject',
    'PartDesign::Pad',
    'PartDesign::Pocket',
    'PartDesign::Chamfer',
    'PartDesign::Fillet',
    'PartDesign::Revolution',
    'PartDesign::Boolean',
    'PartDesign::Mirrored',
    'Part::Feature',
}
SKIP_KEYWORDS = {
    "Sketch", "Pocket", "Pad", "Groove", "Chamfer", "Pattern",
    "Thread"  #,"Stud","Washer", "HexNut", "Fastener"
}

def should_skip(obj):
    if obj.TypeId in SKIP_TYPES:
        return True
    if any(kw.lower() in obj.Label.lower() for kw in SKIP_KEYWORDS):
        return True
    return False

def get_children(obj):
    if obj.TypeId == 'App::Link' and obj.LinkedObject:
        obj = obj.LinkedObject
    return obj.Group if hasattr(obj, 'Group') else []

def format_label(label, indent, is_last):
    prefix = ""
    for i in range(indent):
        prefix += "│   " if i < indent - 1 else ("└── " if is_last else "├── ")
    return prefix + label

def process(obj, indent=0, is_last=False):
    if obj in visited_objects or should_skip(obj):
        return

    visited_objects.add(obj)
    target = obj.LinkedObject if obj.TypeId == 'App::Link' and obj.LinkedObject else obj

    # Compute volume
    volume = 0.0
    shape = getattr(target, "Shape", None)
    if shape and not shape.isNull():
        shape_hash = shape.hashCode()
        if shape_hash not in processed_shapes:
            processed_shapes.add(shape_hash)
            volume = sum(s.Volume for s in shape.Solids)

    label = format_label(obj.Label, indent, is_last)
    volume_cm3 = round(volume / 1000.0, 2) if volume > 0 else ""
    rows.append([label, volume_cm3])

    # Traverse children
    children = get_children(target)
    for i, child in enumerate(children):
        process(child, indent + 1, is_last=(i == len(children) - 1))

# === START FROM WINDTURBINE ROOT ===
root = doc.getObject("WindTurbine") or next((o for o in doc.Objects if o.Label == "WindTurbine"), None)
if root:
    process(root, indent=0, is_last=True)
else:
    # fallback: process everything (flat)
    for obj in doc.Objects:
        process(obj, indent=0, is_last=False)

# === EXPORT TO CSV ===
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['Diameter',turbine_diameter])
    for row in rows:
        writer.writerow(row)

print(f"✅ Exported to: {os.path.abspath(CSV_PATH)}")
