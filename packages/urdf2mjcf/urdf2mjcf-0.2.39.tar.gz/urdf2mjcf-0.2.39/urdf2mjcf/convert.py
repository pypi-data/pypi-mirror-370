"""Converts URDF files to MJCF files."""

import argparse
import json
import logging
import math
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import colorlogging

from urdf2mjcf.model import ActuatorMetadata, ConversionMetadata, JointMetadata
from urdf2mjcf.postprocess.add_backlash import add_backlash
from urdf2mjcf.postprocess.add_floor import add_floor
from urdf2mjcf.postprocess.add_sensors import add_sensors
from urdf2mjcf.postprocess.base_joint import fix_base_joint
from urdf2mjcf.postprocess.collisions import update_collisions
from urdf2mjcf.postprocess.explicit_floor_contacts import add_explicit_floor_contacts
from urdf2mjcf.postprocess.make_degrees import make_degrees
from urdf2mjcf.postprocess.remove_redundancies import remove_redundancies
from urdf2mjcf.utils import save_xml

logger = logging.getLogger(__name__)

ROBOT_CLASS = "robot"


@dataclass
class ParsedJointParams:
    """Parsed joint parameters from URDF.

    Attributes:
        name: Joint name.
        type: Joint type (hinge, slide, etc.).
        lower: Lower joint limit, if any.
        upper: Upper joint limit, if any.
    """

    name: str
    type: str
    lower: float | None = None
    upper: float | None = None


@dataclass
class GeomElement:
    type: str
    size: str | None = None
    scale: str | None = None
    mesh: str | None = None


def parse_vector(s: str) -> list[float]:
    """Convert a string of space-separated numbers to a list of floats.

    Args:
        s: Space-separated string of numbers (e.g., "1 2 3").

    Returns:
        List of parsed float values.
    """
    return list(map(float, s.split()))


def quat_from_str(s: str) -> list[float]:
    """Convert a quaternion string to a list of floats.

    Args:
        s: Space-separated string of quaternion values (w x y z).

    Returns:
        List of parsed quaternion values [w, x, y, z].
    """
    return list(map(float, s.split()))


def quat_to_rot(q: list[float]) -> list[list[float]]:
    """Convert quaternion [w, x, y, z] to a 3x3 rotation matrix."""
    w, x, y, z = q
    r00 = 1 - 2 * (y * y + z * z)
    r01 = 2 * (x * y - z * w)
    r02 = 2 * (x * z + y * w)
    r10 = 2 * (x * y + z * w)
    r11 = 1 - 2 * (x * x + z * z)
    r12 = 2 * (y * z - x * w)
    r20 = 2 * (x * z - y * w)
    r21 = 2 * (y * z + x * w)
    r22 = 1 - 2 * (x * x + y * y)
    return [[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]]


def build_transform(pos_str: str, quat_str: str) -> list[list[float]]:
    """Build a 4x4 homogeneous transformation matrix from position and quaternion strings.

    Args:
        pos_str: Space-separated string of position values (x y z).
        quat_str: Space-separated string of quaternion values (w x y z).

    Returns:
        A 4x4 homogeneous transformation matrix.
    """
    pos = parse_vector(pos_str)
    q = quat_from_str(quat_str)
    r_mat = quat_to_rot(q)
    transform = [
        [r_mat[0][0], r_mat[0][1], r_mat[0][2], pos[0]],
        [r_mat[1][0], r_mat[1][1], r_mat[1][2], pos[1]],
        [r_mat[2][0], r_mat[2][1], r_mat[2][2], pos[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]
    return transform


def mat_mult(mat_a: list[list[float]], mat_b: list[list[float]]) -> list[list[float]]:
    """Multiply two 4x4 matrices A and B."""
    result = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            result[i][j] = sum(mat_a[i][k] * mat_b[k][j] for k in range(4))
    return result


def compute_min_z(body: ET.Element, parent_transform: list[list[float]] | None = None) -> float:
    """Recursively computes the minimum Z value in the world frame.

    This is used to compute the starting height of the robot.

    Args:
        body: The current body element.
        parent_transform: The transform of the parent body.

    Returns:
        The minimum Z value in the world frame.
    """
    if parent_transform is None:
        parent_transform = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    pos_str: str = body.attrib.get("pos", "0 0 0")
    quat_str: str = body.attrib.get("quat", "1 0 0 0")
    body_tf: list[list[float]] = mat_mult(parent_transform, build_transform(pos_str, quat_str))
    local_min_z: float = float("inf")

    for child in body:
        if child.tag == "geom":
            gpos_str: str = child.attrib.get("pos", "0 0 0")
            gquat_str: str = child.attrib.get("quat", "1 0 0 0")
            geom_tf: list[list[float]] = build_transform(gpos_str, gquat_str)
            total_tf: list[list[float]] = mat_mult(body_tf, geom_tf)

            # The translation part of T_total is in column 3.
            z: float = total_tf[2][3]
            geom_type: str = child.attrib.get("type", "")
            if geom_type == "box":
                size_vals: list[float] = list(map(float, child.attrib.get("size", "0 0 0").split()))
                half_height: float = size_vals[2] if len(size_vals) >= 3 else 0.0
                candidate: float = z - half_height
            elif geom_type == "cylinder":
                size_vals = list(map(float, child.attrib.get("size", "0 0").split()))
                half_length: float = size_vals[1] if len(size_vals) >= 2 else 0.0
                candidate = z - half_length
            elif geom_type == "sphere":
                r = float(child.attrib.get("size", "0"))
                candidate = z - r
            elif geom_type == "mesh":
                candidate = z
            else:
                candidate = z

            local_min_z = min(candidate, local_min_z)

        elif child.tag == "body":
            child_min: float = compute_min_z(child, body_tf)
            local_min_z = min(child_min, local_min_z)

    return local_min_z


def add_compiler(root: ET.Element) -> None:
    """Add a compiler element to the MJCF root.

    Args:
        root: The MJCF root element.
    """
    attrib = {
        "angle": "radian",
        # "eulerseq": "zyx",
        # "autolimits": "true",
    }

    element = ET.Element("compiler", attrib=attrib)
    existing_element = root.find("compiler")
    if isinstance(existing_element, ET.Element):
        root.remove(existing_element)
    root.insert(0, element)


def add_default(
    root: ET.Element,
    metadata: ConversionMetadata,
    joint_metadata: dict[str, JointMetadata] | None = None,
    actuator_metadata: dict[str, ActuatorMetadata] | None = None,
) -> None:
    """Add default settings with hierarchical structure for robot components."""
    default = ET.Element("default")

    if joint_metadata is None:
        raise ValueError("Missing joint metadata")
    if actuator_metadata is None:
        raise ValueError("Missing actuator metadata")

    # Main robot class defaults
    robot_default = ET.SubElement(default, "default", attrib={"class": ROBOT_CLASS})

    # Get the set of actuator types to make the classes at the top of the mjcf
    actuator_types = set()
    for current_joint_name, current_joint_metadata in joint_metadata.items():
        if current_joint_metadata is None:
            raise ValueError(f"Missing metadata for joint: {current_joint_name}")
        if not isinstance(current_joint_metadata, JointMetadata):
            raise ValueError(f"Metadata for joint {current_joint_name} is not a JointMetadata instance")
        actuator_types.add(current_joint_metadata.actuator_type)
        logger.info("Joint %s uses actuator type: %s", current_joint_name, current_joint_metadata.actuator_type)
    logger.info("Found %d actuator types in metadata: %s", len(actuator_types), actuator_types)

    # Create default classes for each actuator type
    for actuator_type in actuator_types:
        if actuator_type is None:
            raise ValueError(f"Actuator type: {actuator_type} cannot be None")

        sub_default = ET.SubElement(robot_default, "default", attrib={"class": str(actuator_type)})

        joint_attrib = {}
        motor_attrib = {}
        if actuator_type not in actuator_metadata:
            raise ValueError(f"Missing actuator type metadata for {actuator_type}")

        actuator_data = actuator_metadata[str(actuator_type)]
        if actuator_data.armature is not None:
            joint_attrib["armature"] = str(actuator_data.armature)
        if actuator_data.frictionloss is not None:
            joint_attrib["frictionloss"] = str(actuator_data.frictionloss)
        if actuator_data.damping is not None:
            joint_attrib["damping"] = str(actuator_data.damping)
        if actuator_data.max_torque is not None:
            joint_attrib["actuatorfrcrange"] = f"-{actuator_data.max_torque} {actuator_data.max_torque}"
            motor_attrib["ctrlrange"] = f"-{actuator_data.max_torque} {actuator_data.max_torque}"

        ET.SubElement(sub_default, "joint", attrib=joint_attrib)
        ET.SubElement(sub_default, "motor", attrib=motor_attrib)
        logger.info(
            "Added actuator class for %s: with joint attrib %s and motor attrib %s",
            actuator_type,
            joint_attrib,
            motor_attrib,
        )

    # Visual geometry class
    visual_default = ET.SubElement(
        robot_default,
        "default",
        attrib={"class": "visual"},
    )
    ET.SubElement(
        visual_default,
        "geom",
        attrib={
            "material": "visualgeom",
            "contype": "0",
            "conaffinity": "0",
            "group": "2",
        },
    )

    # Collision geometry class
    collision_default = ET.SubElement(
        robot_default,
        "default",
        attrib={"class": "collision"},
    )
    ET.SubElement(
        collision_default,
        "geom",
        attrib={
            "material": "collision_material",
            "condim": str(metadata.collision_params.condim),
            "contype": str(metadata.collision_params.contype),
            "conaffinity": str(metadata.collision_params.conaffinity),
            "priority": str(metadata.collision_params.priority),
            "group": "1",
            "solref": " ".join(f"{x:.6g}" for x in metadata.collision_params.solref),
            "solimp": " ".join(f"{x:.6g}" for x in metadata.collision_params.solimp),
            "friction": " ".join(f"{x:.6g}" for x in metadata.collision_params.friction),
        },
    )

    # Add maxhullvert for efficient collising handling.
    if metadata.maxhullvert is not None:
        ET.SubElement(default, "mesh", attrib={"maxhullvert": str(metadata.maxhullvert)})

    # Replace existing default element if present
    existing_element = root.find("default")
    if isinstance(existing_element, ET.Element):
        root.remove(existing_element)
    root.insert(0, default)


def add_contact(root: ET.Element, robot: ET.Element) -> None:
    """Add a contact element to the MJCF root.

    For each pair of adjacent links that each have collision elements, we need
    to add an exclude tag to the contact element to make sure the links do not
    collide with each other.

    Args:
        root: The MJCF root element.
        robot: The URDF robot element.
    """
    links_with_collision: dict[str, ET.Element] = {}
    for link in robot.findall("link"):
        if link.find("collision") is not None and (name := link.attrib.get("name")) is not None:
            links_with_collision[name] = link

    contact: ET.Element | None = None
    for joint in robot.findall("joint"):
        parent_link = joint.find("parent")
        child_link = joint.find("child")
        if (
            parent_link is None
            or child_link is None
            or (parent_name := parent_link.attrib.get("link")) is None
            or (child_name := child_link.attrib.get("link")) is None
        ):
            continue

        if parent_name in links_with_collision and child_name in links_with_collision:
            if contact is None:
                contact = ET.SubElement(root, "contact")

            ET.SubElement(
                contact,
                "exclude",
                attrib={
                    "body1": parent_name,
                    "body2": child_name,
                },
            )


def add_weld_constraints(root: ET.Element, metadata: ConversionMetadata) -> None:
    """Add weld constraints to the MJCF root.

    Args:
        root: The MJCF root element.
        metadata: The conversion metadata containing weld constraints.
    """
    if not metadata.weld_constraints:
        return

    equality = ET.SubElement(root, "equality")
    for weld in metadata.weld_constraints:
        ET.SubElement(
            equality,
            "weld",
            attrib={
                "body1": weld.body1,
                "body2": weld.body2,
                "solimp": " ".join(f"{x:.6g}" for x in weld.solimp),
                "solref": " ".join(f"{x:.6g}" for x in weld.solref),
            },
        )


def add_option(root: ET.Element) -> None:
    """Add an option element to the MJCF root.

    Args:
        root: The MJCF root element.
    """
    # ET.SubElement(
    #     root,
    #     "option",
    #     attrib={
    #         "integrator": "implicitfast",
    #         "cone": "elliptic",
    #         "impratio": "100",
    #     },
    # )


def add_visual(root: ET.Element) -> None:
    """Add a visual element to the MJCF root.

    Args:
        root: The MJCF root element.
    """
    # visual = ET.SubElement(root, "visual")
    # ET.SubElement(
    #     visual,
    #     "global",
    #     attrib={
    #         "ellipsoidinertia": "true",
    #     },
    # )


def add_assets(root: ET.Element, materials: dict[str, str], visualize_collision_meshes: bool = True) -> None:
    """Add texture and material assets to the MJCF root.

    Args:
        root: The MJCF root element.
        materials: Dictionary mapping material names to RGBA color strings.
        visualize_collision_meshes: If True, add a visual element for collision meshes.
    """
    asset = root.find("asset")
    if asset is None:
        asset = ET.SubElement(root, "asset")

    # Add materials from URDF
    for name, rgba in materials.items():
        ET.SubElement(
            asset,
            "material",
            attrib={
                "name": name,
                "rgba": rgba,
            },
        )

    # Add default material for visual elements without materials
    ET.SubElement(
        asset,
        "material",
        attrib={
            "name": "default_material",
            "rgba": "0.7 0.7 0.7 1",
        },
    )

    # Add blue transparent material for collision geometries
    ET.SubElement(
        asset,
        "material",
        attrib={
            "name": "collision_material",
            "rgba": "1.0 0.28 0.1 0.9" if visualize_collision_meshes else "0.0 0.0 0.0 0.0",
        },
    )


def rpy_to_quat(rpy_str: str) -> str:
    """Convert roll, pitch, yaw angles (in radians) to a quaternion (w, x, y, z)."""
    try:
        r, p, y = map(float, rpy_str.split())
    except Exception:
        r, p, y = 0.0, 0.0, 0.0
    cy = math.cos(y * 0.5)
    sy = math.sin(y * 0.5)
    cp = math.cos(p * 0.5)
    sp = math.sin(p * 0.5)
    cr = math.cos(r * 0.5)
    sr = math.sin(r * 0.5)
    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return f"{qw} {qx} {qy} {qz}"


def _get_empty_joint_and_actuator_metadata(
    robot_elem: ET.Element,
) -> tuple[dict[str, JointMetadata], dict[str, ActuatorMetadata]]:
    """Create placeholder metadata for joints and actuators if none are provided.

    Each joint is simply assigned a "motor" actuator type, which has no other parameters.
    """
    joint_meta: dict[str, JointMetadata] = {}
    for idx, joint in enumerate(robot_elem.findall("joint")):
        name = joint.attrib.get("name")
        if not name:
            continue
        joint_meta[name] = JointMetadata(
            actuator_type="motor",
            id=idx,
            nn_id=idx,
            kp=1.0,
            kd=1.0,
            soft_torque_limit=1.0,
            min_angle_deg=0.0,
            max_angle_deg=0.0,
        )

    actuator_meta = {"motor": ActuatorMetadata(actuator_type="motor")}
    return joint_meta, actuator_meta


def convert_urdf_to_mjcf(
    urdf_path: str | Path,
    mjcf_path: str | Path | None = None,
    copy_meshes: bool = False,
    metadata: ConversionMetadata | None = None,
    metadata_file: str | Path | None = None,
    *,
    joint_metadata: dict[str, JointMetadata] | None = None,
    actuator_metadata: dict[str, ActuatorMetadata] | None = None,
) -> None:
    """Converts a URDF file to an MJCF file.

    Args:
        urdf_path: The path to the URDF file.
        mjcf_path: The desired output MJCF file path.
        copy_meshes: If True, mesh files will be copied.
        metadata: Optional conversion metadata.
        metadata_file: Optional path to metadata file.
        joint_metadata: Optional joint metadata.
        actuator_metadata: Optional actuator metadata.
    """
    urdf_path = Path(urdf_path)
    mjcf_path = Path(mjcf_path) if mjcf_path is not None else urdf_path.with_suffix(".mjcf")
    if not urdf_path.exists():
        raise FileNotFoundError(f"URDF file not found: {urdf_path}")
    mjcf_path.parent.mkdir(parents=True, exist_ok=True)

    urdf_tree = ET.parse(urdf_path)
    robot = urdf_tree.getroot()
    if robot is None:
        raise ValueError("URDF file has no root element")

    if metadata_file is not None and metadata is not None:
        raise ValueError("Cannot specify both metadata and metadata_file")
    elif metadata_file is not None:
        with open(metadata_file, "r") as f:
            metadata = ConversionMetadata.model_validate_json(f.read())
    if metadata is None:
        metadata = ConversionMetadata()

    if joint_metadata is None or actuator_metadata is None:
        missing = []
        if joint_metadata is None:
            missing.append("joint")
        if actuator_metadata is None:
            missing.append("actuator")
        logger.warning("Missing %s metadata, falling back to single empty 'motor' class.", " and ".join(missing))
        joint_metadata, actuator_metadata = _get_empty_joint_and_actuator_metadata(robot)
    assert joint_metadata is not None and actuator_metadata is not None

    # Parse materials from URDF - both from root level and from link visuals
    materials: dict[str, str] = {}

    # Get materials defined at the robot root level
    for material in robot.findall("material"):
        name = material.attrib.get("name")
        if name is None:
            continue
        color = material.find("color")
        if color is not None:
            rgba = color.attrib.get("rgba")
            if rgba is not None:
                materials[name] = rgba

    # Get materials defined in link visual elements
    for link in robot.findall("link"):
        for visual in link.findall("visual"):
            visual_material = visual.find("material")
            if visual_material is None:
                continue
            name = visual_material.attrib.get("name")
            if name is None:
                continue
            color = visual_material.find("color")
            if color is not None:
                rgba = color.attrib.get("rgba")
                if rgba is not None:
                    materials[name] = rgba

    # Create a new MJCF tree root element.
    mjcf_root: ET.Element = ET.Element("mujoco", attrib={"model": robot.attrib.get("name", "converted_robot")})

    # Add compiler, assets, and default settings.
    add_compiler(mjcf_root)
    add_option(mjcf_root)
    add_visual(mjcf_root)
    add_assets(mjcf_root, materials, metadata.visualize_collision_meshes)
    add_default(mjcf_root, metadata, joint_metadata, actuator_metadata)

    # Creates the worldbody element.
    worldbody = ET.SubElement(mjcf_root, "worldbody")

    # Build mappings for URDF links and joints.
    link_map: dict[str, ET.Element] = {link.attrib["name"]: link for link in robot.findall("link")}
    parent_map: dict[str, list[tuple[str, ET.Element]]] = {}
    child_joints: dict[str, ET.Element] = {}
    for joint in robot.findall("joint"):
        parent_elem = joint.find("parent")
        child_elem = joint.find("child")
        if parent_elem is None or child_elem is None:
            logger.warning("Joint missing parent or child element")
            continue
        parent_name = parent_elem.attrib.get("link", "")
        child_name = child_elem.attrib.get("link", "")
        if not parent_name or not child_name:
            logger.warning("Joint missing parent or child link name")
            continue
        parent_map.setdefault(parent_name, []).append((child_name, joint))
        child_joints[child_name] = joint

    all_links = set(link_map.keys())
    child_links = set(child_joints.keys())
    root_links: list[str] = list(all_links - child_links)
    if not root_links:
        raise ValueError("No root link found in URDF.")
    root_link_name: str = root_links[0]

    # These dictionaries are used to collect mesh assets and actuator joints.
    mesh_assets: dict[str, str] = {}
    actuator_joints: list[ParsedJointParams] = []

    def handle_geom_element(geom_elem: ET.Element | None, default_size: str) -> GeomElement:
        """Helper to handle geometry elements safely.

        Args:
            geom_elem: The geometry element to process
            default_size: Default size to use if not specified

        Returns:
            A GeomElement instance
        """
        if geom_elem is None:
            return GeomElement(type="box", size=default_size, scale=None, mesh=None)

        box_elem = geom_elem.find("box")
        if box_elem is not None:
            size_str = box_elem.attrib.get("size", default_size)
            return GeomElement(
                type="box",
                size=" ".join(str(float(s) / 2) for s in size_str.split()),
            )

        cyl_elem = geom_elem.find("cylinder")
        if cyl_elem is not None:
            radius = cyl_elem.attrib.get("radius", "0.1")
            length = cyl_elem.attrib.get("length", "1")
            return GeomElement(
                type="cylinder",
                size=f"{radius} {float(length) / 2}",
            )

        sph_elem = geom_elem.find("sphere")
        if sph_elem is not None:
            radius = sph_elem.attrib.get("radius", "0.1")
            return GeomElement(
                type="sphere",
                size=radius,
            )

        mesh_elem = geom_elem.find("mesh")
        if mesh_elem is not None:
            filename = mesh_elem.attrib.get("filename")
            if filename is not None:
                mesh_name = Path(filename).name
                if mesh_name not in mesh_assets:
                    mesh_assets[mesh_name] = filename
                scale = mesh_elem.attrib.get("scale")
                return GeomElement(
                    type="mesh",
                    size=None,
                    scale=scale,
                    mesh=mesh_name,
                )

        return GeomElement(
            type="box",
            size=default_size,
        )

    def build_body(
        link_name: str,
        joint: ET.Element | None = None,
        actuator_joints: list[ParsedJointParams] = actuator_joints,
    ) -> ET.Element | None:
        """Recursively build a MJCF body element from a URDF link."""
        link: ET.Element = link_map[link_name]

        if joint is not None:
            origin_elem: ET.Element | None = joint.find("origin")
            if origin_elem is not None:
                pos = origin_elem.attrib.get("xyz", "0 0 0")
                rpy = origin_elem.attrib.get("rpy", "0 0 0")
                quat = rpy_to_quat(rpy)
            else:
                pos = "0 0 0"
                quat = "1 0 0 0"
        else:
            pos = "0 0 0"
            quat = "1 0 0 0"

        body: ET.Element = ET.Element("body", attrib={"name": link_name, "pos": pos, "quat": quat})

        # Add joint element if this is not the root and the joint type is not fixed.
        if joint is not None:
            jtype: str = joint.attrib.get("type", "fixed")

            if jtype in ("revolute", "continuous", "prismatic"):
                j_name: str = joint.attrib.get("name", link_name + "_joint")
                j_attrib: dict[str, str] = {"name": j_name}

                if jtype in ["revolute", "continuous"]:
                    j_attrib["type"] = "hinge"
                elif jtype == "prismatic":
                    j_attrib["type"] = "slide"
                else:
                    raise ValueError(f"Unsupported joint type: {jtype}")

                # Only for slide and hinge joints
                j_attrib["ref"] = "0.0"

                if j_name not in joint_metadata:
                    raise ValueError(f"Joint {j_name} not found in joint_metadata")
                actuator_type_value = joint_metadata[j_name].actuator_type
                j_attrib["class"] = str(actuator_type_value)
                logger.info("Joint %s assigned to class: %s", j_name, actuator_type_value)

                limit = joint.find("limit")
                if limit is not None:
                    lower_val = limit.attrib.get("lower")
                    upper_val = limit.attrib.get("upper")
                    if lower_val is not None and upper_val is not None:
                        j_attrib["range"] = f"{lower_val} {upper_val}"
                        lower_num: float | None = float(lower_val)
                        upper_num: float | None = float(upper_val)
                    else:
                        lower_num = upper_num = None
                else:
                    lower_num = upper_num = None
                axis_elem = joint.find("axis")
                if axis_elem is not None:
                    j_attrib["axis"] = axis_elem.attrib.get("xyz", "0 0 1")
                ET.SubElement(body, "joint", attrib=j_attrib)

                actuator_joints.append(
                    ParsedJointParams(
                        name=j_name,
                        type=j_attrib["type"],
                        lower=lower_num,
                        upper=upper_num,
                    )
                )

        # Process inertial information.
        inertial = link.find("inertial")
        if inertial is not None:
            inertial_elem = ET.Element("inertial")
            origin_inertial = inertial.find("origin")
            if origin_inertial is not None:
                inertial_elem.attrib["pos"] = origin_inertial.attrib.get("xyz", "0 0 0")
                rpy = origin_inertial.attrib.get("rpy", "0 0 0")
                inertial_elem.attrib["quat"] = rpy_to_quat(rpy)
            mass_elem = inertial.find("mass")
            if mass_elem is not None:
                inertial_elem.attrib["mass"] = mass_elem.attrib.get("value", "0")
            inertia_elem = inertial.find("inertia")
            if inertia_elem is not None:
                ixx = float(inertia_elem.attrib.get("ixx", "0"))
                ixy = float(inertia_elem.attrib.get("ixy", "0"))
                ixz = float(inertia_elem.attrib.get("ixz", "0"))
                iyy = float(inertia_elem.attrib.get("iyy", "0"))
                iyz = float(inertia_elem.attrib.get("iyz", "0"))
                izz = float(inertia_elem.attrib.get("izz", "0"))
                if abs(ixy) > 1e-6 or abs(ixz) > 1e-6 or abs(iyz) > 1e-6:
                    logger.warning(
                        "Warning: off-diagonal inertia terms for link '%s' are nonzero and will be ignored.",
                        link_name,
                    )
                inertial_elem.attrib["diaginertia"] = f"{ixx} {iyy} {izz}"
            body.append(inertial_elem)

        # Process collision geometries.
        collisions = link.findall("collision")
        for idx, collision in enumerate(collisions):
            origin_collision = collision.find("origin")
            if origin_collision is not None:
                pos_geom: str = origin_collision.attrib.get("xyz", "0 0 0")
                rpy_geom: str = origin_collision.attrib.get("rpy", "0 0 0")
                quat_geom: str = rpy_to_quat(rpy_geom)
            else:
                pos_geom = "0 0 0"
                quat_geom = "1 0 0 0"
            name = f"{link_name}_collision"
            if len(collisions) > 1:
                name = f"{name}_{idx}"
            collision_geom_attrib: dict[str, str] = {"name": name, "pos": pos_geom, "quat": quat_geom}

            # Get material from collision element
            collision_geom_elem: ET.Element | None = collision.find("geometry")
            if collision_geom_elem is not None:
                geom = handle_geom_element(collision_geom_elem, "1 1 1")
                collision_geom_attrib["type"] = geom.type
                if geom.type == "mesh":
                    if geom.mesh is not None:
                        collision_geom_attrib["mesh"] = geom.mesh
                elif geom.size is not None:
                    collision_geom_attrib["size"] = geom.size
                if geom.scale is not None:
                    collision_geom_attrib["scale"] = geom.scale
            collision_geom_attrib["class"] = "collision"
            ET.SubElement(body, "geom", attrib=collision_geom_attrib)

        # Process visual geometries.
        visuals = link.findall("visual")
        for idx, visual in enumerate(visuals):
            origin_elem = visual.find("origin")
            if origin_elem is not None:
                pos_geom = origin_elem.attrib.get("xyz", "0 0 0")
                rpy_geom = origin_elem.attrib.get("rpy", "0 0 0")
                quat_geom = rpy_to_quat(rpy_geom)
            else:
                pos_geom = "0 0 0"
                quat_geom = "1 0 0 0"
            name = f"{link_name}_visual"
            if len(visuals) > 1:
                name = f"{name}_{idx}"
            visual_geom_attrib: dict[str, str] = {"name": name, "pos": pos_geom, "quat": quat_geom}

            # Get material from visual element
            material_elem = visual.find("material")
            if material_elem is not None:
                material_name = material_elem.attrib.get("name")
                if material_name in materials:
                    visual_geom_attrib["material"] = material_name
                else:
                    visual_geom_attrib["material"] = "default_material"
            else:
                visual_geom_attrib["material"] = "default_material"

            visual_geom_elem: ET.Element | None = visual.find("geometry")
            if visual_geom_elem is not None:
                geom = handle_geom_element(visual_geom_elem, "1 1 1")
                visual_geom_attrib["type"] = geom.type
                if geom.type == "mesh":
                    if geom.mesh is not None:
                        visual_geom_attrib["mesh"] = geom.mesh
                elif geom.size is not None:
                    visual_geom_attrib["size"] = geom.size
                if geom.scale is not None:
                    visual_geom_attrib["scale"] = geom.scale
            visual_geom_attrib["class"] = "visual"
            ET.SubElement(body, "geom", attrib=visual_geom_attrib)

        # Recurse into child links.
        if link_name in parent_map:
            for child_name, child_joint in parent_map[link_name]:
                child_body = build_body(child_name, child_joint, actuator_joints)
                if child_body is not None:
                    body.append(child_body)
        return body

    # Build the robot body hierarchy starting from the root link.
    robot_body = build_body(root_link_name, None, actuator_joints)
    if robot_body is None:
        raise ValueError("Failed to build robot body")

    # Gets the minimum z coordinate of the robot body.
    min_z: float = compute_min_z(robot_body)
    computed_offset: float = -min_z + metadata.height_offset
    logger.info("Auto-detected base offset: %s (min z = %s)", computed_offset, min_z)

    # Moves the robot body to the computed offset.
    body_pos = robot_body.attrib.get("pos", "0 0 0")
    body_pos = [float(x) for x in body_pos.split()]
    body_pos[2] += computed_offset
    robot_body.attrib["pos"] = " ".join(f"{x:.8f}" for x in body_pos)

    robot_body.attrib["childclass"] = ROBOT_CLASS
    worldbody.append(robot_body)

    # Add a site to the root link for sensors
    root_site_name = f"{root_link_name}_site"
    ET.SubElement(
        robot_body,
        "site",
        attrib={"name": root_site_name, "pos": "0 0 0", "quat": "1 0 0 0"},
    )

    # Replace the actuator block with one that uses positional control.
    actuator_elem = ET.SubElement(mjcf_root, "actuator")
    for actuator_joint in actuator_joints:
        # The class name is the actuator type
        attrib: dict[str, str] = {"joint": actuator_joint.name}
        if actuator_joint.name not in joint_metadata:
            raise ValueError(f"Actuator {actuator_joint.name} not found in joint_metadata")
        actuator_type_value = joint_metadata[actuator_joint.name].actuator_type

        attrib["class"] = str(actuator_type_value)
        logger.info(f"Creating actuator {actuator_joint.name}_ctrl with class: {actuator_type_value}")

        ET.SubElement(actuator_elem, "motor", attrib={"name": f"{actuator_joint.name}_ctrl", **attrib})

    # Add mesh assets to the asset section before saving
    asset_elem: ET.Element | None = mjcf_root.find("asset")
    if asset_elem is None:
        asset_elem = ET.SubElement(mjcf_root, "asset")
    for mesh_name, filename in mesh_assets.items():
        ET.SubElement(asset_elem, "mesh", attrib={"name": mesh_name, "file": filename})

    add_contact(mjcf_root, robot)

    # Add weld constraints if specified in metadata
    add_weld_constraints(mjcf_root, metadata)

    # Copy mesh files if requested.
    if copy_meshes:
        urdf_dir: Path = urdf_path.parent.resolve()
        target_mesh_dir: Path = (mjcf_path.parent / "meshes").resolve()
        target_mesh_dir.mkdir(parents=True, exist_ok=True)
        for mesh_name, filename in mesh_assets.items():
            source_path: Path = (urdf_dir / filename).resolve()
            target_path: Path = target_mesh_dir / Path(filename).name
            if source_path != target_path:
                shutil.copy2(source_path, target_path)

    # Save the initial MJCF file
    save_xml(mjcf_path, ET.ElementTree(mjcf_root))

    # Apply post-processing steps
    if metadata.angle != "radian":
        assert metadata.angle == "degree", "Only 'radian' and 'degree' are supported."
        make_degrees(mjcf_path)
    if metadata.backlash:
        add_backlash(mjcf_path, metadata.backlash, metadata.backlash_damping)
    if metadata.floating_base:
        fix_base_joint(mjcf_path, metadata.freejoint)
    if metadata.remove_redundancies:
        remove_redundancies(mjcf_path)
    if (collision_geometries := metadata.collision_geometries) is not None:
        update_collisions(mjcf_path, collision_geometries)
    if metadata.add_floor:
        add_floor(mjcf_path, floor_name=metadata.floor_name)
    if (explicit_contacts := metadata.explicit_contacts) is not None:
        add_explicit_floor_contacts(
            mjcf_path,
            contact_links=explicit_contacts.contact_links,
            class_name=explicit_contacts.class_name,
            floor_name=metadata.floor_name,
        )
    add_sensors(mjcf_path, root_link_name, metadata=metadata)


def main() -> None:
    """Parse command-line arguments and execute the URDF to MJCF conversion."""
    parser = argparse.ArgumentParser(description="Convert a URDF file to an MJCF file.")

    parser.add_argument(
        "urdf_path",
        type=str,
        help="The path to the URDF file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="The path to the output MJCF file.",
    )
    parser.add_argument(
        "--copy-meshes",
        action="store_true",
        help="Copy mesh files to the output MJCF directory.",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        help="A JSON string containing conversion metadata (joint params and sensors).",
    )
    parser.add_argument(
        "--metadata-file",
        type=str,
        help="A JSON file containing conversion metadata (joint params and sensors).",
    )
    parser.add_argument(
        "--log-level",
        type=int,
        default=logging.INFO,
        help="The log level to use.",
    )
    args = parser.parse_args()

    colorlogging.configure(level=args.log_level)

    # Parse the raw metadata from the command line arguments.
    raw_metadata: dict | None = None
    if args.metadata_file is not None and args.metadata is not None:
        raise ValueError("Cannot specify both --metadata and --metadata-file")
    elif args.metadata_file is not None:
        with open(args.metadata_file, "r") as f:
            raw_metadata = json.load(f)
    elif args.metadata is not None:
        raw_metadata = json.loads(args.metadata)
    elif (metadata_path := Path(args.urdf_path).parent / "metadata.json").exists():
        logger.warning("Using metadata from %s", metadata_path)
        with open(metadata_path, "r") as f:
            raw_metadata = json.load(f)

    metadata: ConversionMetadata | None = (
        None if raw_metadata is None else ConversionMetadata.model_validate(raw_metadata, strict=True)
    )

    convert_urdf_to_mjcf(
        urdf_path=args.urdf_path,
        mjcf_path=args.output,
        copy_meshes=args.copy_meshes,
        metadata=metadata,
    )


if __name__ == "__main__":
    main()
