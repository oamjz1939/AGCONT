import argparse
import os
import sys
import bpy
import addon_utils


def parse_args():
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1 :]
    else:
        args = []

    parser = argparse.ArgumentParser(
        description="Convert Endfield / MMD PMX model into an artist-ready Blender .blend file."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to input PMX file")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Path to output .blend file (default: same folder with .blend extension)",
    )
    parser.add_argument(
        "--stick-bones",
        action="store_true",
        default=True,
        help="Set bone display type to STICK for clear visibility",
    )
    parser.add_argument(
        "--hide-physics",
        action="store_true",
        default=True,
        help="Hide physics / collision bones and rigidbodies",
    )
    parser.add_argument(
        "--pack-textures",
        action="store_true",
        default=True,
        help="Pack all textures into the .blend file",
    )
    return parser.parse_args(args)


def ensure_mmd_tools():
    # Enable mmd_tools addon
    res = addon_utils.enable("mmd_tools")
    if not res:
        raise RuntimeError("Failed to enable mmd_tools addon in Blender.")
    if not hasattr(bpy.ops, "mmd_tools"):
        raise RuntimeError("mmd_tools operator is not available.")


def convert_model(input_path, output_path, stick_bones=True, hide_physics=True, pack_textures=True):
    input_path = os.path.abspath(input_path)
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not output_path:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{base_name}.blend")
    output_path = os.path.abspath(output_path)

    print(f"=== Converting PMX to Blend ===")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")

    # 1. Reset factory settings and enable addon
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ensure_mmd_tools()

    # 2. Import PMX
    bpy.ops.mmd_tools.import_model(
        filepath=input_path,
        types={"MESH", "ARMATURE", "PHYSICS", "DISPLAY", "MORPHS"},
        clean_model=True,
        fix_ik_links=True,
        rename_bones=True,
    )

    # Find imported armature and mesh
    arm_obj = None
    mesh_objs = []
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            arm_obj = obj
        elif obj.type == "MESH" and not obj.name.startswith(("0", "1", "2")):
            # Non-rigid-body mesh
            mesh_objs.append(obj)

    # 3. Clean material textures (remove missing toon BMPs)
    for mat in bpy.data.materials:
        if not mat.node_tree:
            continue
        for node in list(mat.node_tree.nodes):
            if node.name == "mmd_toon_tex":
                mat.node_tree.nodes.remove(node)
            elif node.type == "GROUP" and node.node_tree and "MMDShader" in node.node_tree.name:
                if "Toon Tex" in node.inputs:
                    node.inputs["Toon Tex"].default_value = (1.0, 1.0, 1.0, 1.0)
                if "Toon Tex Fac" in node.inputs:
                    node.inputs["Toon Tex Fac"].default_value = 0.0

    # 4. Organize armature & bones
    if arm_obj:
        arm_data = arm_obj.data
        if stick_bones:
            arm_data.display_type = "STICK"
        arm_obj.show_in_front = True

        # Classify unorganized bones in '新規' collection
        col_new = arm_data.collections.get("新規")
        bones_to_categorize = list(col_new.bones) if col_new else []

        col_hair = arm_data.collections.get("头发与耳朵与尾巴") or arm_data.collections.new("头发与耳朵与尾巴")
        col_clothes = arm_data.collections.get("衣物与饰品") or arm_data.collections.new("衣物与饰品")
        col_face = arm_data.collections.get("面部表情骨") or arm_data.collections.new("面部表情骨")
        col_sec = arm_data.collections.get("次级与物理骨骼(已隐藏)") or arm_data.collections.new("次级与物理骨骼(已隐藏)")

        for bone in bones_to_categorize:
            name = bone.name
            if any(k in name for k in ["QB_", "HB_", "spring_", "錘", "Bip", "捩", "_dummy_", "_shadow_"]):
                col_sec.assign(bone)
            elif any(k in name for k in ["hair_", "ear_", "tail_"]):
                col_hair.assign(bone)
            elif any(k in name for k in ["clothes_", "spike_", "cuff_", "board_", "strap_", "shawl_", "ornament_"]):
                col_clothes.assign(bone)
            elif any(k in name for k in ["眉毛", "二重", "目", "舌头", "鼻子"]):
                col_face.assign(bone)
            else:
                col_clothes.assign(bone)

        if col_new:
            arm_data.collections.remove(col_new)

        # Set collection visibility
        visible_names = {
            "Root",
            "センター",
            "ＩＫ",
            "体(上)",
            "体(下)",
            "腕",
            "足",
            "指",
            "头发与耳朵与尾巴",
            "衣物与饰品",
        }
        for col in arm_data.collections:
            col.is_visible = col.name in visible_names

        # 5. Set active object and switch to Pose Mode
        bpy.context.view_layer.objects.active = arm_obj
        arm_obj.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")

    # 6. Hide rigidbodies and joints in outliner
    if hide_physics:
        for col in bpy.data.collections:
            if any(k in col.name.lower() for k in ["rigid", "joint"]):
                col.hide_viewport = True
                col.hide_render = True

    # 7. Configure 3D viewports to Material Preview shading
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.shading.type = "MATERIAL"

    # 8. Clean up unused/missing images
    for img in list(bpy.data.images):
        if img.filepath.endswith(".bmp") or not os.path.exists(bpy.path.abspath(img.filepath)):
            bpy.data.images.remove(img)

    # 9. Pack textures
    if pack_textures:
        try:
            bpy.ops.file.pack_all()
            print("Successfully packed textures into .blend.")
        except Exception as e:
            print(f"Warning packing textures: {e}")

    # 10. Save file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"=== Successfully saved: {output_path} ===")


if __name__ == "__main__":
    args = parse_args()
    convert_model(
        input_path=args.input,
        output_path=args.output,
        stick_bones=args.stick_bones,
        hide_physics=args.hide_physics,
        pack_textures=args.pack_textures,
    )
